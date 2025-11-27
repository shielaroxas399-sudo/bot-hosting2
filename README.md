# 🤖 Bot Hosting Panel

A complete bot hosting platform to earn money! Users pay to host their bots 24/7.

## Features

✅ User Authentication (Register/Login)  
✅ Upload bots (ZIP or individual files)  
✅ Start/Stop/Restart bots  
✅ Real-time logs viewer  
✅ Pricing plans (1/3/6/12 months)  
✅ Payment processing (Stripe/PayPal integration ready)  
✅ Beautiful dashboard  
✅ Auto-restart on crash  

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Locally
```bash
python app.py
```

Visit: http://localhost:5000

### 3. Deploy on VPS (DigitalOcean / Linode / AWS)

**Step-by-step:**

1. Create VPS account (DigitalOcean/Linode - $5/month)
2. SSH into server:
   ```bash
   ssh root@your_server_ip
   ```

3. Install Python & dependencies:
   ```bash
   apt update
   apt install python3 python3-pip python3-venv
   ```

4. Clone your repo:
   ```bash
   git clone https://github.com/yourusername/hosting_panel.git
   cd hosting_panel
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. Run with Gunicorn (production server):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app &
   ```

6. (Optional) Setup SSL with Let's Encrypt:
   ```bash
   apt install certbot python3-certbot-nginx
   certbot certonly --standalone -d yourdomainname.com
   ```

7. (Optional) Setup Nginx reverse proxy for better performance

### 4. Add Payment Integration

**Stripe Setup:**
1. Create account at stripe.com
2. Get API keys
3. Add to `app.py`:
   ```python
   import stripe
   stripe.api_key = "your_secret_key"
   ```

**PayPal Setup:**
1. Create account at paypal.com/developers
2. Get credentials
3. Integrate PayPal SDK

## How to Earn Money

1. **Setup pricing** (in `PLANS` dictionary)
2. **Users upload bots** → Pay monthly fee
3. **Your server hosts them** 24/7
4. **Profit!** 💰

### Example Profit Model:
- 1 Month: ₱100 = ~40% profit margin
- 100 users × ₱100 = ₱10,000/month
- Server cost: ₱500-2000/month
- **Net profit: ₱8,000-9,500/month!**

## File Structure
```
hosting_panel/
├── app.py                 # Main Flask app
├── requirements.txt       # Dependencies
├── hosting_panel.db      # SQLite database (auto-created)
├── user_bots/            # Hosted bot files (auto-created)
└── templates/
    ├── login.html
    ├── register.html
    ├── dashboard.html
    └── pricing.html
```

## Security Tips

1. ⚠️ Change `SECRET_KEY` in production
2. ⚠️ Use HTTPS (Let's Encrypt)
3. ⚠️ Sandbox each bot (file permissions)
4. ⚠️ Monitor resource usage (CPU/RAM limits)
5. ⚠️ Backup database regularly

## Common Issues

**Q: Bot not starting?**
A: Check main_file path and requirements installed

**Q: Process not stopping?**
A: Use `pkill -f bot_name` from server

**Q: Database locked error?**
A: Restart Flask app

## Next Steps

1. Deploy on DigitalOcean/Render
2. Add Stripe payment processing
3. Add refund system
4. Add admin dashboard
5. Add SMS notifications
6. Add API for automated purchases

## Support

For issues, create an issue on GitHub or contact support.

---

Made with ❤️ for earning passive income! 💰
