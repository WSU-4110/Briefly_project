# TheNewsAPI Fetcher Strategy

This project demonstrates a Strategy Pattern implementation to fetch news from **TheNewsAPI**.

## Files
- `news_fetcher_strategy.py` — Abstract base class defining the interface.
- `thenewsapi_fetcher.py` — Concrete class using TheNewsAPI.
- `main.py` — Example script to run the fetcher.

## Setup
1. Install dependencies:
   ```bash
   pip install requests
   ```

2. Set your API key:

   **Windows (PowerShell):**
   ```powershell
   [Environment]::SetEnvironmentVariable("THENEWSAPI_KEY", "imJkBOBm28B4wskKKdWH582f2TLTGMlHWVKutN9z", "User")
   ```

   **macOS/Linux:**
   ```bash
   export THENEWSAPI_KEY="imJkBOBm28B4wskKKdWH582f2TLTGMlHWVKutN9z"
   ```

3. Run the script:
   ```bash
   python main.py
   ```

The script fetches 20 articles about "Artificial Intelligence" and saves them into a date-stamped JSON file.
