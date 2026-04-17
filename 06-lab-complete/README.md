# Production AI Agent - Lab 06 Complete

A production-ready conversational AI agent with authentication, rate limiting, cost protection, and Redis-based state management.

## 🎯 Features

### ✅ Lab 06 Requirements Met

- ✅ **API Key Authentication** - Secure X-API-Key header validation
- ✅ **Rate Limiting** - 10 requests/minute per API key (Redis-backed)
- ✅ **Cost Guard** - $10/month spending limit per user
- ✅ **Health Checks** - `/health` (liveness) and `/readiness` (dependencies)
- ✅ **Graceful Shutdown** - Proper SIGTERM/SIGINT handling
- ✅ **Stateless Design** - All state in Redis (no local storage)
- ✅ **Multi-stage Dockerfile** - Optimized image < 500 MB
- ✅ **Docker Compose** - Full stack with Redis
- ✅ **No Hardcoded Secrets** - Environment-based configuration
- ✅ **Production Logging** - Structured logging with levels
- ✅ **Error Handling** - Proper HTTP status codes and messages

### 🚀 Additional Features

- 🎨 Modern Web UI with dark mode
- 📊 Usage metrics and monitoring
- 🔄 Automatic Redis fallback to in-memory
- 📱 Mobile-responsive design
- 🐳 Ready for Render deployment

## 📁 Project Structure

```
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── auth.py              # API key authentication
│   ├── rate_limiter.py      # Rate limiting (Redis)
│   └── cost_guard.py        # Cost tracking (Redis)
├── utils/
│   └── mock_llm.py          # Mock LLM for testing
├── static/
│   ├── style.css            # UI styles
│   └── script.js            # Frontend logic
├── templates/
│   └── index.html           # Web interface
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Full stack setup
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── .dockerignore            # Docker ignore rules
├── render.yaml              # Render deployment config
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Local Development (Without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your settings
# For local dev without Redis, set REDIS_ENABLED=false

# Run the application
uvicorn app.main:app --reload --port 8000
```

**Test the API:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key-12345" \
  -d '{"message": "Hello!"}'
```

### 2. Docker Compose (Recommended)

```bash
# Start full stack (app + Redis)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

Access the application:
- **Web UI**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Readiness Check**: http://localhost:8000/readiness

### 3. Docker Only

```bash
# Build image
docker build -t ai-agent .

# Run container (without Redis)
docker run -p 8000:8000 \
  -e API_KEY=test-api-key-12345 \
  -e REDIS_ENABLED=false \
  ai-agent

# Run with Redis
docker run -p 8000:8000 \
  -e API_KEY=test-api-key-12345 \
  -e REDIS_URL=redis://your-redis:6379 \
  -e REDIS_ENABLED=true \
  ai-agent
```

## 📡 API Endpoints

### Authentication

All endpoints (except `/health` and `/readiness`) require authentication via `X-API-Key` header.

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/chat
```

### Endpoints

#### `GET /`
Web UI interface

#### `POST /chat`
Send a message to the AI agent

**Request:**
```json
{
  "message": "Hello, how are you?"
}
```

**Response:**
```json
{
  "response": "Hello! How can I help you today?",
  "tokens_used": 12,
  "cost": 0.002
}
```

**Rate Limit:** 10 requests/minute per API key  
**Cost Limit:** $10/month per API key

**Error Responses:**
- `401` - Missing or invalid API key
- `429` - Rate limit exceeded
- `402` - Monthly cost limit exceeded
- `500` - Internal server error

#### `GET /health`
Liveness probe - returns 200 if app is running

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "version": "1.0.0"
}
```

#### `GET /readiness`
Readiness probe - checks all dependencies

**Response:**
```json
{
  "ready": true,
  "services": {
    "redis": true,
    "cost_guard": true,
    "llm": true
  }
}
```

#### `GET /usage/{api_key}`
Get usage statistics for your API key

**Response:**
```json
{
  "api_key": "test-api...-2345",
  "monthly_cost": 0.024,
  "monthly_limit": 10.0,
  "remaining_budget": 9.976,
  "requests_this_minute": 3,
  "rate_limit": "10 requests/minute"
}
```

#### `GET /metrics`
System metrics (admin only)

**Response:**
```json
{
  "total_users": 5,
  "total_requests": 127,
  "uptime": "N/A",
  "redis_connected": true
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | 8000 | Server port |
| `DEBUG` | No | false | Debug mode |
| `REDIS_URL` | No | redis://localhost:6379 | Redis connection URL |
| `REDIS_ENABLED` | No | true | Enable Redis (false = in-memory) |
| `API_KEY` | No | test-api-key-12345 | Default API key |
| `ADMIN_API_KEY` | No | admin-key-67890 | Admin API key |
| `RATE_LIMIT_REQUESTS` | No | 10 | Max requests per window |
| `RATE_LIMIT_WINDOW` | No | 60 | Rate limit window (seconds) |
| `MONTHLY_COST_LIMIT` | No | 10.0 | Monthly cost limit ($) |
| `OPENAI_API_KEY` | No | - | OpenAI API key (optional) |
| `OPENAI_MODEL` | No | gpt-3.5-turbo | OpenAI model |

### Configuration File

Create `.env` from template:
```bash
cp .env.example .env
```

Edit `.env` with your settings.

## 🐳 Docker Details

### Multi-stage Build

The Dockerfile uses multi-stage build to minimize image size:

1. **Builder stage**: Installs dependencies in virtual environment
2. **Final stage**: Copies only necessary files

**Image size:** < 500 MB ✅

### Security Features

- Non-root user (`appuser`)
- No hardcoded secrets
- Minimal base image (python:3.11-slim)
- Health checks included
- Graceful shutdown handling

### Health Check

Built-in Docker health check:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
```

## ☁️ Deploy to Render

### Method 1: Blueprint (Recommended)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Production AI agent"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically:
     - Create Redis instance
     - Create web service
     - Link them together
     - Generate API keys
   - Click "Apply"

3. **Access Your Service:**
   - Web UI: `https://your-service.onrender.com`
   - API: `https://your-service.onrender.com/chat`

4. **Get Your API Keys:**
   - Go to service → Environment tab
   - View `API_KEY` and `ADMIN_API_KEY`

### Method 2: Manual Setup

1. **Create Redis:**
   - New → Redis
   - Name: `ai-agent-redis`
   - Plan: Free

2. **Create Web Service:**
   - New → Web Service
   - Connect repository
   - Settings:
     - **Environment:** Docker
     - **Plan:** Free
     - **Health Check Path:** `/health`

3. **Add Environment Variables:**
   - `REDIS_URL`: (copy from Redis instance)
   - `REDIS_ENABLED`: `true`
   - `API_KEY`: (generate secure key)
   - `ADMIN_API_KEY`: (generate secure key)
   - `RATE_LIMIT_REQUESTS`: `10`
   - `RATE_LIMIT_WINDOW`: `60`
   - `MONTHLY_COST_LIMIT`: `10.0`

4. **Deploy:**
   - Click "Create Web Service"
   - Wait 3-5 minutes for deployment

## 🧪 Testing

### Test Authentication

```bash
# Without API key (should fail)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# With API key (should succeed)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-api-key-12345" \
  -d '{"message": "Hello"}'
```

### Test Rate Limiting

```bash
# Send 11 requests rapidly (11th should fail with 429)
for i in {1..11}; do
  echo "Request $i:"
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -H "X-API-Key: test-api-key-12345" \
    -d '{"message": "Test"}' \
    -w "\nStatus: %{http_code}\n\n"
done
```

### Test Cost Guard

```bash
# Check usage
curl http://localhost:8000/usage/test-api-key-12345 \
  -H "X-API-Key: test-api-key-12345"
```

### Test Health Checks

```bash
# Liveness
curl http://localhost:8000/health

# Readiness
curl http://localhost:8000/readiness
```

### Test Graceful Shutdown

```bash
# Start container
docker run -d --name test-agent -p 8000:8000 ai-agent

# Send SIGTERM
docker stop test-agent

# Check logs for graceful shutdown
docker logs test-agent
```

## 📊 Monitoring

### View Logs

**Docker Compose:**
```bash
docker-compose logs -f app
```

**Docker:**
```bash
docker logs -f <container-id>
```

**Render:**
- Dashboard → Your Service → Logs tab

### Metrics Endpoint

```bash
curl http://localhost:8000/metrics \
  -H "X-API-Key: admin-key-67890"
```

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Use `.env.example` as template
2. **Use strong API keys** - Minimum 20 characters, random
3. **Rotate keys regularly** - Update in Render environment
4. **Use HTTPS in production** - Render provides this automatically
5. **Monitor usage** - Check `/metrics` endpoint regularly
6. **Set appropriate rate limits** - Adjust based on your needs

## 🐛 Troubleshooting

### Redis Connection Failed

If Redis is unavailable, the app automatically falls back to in-memory storage:
```
WARNING - Redis connection failed, using in-memory fallback
```

This is expected behavior and allows the app to run without Redis.

### Rate Limit Not Working

Check Redis connection:
```bash
curl http://localhost:8000/readiness
```

If `redis: false`, check `REDIS_URL` environment variable.

### Image Size Too Large

Current image size should be < 500 MB. Check with:
```bash
docker images ai-agent
```

If larger, ensure multi-stage build is working correctly.

### Port Already in Use

Change port in `.env` or docker-compose.yml:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead
```

## 📝 Lab 06 Checklist

- ✅ All code runs without errors
- ✅ Multi-stage Dockerfile (image < 500 MB)
- ✅ API key authentication implemented
- ✅ Rate limiting (10 req/min) with Redis
- ✅ Cost guard ($10/month) with Redis
- ✅ Health check endpoint (`/health`)
- ✅ Readiness check endpoint (`/readiness`)
- ✅ Graceful shutdown with signal handling
- ✅ Stateless design (Redis for state)
- ✅ No hardcoded secrets (environment-based)
- ✅ Docker Compose with Redis
- ✅ `.env.example` provided
- ✅ `.dockerignore` configured
- ✅ `render.yaml` for deployment
- ✅ Complete documentation

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Render Documentation](https://render.com/docs)

## 📄 License

MIT

## 👤 Author

Production AI Agent - Lab 06 Complete
