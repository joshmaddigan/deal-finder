# 🕵️ How to Manage Scouts

This directory contains the "Scouts" - modular scripts that check for deals.

## How to Add a New Scout
1. **Create a Python file**: Create `scouts/my_new_site_scout.py`.
2. **Implement `check_deals(config)`**: Every scout MUST have this function.
   ```python
   def check_deals(config):
       # Your logic here
       # Use config.get('your_custom_key') for settings
       pass
   ```
3. **Import Utilities**: Use `from database import is_new_deal, save_deal` and `from notifier import send_deal`.
4. **Done**: The engine will automatically detect and run your new scout on the next cycle.

## How to Disable a Scout
- **Option A (Remove)**: Delete the file or move it out of the `scouts/` directory.
- **Option B (Rename)**: Rename the file to end in anything other than `.py` (e.g., `rfd_scout.py.disabled`).
- **Option C (Comment Out)**: Use the engine to check for a "disabled" flag in `filters.yaml` if you want to get fancy, but renaming is the easiest "Vibe" way.

## Best Practices
- **Persistence**: Always check `is_new_deal(id)` before notifying.
- **Error Handling**: Wrap your logic in `try/except` to prevent one bad scout from crashing the whole engine.
- **Timing**: Don't use `time.sleep()` inside a scout; the engine handles the interval.
