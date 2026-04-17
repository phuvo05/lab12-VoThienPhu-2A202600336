# Screenshots Directory

This directory contains deployment and testing screenshots for the Production AI Agent.

## Required Screenshots

### Deployment Screenshots
1. **dashboard.png** - Render dashboard showing both services (web service + Redis)
2. **running.png** - Services status page showing healthy state
3. **logs.png** - Application logs showing startup and requests

### API Testing Screenshots
4. **health_check.png** - Health endpoint returning 200 OK
   ```bash
   curl https://conversational-ai-agent-z3q1.onrender.com/health
   ```

5. **auth_test.png** - Authentication test showing 401 without API key
   ```bash
   curl -X POST https://conversational-ai-agent-z3q1.onrender.com/chat
   ```

6. **rate_limit.png** - Rate limiting test showing 429 after 10 requests
   ```bash
   # Send 11 requests, 11th returns 429
   ```

7. **cost_guard.png** - Usage statistics endpoint response
   ```bash
   curl https://conversational-ai-agent-z3q1.onrender.com/usage/YOUR_KEY
   ```

### Technical Screenshots
8. **docker_build.png** - Docker image size showing < 500 MB
   ```bash
   docker images ai-agent
   ```

9. **redis_connected.png** - Readiness check showing Redis connected
   ```bash
   curl https://conversational-ai-agent-z3q1.onrender.com/readiness
   ```

### UI Screenshots
10. **web_ui_light.png** - Web interface in light mode
11. **web_ui_dark.png** - Web interface in dark mode

## How to Take Screenshots

### For API Tests
Use a tool like Postman, Insomnia, or curl with terminal screenshots:
```bash
# Example with curl
curl -X POST https://conversational-ai-agent-z3q1.onrender.com/chat \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### For Web UI
1. Open https://conversational-ai-agent-z3q1.onrender.com in browser
2. Take screenshot of light mode
3. Click theme toggle (🌙/☀️)
4. Take screenshot of dark mode

### For Render Dashboard
1. Go to https://dashboard.render.com/
2. Navigate to your services
3. Take screenshot showing both services running

## Screenshot Guidelines

- **Format:** PNG or JPG
- **Resolution:** At least 1280x720
- **Content:** Clear, readable text
- **Annotations:** Optional but helpful (arrows, highlights)
- **File Size:** Keep under 2 MB each

## Naming Convention

Use the exact names listed above for consistency with documentation references.
