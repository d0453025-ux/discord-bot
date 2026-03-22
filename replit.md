# Discord Price Bot

A Discord bot for displaying Robux prices, turf prices, and game links.

## Setup

- **Language**: Python 3.12
- **Library**: discord.py 2.x
- **Secrets**: `DISCORD_TOKEN` — your Discord bot token

## Features

- `/prices` — Shows a price menu with reaction buttons
- `/normal_prices` — Shows Robux price list
- `/turf_prices` — Shows turf prices
- `/game_links` — Shows game and Discord links
- Reaction-based navigation: react with 1️⃣, 2️⃣, or 3️⃣ on the price menu to get a DM with details

## Configuration

Edit the price/link values at the top of `main.py` in the clearly marked sections.

## Running

The bot is configured as a console workflow (`python main.py`). It uses slash commands and does not require any privileged gateway intents.
