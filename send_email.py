import os
import requests
from datetime import datetime, timedelta

from dotenv import load_dotenv
import yfinance as yf

# load environment file if present
load_dotenv()

# configuration via environment variables
API_KEY = os.getenv("API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_FROM = os.getenv("MAILGUN_FROM")
MAILGUN_TO = os.getenv("MAILGUN_TO")

if not API_KEY or not MAILGUN_DOMAIN or not MAILGUN_FROM or not MAILGUN_TO:
    raise RuntimeError("Please set API_KEY, MAILGUN_DOMAIN, MAILGUN_FROM, and MAILGUN_TO in the environment or .env file")


def fetch_stock_report(tickers):
    """Fetch yesterday's close and computes percentage move for each ticker."""
    end = datetime.now()
    start = end - timedelta(days=5)
    data = yf.download(tickers, start=start, end=end, progress=False)
    report_lines = []
    # data['Close'] is a DataFrame with tickers as columns
    closes = data["Close"].dropna()
    yesterday = closes.index.max()
    previous = closes.index[closes.index != yesterday].max()
    for symbol in tickers:
        try:
            y_close = closes.loc[yesterday, symbol]
            p_close = closes.loc[previous, symbol]
            pct = (y_close - p_close) / p_close * 100
            report_lines.append(
                f"{symbol}: {p_close:.2f} -> {y_close:.2f} ({pct:+.2f}%)"
            )
        except Exception as e:
            report_lines.append(f"{symbol}: data unavailable ({e})")
    report = "\n".join(report_lines)
    return report


def send_simple_message(subject: str, text: str):
    return requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        # use the API_KEY variable loaded from environment; no hardcoded fallback
        auth=("api", API_KEY),
        data={
            "from": MAILGUN_FROM,
            "to": MAILGUN_TO,
            "subject": subject,
            "text": text,
        },
    )


def main():
    tickers = ["AAPL", "MA", "WDC"]
    text = fetch_stock_report(tickers)
    subj = f"Stock movement report for {datetime.now().date() - timedelta(days=1)}"
    print("Report text:\n", text)
    response = send_simple_message(subj, text)
    print("Mailgun response status", response.status_code)
    print(response.text)


if __name__ == "__main__":
    import sys
    # allow running as scheduled daemon
    if "--daemon" in sys.argv:
        try:
            import schedule
            import time
            import zoneinfo
        except ImportError:
            print("Missing scheduling dependencies. Install with `pip install schedule`.")
            sys.exit(1)
        # schedule for 10:00 IST daily
        ist = zoneinfo.ZoneInfo("Asia/Kolkata")
        # schedule library uses local time; adjust environment or compute next run
        # We'll assume system local time is IST, else schedule may run at wrong hour.
        schedule.every().day.at("10:00").do(main)
        print("Scheduler started, hitting 10:00 IST daily. Press Ctrl+C to exit.")
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        main()