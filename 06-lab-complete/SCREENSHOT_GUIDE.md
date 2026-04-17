# Screenshot Guide for Lab 06 Submission

This guide helps you capture all required screenshots for the lab submission.

---

## 📸 Required Screenshots (10 total)

### 1. dashboard.png - Render Dashboard
**What to capture:** Render dashboard showing both services

**Steps:**
1. Go to https://dashboard.render.com/
2. Make sure you can see both services:
   - `ai-agent-redis` (Redis)
   - `ai-agent-app` (Web Service)
3. Both should show "Active" or "Running" status
4. Take screenshot of the entire dashboard

**What should be visible:**
- Service names
- Service types (Redis, Web Service)
- Status indicators (green = healthy)
- Region information

---

### 2. running.png - Service Details
**What to capture:** Individual service status page

**Steps:**
1. Click on `ai-agent-app` service
2. You should see:
   - Service status: "Live"
   - Latest deploy status
   - Health check status
   - Environment variables (blurred if needed)
3. Take screenshot

**What should be visible:**
- Service name and URL
- Deploy status
- Health check passing
- Last deployed time

---

### 3. logs.png - Application Logs
**What to capture:** Live application logs

**Steps:**
1. In the service page, click "Logs" tab
2. You should see logs like:
   ```
   INFO: Starting application...
   INFO: Redis rate limiter initialized
   INFO: Application started successfully
   INFO: Uvicorn running on http://0.0.0.0:10000
   ```
3. Take screenshot showing recent logs

**What should be visible:**
- Startup logs
- Request logs (if any)
- No error messages
- Timestamps

---

### 4. health_check.png - Health Endpoint
**What to capture:** Health endpoint response

**Steps:**
1. Open terminal or Postman
2. Run:
   ```bash
   curl https://conversational-ai-agent-z3q1.onrender.com/health
   ```
3. You should see:
   ```json
   {
     "status": "healthy",
     "timestamp": "2026-04-17T10:30:00",
     "version": "1.0.0"
   }
   ```
4. Take screenshot

**Alternative:** Use browser and visit the URL directly

---

### 5. auth_test.png - Authentication Test
**What to capture:** 401 error when no API key provided

**Steps:**
1. Run:
   ```bash
   curl -X POST https://conversational-ai-agent-z3q1.onrender.com/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}'
   ```
2. You should see:
   ```json
   {
     "detail": "Missing API key. Include X-API-Key header."
   }
   ```
3. Status code should be 401
4. Take screenshot

**Using Postman:**
- Method: POST
- URL: https://conversational-ai-agent-z3q1.onrender.com/chat
- Body: `{"message": "Hello"}`
- Don't add X-API-Key header
- Send and screenshot the 401 response

---

### 6. rate_limit.png - Rate Limiting Test
**What to capture:** 429 error after exceeding rate limit

**Steps:**
1. Run the test script:
   ```bash
   for i in {1..11}; do
     echo "Request $i:"
     curl -X POST https://conversational-ai-agent-z3q1.onrender.com/chat \
       -H "X-API-Key: YOUR_KEY" \
       -H "Content-Type: application/json" \
       -d '{"message":"test"}' \
       -w "\nStatus: %{http_code}\n\n"
     sleep 0.5
   done
   ```
2. The 11th request should return:
   ```json
   {
     "detail": "Rate limit exceeded. Maximum 10 requests per minute."
   }
   ```
3. Status code: 429
4. Take screenshot showing the 429 response

---

### 7. cost_guard.png - Usage Statistics
**What to capture:** Usage endpoint response

**Steps:**
1. Run:
   ```bash
   curl https://conversational-ai-agent-z3q1.onrender.com/usage/YOUR_API_KEY \
     -H "X-API-Key: YOUR_API_KEY"
   ```
2. You should see:
   ```json
   {
     "api_key": "YOUR_API...KEY",
     "monthly_cost": 0.024,
     "monthly_limit": 10.0,
     "remaining_budget": 9.976,
     "requests_this_minute": 3,
     "rate_limit": "10 requests/minute"
   }
   ```
3. Take screenshot

---

### 8. docker_build.png - Docker Image Size
**What to capture:** Docker image size < 500 MB

**Steps:**
1. Run locally:
   ```bash
   docker build -t ai-agent .
   docker images ai-agent
   ```
2. You should see output like:
   ```
   REPOSITORY   TAG       IMAGE ID       CREATED         SIZE
   ai-agent     latest    1f3fa0ea853c   2 minutes ago   187MB
   ```
3. Take screenshot showing SIZE < 500 MB

**Alternative:** Show Render build logs with image size

---

### 9. redis_connected.png - Readiness Check
**What to capture:** Readiness endpoint showing Redis connected

**Steps:**
1. Run:
   ```bash
   curl https://conversational-ai-agent-z3q1.onrender.com/readiness
   ```
2. You should see:
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
3. Take screenshot showing `"redis": true`

---

### 10. web_ui_light.png & web_ui_dark.png - Web Interface
**What to capture:** Web UI in both themes

**Steps for Light Mode:**
1. Open https://conversational-ai-agent-z3q1.onrender.com in browser
2. If in dark mode, click the theme toggle (🌙/☀️)
3. Take screenshot showing:
   - Chat interface
   - Light theme colors
   - Suggestion cards
   - Input box

**Steps for Dark Mode:**
1. Click theme toggle to switch to dark mode
2. Take screenshot showing:
   - Chat interface
   - Dark theme colors
   - Same layout as light mode

---

## 📋 Screenshot Checklist

Before submitting, verify you have:

- [ ] dashboard.png - Render dashboard with both services
- [ ] running.png - Service status page
- [ ] logs.png - Application logs
- [ ] health_check.png - Health endpoint (200 OK)
- [ ] auth_test.png - Authentication test (401)
- [ ] rate_limit.png - Rate limiting (429)
- [ ] cost_guard.png - Usage statistics
- [ ] docker_build.png - Image size < 500 MB
- [ ] redis_connected.png - Readiness with Redis
- [ ] web_ui_light.png - Web UI light mode
- [ ] web_ui_dark.png - Web UI dark mode (optional)

---

## 🛠️ Tools for Taking Screenshots

### Terminal/CLI Screenshots
- **macOS:** Cmd + Shift + 4
- **Windows:** Windows + Shift + S
- **Linux:** Flameshot, Spectacle, or built-in screenshot tool

### Browser Screenshots
- **Chrome/Edge:** F12 → Ctrl+Shift+P → "Capture screenshot"
- **Firefox:** Right-click → "Take Screenshot"
- **Extension:** Awesome Screenshot, Nimbus Screenshot

### API Testing Screenshots
- **Postman:** Built-in screenshot feature
- **Insomnia:** Take screenshot of response
- **Terminal:** Use terminal screenshot tool

---

## 📐 Screenshot Guidelines

### Format
- **File Type:** PNG (preferred) or JPG
- **Resolution:** At least 1280x720
- **File Size:** Keep under 2 MB each

### Content
- ✅ Clear and readable text
- ✅ Relevant information visible
- ✅ No sensitive data (blur API keys if needed)
- ✅ Proper framing (not too zoomed in/out)

### Naming
Use exact names as listed:
- `dashboard.png`
- `running.png`
- `logs.png`
- etc.

### Organization
Save all screenshots in the `screenshots/` directory:
```
screenshots/
├── dashboard.png
├── running.png
├── logs.png
├── health_check.png
├── auth_test.png
├── rate_limit.png
├── cost_guard.png
├── docker_build.png
├── redis_connected.png
├── web_ui_light.png
└── web_ui_dark.png
```

---

## 🔒 Security Notes

### Blur Sensitive Information
Before taking screenshots, blur or hide:
- API keys (except in test examples)
- Admin keys
- Personal information
- Email addresses
- Internal URLs (if any)

### Safe to Show
These are OK to include:
- Public URLs (https://conversational-ai-agent-z3q1.onrender.com)
- Service names
- Status indicators
- Response structures
- HTTP status codes
- Timestamps

---

## ✅ After Taking Screenshots

1. **Review Each Screenshot**
   - Is text readable?
   - Is relevant info visible?
   - Are sensitive data blurred?

2. **Rename Files**
   - Use exact names from checklist
   - All lowercase
   - Use .png extension

3. **Save to Directory**
   ```bash
   mv ~/Downloads/screenshot1.png screenshots/dashboard.png
   mv ~/Downloads/screenshot2.png screenshots/running.png
   # etc.
   ```

4. **Commit to Git**
   ```bash
   git add screenshots/
   git commit -m "Add deployment screenshots"
   git push
   ```

5. **Verify in GitHub**
   - Go to your repository
   - Navigate to `screenshots/` folder
   - Verify all images are visible

---

## 🆘 Troubleshooting

### Screenshot Too Large
```bash
# Compress with ImageMagick
convert input.png -quality 85 -resize 1920x1080 output.png

# Or use online tools
# - TinyPNG.com
# - Squoosh.app
```

### Can't Access Render Dashboard
- Make sure you're logged in
- Check if services are deployed
- Refresh the page

### API Tests Not Working
- Verify URL is correct
- Check API key is set
- Ensure service is running (check Render dashboard)

### Web UI Not Loading
- Check if service is deployed
- Look at Render logs for errors
- Try accessing health endpoint first

---

## 📞 Need Help?

If you encounter issues:
1. Check Render logs for errors
2. Verify all services are running
3. Test endpoints with curl first
4. Review DEPLOYMENT.md for troubleshooting

---

**Good luck with your screenshots! 📸**
