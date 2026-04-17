const fetch = require('node-fetch');

const TAX_RATE = 0.0125;
const COFLNET_BZ_SPREAD_URL = "https://sky.coflnet.com/api/flip/bazaar/spread";
const COFLNET_CRAFT_URL = "https://sky.coflnet.com/api/craft/profit";

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
            
            return {
                productId: item.itemId,
                name: cleanMinecraftText(item.itemName || item.itemId || "Unknown"),
                sellPrice: Math.round(sellPrice * 100) / 100,
                craftCost: Math.round(craftCost * 100) / 100,
                profit: Math.round(profit * 100) / 100,
                marginPct: Math.round(marginPct * 10) / 10,
                volume: Math.floor(item.volume || 0),
                requirements: (item.requirements || []).map(req => ({
                    name: req.name || "Unknown",
                    level: req.level || 0
                })),
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

exports.handler = async (event) => {
    const player = event.queryStringParameters.player || "";
    const profile = event.queryStringParameters.profile || "";
    
    console.log(`Fetching flips for ${player} (${profile})`);
    
    const [bazaarFlips, craftFlips] = await Promise.all([
        fetchBazaarFlips(),
        fetchCraftFlips(player, profile)
    ]);

    return {
        statusCode: 200,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            success: true,
            updated: new Date().toISOString(),
            totalProducts: bazaarFlips.length,
            flips: bazaarFlips,
            craftFlips: craftFlips
        })
    };
};