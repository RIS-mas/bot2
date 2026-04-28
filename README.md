# ENLIGHTEN COMMUNITY Discord Bot

Production-ready Discord bot built with `discord.py` using prefix commands (`>`), embed-only responses, invite tracking, and JSON persistence.

## Features
- Commission/tax calculators
- Invite attribution tracking (old vs new invite uses)
- Price list management (admin-only mutation)
- Vouch system
- Clean modular code with Cogs
- Centralized embed style
- Error handling + logging

## Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create your env file:
   ```bash
   cp .env.example .env
   ```
4. Set your token in `.env`:
   ```env
   DISCORD_TOKEN=your_real_token
   ```
5. Run the bot:
   ```bash
   python bot.py
   ```

## Notes on Invite Tracking
- On startup, the bot caches all guild invites.
- On member join, it compares cached uses vs current uses to detect the invite used.
- Handles edge cases:
  - Vanity URLs (`guild.vanity_url_code`)
  - Unknown invite attribution
  - Cache recovery after restarts

## Data Files
Created automatically in `data/`:
- `invite_data.json` : `{ "user_id": "inviter_id" }`
- `prices.json` : service prices
- `vouches.json` : vouch entries by user

## Required Discord Settings
- Enable **Server Members Intent** in Discord Developer Portal.
- Ensure bot has permission to view invites in each guild for invite tracking.
