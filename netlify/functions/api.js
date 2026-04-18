const fetch = require('node-fetch');

const TAX_RATE = 0.0125;
const COFLNET_BZ_SPREAD_URL = "https://sky.coflnet.com/api/flip/bazaar/spread";
const COFLNET_CRAFT_URL = "https://sky.coflnet.com/api/craft/profit";
const COFLNET_KAT_PROFIT_URL = "https://sky.coflnet.com/api/kat/profit";

const katCache = { data: null, timestamp: 0 };
const KAT_CACHE_DURATION = 3 * 60 * 1000;

function cleanMinecraftText(text) {
    if (!text) return "";
    return text.replace(/§[0-9a-fk-or]/g, '');
}

async function fetchBazaarFlips() {
    try {
        const res = await fetch(COFLNET_BZ_SPREAD_URL, { timeout: 8000 });
        const data = await res.json();
        
        return data.map(item => {
            const f = item.flip || {};
            const buyAt = f.sellPrice || 0;
            const sellAt = f.buyPrice || 0;
            
            if (buyAt <= 0 || sellAt <= 0) return null;
            
            const revenue = sellAt * (1 - TAX_RATE);
            const profitPer = revenue - buyAt;
            const marginPct = buyAt > 0 ? (profitPer / buyAt * 100) : 0;
            
            return {
                productId: f.itemTag,
                name: cleanMinecraftText(item.itemName || f.itemTag || "Unknown"),
                buyAt: Math.round(buyAt * 100) / 100,
                sellAt: Math.round(sellAt * 100) / 100,
                marginPct: Math.round(marginPct * 10) / 10,
                profitPotential: Math.round(profitPer * (f.volume || 0)),
                profitPerHour: Math.round((f.profitPerHour || 0) * 100) / 100,
                weeklyVolume: Math.floor(f.volume || 0),
                isManipulated: item.isManipulated || false,
                manipulationReason: item.isManipulated ? "Potential Manipulation" : null
            };
        }).filter(f => f !== null);
    } catch (e) {
        console.error("Bazaar API Error:", e);
        return [];
    }
}

async function fetchCraftFlips(player, profile) {
    try {
        let url = COFLNET_CRAFT_URL;
        const params = new URLSearchParams();
        if (player) params.append("player", player);
        if (profile) params.append("profile", profile);
        if (params.toString()) url += `?${params.toString()}`;

        const res = await fetch(url, { timeout: 8000 });
        const data = await res.json();
        
        return data.map(item => {
            const sellPrice = item.sellPrice || 0;
            const craftCost = item.craftCost || 0;
            const profit = sellPrice - craftCost;
            const marginPct = craftCost > 0 ? (profit / craftCost * 100) : 0;
            
            const requirements = [];
            if (item.reqCollection) {
                requirements.push({
                    name: item.reqCollection.name || "Unknown",
                    level: item.reqCollection.level || 0,
                    type: "Collection"
                });
            }
            if (item.reqSlayer) {
                requirements.push({
                    name: item.reqSlayer.name || "Unknown",
                    level: item.reqSlayer.level || 0,
                    type: "Slayer"
                });
            }
            
            return {
                productId: item.itemId,
                name: cleanMinecraftText(item.itemName || item.itemId || "Unknown"),
                sellPrice: Math.round(sellPrice * 100) / 100,
                craftCost: Math.round(craftCost * 100) / 100,
                profit: Math.round(profit * 100) / 100,
                marginPct: Math.round(marginPct * 10) / 10,
                volume: Math.floor(item.volume || 0),
                requirements: requirements,
                ingredients: (item.ingredients || []).map(ing => ({
                    name: cleanMinecraftText((ing.itemId || "Unknown").replace(/_/g, ' ')),
                    count: ing.count || 0
                }))
            };
        }).sort((a, b) => b.profit - a.profit);
    } catch (e) {
        console.error("Craft API Error:", e);
        return [];
    }
}

async function fetchKatFlips() {
    try {
        const now = Date.now();
        if (katCache.data && (now - katCache.timestamp) < KAT_CACHE_DURATION) {
            return katCache.data;
        }

        const res = await fetch(COFLNET_KAT_PROFIT_URL, { timeout: 10000 });
        const data = await res.json();

        const katFlips = data.map(item => ({
            name: item.name || item.coreData?.name || "Unknown Pet",
            fromRarity: item.coreData?.baseRarity || item.fromRarity || "UNKNOWN",
            toRarity: item.targetRarity || "UNKNOWN",
            purchaseCost: Math.round(item.purchaseCost || 0),
            materialCost: Math.round(item.materialCost || 0),
            median: Math.round(item.median || 0),
            profit: Math.round(item.profit || 0),
            volume: Math.floor(item.volume || 0),
            hours: item.hours || 0,
            materials: item.materials || item.coreData?.materials || {}
        }));

        katCache.data = katFlips;
        katCache.timestamp = now;

        return katFlips;
    } catch (e) {
        console.error("KAT API Error:", e);
        return katCache.data || [];
    }
}

exports.handler = async (event) => {
    const player = event.queryStringParameters.player || "";
    const profile = event.queryStringParameters.profile || "";
    
    console.log(`Fetching flips for ${player} (${profile})`);
    
    const [bazaarFlips, craftFlips, katFlips] = await Promise.all([
        fetchBazaarFlips(),
        fetchCraftFlips(player, profile),
        fetchKatFlips()
    ]);

    return {
        statusCode: 200,
        headers: { 
            "Content-Type": "application/json",
            "Cache-Control": "public, max-age=55"
        },
        body: JSON.stringify({
            success: true,
            updated: new Date().toISOString(),
            totalProducts: bazaarFlips.length,
            flips: bazaarFlips,
            craftFlips: craftFlips,
            katFlips: katFlips
        })
    };
};