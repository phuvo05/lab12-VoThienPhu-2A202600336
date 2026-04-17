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

**URL:** https://your-agent.railway.app

*(Cần deploy thực tế để điền URL)*

**Steps thực hiện:**
1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Set variables:
   ```bash
   railway variables set PORT=8000
   railway variables set AGENT_API_KEY=my-secret-key
   ```
5. Deploy: `railway up`
6. Get URL: `railway domain`

### Exercise 3.2: Render vs Railway comparison

| Aspect | Railway | Render |
|--------|---------|--------|
| Config file | `railway.toml` | `render.yaml` |
| Pricing | $5 credit free | 750h/month free |
| Region | Auto (or manual) | Singapore (gần VN) |
| Ease | ⭐⭐⭐⭐ | ⭐⭐⭐ |

**`railway.toml`** — dùng Nixpacks để auto-detect Python, deploy đơn giản.

**`render.yaml`** — Infrastructure as Code, dùng Blueprint, auto-deploy khi push GitHub.

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

```
06-lab-complete/
├── app/
│   ├── main.py         # Entry point — kết hợp tất cả features
│   ├── config.py       # 12-Factor config (Settings dataclass)
│   └── auth.py         # API Key + JWT (từ 04-api-gateway/production)
├── Dockerfile          # Multi-stage: builder + runtime, < 500 MB
├── docker-compose.yml  # Full stack: agent + redis
├── railway.toml        # Deploy Railway
├── render.yaml         # Deploy Render
├── .env.example        # Template
├── .dockerignore       # Ignore venv, .git, .env
└── requirements.txt    # fastapi, uvicorn, pydantic, pyjwt, redis, psutil
```

### Exercise 6.2: Production readiness checklist

| Feature | Status | Implementation |
|---------|--------|----------------|
| Multi-stage Dockerfile | ✅ | `python:3.11-slim` base, builder+runtime stages, ~160 MB |
| API Key authentication | ✅ | `APIKeyHeader` + `Depends(verify_api_key)` |
| Rate limiting | ✅ | Sliding window counter, 20 req/min default |
| Cost guard | ✅ | $5/day budget, 402 khi vượt |
| Health check | ✅ | `/health` liveness probe |
| Readiness check | ✅ | `/ready` readiness probe |
| Graceful shutdown | ✅ | SIGTERM handler, 30s timeout |
| Stateless design | ✅ | Rate limiter + cost guard có thể swap sang Redis |
| Structured logging | ✅ | JSON format logging |
| 12-Factor config | ✅ | Settings dataclass đọc từ env vars |
| CORS middleware | ✅ | `CORSMiddleware` với configurable origins |
| Security headers | ✅ | `X-Content-Type-Options`, `X-Frame-Options` |
| Pydantic validation | ✅ | `AskRequest` với min/max length |
| Public URL ready | ✅ | `railway.toml` + `render.yaml` |

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
