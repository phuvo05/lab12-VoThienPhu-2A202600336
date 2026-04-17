# Day 12 Lab - Mission Answers

**Student Name:** Võ Thiên Phú
**Student ID:** 2A202600336
**Date:** 17/04/2026

---

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

Trong `01-localhost-vs-production/develop/app.py`, tôi đã tìm được **5 anti-patterns**:

1. **API key hardcode trong code** (line 17-18)
   - `OPENAI_API_KEY = "sk-hardcoded-fake-key-never-do-this"` và `DATABASE_URL = "postgresql://admin:password123@localhost:5432/mydb"`
   - Nếu push lên GitHub → key bị lộ ngay lập tức

2. **Không có config management** (line 21-22)
   - DEBUG, MAX_TOKENS là biến Python cứng, không đọc từ environment
   - Không thể thay đổi mà không sửa code

3. **Print thay vì proper logging** (line 33-38)
   - `print(f"[DEBUG] Using key: {OPENAI_API_KEY}")` log ra secret ra console
   - Không có structured log, không parse được bằng log aggregator

4. **Không có health check endpoint**
   - Không có `/health` hay `/ready`
   - Nếu agent crash, cloud platform không biết để restart

5. **Port cố định** (line 49-53)
   - `host="localhost"` và `port=8000` cứng trong code
   - Trên Railway/Render, PORT được inject qua env var, không phải 8000
   - `reload=True` trong production gây crash loop

### Exercise 1.3: Comparison table

| Feature | Develop (Basic) | Production (Advanced) | Why Important? |
|---------|----------------|-----------------------|---------------|
| Config | Hardcode trong code | Environment variables (12-Factor) | Dễ deploy, không sửa code khi đổi môi trường |
| Health check | Không có | `/health` và `/ready` endpoints | Platform biết khi nào restart container |
| Logging | `print()` | Structured JSON logging | Dễ parse, tích hợp log aggregator (Datadog, Loki) |
| Shutdown | Đột ngột (Ctrl+C) | Graceful shutdown (SIGTERM handler) | Hoàn thành request đang xử lý trước khi tắt |
| Host binding | `localhost` | `0.0.0.0` | Container cần nhận kết nối từ bên ngoài |
| Port | Cố định `8000` | Từ `PORT` env var | Cloud platforms inject PORT tự động, không phải 8000 |
| Secrets | Hardcode | `.env` file + env vars | Không lộ secrets khi commit lên Git |
| Debug mode | Bật sẵn | `DEBUG=false` mặc định | Không leak thông tin debug trong production |

---

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

**File:** `02-docker/develop/Dockerfile`

1. **Base image là gì?**
   - `python:3.11` — full Python distribution, khoảng ~1 GB

2. **Working directory là gì?**
   - `/app` — được set bằng `WORKDIR /app`

3. **Tại sao COPY requirements.txt trước khi COPY code?**
   - Docker layer caching: nếu `requirements.txt` không đổi, layer `pip install` được cache và không phải chạy lại. Chỉ khi `requirements.txt` thay đổi mới rebuild dependencies.

4. **CMD vs ENTRYPOINT khác nhau thế nào?**
   - `CMD`: command mặc định khi container chạy, có thể override bởi command line argument khi `docker run`
   - `ENTRYPOINT`: command cố định, argument từ `CMD` được truyền vào sau. Dùng khi container là executable thực sự.
   - Trong Dockerfile này dùng `CMD ["python", "app.py"]` — đơn giản, chạy script Python trực tiếp.

### Exercise 2.2: Build và test

Image đã build thành công với size **160 MB** (production multi-stage).

### Exercise 2.3: Image size comparison

- **Develop (single-stage):** ~800 MB — dùng `python:3.11` base image đầy đủ
- **Production (multi-stage):** ~160 MB — dùng `python:3.11-slim` + multi-stage build
- **Difference:** Giảm khoảng **80%** (640 MB tiết kiệm)

**Multi-stage build hoạt động như sau:**
- Stage 1 (builder): Cài đặt tất cả dependencies (gcc, libpq-dev, pip packages)
- Stage 2 (runtime): Copy chỉ những gì cần để chạy (`site-packages` và code) sang image mới từ `python:3.11-slim`
- Kết quả: Final image chỉ có Python runtime + packages, không có build tools, không có pip gốc → nhỏ và an toàn hơn.

### Exercise 2.4: Docker Compose stack

**Architecture:**

```
                    ┌─────────────────────────────────────────────┐
                    │         Docker Compose Network               │
                    │                                             │
  Internet ──────►  │  ┌──────────┐    ┌─────────────────────┐  │
                    │  │  Nginx   │───►│  Agent (uvicorn)    │  │
                    │  │  :80      │    │  2 workers         │  │
                    │  └──────────┘    └─────────────────────┘  │
                    │       │                   │               │
                    │                              │               │
                    │               ┌──────────────┴───────┐       │
                    │               ▼                      ▼       │
                    │         ┌──────────┐          ┌──────────┐  │
                    │         │  Redis   │          │  Qdrant  │  │
                    │         │  :6379   │          │  :6333   │  │
                    │         └──────────┘          └──────────┘  │
                    └─────────────────────────────────────────────┘
```

**Services:**
1. **nginx** — Reverse proxy + load balancer (port 80/443)
2. **agent** — FastAPI app, chạy 2 uvicorn workers, health check
3. **redis** — Cache + rate limiting storage
4. **qdrant** — Vector database cho RAG

**Communication:**
- Client → Nginx (port 80) → Agent (internal port 8000)
- Agent → Redis (internal port 6379) cho session/rate-limit
- Agent → Qdrant (internal port 6333) cho vector search

---

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

**Railway Project:** https://railway.com/project/883835fa-980b-4782-a2b4-c9a6c90b382d?environmentId=2d65fdd5-24ab-419c-8699-69e76da5479e

**Deployment URL:** https://conversational-ai-agent-production.up.railway.app

**Steps thực hiện:**
1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Connect to existing project: `railway link 883835fa-980b-4782-a2b4-c9a6c90b382d`
5. Set variables:
   ```bash
   railway variables set PORT=8000
   railway variables set REDIS_URL=${{Redis.REDIS_URL}}
   railway variables set API_KEY=railway-api-key-12345
   railway variables set ADMIN_API_KEY=railway-admin-key-67890
   railway variables set RATE_LIMIT_REQUESTS=10
   railway variables set MONTHLY_COST_LIMIT=10.0
   ```
6. Deploy: `railway up`
7. Get URL: `railway domain`

**Services deployed:**
- **Web Service:** FastAPI application
- **Redis:** Cache and rate limiting storage

**Environment ID:** 2d65fdd5-24ab-419c-8699-69e76da5479e

### Exercise 3.2: Render deployment

**Render URL:** https://ai-agent-render-tp5e.onrender.com

**Steps thực hiện:**
1. Push code to GitHub repository
2. Connect GitHub repo to Render
3. Create Blueprint deployment using `render.yaml`
4. Services created:
   - **Web Service:** `ai-agent-app` (Docker)
   - **Redis:** `ai-agent-redis` (Managed Redis)
5. Environment variables configured:
   ```bash
   PORT=10000
   REDIS_URL=redis://...
   API_KEY=render-api-key-12345
   ADMIN_API_KEY=render-admin-key-67890
   RATE_LIMIT_REQUESTS=10
   MONTHLY_COST_LIMIT=10.0
   ```
6. Auto-deploy on GitHub push

### Exercise 3.3: Render vs Railway comparison

| Aspect | Railway | Render |
|--------|---------|--------|
| **Project URL** | https://railway.com/project/883835fa-980b-4782-a2b4-c9a6c90b382d | https://dashboard.render.com/ |
| **Deployment URL** | https://conversational-ai-agent-production.up.railway.app | https://ai-agent-render-tp5e.onrender.com |
| **Config file** | `railway.toml` | `render.yaml` |
| **Pricing** | $5 credit free | 750h/month free |
| **Region** | Auto (or manual) | Singapore (gần VN) |
| **Ease** | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Build System** | Nixpacks (auto-detect) | Docker |
| **Redis** | Add-on service | Managed service |
| **Deploy Speed** | ~2-3 minutes | ~3-5 minutes |
| **Logs** | Real-time in dashboard | Real-time in dashboard |

**`railway.toml`** — dùng Nixpacks để auto-detect Python, deploy đơn giản với health check.

**`render.yaml`** — Infrastructure as Code, dùng Blueprint, auto-deploy khi push GitHub.

**Kết luận:** Cả hai platform đều hoạt động tốt. Railway đơn giản hơn cho setup nhanh, Render ổn định hơn cho production dài hạn.

---

## Part 4: API Security

### Exercise 4.1: API Key authentication

**File:** `04-api-gateway/develop/app.py`

API key được check ở dependency `verify_api_key()` (line 39-54). Kiểm tra header `X-API-Key` với giá trị từ env var `AGENT_API_KEY`. Nếu sai → trả về 401 hoặc 403.

**Làm sao rotate key?**
- Đổi giá trị `AGENT_API_KEY` trong environment variable trên dashboard
- Không cần sửa code
- Key cũ sẽ không hoạt động ngay lập tức

**Test:**
```bash
# Không có key → 401
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"hello"}'
# {"detail":"Missing API key..."}

# Có key → 200
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: demo-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"question":"hello"}'
# {"question":"hello","answer":"..."}
```

### Exercise 4.2: JWT authentication

**File:** `04-api-gateway/production/auth.py`

**JWT Flow:**
1. Client gửi username/password → `POST /auth/token`
2. Server tạo JWT chứa `sub` (username), `role`, `exp` (expiry)
3. Client gửi JWT trong header `Authorization: Bearer <token>`
4. Server verify signature bằng `JWT_SECRET` và `HS256` algorithm
5. Nếu valid → extract user info → process request
6. Nếu expired → 401 Token expired

**Token chứa:**
```json
{
  "sub": "student",
  "role": "user",
  "iat": 1713300000,
  "exp": 1713303600
}
```

**Key points:**
- Stateless: server không cần lưu token, chỉ verify signature
- Có expiry: token tự hết hạn sau 60 phút
- Scalable: nhiều instances đều verify được vì dùng shared secret

### Exercise 4.3: Rate limiting

**File:** `04-api-gateway/production/rate_limiter.py`

**Algorithm: Sliding Window Counter**
- Mỗi user có 1 deque lưu timestamps của requests
- Mỗi request: loại bỏ timestamps cũ (> 60s), đếm còn lại
- Nếu >= limit → raise 429 với headers `X-RateLimit-*` và `Retry-After`

**Configuration:**
- User tier: **10 requests/phút**
- Admin tier: **100 requests/phút**

**Anti-pattern:** In-memory rate limiter không hoạt động khi scale nhiều instances vì mỗi instance có memory riêng. Cần dùng Redis-based rate limiter (sliding window stored in Redis).

### Exercise 4.4: Cost guard implementation

**File:** `04-api-gateway/production/cost_guard.py`

**Approach:**
1. Mỗi user có `UsageRecord` lưu input_tokens, output_tokens, request_count theo ngày
2. Tính cost: `input_tokens/1000 * $0.00015 + output_tokens/1000 * $0.0006`
3. **Per-user budget:** $1/ngày — block bằng HTTP 402
4. **Global budget:** $10/ngày — block toàn bộ bằng HTTP 503
5. **Warning at 80%:** log warning khi gần hết budget
6. **Reset:** Mỗi ngày mới (UTC midnight) tự reset

**Production improvement:** Thay in-memory storage bằng Redis để:
- Scale được nhiều instances
- Data không mất khi restart
- Distributed budget tracking

---

## Part 5: Scaling & Reliability

### Exercise 5.1: Health checks

**File:** `05-scaling-reliability/develop/app.py`

**Liveness probe (`/health`):**
- Trả về `status: ok` nếu process còn sống
- Bao gồm: uptime, version, environment, timestamp
- Platform restart container nếu health check fail

**Readiness probe (`/ready`):**
- Trả về 503 nếu `_is_ready = False` (đang startup hoặc shutdown)
- Load balancer dùng để quyết định có route traffic vào không
- Kiểm tra: dependencies (DB, Redis) đã connect chưa

### Exercise 5.2: Graceful shutdown

**Implement:**
```python
signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)
```

**Flow khi shutdown:**
1. Platform gửi SIGTERM
2. uvicorn gọi lifespan shutdown handler
3. `_is_ready = False` — không nhận request mới
4. Chờ `_in_flight_requests` hoàn thành (tối đa 30s)
5. Đóng connections, exit

**Test:**
```bash
python app.py &
PID=$!
curl http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "Long task"}' &
kill -TERM $PID
# Request đang chạy sẽ hoàn thành trước khi tắt
```

### Exercise 5.3: Stateless design

**Anti-pattern (in-memory):**
```python
conversation_history = {}  # ❌ State trong memory
@app.post("/ask")
def ask(user_id: str, question: str):
    history = conversation_history.get(user_id, [])
```

**Correct (Redis-based):**
```python
@app.post("/ask")
def ask(user_id: str, question: str):
    history = r.lrange(f"history:{user_id}", 0, -1)
    # process...
    r.rpush(f"history:{user_id}", new_message)
```

**Tại sao quan trọng?**
- Khi scale ra nhiều instances, mỗi instance có memory riêng
- User A có thể hit instance 1 (có history), rồi hit instance 2 (không có history)
- Redis là shared storage: tất cả instances đều đọc/ghi cùng data

### Exercise 5.4: Load balancing

**Test với Nginx:**
```bash
docker compose up --scale agent=3
```

- 3 agent instances được start
- Nginx phân tán requests theo thuật toán `least_conn`
- Nếu 1 instance die, Nginx tự chuyển traffic sang instances khác (max_fails=3)
- Mỗi instance đều stateless → user nhận cùng trải nghiệm bất kể instance nào xử lý

### Exercise 5.5: Test stateless

```bash
python test_stateless.py
```

Script test:
1. Gọi API tạo conversation (instance 1)
2. Kill instance 1
3. Gọi tiếp — conversation vẫn còn vì history lưu trong Redis

---

## Part 6: Final Project

### Exercise 6.1: Lab 06 Complete structure

**GitHub Repository:** https://github.com/phuvo05/conversational-ai-agent

**Deployed URL:** https://conversational-ai-agent-z3q1.onrender.com

```
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with all endpoints
│   ├── config.py            # Environment configuration (12-Factor)
│   ├── auth.py              # API key authentication
│   ├── rate_limiter.py      # Redis-based rate limiting (10 req/min)
│   └── cost_guard.py        # Cost tracking ($10/month limit)
├── utils/
│   ├── __init__.py
│   └── mock_llm.py          # Mock LLM for testing
├── static/
│   ├── style.css            # Modern UI styles with dark mode
│   └── script.js            # Frontend logic
├── templates/
│   └── index.html           # Web interface
├── screenshots/
│   ├── dashboard.png        # Render dashboard
│   ├── running.png          # Services running
│   ├── health_check.png     # Health endpoint
│   ├── auth_test.png        # Authentication test
│   ├── rate_limit.png       # Rate limiting test
│   ├── cost_guard.png       # Usage statistics
│   ├── docker_build.png     # Docker image size
│   └── redis_connected.png  # Readiness check
├── Dockerfile               # Multi-stage: builder + runtime, < 500 MB
├── docker-compose.yml       # Full stack: agent + redis
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── .dockerignore            # Docker ignore rules
├── render.yaml              # Render deployment config (Blueprint)
├── README.md                # Complete documentation
├── DEPLOYMENT.md            # Deployment guide with live URL
├── MISSION_ANSWERS.md       # Exercise answers
├── CHECKLIST.md             # Pre-submission checklist
├── DAY12_DELIVERY_CHECKLIST.md  # This file
└── test_api.sh              # API test script
```

### Exercise 6.2: Production readiness checklist

| Feature | Status | Implementation |
|---------|--------|----------------|
| Multi-stage Dockerfile | ✅ | `python:3.11-slim` base, builder+runtime stages, ~187 MB |
| API Key authentication | ✅ | `X-API-Key` header + `Depends(verify_api_key)` |
| Rate limiting | ✅ | Redis-based sliding window, 10 req/min per API key |
| Cost guard | ✅ | $10/month budget per user, 402 khi vượt |
| Health check | ✅ | `/health` liveness probe |
| Readiness check | ✅ | `/readiness` readiness probe (checks Redis) |
| Graceful shutdown | ✅ | SIGTERM/SIGINT handler, 10s timeout |
| Stateless design | ✅ | All state in Redis (rate limit + cost tracking) |
| Structured logging | ✅ | Python logging with INFO level |
| 12-Factor config | ✅ | Pydantic Settings class đọc từ env vars |
| CORS middleware | ✅ | `CORSMiddleware` allow all origins |
| Docker Compose | ✅ | Full stack: app + Redis with health checks |
| Web UI | ✅ | Modern interface with dark mode, localStorage |
| Public URL | ✅ | https://conversational-ai-agent-z3q1.onrender.com |
| GitHub Repository | ✅ | https://github.com/phuvo05/conversational-ai-agent |

### Exercise 6.3: Deployment verification

**Live URL:** https://conversational-ai-agent-z3q1.onrender.com

#### Test Results:

**1. Health Check ✅**
```bash
curl https://conversational-ai-agent-z3q1.onrender.com/health
```
Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-17T10:30:00",
  "version": "1.0.0"
}
```

**2. Readiness Check ✅**
```bash
curl https://conversational-ai-agent-z3q1.onrender.com/readiness
```
Response:
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

**3. Authentication Test ✅**
```bash
# Without API key - Returns 401
curl -X POST https://conversational-ai-agent-z3q1.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```
Response:
```json
{
  "detail": "Missing API key. Include X-API-Key header."
}
```

**4. Chat API with Authentication ✅**
```bash
curl -X POST https://conversational-ai-agent-z3q1.onrender.com/chat \
  -H "X-API-Key: test-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```
Response:
```json
{
  "response": "Hello! How can I help you today?",
  "tokens_used": 12,
  "cost": 0.002
}
```

**5. Rate Limiting Test ✅**
Sent 11 requests rapidly - 11th request returned 429:
```json
{
  "detail": "Rate limit exceeded. Maximum 10 requests per minute."
}
```

**6. Web UI ✅**
Access at: https://conversational-ai-agent-z3q1.onrender.com
- Modern chat interface
- Dark mode toggle
- Message history in localStorage
- Responsive design

### Exercise 6.4: Screenshots

All screenshots are available in the `screenshots/` directory:

1. **dashboard.png** - Render dashboard showing both services (web + Redis)
2. **running.png** - Services status showing healthy state
3. **health_check.png** - Health endpoint returning 200 OK
4. **auth_test.png** - Authentication test showing 401 without API key
5. **rate_limit.png** - Rate limiting test showing 429 after 10 requests
6. **cost_guard.png** - Usage statistics endpoint response
7. **docker_build.png** - Docker image size showing < 500 MB
8. **redis_connected.png** - Readiness check showing Redis connected
9. **web_ui_light.png** - Web interface in light mode
10. **web_ui_dark.png** - Web interface in dark mode

---

## Summary

Lab này đã giúp tôi hiểu toàn bộ pipeline đưa một AI Agent từ localhost lên production:

1. **Localhost vs Production** — Tránh 5 anti-patterns phổ biến, dùng 12-Factor App
2. **Docker** — Containerize với multi-stage build, giảm image 80%, dùng Docker Compose cho full stack
3. **Cloud Deployment** — Deploy lên Railway và Render với health check tự động
4. **API Security** — API Key + JWT authentication, rate limiting (sliding window), cost guard
5. **Scaling & Reliability** — Health checks, graceful shutdown, stateless design, load balancing với Nginx

**Key lessons:**
- Secrets KHÔNG BAO GIỜ hardcode
- Health checks là bắt buộc để cloud platform quản lý container
- Stateless design là nền tảng của horizontal scaling
- Rate limiting + cost guard là hai lớp bảo vệ cuối cùng trước khi hết tiền
