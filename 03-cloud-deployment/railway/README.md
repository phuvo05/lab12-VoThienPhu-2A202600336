# Deploy AI Agent lên Railway

Railway là platform deploy đơn giản nhất cho AI agent. Không cần config phức tạp, tự động scale, và có free tier.

## 🚀 Quick Deploy (< 5 phút)

### Cách 1: Deploy từ GitHub (Khuyến nghị)

1. **Push code lên GitHub repository**
2. **Vào Railway Dashboard**: https://railway.app
3. **New Project** → **Deploy from GitHub repo**
4. **Chọn repository** và branch
5. **Railway tự động detect Python** và deploy
6. **Nhận URL**: `https://your-app.up.railway.app`

### Cách 2: Deploy từ CLI

```bash
# 1. Cài Railway CLI
npm install -g @railway/cli
# hoặc
brew install railway

# 2. Login
railway login

# 3. Khởi tạo project (trong thư mục này)
cd 03-cloud-deployment/railway
railway init

# 4. Deploy
railway up

# 5. Xem logs
railway logs

# 6. Mở app trong browser
railway open
```

## 📋 Cấu trúc file

```
railway/
├── app.py              # FastAPI app (Railway-ready)
├── requirements.txt    # Python dependencies
├── railway.toml        # Railway configuration
├── Procfile           # Start command (alternative)
├── .env.example       # Environment variables template
└── utils/
    └── mock_llm.py    # Mock LLM cho demo
```

## ⚙️ Cấu hình quan trọng

### 1. PORT Environment Variable

Railway tự động inject biến `PORT`. App **PHẢI** đọc từ env:

```python
port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)
```

### 2. Health Check

Railway check `/health` endpoint để biết app còn sống không:

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

### 3. Start Command

Railway dùng 1 trong 3 (theo thứ tự ưu tiên):

1. `railway.toml` → `[deploy].startCommand`
2. `Procfile` → `web: python app.py`
3. Auto-detect (Nixpacks)

## 🔧 Set Environment Variables

### Qua CLI:
```bash
railway variables set OPENAI_API_KEY=sk-xxx
railway variables set ENVIRONMENT=production
```

### Qua Dashboard:
1. Vào project → **Variables** tab
2. Add variable: `OPENAI_API_KEY` = `sk-xxx`
3. Railway tự động redeploy

## 📊 Monitoring

```bash
# Xem logs real-time
railway logs

# Xem metrics
railway status

# SSH vào container (debug)
railway shell
```

## 🧪 Test sau khi deploy

```bash
# Lấy URL
RAILWAY_URL=$(railway status --json | jq -r '.url')

# Test root endpoint
curl $RAILWAY_URL/

# Test health check
curl $RAILWAY_URL/health

# Test AI agent
curl -X POST $RAILWAY_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello Railway!"}'
```

## 💰 Pricing

- **Free tier**: $5 credit/month (đủ cho demo/MVP)
- **Hobby**: $5/month (500 hours execution)
- **Pro**: $20/month (unlimited)

## 🐛 Troubleshooting

### App không start được

```bash
# Xem logs chi tiết
railway logs

# Check biến môi trường
railway variables

# Restart service
railway restart
```

### Port binding error

❌ **Sai**: Hard-code port
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

✅ **Đúng**: Đọc từ env
```python
port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)
```

### Health check fail

- Đảm bảo `/health` endpoint trả về 200 OK
- Tăng `healthcheckTimeout` trong `railway.toml`
- Check logs xem app có crash không

## 🔄 CI/CD Tự động

Railway tự động deploy khi:
- Push code lên GitHub branch được connect
- Merge pull request
- Manual trigger từ dashboard

Không cần setup GitHub Actions hay CI/CD pipeline riêng!

## 📚 Tài liệu thêm

- [Railway Docs](https://docs.railway.com)
- [Railway Config Reference](https://docs.railway.com/reference/config-as-code)
- [Railway CLI](https://docs.railway.com/develop/cli)

## 🎯 Next Steps

Sau khi deploy thành công:
1. ✅ Test tất cả endpoints
2. ✅ Setup custom domain (nếu cần)
3. ✅ Enable monitoring/alerts
4. ✅ Setup staging environment
5. ✅ Integrate với real LLM API (OpenAI/Anthropic)
