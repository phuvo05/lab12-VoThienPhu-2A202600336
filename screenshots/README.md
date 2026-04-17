# Screenshots Directory

This directory contains screenshots demonstrating the deployment and functionality of the production AI agent for Day 12 Lab submission.

## Required Screenshots for MISSION_ANSWERS.md

### Part 3: Cloud Deployment
- `railway-dashboard.png` - Railway project dashboard showing deployment status
- `railway-running.png` - Live service with logs and metrics  
- `railway-environment.png` - Environment variables configuration
- `railway-api-test.png` - Successful API calls with authentication
- `railway-health-check.png` - Health endpoint response

### Part 4: API Security
- `authentication-test.png` - 401 response without API key and 200 with valid key
- `rate-limiting-test.png` - Rate limiting in action (429 responses after 20 requests)

### Part 5: Scaling & Reliability
- `docker-compose-scale.png` - 3 agent instances running with docker compose
- `load-balancing-test.png` - Requests distributed across multiple instances

### Part 6: Final Production Agent
- `production-readiness-check.png` - 20/20 checks passed with detailed breakdown
- `final-deployment.png` - Both Railway and Render deployments working
- `railway-dashboard-final.png` - Final Railway dashboard with metrics
- `render-dashboard.png` - Render deployment dashboard (backup)
- `api-documentation.png` - FastAPI auto-generated documentation
- `monitoring-logs.png` - Structured JSON logs showing request processing

## Additional Screenshots for DEPLOYMENT.md

### Performance & Monitoring
- `load-test-results.png` - Performance testing results
- `metrics-dashboard.png` - Service metrics and monitoring
- `error-handling.png` - Proper error responses (401, 429, 503)
- `security-headers.png` - Security headers in responses

## How to Capture Screenshots

### 1. Railway Dashboard Screenshots

```bash
# Go to https://railway.app/dashboard
# Select your project
# Capture screenshots showing:
# - Service status (green/running)
# - Recent deployments
# - Environment variables
# - Metrics/usage
# - Logs with JSON format
```

### 2. API Testing Screenshots

```bash
# Use curl with verbose output or Postman
curl -v https://day12-agent-production.up.railway.app/health

# Test authentication (should show 401 then 200)
curl -v -X POST https://day12-agent-production.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'

curl -v -X POST https://day12-agent-production.up.railway.app/ask \
  -H "X-API-Key: prod-secure-key-vtp-2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'

# Test rate limiting (capture 429 responses)
for i in {1..25}; do 
  curl -X POST https://day12-agent-production.up.railway.app/ask \
    -H "X-API-Key: prod-secure-key-vtp-2026" \
    -H "Content-Type: application/json" \
    -d '{"question": "Test '$i'"}' \
    -w "Status: %{http_code}\n"
done
```

### 3. Docker & Scaling Screenshots

```bash
# Show multiple instances
docker compose up --scale agent=3
docker compose ps

# Show load balancing
for i in {1..10}; do
  curl http://localhost/ask -X POST \
    -H "X-API-Key: dev-key-change-me" \
    -H "Content-Type: application/json" \
    -d '{"question": "Request '$i'"}'
done

# Check logs to see distribution
docker compose logs agent
```

### 4. Production Readiness Check

```bash
# Run the checker and capture output
cd 06-lab-complete
python check_production_ready.py
```

### 5. Browser Screenshots

- Open https://day12-agent-production.up.railway.app/docs
- Test endpoints through Swagger UI
- Show successful and error responses
- Capture API documentation

## Screenshot Guidelines

### Quality Requirements
- **Resolution**: Minimum 1920x1080 for desktop screenshots
- **Format**: PNG preferred for clarity
- **Content**: Should be clearly readable
- **Timestamps**: Include when possible to show recency

### What to Show
- ✅ **Success scenarios**: Working deployments, successful API calls
- ✅ **Error scenarios**: 401, 429, 503 responses as expected
- ✅ **Security features**: Authentication, rate limiting in action
- ✅ **Monitoring**: Logs, metrics, health checks
- ✅ **Infrastructure**: Multiple instances, load balancing

### What to Avoid
- ❌ **Sensitive data**: API keys, secrets, personal information
- ❌ **Blurry images**: Ensure text is readable
- ❌ **Incomplete captures**: Show full context, not partial screens
- ❌ **Old screenshots**: Should reflect current deployment state

## File Naming Convention

Use descriptive names that match the references in MISSION_ANSWERS.md:
- `railway-dashboard.png` (not `screenshot1.png`)
- `authentication-test.png` (not `auth.png`)
- `production-readiness-check.png` (not `check.png`)

## Verification Checklist

Before submission, ensure you have:
- [ ] All screenshots referenced in MISSION_ANSWERS.md
- [ ] Screenshots show successful deployments
- [ ] API testing screenshots show both success and error cases
- [ ] Production readiness check shows 20/20 passed
- [ ] No sensitive information visible
- [ ] All images are clear and readable
- [ ] File names match the references in documentation

---

*Note: These screenshots serve as evidence of successful completion of all lab requirements and demonstrate the working production deployment.*