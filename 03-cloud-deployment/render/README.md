# Deploy AI Agent lên Render

Render là platform Infrastructure as Code (IaC) — định nghĩa toàn bộ infrastructure trong file `render.yaml`, commit vào git, và Render tự động sync.

## 🎯 Ưu điểm của Render

- ✅ **Infrastructure as Code**: Mọi thứ trong `render.yaml`
- ✅ **Auto Deploy**: Push code → Tự động deploy
- ✅ **Free Tier**: 750 giờ/tháng miễn phí
- ✅ **Zero Config**: Không cần setup server
- ✅ **Built-in SSL**: HTTPS tự động
- ✅ **Health Checks**: Tự động restart nếu app crash

## 🚀 Quick Deploy (< 10 phút)

### Cách 1: Deploy từ GitHub (Khuyến nghị)

1. **Push code lên GitHub repository**

2. **Vào Render Dashboard**: https://dashboard.render.com

3. **New → Blueprint**
   - Connect GitHub repository
   - Render tự động detect `render.yaml`
   - Review services sẽ được tạo

4. **Apply Blueprint**
   - Render tạo services theo `render.yaml`
   - Tự động build và deploy

5. **Nhận URL**: `https://ai-agent-render.onrender.com`

### Cách 2: Deploy Manual (không dùng Blueprint)

1. **New → Web Service**
2. **Connect repository**
3. **Configure**:
   - Name: `ai-agent-render`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
   - Root Directory: `03-cloud-deployment/render`
4. **Create Web Service**

### Cách 3: Render CLI

```bash
# 1. Cài Render CLI
npm install -g render-cli
# hoặc
brew install render

# 2. Login
render login

# 3. Deploy từ render.yaml
cd 03-cloud-deployment/render
render blueprint launch

# 4. Xem logs
render logs
```

## 📋 Cấu trúc file

```
render/
├── render.yaml         # Infrastructure as Code (quan trọng nhất!)
├── app.py              # FastAPI app
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Ignore sensitive files
├── README.md           # Hướng dẫn này
└── utils/
    └── mock_llm.py     # Mock LLM cho demo
```

## ⚙️ Cấu hình quan trọng

### 1. render.yaml — Infrastructure as Code

File này định nghĩa **toàn bộ infrastructure**:

```yaml
services:
  - type: web
    name: ai-agent-render
    runtime: python
    region: singapore
    plan: free
    
    rootDir: 03-cloud-deployment/render
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    
    healthCheckPath: /health
    autoDeploy: true
    
    envVars:
      - key: ENVIRONMENT
        value: production
```

### 2. PORT Environment Variable

Render tự động inject biến `PORT` (default: 10000). App **PHẢI** đọc từ env:

```python
port = int(os.getenv("PORT", 10000))
uvicorn.run(app, host="0.0.0.0", port=port)
```

### 3. Health Check

Render ping `/health` endpoint định kỳ. Nếu fail → auto restart:

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

### 4. Root Directory

Nếu app không ở root của repo, chỉ định `rootDir`:

```yaml
rootDir: 03-cloud-deployment/render
```

## 🔧 Environment Variables

### Set qua Dashboard:
1. Vào service → **Environment** tab
2. Add variable: `OPENAI_API_KEY` = `sk-xxx`
3. **Save Changes** → Render tự động redeploy

### Set qua render.yaml:
```yaml
envVars:
  - key: ENVIRONMENT
    value: production
  - key: OPENAI_API_KEY
    sync: false  # Không sync từ file, set manual trên dashboard
  - key: AGENT_API_KEY
    generateValue: true  # Render tự sinh random value
```

### Set qua CLI:
```bash
render env set OPENAI_API_KEY=sk-xxx
```

## 📊 Monitoring & Logs

### Xem logs real-time:
```bash
# Qua CLI
render logs --tail

# Qua Dashboard
Service → Logs tab
```

### Metrics:
- Dashboard → Service → Metrics
- CPU, Memory, Request count, Response time

### Alerts:
- Dashboard → Service → Settings → Notifications
- Email/Slack alerts khi service down

## 🧪 Test sau khi deploy

```bash
# Lấy URL từ dashboard hoặc
RENDER_URL="https://ai-agent-render.onrender.com"

# Test root endpoint
curl $RENDER_URL/

# Test health check
curl $RENDER_URL/health

# Test AI agent
curl -X POST $RENDER_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello Render!"}'

# Test info endpoint
curl $RENDER_URL/info
```

## 💰 Pricing

| Plan | Price | Hours | RAM | Features |
|------|-------|-------|-----|----------|
| **Free** | $0 | 750h/month | 512MB | Auto-sleep after 15min inactive |
| **Starter** | $7/month | Unlimited | 512MB | No sleep |
| **Standard** | $25/month | Unlimited | 2GB | Faster builds |
| **Pro** | $85/month | Unlimited | 4GB | Priority support |

**Lưu ý Free tier**:
- App sleep sau 15 phút không có traffic
- Cold start ~30s khi có request mới
- Đủ cho demo/MVP

## 🐛 Troubleshooting

### 1. App không start được

```bash
# Xem logs chi tiết
render logs --tail

# Check build logs
Dashboard → Service → Events → Build logs
```

**Nguyên nhân thường gặp**:
- ❌ Sai `startCommand` trong render.yaml
- ❌ Thiếu dependencies trong requirements.txt
- ❌ Port không đọc từ env

### 2. Port binding error

❌ **Sai**: Hard-code port
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

✅ **Đúng**: Đọc từ env
```python
port = int(os.getenv("PORT", 10000))
uvicorn.run(app, host="0.0.0.0", port=port)
```

### 3. Health check fail

- Đảm bảo `/health` endpoint trả về 200 OK
- Check logs xem app có crash không
- Tăng timeout nếu app start chậm

### 4. App bị sleep (Free tier)

Free tier sleep sau 15 phút không có traffic. Giải pháp:

**Option 1**: Upgrade lên Starter plan ($7/month)

**Option 2**: Dùng cron job ping định kỳ
```bash
# Ping mỗi 10 phút để keep alive
*/10 * * * * curl https://ai-agent-render.onrender.com/health
```

**Option 3**: Dùng UptimeRobot (free) để ping

### 5. Build quá chậm

- Dùng `pip install --no-cache-dir` để giảm cache
- Upgrade lên Standard plan (faster builds)
- Optimize requirements.txt (chỉ cài packages cần thiết)

## 🔄 CI/CD Tự động

Render tự động deploy khi:
- ✅ Push code lên GitHub branch được connect
- ✅ Merge pull request
- ✅ Update `render.yaml`

**Disable auto-deploy**:
```yaml
autoDeploy: false
```

Sau đó deploy manual qua Dashboard hoặc CLI.

## 🌐 Custom Domain

### 1. Qua Dashboard:
- Service → Settings → Custom Domain
- Add domain: `api.yourdomain.com`
- Update DNS: CNAME → `ai-agent-render.onrender.com`

### 2. SSL Certificate:
- Render tự động provision Let's Encrypt SSL
- HTTPS enabled tự động

## 🔐 Security Best Practices

### 1. Không commit secrets vào git:
```yaml
envVars:
  - key: OPENAI_API_KEY
    sync: false  # Set manual trên dashboard
```

### 2. Dùng `.gitignore`:
```
.env
.env.local
__pycache__/
```

### 3. Enable CORS đúng cách:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Không dùng "*" trong production
    allow_credentials=True,
)
```

## 📚 So sánh với Railway

| Feature | Render | Railway |
|---------|--------|---------|
| **IaC** | render.yaml | railway.toml |
| **Free tier** | 750h/month | $5 credit/month |
| **Auto-sleep** | Yes (15min) | No |
| **Cold start** | ~30s | ~5s |
| **Pricing** | $7/month (no sleep) | $5/month |
| **Best for** | IaC, team projects | Quick prototypes |

## 🎯 Next Steps

Sau khi deploy thành công:

1. ✅ Test tất cả endpoints
2. ✅ Setup custom domain
3. ✅ Configure environment variables
4. ✅ Enable monitoring/alerts
5. ✅ Setup staging environment (duplicate blueprint)
6. ✅ Integrate với real LLM API
7. ✅ Add Redis cache (uncomment trong render.yaml)

## 📚 Tài liệu thêm

- [Render Docs](https://render.com/docs)
- [Blueprint Spec](https://render.com/docs/blueprint-spec)
- [Deploy Python Apps](https://render.com/docs/deploy-fastapi)
- [Environment Variables](https://render.com/docs/environment-variables)

## 💡 Tips

1. **Dùng Blueprint cho team projects** — Infrastructure as Code giúp team sync dễ dàng
2. **Free tier đủ cho MVP** — Upgrade khi có traffic thật
3. **Monitor cold start time** — Nếu > 30s, consider upgrade hoặc optimize
4. **Dùng Redis cho caching** — Giảm latency và cost LLM API calls
5. **Setup staging environment** — Duplicate blueprint với branch khác

---

**Có vấn đề?** Check [TROUBLESHOOTING.md](../../TROUBLESHOOTING.md) hoặc Render Community Forum.
