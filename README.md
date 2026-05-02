# 🎯 Deal Sniper

A modular, config-driven deal tracker for Python and Railway.

## 🛠 Configuration (Filters)

All settings are stored in `filters.yaml`.

### How to Modify Filters
1. Open `filters.yaml`.
2. **Keywords**: Add strings to the `rfd_keywords` list. The sniper is case-insensitive.
3. **Thresholds**: Change `rfd_min_votes` or `steam_min_discount`.
4. **Speed**: Change `check_interval_seconds` to control how often the scouts run.

### Deployment on Railway
1. **GitHub**: Push this repo to GitHub.
2. **Railway Service**: Create a new "Empty Service" or "GitHub Repo" service.
3. **Variables**: Add `DISCORD_WEBHOOK_URL` to your Service Variables.
4. **Nixpacks**: The included `nixpacks.toml` handles Playwright and browser dependencies automatically.

## 📁 Project Structure
- `main.py`: The orchestrator.
- `scouts/`: Add your scraping scripts here.
- `filters.yaml`: Your settings.
- `deals.db`: SQLite database (auto-created).

## 🚀 Adding New Sites
Check out the [Scouts README](scouts/README.md) for instructions on extending the sniper.
