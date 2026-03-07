# ScraperFC API - Sports Match Aggregation Backend

A production-ready REST API and synchronization service for aggregating sports match data from multiple sources. Built on top of the ScraperFC scraping library, this service provides a unified API for consuming match data across multiple sports with automated synchronization.

## 🏗️ Architecture Overview

This project transforms ScraperFC into a complete backend service with:

- **FastAPI REST API** for querying match data
- **Automated synchronization** every 5 minutes using APScheduler
- **PostgreSQL/Supabase database** for data persistence
- **Deduplication engine** to prevent duplicate records across sources
- **Provider abstraction** for multiple data sources
- **Docker-ready** with health checks
- **Coolify compatible** for easy deployment

## 📊 Database Structure

### Tables

- **sports**: Sports/modalities (football, basketball, etc.)
- **leagues**: Competitions/championships with canonical names
- **teams**: Teams/clubs with deduplication
- **matches**: Match records with status, scores, and metadata
- **external_mappings**: Source ID tracking for deduplication
- **sync_runs**: Synchronization job history and status

### Key Features

- Canonical name normalization for deduplication
- External ID mapping to track records across sources
- Unique constraints to prevent duplicate matches
- Optimized indexes for common queries
- 30-day history window (past and future)

## 🚀 Quick Start

### Local Development with Docker Compose

1. **Clone the repository**
```bash
git clone <repository-url>
cd ScraperFC
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Access the API**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Local Development without Docker

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -e .
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Run the application**
```bash
python -m uvicorn app.main:app --reload --port 8000
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Application
APP_ENV=production
PORT=8000
LOG_LEVEL=INFO

# Database (Option 1: Complete URL)
DATABASE_URL=postgresql://user:password@host:port/database

# Database (Option 2: Components)
SUPABASE_DB_HOST=db.your-project.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=your_user
SUPABASE_DB_PASSWORD=your_password

# Sync Settings
SYNC_INTERVAL_MINUTES=5
HISTORY_DAYS_PAST=30
HISTORY_DAYS_FUTURE=30

# Providers
ENABLE_SOFASCORE=true
ENABLE_FBREF=false
```

### Critical Configuration Notes

- **NEVER** commit `.env` or credentials to version control
- Use `DATABASE_URL` for simplicity or individual components for flexibility
- Adjust `SYNC_INTERVAL_MINUTES` based on your needs (minimum: 1 minute)
- `ENABLE_FBREF=false` by default (slower due to rate limiting)

## 🔌 API Endpoints

### Health & Status

- `GET /health` - Service health check
- `GET /sync/status` - Synchronization status
- `GET /sync/history` - Recent sync job history
- `POST /sync/run` - Manually trigger sync

### Data Queries

- `GET /sports` - List all sports
- `GET /leagues?sport=football` - List leagues (optional sport filter)
- `GET /teams/search?q=barcelona` - Search teams
- `GET /matches/today` - Today's matches
- `GET /matches/date/2026-03-10` - Matches for specific date
- `GET /matches/range?start=2026-03-01&end=2026-03-15` - Date range
- `GET /matches/search?team=flamengo` - Search by team
- `GET /matches/{id}` - Get match details

### Filtering

Most endpoints support filters:
- `sport`: Sport key (e.g., "football")
- `league`: League name (partial match)
- `status`: Match status (scheduled, live, finished, postponed, cancelled)

### Pagination

Range endpoints support pagination:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50, max: 100)

## 📅 Automatic Synchronization

The service automatically syncs data every 5 minutes (configurable):

1. Fetches matches from 30 days ago to 30 days ahead
2. Creates new matches
3. Updates existing matches (scores, status)
4. Prevents duplicates using canonical names and external IDs
5. Logs all operations

### Sync Logic

- **Scheduled matches**: Fetched and stored
- **Live matches**: Updated each sync cycle
- **Finished matches**: Updated for a period after completion
- **Deduplication**: Same match from multiple sources = single record

## 🐳 Deployment to Coolify

### Prerequisites

- Coolify instance running
- Supabase/PostgreSQL database ready

### Steps

1. **In Coolify, create new service**
   - Type: Docker Compose or Dockerfile
   - Repository: Your Git repository
   - Branch: main

2. **Set environment variables**
   ```
   APP_ENV=production
   PORT=8000
   DATABASE_URL=postgresql://user:pass@host:port/db
   SYNC_INTERVAL_MINUTES=5
   HISTORY_DAYS_PAST=30
   HISTORY_DAYS_FUTURE=30
   ENABLE_SOFASCORE=true
   LOG_LEVEL=INFO
   ```

3. **Configure service**
   - Port: 8000
   - Health check: `/health`
   - Build context: `.`
   - Dockerfile: `Dockerfile`

4. **Deploy**
   - Coolify will build and deploy automatically
   - Monitor logs for startup

5. **Verify**
   - Access `https://your-domain.com/health`
   - Check `https://your-domain.com/docs` for API documentation

### Coolify Tips

- Enable automatic deployments on push
- Set up custom domain with SSL
- Monitor resource usage
- Configure backup for database
- Use Coolify's logs viewer for debugging

## 🔄 How Synchronization Works

```
┌─────────────────┐
│   Scheduler     │ Every 5 minutes
│  (APScheduler)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Sync Service   │ Orchestrates sync
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Providers    │ Sofascore, FBref, etc.
│   (Pluggable)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Dedup Service   │ Canonical names
│                 │ External mappings
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Database     │ Supabase/Postgres
└─────────────────┘
```

## 🧩 Multi-Sport Support

Currently implemented:
- **Football/Soccer** ⚽ (Primary focus, fully supported)

Architecture ready for:
- Basketball 🏀
- Volleyball 🏐
- Tennis 🎾
- Others...

### Adding a New Sport

1. Create provider in `app/services/providers/`
2. Implement `BaseProvider` interface
3. Register in `ProviderRegistry`
4. Add sport configuration
5. Test with sample data

## 🛠️ Technical Stack

- **Python 3.11+**
- **FastAPI** - Modern async web framework
- **SQLAlchemy** - ORM for database
- **Pydantic** - Data validation
- **APScheduler** - Background jobs
- **PostgreSQL** - Database
- **Docker** - Containerization
- **Uvicorn** - ASGI server

## 📝 Data Sources

Current providers:

### Sofascore ✅
- Primary provider for football
- Real-time match data
- Extensive league coverage
- Status updates

### FBref ⚠️
- Available but disabled by default
- Rate-limited (requires wait time)
- Detailed match statistics
- Enable with `ENABLE_FBREF=true`

## 🔍 Deduplication Strategy

The service prevents duplicates using:

1. **Canonical names**: Normalized names for leagues and teams
2. **External mappings**: Track IDs from each source
3. **Match fingerprinting**: League + teams + datetime
4. **Time windows**: 2-hour tolerance for same match
5. **Unique constraints**: Database-level protection

## 🐛 Troubleshooting

### Database connection fails
```bash
# Check DATABASE_URL format
DATABASE_URL=postgresql://user:password@host:port/database

# Test connection
psql $DATABASE_URL
```

### Sync not running
```bash
# Check logs
docker logs scraperfc_api

# Verify scheduler status
curl http://localhost:8000/sync/status
```

### No matches appearing
```bash
# Manually trigger sync
curl -X POST http://localhost:8000/sync/run

# Check sync history
curl http://localhost:8000/sync/history
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Sync Status
```bash
curl http://localhost:8000/sync/status
```

### Recent Sync Runs
```bash
curl http://localhost:8000/sync/history?limit=10
```

## 🚧 Limitations & Future Work

### Current Limitations

- Sofascore as primary source (others available but limited)
- Football as main sport (architecture ready for others)
- No odds/betting data (by design)
- 30-day rolling window (configurable)

### Planned Improvements

- [ ] Additional providers (ESPN, FlashScore, etc.)
- [ ] Enhanced team matching algorithms
- [ ] Player data integration
- [ ] Advanced filtering and search
- [ ] Webhook notifications
- [ ] GraphQL API option
- [ ] Performance optimizations
- [ ] Automated tests

## 📄 License

Same as original ScraperFC project. See LICENSE file.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/docs`

## ⚠️ Important Notes

- **Never hardcode credentials** - always use environment variables
- **Test locally first** before deploying to production
- **Monitor resource usage** - scraping can be resource-intensive
- **Respect rate limits** - sources may block excessive requests
- **Backup your database** regularly

---

**Original ScraperFC Library**: This API builds on the excellent ScraperFC library for web scraping. The original library documentation and features are still available in the `src/ScraperFC/` directory.

For the original library documentation, see: https://scraperfc.readthedocs.io
