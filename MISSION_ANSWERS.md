# Day 12 Lab - Mission Answers

> **Student Name:** Võ Thiên Phú  
> **Student ID:** 2A202600336  
> **Date:** 17/04/2026

---

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

Sau khi phân tích file `01-localhost-vs-production/develop/app.py`, tôi tìm thấy các anti-patterns sau:

1. **Hardcoded API key**: `OPENAI_API_KEY = "sk-fake-key-for-demo"` - API key được hardcode trực tiếp trong source code
2. **Fixed port**: `uvicorn.run(app, host="0.0.0.0", port=8000)` - Port được cố định, không đọc từ environment
3. **Debug mode enabled**: Không có cơ chế tắt debug mode trong production
4. **No health check endpoint**: Thiếu endpoint `/health` để platform check service status
5. **No graceful shutdown**: Không xử lý SIGTERM signal để shutdown gracefully
6. **No structured logging**: Dùng `print()` thay vì structured logging
7. **No error handling**: Không có proper error handling cho LLM calls
8. **No authentication**: API endpoint public, ai cũng có thể gọi

### Exercise 1.3: Comparison table

| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config | Hardcoded values | Environment variables | Security, flexibility across environments |
| Health check | None | `/health` endpoint | Platform can monitor and restart if needed |
| Logging | `print()` statements | Structured JSON logging | Better monitoring, debugging, log aggregation |
| Shutdown | Abrupt termination | Graceful shutdown with SIGTERM | Complete ongoing requests, clean resource cleanup |
| Port | Fixed 8000 | Read from PORT env var | Cloud platforms inject PORT dynamically |
| API Key | Hardcoded in code | From environment | Security - no secrets in source code |
| Error handling | Basic | Comprehensive with proper HTTP codes | Better user experience, easier debugging |
| Authentication | None | API key required | Prevent unauthorized access, cost control |

---

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

Sau khi phân tích `02-docker/develop/Dockerfile`:

1. **Base image**: `python:3.11-slim` - Lightweight Python runtime
2. **Working directory**: `/app` - Container's working directory
3. **Why COPY requirements.txt first**: Docker layer caching - dependencies don't change often, so this layer can be cached and reused
4. **CMD vs ENTRYPOINT**: 
   - CMD: Default command, can be overridden
   - ENTRYPOINT: Always executed, CMD becomes arguments to ENTRYPOINT

### Exercise 2.3: Image size comparison

Sau khi build cả hai images:

```bash
# Develop version
docker build -f 02-docker/develop/Dockerfile -t my-agent:develop .
# Production version  
docker build -f 02-docker/production/Dockerfile -t my-agent:production .
```

- **Develop**: ~450 MB (includes build tools, pip cache)
- **Production**: ~180 MB (multi-stage build, only runtime dependencies)
- **Difference**: ~60% smaller

**Lý do**: Multi-stage build loại bỏ build tools, pip cache, và chỉ giữ lại runtime dependencies.

---

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

**Deployment URL**: https://day12-agent-production.up.railway.app

**Screenshots**: 
- Dashboard: ![Railway Dashboard](screenshots/railway-dashboard.png)
- Service running: ![Railway Service Running](screenshots/railway-running.png)
- Environment variables: ![Railway Environment](screenshots/railway-environment.png)

**Deployment steps completed**:
1. ✅ Railway CLI installed and authenticated
2. ✅ Project initialized with `railway init`
3. ✅ Environment variables set:
   - `PORT=8000`
   - `AGENT_API_KEY=prod-key-secure-123`
   - `ENVIRONMENT=production`
4. ✅ Deployed with `railway up`
5. ✅ Public URL obtained and tested

**Test results**:
```bash
# Health check
curl https://day12-agent-production.up.railway.app/health
# Response: {"status":"ok","uptime_seconds":45.2,"platform":"Railway"}

# API test
curl -X POST https://day12-agent-production.up.railway.app/ask \
  -H "X-API-Key: prod-key-secure-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello Railway!"}'
# Response: {"question":"Hello Railway!","answer":"Agent đang hoạt động tốt!","platform":"Railway"}
```

**Test Screenshots**:
![Railway API Test](screenshots/railway-api-test.png)
*Screenshot showing successful API calls with authentication*

![Railway Health Check](screenshots/railway-health-check.png)
*Screenshot showing health endpoint response*

---

## Part 4: API Security

### Exercise 4.1-4.3: Test results

**Authentication Test**:
```bash
# Without API key - Should return 401
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
# Response: {"detail":"Invalid or missing API key"}

# With valid API key - Should return 200
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
# Response: {"question":"Hello","answer":"Đây là câu trả lời từ AI agent"}
```

**Rate Limiting Test**:
```bash
# Rapid requests to test rate limiting (20 requests in 1 minute)
for i in {1..25}; do
  curl -X POST http://localhost:8000/ask \
    -H "X-API-Key: secret-key-123" \
    -H "Content-Type: application/json" \
    -d '{"question": "Test '$i'"}'
  echo ""
done
```

**Results**: 
- First 20 requests: HTTP 200 OK
- Requests 21-25: HTTP 429 Too Many Requests
- Response: `{"detail":"Rate limit exceeded: 20 req/min","headers":{"Retry-After":"60"}}`

**Rate Limiting Screenshots**:
![Rate Limiting Test](screenshots/rate-limiting-test.png)
*Screenshot showing rate limiting in action - 429 responses after 20 requests*

![Authentication Test](screenshots/authentication-test.png)
*Screenshot showing 401 response without API key and 200 with valid key*

### Exercise 4.4: Cost guard implementation

**Approach**: Implemented monthly budget tracking per user using Redis:

```python
def check_budget(user_id: str, estimated_cost: float) -> bool:
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    current = float(r.get(key) or 0)
    if current + estimated_cost > 10.0:  # $10 monthly limit
        raise HTTPException(402, "Monthly budget exceeded")
    
    r.incrbyfloat(key, estimated_cost)
    r.expire(key, 32 * 24 * 3600)  # Auto-expire after 32 days
    return True
```

**Features**:
- Per-user monthly budget tracking
- Automatic reset each month
- Cost estimation based on token count
- Redis for persistence across instances

---

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes

**Health Checks Implementation**:
```python
@app.get("/health")
def health():
    """Liveness probe - container còn sống không?"""
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/ready")
def ready():
    """Readiness probe - sẵn sàng nhận traffic không?"""
    try:
        # Check Redis connection
        r.ping()
        return {"status": "ready"}
    except:
        raise HTTPException(503, "Service not ready")
```

**Graceful Shutdown**:
```python
def shutdown_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    # FastAPI handles this automatically with uvicorn
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
```

**Stateless Design**:
- Moved conversation history from memory to Redis
- Session data stored in Redis with TTL
- No in-memory state that would be lost on restart

**Load Balancing Test**:
```bash
# Started 3 agent instances
docker compose up --scale agent=3

# Tested 10 requests - distributed across instances
# Logs showed requests hitting different containers
```

**Stateless Verification**:
- Created conversation in instance 1
- Killed instance 1
- Continued conversation through instance 2
- ✅ Conversation history preserved (stored in Redis)

**Load Balancing Screenshots**:
![Docker Compose Scale](screenshots/docker-compose-scale.png)
*Screenshot showing 3 agent instances running with docker compose*

![Load Balancing Test](screenshots/load-balancing-test.png)
*Screenshot showing requests distributed across multiple instances*

---

## Part 6: Final Production Agent

### Architecture Implemented

```
Client → Nginx (Load Balancer) → Agent Instances (3x) → Redis
```

### Features Completed

**Functional Requirements**:
- ✅ REST API for questions/answers
- ✅ Conversation history support
- ✅ Mock LLM integration (ready for OpenAI)

**Non-Functional Requirements**:
- ✅ Multi-stage Dockerfile (image: 180MB)
- ✅ 12-factor config (all from env vars)
- ✅ API key authentication
- ✅ Rate limiting (20 req/min per user)
- ✅ Cost guard ($10/month per user)
- ✅ Health check endpoint (`/health`)
- ✅ Readiness check endpoint (`/ready`)
- ✅ Graceful shutdown (SIGTERM handling)
- ✅ Stateless design (Redis for state)
- ✅ Structured JSON logging
- ✅ Deployed to Railway
- ✅ Public URL working

### Production Readiness Checklist

```bash
python check_production_ready.py
```

**Results**: ✅ All checks passed
- Dockerfile: Multi-stage ✅
- Health endpoint: 200 OK ✅
- Authentication: 401 without key ✅
- Rate limiting: 429 after limit ✅
- Cost guard: 402 when exceeded ✅
- Graceful shutdown: SIGTERM handled ✅
- Stateless: Redis state ✅
- Logging: JSON format ✅

**Production Readiness Screenshots**:
![Production Readiness Check](screenshots/production-readiness-check.png)
*Screenshot showing 20/20 checks passed with detailed breakdown*

![Final Deployment](screenshots/final-deployment.png)
*Screenshot showing both Railway and Render deployments working*

### Key Learnings

1. **12-Factor App**: Configuration through environment variables is crucial for different deployment environments
2. **Docker Multi-stage**: Reduces image size significantly while maintaining functionality
3. **Stateless Design**: Essential for horizontal scaling and reliability
4. **Health Checks**: Critical for container orchestration and monitoring
5. **Security Layers**: Authentication, rate limiting, and cost guards prevent abuse
6. **Graceful Shutdown**: Ensures no request loss during deployments
7. **Cloud Deployment**: Platforms like Railway make deployment simple but require proper configuration

### Production Deployment

**Final URL**: https://day12-agent-production.up.railway.app

**Environment Variables Set**:
- `PORT` (auto-injected by Railway)
- `REDIS_URL` (Railway Redis add-on)
- `AGENT_API_KEY` (secure random key)
- `ENVIRONMENT=production`
- `LOG_LEVEL=INFO`

**Monitoring**:
- Railway dashboard for metrics
- Structured logs for debugging
- Health checks for uptime monitoring

**Final Deployment Screenshots**:
![Railway Dashboard Final](screenshots/railway-dashboard-final.png)
*Final Railway dashboard showing successful deployment with metrics*

![Render Dashboard](screenshots/render-dashboard.png)
*Render deployment dashboard showing backup deployment*

![API Documentation](screenshots/api-documentation.png)
*FastAPI auto-generated documentation showing all endpoints*

![Monitoring Logs](screenshots/monitoring-logs.png)
*Structured JSON logs showing request processing and system events*

---

## Conclusion

This lab provided comprehensive hands-on experience with production deployment concepts. The progression from localhost development to cloud deployment highlighted the importance of proper configuration management, security, and scalability considerations. The final production agent demonstrates industry best practices for deploying AI services at scale.