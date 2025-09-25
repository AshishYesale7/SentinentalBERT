# Local PostgreSQL Setup Guide for SentinelBERT

This guide helps you configure SentinelBERT to use your local PostgreSQL database instead of Docker containers.

## 🎯 Overview

The application has been configured to connect to your local PostgreSQL database with these settings:

- **Host**: localhost
- **Port**: 5432
- **Database**: sentinelbert
- **User**: sentinel
- **Password**: sentinel_native_2024

## 📋 Prerequisites

1. **PostgreSQL installed and running** on your local machine
2. **Python environment** with required packages
3. **Node.js** (for React frontend)

## 🚀 Setup Steps

### 1. Verify PostgreSQL is Running

**On macOS (Homebrew):**
```bash
brew services list | grep postgresql
brew services start postgresql@15  # or your version
```

**On Ubuntu/Debian:**
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

**On Windows:**
```bash
# Check if PostgreSQL service is running in Services app
# Or use pg_ctl if installed via installer
```

### 2. Create Database and User

Connect to PostgreSQL as superuser and run:

```sql
-- Connect as postgres user
psql -U postgres

-- Create user and database
CREATE USER sentinel WITH PASSWORD 'sentinel_native_2024';
CREATE DATABASE sentinelbert OWNER sentinel;
GRANT ALL PRIVILEGES ON DATABASE sentinelbert TO sentinel;

-- Exit
\q
```

### 3. Test Database Connection

Run the connection test script:

```bash
cd /path/to/SentinentalBERT
python test_local_db_connection.py
```

### 4. Setup Database Schema (Optional)

If you want to use the full database features:

```bash
python setup_local_db.py
```

### 5. Start Services

**Option A: Native Deployment (Recommended)**
```bash
./native-deploy.sh
```

**Option B: Docker with Local Database**
```bash
docker-compose -f docker-compose.local.yml up
```

## 🔧 Configuration Files

### Environment Configuration (.env)
```bash
# Database Configuration - Local PostgreSQL
DB_HOST=localhost
DB_NAME=sentinelbert
DB_USER=sentinel
DB_PASSWORD=sentinel_native_2024
DB_PORT=5432
DATABASE_URL=postgresql://sentinel:sentinel_native_2024@localhost:5432/sentinelbert
POSTGRES_PASSWORD=sentinel_native_2024
```

### Docker Compose for Local DB
- `docker-compose.local.yml` - Excludes PostgreSQL container
- Uses local PostgreSQL via host networking

## 🌐 Service URLs

After successful deployment:

- **Streamlit Dashboard**: http://localhost:12000
- **React Frontend**: http://localhost:12001
- **NLP Service**: http://localhost:8000
- **Backend API**: http://localhost:8080 (if using Docker)

## 🔍 Troubleshooting

### Connection Refused Error
```
connection to server at "localhost", port 5432 failed: Connection refused
```

**Solutions:**
1. Start PostgreSQL service
2. Check if PostgreSQL is listening on port 5432:
   ```bash
   netstat -an | grep 5432
   # or
   lsof -i :5432
   ```

### Authentication Failed
```
FATAL: password authentication failed for user "sentinel"
```

**Solutions:**
1. Verify user exists: `psql -U postgres -c "\du"`
2. Reset password: `ALTER USER sentinel PASSWORD 'sentinel_native_2024';`
3. Check pg_hba.conf for authentication method

### Database Does Not Exist
```
FATAL: database "sentinelbert" does not exist
```

**Solutions:**
1. Create database: `CREATE DATABASE sentinelbert OWNER sentinel;`
2. List databases: `psql -U postgres -c "\l"`

### Permission Denied
```
ERROR: permission denied for database sentinelbert
```

**Solutions:**
1. Grant privileges: `GRANT ALL PRIVILEGES ON DATABASE sentinelbert TO sentinel;`
2. Make user owner: `ALTER DATABASE sentinelbert OWNER TO sentinel;`

## 📊 Database Schema

The application uses these main components:

1. **SQLite Cache** (`data/tracking_cache.db`) - For local caching
2. **PostgreSQL** (optional) - For advanced features:
   - Viral tracking sessions
   - Post analysis data
   - Evidence collection
   - User management

## 🔄 Switching Back to Docker

To switch back to Docker PostgreSQL:

1. Use original docker-compose.yml:
   ```bash
   docker-compose up
   ```

2. Update .env to use container database:
   ```bash
   DB_HOST=postgres  # container name
   ```

## 📝 Custom Configuration

To use different database credentials:

1. Update `.env` file with your settings
2. Run `python test_local_db_connection.py` to verify
3. Restart services

## 🆘 Support

If you encounter issues:

1. Check PostgreSQL logs: `tail -f /var/log/postgresql/postgresql-*.log`
2. Verify network connectivity: `telnet localhost 5432`
3. Test with psql directly: `psql -h localhost -U sentinel -d sentinelbert`

## 🎉 Success Indicators

You'll know everything is working when:

- ✅ Database connection test passes
- ✅ Services start without database errors
- ✅ Streamlit dashboard loads at http://localhost:12000
- ✅ No connection errors in service logs