# Orchestration Levels - Piwik ETL

Simple ETL script that extracts data from Piwik API (sessions, events, query) and saves as JSON files.

## If you want to follow along, you will need:
- Docker Desktop
- A Piwik PRO Demo Account (To Get API KEYS) - Check [docs](https://help.piwik.pro/support/questions/generate-api-credentials/)
- AWS Account with S3 bucket, IAM role with ECR/S3 access policies - Check [docs](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-push-iam.html)

## Quick Start

1. **Setup environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Piwik credentials
   ```

2. **Run with Docker:**
   ```bash
   # Build the image
   docker build -t piwik-etl .
   
   # Run with .env attached
   docker run --rm --env-file .env piwik-etl
   ```

## Automation

## Cron Setup (Local with Virtual Environment)
1. **Be in project root:** `/your-path/orchestration-levels`
2. **Test script first:** 
   ```bash
   python -m venv venv
   source venv/bin/activate
   python main.py --local # Will export the files on piwik-data path
   ```
3. **Add to cron:** `crontab -e`
4. **In the cron editor (vi):**
   - Press `i` (insert mode)
   - Add this exact line:
   ```
   */5 * * * * /bin/bash -c "cd /your-path/orchestration-levels && source venv/bin/activate && python main.py"
   ```
   - Press `Esc`, type `:wq`, press Enter
5. **Verify:** `crontab -l`
6. **Check it works:** `ls -la piwik-data/` (after 5 minutes)
7. **Remove all cron jobs:** `crontab -r`

This is the expected output:

```bash
(venv) ➜  orchestration-levels git:(main) ✗ crontab -e
crontab: no crontab for alejandroaboy - using an empty one
crontab: installing new crontab
(venv) ➜  orchestration-levels git:(main) ✗ crontab -l
*/5 * * * * /bin/bash -c "cd Users/Desktop/alejandroaboy/orchestration-levels && source venv/bin/ activate && python main.py
(venv) ➜  orchestration-levels git:(main) ✗ ls -la piwik-data/
total 0
drwxr-xr-x   4 alejandroaboy  staff  128 25 sep 20:23 .
drwxr-xr-x@ 17 alejandroaboy  staff  544 25 sep 20:23 ..
-rw-r--r--   1 alejandroaboy  staff    0 25 sep 20:20 .gitkeep
drwxr-xr-x   3 alejandroaboy  staff   96 25 sep 20:22 2021
(venv) ➜  orchestration-levels git:(main) ✗ 
```

What this means:

  - drwxr-xr-x = Directory permissions (d = directory, rwx = read/write/execute for
  owner, r-x = read/execute for group/others)
  - -rw-r--r-- = File permissions (- = regular file, rw- = read/write for owner, r-- =
  read-only for group/others)
  - 4, 7, 1, 3 = Number of hard links
  - alejandroaboy staff = Owner and group
  - 128, 544, 0, 96 = File/directory size in bytes
  - Date/time = Last modification time



## GitHub Actions
- Runs daily at 2 AM UTC (see `.github/workflows/etl.yml`)
- Manual trigger available in Actions tab
- Your `.env` creds need to be configured as Action Secrets - [Check docs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)

