# Screenshot Capture Guide for Day 12 Lab

> **Quick guide to capture all required screenshots for MISSION_ANSWERS.md**

## 🎯 Required Screenshots Checklist

### Part 3: Cloud Deployment (5 screenshots)
- [ ] `railway-dashboard.png` - Main dashboard
- [ ] `railway-running.png` - Service logs  
- [ ] `railway-environment.png` - Environment variables
- [ ] `railway-api-test.png` - API testing
- [ ] `railway-health-check.png` - Health endpoint

### Part 4: API Security (2 screenshots)  
- [ ] `authentication-test.png` - Auth success/failure
- [ ] `rate-limiting-test.png` - Rate limiting demo

### Part 5: Scaling (2 screenshots)
- [ ] `docker-compose-scale.png` - Multiple instances
- [ ] `load-balancing-test.png` - Load distribution

### Part 6: Final Production (6 screenshots)
- [ ] `production-readiness-check.png` - 20/20 checks
- [ ] `final-deployment.png` - Both platforms working
- [ ] `railway-dashboard-final.png` - Final metrics
- [ ] `render-dashboard.png` - Render deployment
- [ ] `api-documentation.png` - FastAPI docs
- [ ] `monitoring-logs.png` - JSON logs

---

## 📸 Step-by-Step Capture Instructions

### 1. Railway Dashboard Screenshots

**A. Main Dashboard (`railway-dashboard.png`)**
```bash
# 1. Go to https://railway.app/dashboard
# 2. Click on your project
# 3. Screenshot showing:
#    - Project name and status (green)
#    - Recent deployments
#    - Service overview
#    - Usage metrics
```

**B. Service Running (`railway-running.png`)**
```bash
# 1. In Railway dashboard, click on your service
# 2. Go to "Logs" tab
# 3. Screenshot showing:
#    - Live logs with JSON format
#    - Request processing
#    - No errors
```

**C. Environment Variables (`railway-environment.png`)**
```bash
# 1. In service dashboard, click "Variables" tab
# 2. Screenshot showing:
#    - AGENT_API_KEY (value hidden)
#    - ENVIRONMENT=production
#    - Other variables
```

### 2. API Testing Screenshots

**A. Authentication Test (`authentication-test.png`)**
```bash
# Use terminal or Postman to capture both scenarios:

# Without API key (should return 401)
curl -X POST https://day12-agent-production.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}' \
  -w "\nHTTP Status: %{http_code}\n"

# With API key (should return 200)
curl -X POST https://day12-agent-production.up.railway.app/ask \
  -H "X-API-Key: prod-secure-key-vtp-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}' \
  -w "\nHTTP Status: %{http_code}\n"

# Screenshot both responses side by side
```

**B. Rate Limiting Test (`rate-limiting-test.png`)**
```bash
# Run this script and screenshot the output:
echo "Testing rate limiting..."
for i in {1..25}; do
  echo "Request $i:"
  curl -X POST https://day12-agent-production.up.railway.app/ask \
    -H "X-API-Key: prod-secure-key-vtp-2026" \
    -H "Content-Type: application/json" \
    -d '{"question": "Test '$i'"}' \
    -w "HTTP Status: %{http_code}\n" \
    -s -o /dev/null
  sleep 0.5
done

# Screenshot showing:
# - First 20 requests: Status 200
# - Requests 21+: Status 429
```

**C. Health Check (`railway-health-check.png`)**
```bash
# Test health endpoint
curl https://day12-agent-production.up.railway.app/health | jq

# Screenshot showing JSON response with:
# - "status": "ok"
# - uptime_seconds
# - timestamp
```

### 3. Docker & Scaling Screenshots

**A. Multiple Instances (`docker-compose-scale.png`)**
```bash
# In your 06-lab-complete directory:
docker compose up --scale agent=3 -d
docker compose ps

# Screenshot showing:
# - 3 agent containers running
# - 1 redis container
# - All healthy status
```

**B. Load Balancing (`load-balancing-test.png`)**
```bash
# Test load distribution:
for i in {1..10}; do
  echo "Request $i to load balancer:"
  curl http://localhost/ask -X POST \
    -H "X-API-Key: dev-key-change-me" \
    -H "Content-Type: application/json" \
    -d '{"question": "Request '$i'"}'
  echo ""
done

# Then check logs:
docker compose logs agent

# Screenshot showing requests distributed across different containers
```

### 4. Production Readiness Check

**Production Readiness (`production-readiness-check.png`)**
```bash
cd 06-lab-complete
python check_production_ready.py

# Screenshot the full output showing:
# - All sections (Files, Security, API Endpoints, Docker)
# - All ✅ green checkmarks
# - "Result: 20/20 checks passed (100%)"
# - "🎉 PRODUCTION READY! Deploy nào!"
```

### 5. Final Deployment Screenshots

**A. Railway Final Dashboard (`railway-dashboard-final.png`)**
```bash
# Go to Railway dashboard main view
# Screenshot showing:
# - Project overview with metrics
# - Deployment history
# - Resource usage graphs
# - Public URL
```

**B. Render Dashboard (`render-dashboard.png`)**
```bash
# Go to https://dashboard.render.com
# Click on your service
# Screenshot showing:
# - Service status (Live)
# - Recent deployments
# - Public URL
# - Environment variables
```

**C. API Documentation (`api-documentation.png`)**
```bash
# Open in browser:
# https://day12-agent-production.up.railway.app/docs

# Screenshot showing:
# - FastAPI Swagger UI
# - All endpoints listed (/health, /ready, /ask, /metrics)
# - Try it out functionality
```

**D. Monitoring Logs (`monitoring-logs.png`)**
```bash
# In Railway dashboard, go to Logs tab
# Make a few API requests to generate logs
# Screenshot showing:
# - JSON formatted logs
# - Request/response logging
# - No errors
# - Structured format with timestamps
```

---

## 🛠 Tools for Screenshots

### Recommended Tools
- **Windows**: Snipping Tool, Snagit, or Win+Shift+S
- **Mac**: Cmd+Shift+4 for selection, Cmd+Shift+3 for full screen
- **Linux**: GNOME Screenshot, Flameshot, or Spectacle
- **Browser**: Built-in developer tools for network requests

### Terminal Screenshots
- **Windows**: Windows Terminal with good contrast
- **Mac/Linux**: Terminal with clear font and good contrast
- Use `curl` with `-w` flag for status codes
- Use `jq` for pretty JSON formatting

### Browser Screenshots
- Use incognito/private mode for clean interface
- Zoom to 100% for clarity
- Include URL bar to show the domain
- Use developer tools to show network requests

---

## ✅ Quality Checklist

Before submitting screenshots:

### Technical Quality
- [ ] **Resolution**: At least 1920x1080 for desktop
- [ ] **Format**: PNG for clarity (not JPG)
- [ ] **Readability**: All text clearly visible
- [ ] **Complete**: Full context shown, not cropped

### Content Quality  
- [ ] **Accurate**: Shows current deployment state
- [ ] **Relevant**: Matches the referenced content
- [ ] **Secure**: No API keys or secrets visible
- [ ] **Professional**: Clean, organized appearance

### Verification
- [ ] **File names**: Match references in MISSION_ANSWERS.md
- [ ] **All required**: 15 total screenshots captured
- [ ] **Working URLs**: Screenshots show live, working services
- [ ] **Success cases**: Demonstrate successful deployment
- [ ] **Error cases**: Show proper error handling (401, 429)

---

## 🚨 Common Mistakes to Avoid

### Security Issues
- ❌ **Don't show**: Full API keys, secrets, passwords
- ❌ **Don't include**: Personal information, email addresses
- ❌ **Don't capture**: Private repository URLs

### Technical Issues
- ❌ **Blurry text**: Ensure screenshots are sharp
- ❌ **Wrong URLs**: Use your actual deployment URLs
- ❌ **Old screenshots**: Should show current state
- ❌ **Partial captures**: Show complete context

### Content Issues
- ❌ **Wrong responses**: Ensure APIs are actually working
- ❌ **Missing errors**: Should show 401, 429 responses
- ❌ **No timestamps**: Include when possible for recency

---

## 📝 Final Verification

After capturing all screenshots:

1. **Check file names** match MISSION_ANSWERS.md references
2. **Verify all 15 screenshots** are captured
3. **Test that URLs work** from different devices
4. **Review for sensitive data** before submission
5. **Ensure quality standards** are met

---

**Ready to capture? Start with Railway dashboard and work through the list systematically!** 📸

*This guide ensures you have all evidence needed to demonstrate successful completion of Day 12 Lab requirements.*