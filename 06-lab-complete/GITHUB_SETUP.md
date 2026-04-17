# GitHub Repository Setup Guide

## Quick Setup

### 1. Create GitHub Repository

Go to https://github.com/new and create a new repository:
- **Name:** `conversational-ai-agent`
- **Description:** Production-ready AI conversational agent with FastAPI, Redis, and Render deployment
- **Visibility:** Public
- **Initialize:** Don't add README, .gitignore, or license (we already have them)

### 2. Push Your Code

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Production AI agent - Lab 06 complete"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/conversational-ai-agent.git

# Push to main branch
git branch -M main
git push -u origin main
```

### 3. Verify Repository

Visit your repository at:
```
https://github.com/YOUR_USERNAME/conversational-ai-agent
```

Check that all files are present:
- ✅ app/ directory
- ✅ utils/ directory
- ✅ static/ directory
- ✅ templates/ directory
- ✅ Dockerfile
- ✅ docker-compose.yml
- ✅ requirements.txt
- ✅ render.yaml
- ✅ README.md
- ✅ DEPLOYMENT.md
- ✅ MISSION_ANSWERS.md
- ✅ DAY12_DELIVERY_CHECKLIST.md
- ❌ .env (should NOT be present - only .env.example)

## Update Documentation with Your Repository URL

After creating the repository, update these files:

### 1. DAY12_DELIVERY_CHECKLIST.md
Replace:
```markdown
**GitHub Repository:** https://github.com/phuvo05/conversational-ai-agent
```
With:
```markdown
**GitHub Repository:** https://github.com/YOUR_USERNAME/conversational-ai-agent
```

### 2. MISSION_ANSWERS.md
Add at the bottom:
```markdown
**Repository:** https://github.com/YOUR_USERNAME/conversational-ai-agent
```

### 3. README.md
Add a badge at the top:
```markdown
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

[View on GitHub](https://github.com/YOUR_USERNAME/conversational-ai-agent)
```

## Commit and Push Updates

```bash
git add .
git commit -m "Update repository URLs"
git push
```

## Connect to Render

### Option 1: Blueprint Deployment (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New"** → **"Blueprint"**
3. Click **"Connect GitHub"** (if not already connected)
4. Select your repository: `conversational-ai-agent`
5. Render will detect `render.yaml`
6. Click **"Apply"**
7. Wait 3-5 minutes for deployment

### Option 2: Manual Deployment

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Create Redis:
   - Click **"New"** → **"Redis"**
   - Name: `ai-agent-redis`
   - Plan: Free
   - Click **"Create Redis"**
3. Create Web Service:
   - Click **"New"** → **"Web Service"**
   - Connect your GitHub repository
   - Settings:
     - **Name:** `ai-agent-app`
     - **Environment:** Docker
     - **Plan:** Free
     - **Health Check Path:** `/health`
   - Environment Variables:
     - `REDIS_URL`: (copy from Redis instance)
     - `REDIS_ENABLED`: `true`
     - `API_KEY`: (generate secure key)
     - `ADMIN_API_KEY`: (generate secure key)
     - `RATE_LIMIT_REQUESTS`: `10`
     - `RATE_LIMIT_WINDOW`: `60`
     - `MONTHLY_COST_LIMIT`: `10.0`
   - Click **"Create Web Service"**

## Auto-Deploy on Push

Render automatically deploys when you push to the main branch:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push

# Render will automatically detect and deploy
```

## Repository Best Practices

### Branch Protection (Optional)
1. Go to repository **Settings** → **Branches**
2. Add rule for `main` branch:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass

### Add Topics
Add relevant topics to your repository:
- `fastapi`
- `python`
- `docker`
- `redis`
- `render`
- `ai-agent`
- `chatbot`
- `production-ready`

### Add Description
Set repository description:
```
Production-ready AI conversational agent with FastAPI, Redis, rate limiting, cost guard, and Render deployment
```

### Add README Badge
Add deployment status badge to README.md:
```markdown
![Deployment Status](https://img.shields.io/badge/deployment-active-success)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
```

## Troubleshooting

### Push Rejected
If you get "push rejected" error:
```bash
git pull origin main --rebase
git push origin main
```

### Large Files
If you accidentally committed large files:
```bash
# Remove from git history
git rm --cached large-file.bin
git commit -m "Remove large file"
git push
```

### .env Committed by Mistake
If you accidentally committed .env:
```bash
# Remove from git
git rm --cached .env
git commit -m "Remove .env file"
git push

# Rotate all secrets immediately!
```

## Security Checklist

Before making repository public:
- ✅ No `.env` file committed
- ✅ No API keys in code
- ✅ No passwords in code
- ✅ `.env.example` has placeholder values only
- ✅ `.gitignore` includes `.env`
- ✅ All secrets in Render environment variables

## Next Steps

1. ✅ Create GitHub repository
2. ✅ Push code
3. ✅ Connect to Render
4. ✅ Deploy services
5. ✅ Test deployment
6. ✅ Take screenshots
7. ✅ Update documentation with URLs
8. ✅ Final commit and push
9. ✅ Submit assignment

---

**Need Help?**
- GitHub Docs: https://docs.github.com/
- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com/
