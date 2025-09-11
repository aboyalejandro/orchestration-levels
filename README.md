# Piwik ETL

Simple ETL script that extracts data from Piwik API (sessions, events, query) and saves as JSON files.

## Quick Start

1. **Setup environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Piwik credentials
   ```

2. **Run locally:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

3. **Docker:**
   ```bash
   # Build the image
   docker build -t piwik-etl .
   
   # Run with .env file (outputs to container only)
   docker run --env-file .env piwik-etl
   
   # Run with output mounted to local directory (RECOMMENDED)
   docker run --env-file .env -v $(pwd)/output:/app/output piwik-etl
   ```

## Environment Variables

```
AUTH_URL=https://your-piwik-instance.piwik.pro/auth/token
BASE_URL=https://your-piwik-instance.piwik.pro/api/analytics/v1/
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
WEBSITE_ID=your_website_id
```

## Output

Creates `output/2021-01-01_to_2021-03-30/` with:
- `sessions.json`
- `events.json` 
- `query.json`

## Automation

### Cron Setup (Local)
1. **Be in project root:** `/Users/alejandroaboy/Desktop/orchestration-levels`
2. **Test script first:** 
   ```bash
   source venv/bin/activate
   python main.py
   ```
3. **Add to cron:** `crontab -e`
4. **In the cron editor (vi):**
   - Press `i` (insert mode)
   - Add this exact line:
   ```
   */5 * * * * /bin/bash -c "cd /Users/alejandroaboy/Desktop/orchestration-levels && source venv/bin/activate && python main.py"
   ```
   - Press `Esc`, type `:wq`, press Enter
5. **Verify:** `crontab -l`
6. **Check it works:** `ls -la output/` (after 5 minutes)

### GitHub Actions
- Runs daily at 2 AM UTC (see `.github/workflows/etl.yml`)
- Manual trigger available in Actions tab