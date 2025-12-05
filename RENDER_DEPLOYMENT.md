# Render Deployment Guide for Obsidian BBS

This guide walks you through deploying both the main app and ChromaDB on Render.

## Part 1: Deploy ChromaDB First

### Step 1: Create ChromaDB Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository (same repo)

### Step 2: Configure ChromaDB Service

**Basic Settings:**
- **Name:** `obsidian-bbs-chromadb`
- **Region:** Same as your main app
- **Branch:** `main`
- **Root Directory:** Leave blank
- **Runtime:** `Docker`

**Build & Deploy:**
- **Dockerfile Path:** `Dockerfile.chroma`

**Instance Type:**
- Select **"Free"** (or "Starter" for better performance)

### Step 3: Deploy ChromaDB

- Click **"Create Web Service"**
- Wait for deployment (2-3 minutes)
- **Copy the service URL** (e.g., `https://obsidian-bbs-chromadb.onrender.com`)

### Step 4: Note the Internal URL

Render provides an internal URL for service-to-service communication:
- Format: `obsidian-bbs-chromadb:8000`
- Or use the external URL: `obsidian-bbs-chromadb.onrender.com`

---

## Part 2: Deploy Main Obsidian BBS App

### Step 1: Create Main Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Click **"Connect"**

### Step 2: Configure Main Service

**Basic Settings:**
- **Name:** `obsidian-bbs`
- **Region:** Same as ChromaDB
- **Branch:** `main`
- **Root Directory:** Leave blank
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:**
  ```
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```
  uvicorn backend.main:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- Select **"Free"** or **"Starter"**

### Step 3: Add Environment Variables

Click **"Add from .env"** and paste your entire `.env` file content.

Then **update these specific variables:**

| Variable | Value |
|----------|-------|
| `ENVIRONMENT` | `production` |
| `CORS_ORIGINS` | `https://obsidian-bbs.onrender.com` (update after deploy) |
| `JWT_SECRET_KEY` | Generate new: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `CHROMADB_HOST` | `obsidian-bbs-chromadb.onrender.com` |
| `CHROMADB_PORT` | `443` (for HTTPS) or `8000` (for HTTP) |
| `INSTANT_ANSWER_ENABLED` | `true` |

**Important:** Use the ChromaDB URL you copied in Part 1!

### Step 4: Deploy Main App

- Click **"Create Web Service"**
- Wait for deployment (3-5 minutes)
- You'll get your app URL: `https://obsidian-bbs.onrender.com`

### Step 5: Update CORS

After deployment:
1. Go to **"Environment"** tab
2. Update `CORS_ORIGINS` with your actual Render URL
3. Click **"Save Changes"** (auto-redeploys)

---

## Part 3: Verify Everything Works

### Test ChromaDB Connection

1. Visit: `https://obsidian-bbs-chromadb.onrender.com/api/v1/heartbeat`
2. Should return: `{"nanosecond heartbeat": ...}`

### Test Main App

1. Visit: `https://obsidian-bbs.onrender.com`
2. Register a new account
3. Log in
4. Join Techline: `/join Techline`
5. Ask a question to test Instant Answer

---

## Troubleshooting

### ChromaDB Connection Issues

**Error:** "Connection refused" or "Cannot connect to ChromaDB"

**Solutions:**
1. Check ChromaDB service is running (green status in Render)
2. Verify `CHROMADB_HOST` matches your ChromaDB service URL
3. Try both ports: `443` (HTTPS) or `8000` (HTTP)
4. Check ChromaDB logs for errors

### Using Internal URLs (Faster & Free)

If both services are on Render, use internal networking:

```
CHROMADB_HOST=obsidian-bbs-chromadb
CHROMADB_PORT=8000
```

This is faster and doesn't count against bandwidth limits.

### Free Tier Limitations

- **Both services spin down after 15 minutes of inactivity**
- First request takes 30-60 seconds to wake up
- ChromaDB data persists during the session but may reset on redeploy
- For production, upgrade to paid tier for persistent storage

---

## Cost Estimate

**Free Tier:**
- Main App: Free
- ChromaDB: Free
- Total: $0/month (with limitations)

**Starter Tier (Recommended for Production):**
- Main App: $7/month
- ChromaDB: $7/month
- Total: $14/month (no spin-down, better performance)

---

## Next Steps

1. Set up PostgreSQL for persistent data (optional)
2. Configure custom domain (optional)
3. Set up monitoring and alerts
4. Enable auto-deploy on Git push

Need help? Check Render's [documentation](https://render.com/docs) or their support.
