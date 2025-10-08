# PulseAI Deployment Guide

Complete guide for local setup and deployment of PulseAI.

## Table of Contents

- [Environment Setup](#environment-setup)
- [Local Development](#local-development)
- [Testing](#testing)
- [Services](#services)
- [Production Deployment](#production-deployment)
- [Database Setup](#database-setup)
  - [Database Migrations](#database-migrations)
- [Monitoring](#monitoring)

## Environment Setup

### Prerequisites
- Python 3.11+
- Git
- Supabase account
- OpenAI API key (optional)
- DeepL API key (optional)
- Telegram Bot Token (for bot functionality)

### Installation Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/denius89/news_ai_bot.git
   cd news_ai_bot
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```
   
   Fill in the following variables in `.env`:
   ```bash
   # Required: Supabase Configuration
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   
   # Optional: AI Services
   OPENAI_API_KEY=your_openai_api_key
   DEEPL_API_KEY=your_deepl_api_key
   
   # Optional: Telegram Bot
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   
   # Optional: Environment
   ENV=development
   ```
   
   **Note:** Currently everything runs locally (Python + Supabase), no Docker required.

5. **Verify Installation**
   ```bash
   python -c "import supabase; print('Supabase client imported successfully')"

## Local Development

### Quick Start with .env
```bash
# Load environment variables and run services
ENV=.env python -m telegram_bot.bot    # Start Telegram bot
ENV=config_files/.env python src/webapp.py             # Start web application
ENV=config_files/.env python src/main.py --digest 5    # Generate digest manually
```

### Web Application
```bash
python src/webapp.py
```
Access at: [http://localhost:5000](http://localhost:5000)

### CLI Application
```bash
# Process news from all sources
python src/main.py --source all --limit 20

# Generate digest
python src/main.py --digest 5

# Generate AI digest
python src/main.py --digest 5 --ai
```

### Development Commands (Makefile)
```bash
# Run bot
make run-bot

# Run web application
make run-web

# Run tests
make test

# Run linter
make lint

# Format code
make format

# Run all checks
make check
```

## Testing

### Unit Tests (Fast)
```bash
pytest -m "not integration"
```

### Integration Tests (Requires DB)
```bash
pytest -m integration
```

### Test Coverage
```bash
pytest --cov --cov-report=term-missing
```

## Services

### News ETL Pipeline
```bash
# Fetch and store news
python tools/fetch_and_store_news.py --limit 20

# View stored news
python tools/show_news.py --limit 10
```

### Events Parser
```bash
# Parse economic calendar
python tools/fetch_and_store_events.py
```

### Telegram Bot
```bash
# Start Telegram bot
python -m telegram_bot.bot
```

## Production Deployment

### Render Deployment

1. **Create Web Service**
   - Go to [Render](https://render.com)
   - Create new Web Service
   - Connect GitHub repository

2. **Environment Variables**
   Add the following secrets in Render dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `OPENAI_API_KEY`
   - `DEEPL_API_KEY`
   - `TELEGRAM_BOT_TOKEN`

3. **Build Configuration**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn webapp:app`

### Background Jobs (ETL)

For periodic news and events parsing, use **Render Cron Jobs** or **Linux CRON**:

**Linux CRON Example (every 30 minutes):**
```bash
*/30 * * * * cd /path/to/news_ai_bot && venv/bin/python tools/fetch_and_store_news.py
```

**Render Cron Job:**
- Create Cron Job service
- Set schedule: `*/30 * * * *`
- Command: `python tools/fetch_and_store_news.py`

## Database Setup

### Supabase Configuration

1. **Create Project**
   - Go to [Supabase](https://supabase.com)
   - Create new project

2. **Database Schema**
   Execute the following SQL in Supabase SQL Editor:

   ```sql
   -- News table
   CREATE TABLE IF NOT EXISTS news (
       uid TEXT PRIMARY KEY,
       title TEXT NOT NULL,
       content TEXT,
       link TEXT,
       published_at TIMESTAMPTZ,
       source TEXT,
       category TEXT,
       credibility NUMERIC,
       importance NUMERIC
   );

   -- Events table
   CREATE TABLE IF NOT EXISTS events (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       title TEXT NOT NULL,
       country TEXT,
       currency TEXT,
       importance INTEGER,
       event_time TIMESTAMPTZ,
       fact TEXT,
       forecast TEXT,
       previous TEXT,
       source TEXT,
       created_at TIMESTAMPTZ DEFAULT NOW()
   );

   -- Users table (for future features)
   CREATE TABLE IF NOT EXISTS users (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       telegram_id BIGINT UNIQUE,
       created_at TIMESTAMPTZ DEFAULT NOW()
   );

   -- Subscriptions table (for future features)
   CREATE TABLE IF NOT EXISTS subscriptions (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID REFERENCES users(id),
       category TEXT,
       created_at TIMESTAMPTZ DEFAULT NOW()
   );
   ```

3. **API Keys**
   - Copy `SUPABASE_URL` and `SUPABASE_KEY` to your `.env` file

### Database Migrations

#### Local Development with Supabase CLI

1. **Install Supabase CLI**
   ```bash
   # macOS
   brew install supabase/tap/supabase
   
   # Linux
   curl -fsSL https://supabase.com/install.sh | sh
   
   # Windows
   scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
   scoop install supabase
   ```

2. **Initialize Supabase Project**
   ```bash
   # Initialize Supabase in your project directory
   supabase init
   
   # Link to your remote project
   supabase link --project-ref YOUR_PROJECT_REF
   ```

3. **Create and Apply Migrations**
   ```bash
   # Create new migration
   supabase migration new subscriptions_notifications
   
   # Copy SQL from database/migrations/2025_10_02_subscriptions_notifications.sql
   # to the generated migration file
   
   # Apply migration to remote database
   supabase db push
   ```

4. **Migration Files Location**
   - Local migrations: `supabase/migrations/`
   - Project migrations: `database/migrations/`
   - Copy SQL from project migrations to Supabase CLI migrations

#### Row Level Security (RLS)

**Option 1: Service Key (Recommended for Telegram Bot)**
- If using service key in bot, RLS can remain disabled
- Service key bypasses RLS policies
- Simpler setup for Telegram bot integration

**Option 2: RLS Enabled**
- Enable RLS on tables if using auth.uid() policies
- Configure policies for authenticated users
- More complex but more secure for web applications

```sql
-- Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Example policy for authenticated users
CREATE POLICY "Users can view own data" ON users
FOR ALL USING (auth.uid()::text = telegram_id::text);
```

#### Migration Examples

**Users, Subscriptions, and Notifications Tables:**
```bash
# Create migration
supabase migration new subscriptions_notifications

# Copy content from database/migrations/2025_10_02_subscriptions_notifications.sql
# Then apply:
supabase db push
```

**Published Date Migration:**
```bash
# Create migration
supabase migration new published_at_datetime

# Copy content from database/migrations/2025_10_01_published_at_datetime.sql
# Then apply:
supabase db push
```

## Monitoring

### Logging
- Application logs are written to `logs/app.log`
- Log rotation is configured (max 1MB, 3 backups)
- Log levels: DEBUG, INFO, WARNING, ERROR

### Health Checks
- Web application: `GET /health`
- Database connectivity: Check Supabase dashboard
- Bot status: Monitor bot logs

### Performance Monitoring
- Database query performance via Supabase dashboard
- Application response times
- Error rates and patterns

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify `SUPABASE_URL` and `SUPABASE_KEY`
   - Check Supabase project status
   - Verify network connectivity

2. **AI API Errors**
   - Check `OPENAI_API_KEY` validity
   - Verify API quota and limits
   - Monitor API response times

3. **Telegram Bot Issues**
   - Verify `TELEGRAM_BOT_TOKEN`
   - Check bot permissions
   - Monitor webhook/polling status

4. **Import Errors**
   - Ensure virtual environment is activated
   - Verify all dependencies are installed
   - Check Python version compatibility

### Support
- Check logs in `logs/app.log`
- Review error messages in console
- Verify environment variables
- Test individual components separately