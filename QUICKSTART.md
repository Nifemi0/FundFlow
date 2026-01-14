# 🚀 FundFlow - Quick Start Guide

## Prerequisites

Before you begin, ensure you have:
- Python 3.11 or higher
- PostgreSQL 14+ (or use Docker)
- Redis 7+ (or use Docker)

## Installation

### Option 1: Docker (Recommended for Quick Start)

1. **Clone and navigate to the project:**
```bash
cd fundflow
```

2. **Set up environment variables:**
```bash
cp config/.env.example config/.env
```

3. **Edit `config/.env` and add your API keys:**
```bash
nano config/.env
```

Required keys:
- `TELEGRAM_BOT_TOKEN` - Get from [@BotFather](https://t.me/botfather)
- `CRYPTORANK_API_KEY` - Get from [CryptoRank](https://cryptorank.io/api)

Optional keys (for Phase 2):
- `TWITTER_BEARER_TOKEN`
- `GITHUB_TOKEN`
- `NEWSAPI_KEY`

4. **Start database services:**
```bash
docker-compose up -d postgres redis
```

5. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

6. **Initialize the database:**
```bash
python init.py
```

7. **Start the bot:**
```bash
python bot/main.py
```

### Option 2: Manual Setup (Local PostgreSQL/Redis)

1. **Install PostgreSQL and Redis:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql redis-server

# macOS
brew install postgresql redis
```

2. **Create database:**
```bash
sudo -u postgres psql
CREATE DATABASE fundflow;
CREATE USER fundflow WITH PASSWORD 'fundflow';
GRANT ALL PRIVILEGES ON DATABASE fundflow TO fundflow;
\q
```

3. **Follow steps 2-7 from Option 1**

## Getting API Keys

### Telegram Bot Token
1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Follow the prompts to name your bot
4. Copy the token provided

### CryptoRank API Key
1. Go to [CryptoRank API](https://cryptorank.io/api)
2. Sign up for an account
3. Navigate to your dashboard
4. Generate an API key
5. Copy the key

*Note: Free tier should be sufficient for initial testing*

## Using the Bot

### 1. Start a conversation with your bot
Search for your bot name in Telegram and click "Start"

### 2. Try these commands:

**Get recent funding rounds:**
```
/latest
/latest 30  # Last 30 days
```

**Search for projects:**
```
/search uniswap
/search "compound finance"
```

**View full project report:**
```
/report optimism
```

**Research an investor:**
```
/investor paradigm
/investor "a16z crypto"
```

**Get funding statistics:**
```
/stats
/stats 90  # Last 90 days
```

**Set alerts on projects:**
```
/watch ethereum
/unwatch ethereum
```

## Running the Scraper

The bot includes automatic data collection via scrapers. To manually run:

```python
python scrapers/cryptorank.py
```

To schedule regular updates, you can use cron or systemd timers:

```bash
# Run scraper every 6 hours
0 */6 * * * cd /path/to/fundflow && python scrapers/cryptorank.py
```

## Troubleshooting

### "Database connection failed"
- Ensure PostgreSQL is running: `sudo systemctl status postgresql`
- Check credentials in `config/.env`
- Verify DATABASE_URL format: `postgresql://user:password@localhost:5432/dbname`

### "Telegram bot token invalid"
- Double-check token in `config/.env`
- Ensure no extra spaces or quotes
- Token format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### "CryptoRank API error"
- Verify API key is correct
- Check rate limits (free tier: 100 requests/day)
- Test API key at [CryptoRank docs](https://api-docs.cryptorank.io/)

### "No data returned from scraper"
- CryptoRank API might be rate-limited
- Check scraper logs in `logs/`
- Try again after 1 hour

## Development Tips

### View database contents:
```bash
psql postgresql://fundflow:fundflow@localhost:5432/fundflow

# List tables
\dt

# Query projects
SELECT name, sector, grade_letter FROM projects LIMIT 10;

# Query recent funding
SELECT p.name, fr.amount_raised, fr.announced_date 
FROM funding_rounds fr 
JOIN projects p ON fr.project_id = p.id 
ORDER BY fr.announced_date DESC 
LIMIT 10;
```

### View logs:
```bash
tail -f logs/fundflow_*.log
```

### Reset database:
```bash
python init.py  # Re-run initialization
```

## Next Steps

Once you have the MVP running:

1. **Collect initial data:** Let the scraper run for a few days to build up historical data
2. **Test all commands:** Try each bot command to ensure everything works
3. **Invite researchers:** Share the bot with a small group for feedback
4. **Monitor usage:** Check logs for errors and usage patterns
5. **Plan Phase 2:** Based on feedback, prioritize next features

## Support

For issues or questions:
- Check `README.md` for detailed documentation
- Review logs in `logs/` directory
- Check database with PostgreSQL client

## Production Deployment

For production use:

1. **Use environment-specific configs:**
```bash
export ENVIRONMENT=production
export DEBUG=False
```

2. **Set up monitoring:**
- Application logs → CloudWatch/Datadog
- Database backups → Daily automated backups
- Health checks → Uptime monitoring

3. **Secure API keys:**
- Use secrets manager (AWS Secrets Manager, HashiCorp Vault)
- Never commit `.env` to git
- Rotate keys regularly

4. **Scale infrastructure:**
- Use managed PostgreSQL (RDS, DigitalOcean Managed DB)
- Use managed Redis (ElastiCache, Redis Cloud)
- Deploy bot on VPS or container service

---

**Happy researching! 🚀**
