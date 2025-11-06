# NewsAPI Fetcher Strategy

This project demonstrates a simple Strategy Pattern implementation for fetching news from **NewsAPI**.

## Files
- `news_fetcher_strategy.py`: Abstract base class defining the strategy interface.
- `newsapi_fetcher.py`: Concrete implementation that interacts with NewsAPI.
- `main.py`: Example runner that fetches and saves news data.

## Setup
1. Install dependencies:
   ```bash
   pip install requests
   ```

2. Set your NewsAPI key:
   **Windows (PowerShell):**
   ```powershell
   [Environment]::SetEnvironmentVariable("NEWSAPI_API_KEY", "158dd6c63c814c8ca1489577f1e269df", "User")
   ```
   **macOS/Linux:**
   ```bash
   export NEWSAPI_API_KEY="158dd6c63c814c8ca1489577f1e269df"
   ```

3. Run:
   ```bash
   python main.py
   ```

The script will:
- Fetch top articles about Artificial Intelligence.
- Print the first 3 titles.
- Save all results to a date-stamped JSON file.
