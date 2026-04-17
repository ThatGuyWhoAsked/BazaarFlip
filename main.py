#!/usr/bin/env python3
import argparse
import requests
import time
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table

console = Console()

API_URL = "https://api.hypixel.net/v2/skyblock/bazaar"
API_KEY = os.environ.get("HYPIXEL_API_KEY", "")
TAX_RATE = 0.0125
POLL_INTERVAL = 60
MIN_MARGIN_PCT = 1.0
MIN_WEEKLY_VOLUME = 10000
MIN_SELL_ORDERS = 3
TOP_N = 15


def fetch_bazaar():
    if not API_KEY:
        raise Exception("HYPIXEL_API_KEY environment variable not set")
    headers = {"API-Key": API_KEY}
    response = requests.get(API_URL, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise Exception("API key invalid or rate limited")
    return data["products"]


def calculate_flip(product_id, stats):
    sell_price = stats.get("sellPrice", 0)  # Highest Buy Order
    buy_price = stats.get("buyPrice", 0)    # Lowest Sell Offer
    sell_orders = stats.get("sellOrders", 0)
    buy_orders = stats.get("buyOrders", 0)
    sell_moving_week = stats.get("sellMovingWeek", 0)
    buy_moving_week = stats.get("buyMovingWeek", 0)

    if sell_price <= 0 or buy_price <= 0:
        return None

    # Order-to-order flipping strategy:
    # 1. Place Buy Order at highest_buy_order + 0.1
    # 2. Place Sell Offer at lowest_sell_offer - 0.1
    buy_at = sell_price + 0.1
    sell_at = buy_price - 0.1
    
    if sell_at <= buy_at:
        return None

    # Weekly volume (conservative estimate: the lower of the two fill rates)
    weekly_volume = min(sell_moving_week, buy_moving_week)
    if weekly_volume < MIN_WEEKLY_VOLUME:
        return None

    if sell_orders < MIN_SELL_ORDERS:
        return None

    # Margin calculation after tax
    revenue = sell_at * (1 - TAX_RATE)
    profit_per = revenue - buy_at
    margin_pct = (profit_per / buy_at) * 100
    
    if margin_pct < MIN_MARGIN_PCT:
        return None

    # Total potential weekly profit
    profit_potential = profit_per * weekly_volume

    return {
        "name": product_id.replace("_", " ").title(),
        "buy_at": buy_at,
        "sell_at": sell_at,
        "buy_price_raw": sell_price,
        "sell_price_raw": buy_price,
        "margin": sell_at - buy_at,
        "margin_pct": margin_pct,
        "profit_per": profit_per,
        "weekly_volume": weekly_volume,
        "profit_potential": profit_potential,
        "sell_orders": sell_orders,
        "buy_orders": buy_orders,
    }


def process_products(products):
    flips = []
    for product_id, product_data in products.items():
        stats = product_data.get("quick_status", {})
        flip = calculate_flip(product_id, stats)
        if flip:
            flips.append(flip)

    flips.sort(key=lambda x: x["profit_potential"], reverse=True)
    return flips


def format_coins(value):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}k"
    return f"{value:.2f}"


def format_price(value):
    if value >= 1000:
        return f"{value:,.0f}"
    elif value >= 1:
        return f"{value:.1f}"
    return f"{value:.2f}"


def render_table(flips, total_items):
    table = Table(title=f"Bazaar Flipper — Top {TOP_N} Opportunities")

    table.add_column("Item", style="cyan", no_wrap=True)
    table.add_column("Buy At", justify="right", style="yellow")
    table.add_column("Sell At", justify="right", style="green")
    table.add_column("Margin", justify="right")
    table.add_column("Vol/Week", justify="right")
    table.add_column("Est. Profit", justify="right", style="bold green")

    for flip in flips[:TOP_N]:
        table.add_row(
            flip["name"],
            format_price(flip["buy_at"]),
            format_price(flip["sell_at"]),
            f"[green]{flip['margin_pct']:.1f}%[/green]",
            format_coins(flip["weekly_volume"]),
            format_coins(flip["profit_potential"]),
        )

    return table


def main(once=False):
    if once:
        try:
            products = fetch_bazaar()
            flips = process_products(products)
            table = render_table(flips, len(products))
            console.print(table)
            console.print(f"\n[dim]Tracking {len(products)} products[/dim]")
        except requests.RequestException as e:
            console.print(f"[red]Error fetching data: {e}[/red]")
            raise SystemExit(1)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise SystemExit(1)
        return

    console.clear()
    console.print("[bold cyan]Hypixel Bazaar Flipper[/bold cyan]", justify="center")
    console.print(
        "Polling every 60s | Filters: margin>1%, vol>10k, sellOrders>3\n", style="dim"
    )

    while True:
        try:
            start_time = time.time()
            products = fetch_bazaar()
            flips = process_products(products)

            console.clear()
            console.print(
                "[bold cyan]Hypixel Bazaar Flipper[/bold cyan]", justify="center"
            )
            console.print(
                f"Last update: {datetime.now().strftime('%H:%M:%S')}", style="dim"
            )

            if flips:
                table = render_table(flips, len(products))
                console.print(table)
                console.print(
                    f"\n[dim]Tracking {len(products)} products | Best: {flips[0]['name']} ({flips[0]['margin_pct']:.1f}%)[/dim]"
                )
            else:
                console.print(
                    "[yellow]No flip opportunities found with current filters[/yellow]"
                )

        except requests.RequestException as e:
            console.print(f"[red]Error fetching data: {e}[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

        elapsed = time.time() - start_time
        sleep_time = max(0, POLL_INTERVAL - elapsed)
        time.sleep(sleep_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hypixel Bazaar Flipper")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()
    main(once=args.once)
