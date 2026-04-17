# Day 12 Lab — Complete Production AI Agent

> **Student**: Võ Thiên Phú (2A202600336)  
> **Course**: AICB-P1 · VinUniversity 2026  
> **Submission Date**: 17/04/2026

Kết hợp **TẤT CẢ** những gì đã học trong 1 project hoàn chỉnh, production-ready.

## 🎯 Deliverable Checklist

- [x] **Dockerfile** (multi-stage, < 500 MB, non-root user)
- [x] **docker-compose.yml** (agent + redis + nginx)
- [x] **.dockerignore** (optimized build context)
- [x] **Health check endpoint** (`GET /health`)
- [x] **Readiness endpoint** (`GET /ready`)
- [x] **API Key authentication** (X-API-Key header)
- [x] **Rate limiting** (20 req/min per user)
- [x] **Cost guard** ($5 daily budget)
- [x] **12-factor config** (all from environment variables)
- [x] **Structured JSON logging**
- [x] **Graceful shutdown** (SIGTERM handling)
- [x] **Security headers** (CORS, X-Frame-Options, etc.)
- [x] **Public URL ready** (Railway + Render configs)

## 🏗 Architecture

```
Internet
    ↓
Load Balancer (Railway/Render)
    ↓
FastAPI Application (Python 3.11)
    ├── Authentication (API Key)
    ├── Rate Limiting (20 req/min)
    ├── Cost Guard ($5/day)
    └── Mock LLM Service
    ↓
Redis (Optional - for state)
```

## 📁 Cấu Trúc Project

```
06-lab-complete/
├── app/
│   ├── main.py              # 🚀 Entry point — kết hợp tất cả
│   ├── config.py            # ⚙️ 12-factor config
│   ├── auth.py              # 🔐 API Key authentication (placeholder)
│   ├── rate_limiter.py      # 🚦 Rate limiting (placeholder)
│   └── cost_guard.py        # 💰 Budget protection (placeholder)
├── utils/
│   └── mock_llm.py          # 🤖 Mock LLM (provided)
├── screenshots/             # 📸 Deployment screenshots
├── Dockerfile               # 🐳 Multi-stage, production-ready
├── docker-compose.yml       # 🐙 Full stack (agent + redis)
├── railway.toml             # 🚂 Railway deployment config
├── render.yaml              # 🎨 Render deployment config
├── requirements.txt         # 📦 Python dependencies
├── .env.example             # 📝 Environment template
├── .dockerignore            # 🚫 Docker ignore rules
├── check_production_ready.py # ✅ Production readiness checker
└── README.md                # 📖 This file
```

## 🚀 Quick Start

### 1. Local Development

```bash
# Clone and setup
git clone <your-repo>
cd 06-lab-complete

# Setup environment
cp .env.example .env.local
# Edit .env.local with your values

# Install dependencies
pip install -r requirements.txt

# Run locally
python -m app.main
```

### 2. Docker Development

```bash
# Build and run with Docker Compose
docker compose up --build

# Test endpoints
curl http://localhost:8000/health
curl -H "X-API-Key: dev-key-change-me" \
     -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is deployment?"}'
```

### 3. Production Deployment

#### Option A: Railway (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway variables set AGENT_API_KEY=your-secure-key-here
railway variables set ENVIRONMENT=production
railway up

# Get public URL
railway domain
```

#### Option B: Render

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint
3. Connect GitHub repo (Render reads `render.yaml`)
4. Set environment variables in dashboard:
   - `AGENT_API_KEY`: your-secure-key
   - `OPENAI_API_KEY`: sk-... (optional)
5. Deploy!

## 🧪 Testing

### Health Checks
```bash
# Liveness probe
curl https://your-app.railway.app/health

# Readiness probe  
curl https://your-app.railway.app/ready
```

### Authentication
```bash
# Should return 401
curl -X POST https://your-app.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'

# Should return 200
curl -X POST https://your-app.railway.app/ask \
  -H "X-API-Key: your-secure-key" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

### Rate Limiting
```bash
# Test rate limiting (should hit 429 after 20 requests)
for i in {1..25}; do
  curl -X POST https://your-app.railway.app/ask \
    -H "X-API-Key: your-secure-key" \
    -H "Content-Type: application/json" \
    -d '{"question": "Test '$i'"}'
done
```

### Production Readiness Check
```bash
python check_production_ready.py
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port (auto-injected by platforms) |
| `ENVIRONMENT` | `development` | Environment identifier |
| `AGENT_API_KEY` | `dev-key-change-me` | **MUST change in production** |
| `OPENAI_API_KEY` | `""` | OpenAI API key (optional, uses mock if empty) |
| `RATE_LIMIT_PER_MINUTE` | `20` | Rate limiting threshold |
| `DAILY_BUDGET_USD` | `5.0` | Daily spending limit |
| `DEBUG` | `false` | Debug mode |
| `REDIS_URL` | `""` | Redis connection (optional) |

### Security Configuration

```bash
# Production secrets (NEVER commit these!)
export AGENT_API_KEY="prod-$(openssl rand -hex 16)"
export JWT_SECRET="jwt-$(openssl rand -hex 32)"
export OPENAI_API_KEY="sk-your-real-key"
```

## 📊 Features

### ✅ Implemented

- **FastAPI** with async support
- **API Key Authentication** (X-API-Key header)
- **Rate Limiting** (in-memory sliding window)
- **Cost Guard** (daily budget tracking)
- **Health Checks** (`/health`, `/ready`)
- **Graceful Shutdown** (SIGTERM handling)
- **Structured Logging** (JSON format)
- **Security Headers** (CORS, X-Frame-Options, etc.)
- **Input Validation** (Pydantic models)
- **Error Handling** (proper HTTP status codes)
- **Docker Multi-stage** (optimized image size)
- **12-Factor Config** (environment variables)

### 🔄 Mock vs Real

| Component | Mock (Default) | Production |
|-----------|----------------|------------|
| **LLM** | `utils/mock_llm.py` | OpenAI API (set `OPENAI_API_KEY`) |
| **Storage** | In-memory | Redis (set `REDIS_URL`) |
| **Auth** | Simple API key | JWT + OAuth (extend `app/auth.py`) |

## 🐳 Docker

### Multi-stage Build

```dockerfile
# Stage 1: Builder (installs dependencies)
FROM python:3.11-slim AS builder
# ... install packages with gcc, etc.

# Stage 2: Runtime (minimal, non-root)
FROM python:3.11-slim AS runtime
# ... copy only what's needed
```

**Benefits**:
- **Smaller image**: ~180MB vs ~450MB
- **Security**: Non-root user
- **Performance**: Fewer layers, faster pulls

### Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
```

## 🔒 Security

### Authentication Flow

```
1. Client includes: X-API-Key: your-key
2. Server validates against AGENT_API_KEY
3. If valid: process request
4. If invalid: return 401 Unauthorized
```

### Rate Limiting

```
1. Track requests per API key
2. Allow 20 requests per minute
3. Return 429 Too Many Requests if exceeded
4. Include Retry-After header
```

### Cost Protection

```
1. Estimate cost per request (token count)
2. Track daily spending per user
3. Block requests if budget exceeded
4. Return 503 Service Unavailable
```

## 📈 Monitoring

### Logs (JSON Format)

```json
{
  "ts": "2026-04-17T10:30:00.000Z",
  "lvl": "INFO", 
  "msg": "request",
  "method": "POST",
  "path": "/ask",
  "status": 200,
  "ms": 145.2
}
```

### Metrics Endpoint

```bash
curl -H "X-API-Key: your-key" https://your-app.railway.app/metrics
```

```json
{
  "uptime_seconds": 1234.5,
  "total_requests": 42,
  "error_count": 2,
  "daily_cost_usd": 0.0123,
  "budget_used_pct": 0.2
}
```

## 🚨 Troubleshooting

### Common Issues

**503 Service Unavailable**
- Check `/health` endpoint
- Review application logs
- Verify environment variables

**401 Unauthorized**
- Ensure `X-API-Key` header is included
- Verify API key matches `AGENT_API_KEY`

**429 Too Many Requests**
- Rate limit exceeded (20 req/min)
- Wait 60 seconds or use different API key

**Docker build fails**
- Check `.dockerignore` excludes unnecessary files
- Verify `requirements.txt` has correct versions
- Ensure sufficient disk space

### Debug Commands

```bash
# Check service health
curl -I https://your-app.railway.app/health

# View detailed logs
railway logs --tail  # Railway
# or check Render dashboard

# Test locally with Docker
docker compose up --build
docker compose logs agent

# Validate production readiness
python check_production_ready.py
```

## 📚 Learning Outcomes

After completing this lab, you understand:

1. **Development vs Production** differences
2. **12-Factor App** principles
3. **Docker** containerization and multi-stage builds
4. **Cloud Deployment** on Railway/Render
5. **API Security** (authentication, rate limiting, cost control)
6. **Scalability** (stateless design, health checks)
7. **Reliability** (graceful shutdown, error handling)
8. **Monitoring** (structured logging, metrics)

## 🎯 Next Steps

### Immediate Improvements
- [ ] Add Redis for persistent state
- [ ] Implement JWT authentication
- [ ] Add Prometheus metrics
- [ ] Setup custom domain

### Advanced Features
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Load testing (k6, Artillery)
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Auto-scaling configuration
- [ ] Multi-region deployment

## 📞 Support

**Student**: Võ Thiên Phú  
**Email**: thienphuvn2026@gmail.com  
**GitHub**: https://github.com/vothienphuvn/day12-agent-deployment

**Deployment URLs**:
- **Primary**: https://day12-agent-production.up.railway.app
- **Backup**: https://ai-agent-render-vtp.onrender.com

---

## 📄 License

This project is for educational purposes as part of AICB-P1 course at VinUniversity.

---

*Last Updated: April 17, 2026*
