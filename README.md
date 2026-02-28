# Mailgun Stock Report

This project fetches the previous trading day's closing prices for a list of tickers (AAPL, MA, WDC) using `yfinance` and sends a report via Mailgun.

## Usage

1. **Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
   The `requirements.txt` file should contain:
   ```txt
   requests
   yfinance
   schedule  # only needed for daemon mode
   ```

2. **Run once:**
   ```sh
   python send_email.py
   ```
   This prints the report and sends the email immediately.

3. **Run daily at 10:00 AM IST:**
   ```sh
   python send_email.py --daemon
   ```
   The script will continue running, dispatching the report every day at 10:00 India Standard Time. Make sure your machine's local timezone is set to IST, or adjust the scheduling logic accordingly.

4. **Alternatively (Windows Task Scheduler)**
   You can schedule the script using Task Scheduler instead of `--daemon` mode. Create a task that runs:
   ```sh
   python "D:\Documents\Python Projects\Mailgun\send_email.py"
   ```
   daily at 04:30 UTC (10:00 IST).

## GitHub Repository

To push this code to GitHub:

1. Create a new repository on GitHub (e.g. `Mailgun-stock-report`).
2. In this local directory run:
   ```sh
   git remote add origin https://github.com/<your-username>/Mailgun-stock-report.git
   git push -u origin master
   ```

Alternatively, install the GitHub CLI (`gh`) and run:
```sh
gh repo create Mailgun-stock-report --public --source=. --remote=origin --push
```

## Environment

- Python 3.11+
- Windows (tested) but should work on macOS/Linux

Configuration is now read from environment variables, with support for a `.env` file (ignored by git).

Create a `.env` in the project root containing:
```ini
API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=your-domain.mailgun.org
MAILGUN_FROM="You <you@example.com>"
MAILGUN_TO="Your Name <your.email@example.com>"
```

Alternatively you can still set the variables in your shell:
```sh
export API_KEY="your-key-here"    # Unix-like
setx API_KEY "your-key-here"      # Windows
```

---

## GitHub Actions (automated daily email)

This repository includes a GitHub Actions workflow at `.github/workflows/daily_report.yml` that runs daily at 10:00 AM IST (04:30 UTC). The workflow expects the following repository secrets to be set:

- `API_KEY` — your Mailgun API key
- `MAILGUN_DOMAIN` — your Mailgun domain
- `MAILGUN_FROM` — email sender (e.g. "You <you@example.com>")
- `MAILGUN_TO` — recipient (e.g. "Your Name <your.email@example.com>")

Set the secrets in the repository settings (Settings → Secrets and variables → Actions) or via the GitHub CLI:

```powershell
# example (interactive) using gh:
gh secret set API_KEY --body "<your-key>"
gh secret set MAILGUN_DOMAIN --body "your-domain.mailgun.org"
gh secret set MAILGUN_FROM --body "You <you@example.com>"
gh secret set MAILGUN_TO --body "Your Name <your.email@example.com>"
```

You can manually trigger the workflow from the Actions tab or run:

```powershell
gh workflow run daily_report.yml
```

The workflow installs Python, installs dependencies from `requirements.txt`, and runs `python send_email.py`.

Feel free to expand tickers or formatting as needed.