# 🚀 DEPLOYMENT GUIDE - RENDER.COM

## Step 1: Create GitHub Account (If you don't have one)
- Go to **github.com**
- Sign up (free)
- Create new repository: `hosting-panel`

## Step 2: Upload Files to GitHub

**Option A: Using GitHub Web Interface (Easiest - No Git needed)**

1. Go to your GitHub repo
2. Click **"Add file"** → **"Upload files"**
3. Select ALL files from `c:\Users\Admin\Documents\hosting_panel\`
4. Include:
   - `app.py`
   - `requirements.txt`
   - `README.md`
   - `.gitignore`
   - `templates/` folder (all HTML files)
5. Commit and push

**Option B: Install Git Desktop**
1. Download from **https://desktop.github.com**
2. Follow setup wizard
3. Clone your repo locally
4. Drag files into folder
5. Commit and push

---

## Step 3: Deploy on Render

### A. Connect GitHub to Render

1. Go to **https://render.com**
2. Click **"Sign up"** → use GitHub account
3. Click **"New +"** → **"Web Service"**
4. Select **"Connect a repository"**
5. Select your `hosting-panel` repo
6. Click **"Connect"**

### B. Configure Deployment

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `bot-hosting-panel` |
| **Region** | Singapore or US |
| **Runtime** | Python 3 |
| **Root Directory** | (leave blank) |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -w 4 -b 0.0.0.0:$PORT app:app` |

### C. Add Environment Variables

Click **"Environment"** and add:

```
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here-make-it-random
```

Generate random key:
```
python -c "import secrets; print(secrets.token_hex(32))"
```

### D. Deploy!

1. Click **"Create Web Service"**
2. Wait 2-3 minutes for build to complete
3. Get your URL (looks like: `https://bot-hosting-panel.onrender.com`)

---

## Step 4: Test Your Panel

1. Open your Render URL
2. Create account
3. Test uploading a bot
4. Start/stop bot
5. Check logs

---

## Step 5: Update Your App (if needed)

After making changes:

1. Update files on GitHub (Web interface or Git Desktop)
2. Render auto-detects changes
3. Auto-deploys in ~2 minutes

---

## 🎯 YOUR PANEL IS LIVE!

**Panel URL:** `https://bot-hosting-panel.onrender.com`

### Next: Add Payment Processing

To accept actual payments:
1. Create Stripe account
2. Get API keys
3. Update `app.py` with Stripe code
4. Redeploy

---

## Troubleshooting

**Q: Getting error on deploy?**
A: Check Render logs for error message, fix, and re-push to GitHub

**Q: Panel very slow?**
A: Render free tier has limits, upgrade to paid for better performance

**Q: Can't upload bot files?**
A: Check file permissions and upload_folder exists

**Q: Database not persisting?**
A: Render has ephemeral storage, use PostgreSQL for production

---

## 💡 Pro Tips

1. **Add Stripe payments** to earn real money
2. **Monitor bot resource usage** (CPU/RAM limits)
3. **Setup backups** of database
4. **Use custom domain** (yourdomain.com)
5. **Add SSL certificate** (free on Render)

---

Let me know when done! 🎉
