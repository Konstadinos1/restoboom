# RestoBoom Mini Audit — Deployment Guide

## 🖥️ Localhost (Quick Test)

### Option 1: Open Directly (Fastest)
```bash
# Just open the HTML file in your browser
open /root/.openclaw/workspace/automation/mini-audit-questionnaire.html
# or on Linux:
xdg-open /root/.openclaw/workspace/automation/mini-audit-questionnaire.html
```

### Option 2: Simple HTTP Server
```bash
cd /root/.openclaw/workspace/automation

# Python 3
python3 -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000

# Node.js (if installed)
npx http-server -p 8000

# Then open: http://localhost:8000/mini-audit-questionnaire.html
```

### Option 3: Live Server (VS Code)
1. Install "Live Server" extension
2. Right-click `mini-audit-questionnaire.html`
3. Select "Open with Live Server"

---

## 🌐 Online Deployment Options

### Free Options (No Cost)

#### 1. GitHub Pages (Recommended for demos)
```bash
# 1. Create a new repo on GitHub
# 2. Push the file
git init
git add mini-audit-questionnaire.html
git commit -m "Add RestoBoom audit questionnaire"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/restoboom-audit.git
git push -u origin main

# 3. Enable GitHub Pages in repo settings
# Settings → Pages → Source: main branch → Save

# Access at: https://YOUR_USERNAME.github.io/restoboom-audit/
```

#### 2. Netlify Drag & Drop (Easiest)
1. Go to https://app.netlify.com/drop
2. Drag the `mini-audit-questionnaire.html` file
3. Get instant URL (e.g., `https://random-name.netlify.app`)
4. Custom domain: Add custom domain in settings

#### 3. Vercel
```bash
# Install Vercel CLI
npm i -g vercel

cd /root/.openclaw/workspace/automation
vercel

# Follow prompts, get instant URL
```

### Paid Options (Custom Domain)

#### 4. Cloudflare Pages
- Free tier + custom domain
- Global CDN
- Auto HTTPS

#### 5. Railway / Render
- Easy deployment
- Free tier available
- Good for adding backend later

---

## 📝 Adding Data Capture (Backend)

To save responses to a database or send emails, you'll need a backend. Options:

### Option A: Formspree (Easiest, Free tier)
Add to HTML form:
```html
<form action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
  <!-- Add fields with name attributes -->
  <input type="hidden" name="_subject" value="New Audit Submission">
</form>
```

### Option B: Netlify Forms
Add to HTML:
```html
<form name="audit-submission" method="POST" data-netlify="true">
  <input type="hidden" name="form-name" value="audit-submission">
</form>
```

### Option C: Custom Backend (Node.js, Flask, etc.)
- I can create a simple Express/Flask server
- Connect to database (MongoDB, PostgreSQL)
- Send emails (SendGrid, Mailgun)
- Store in Stripe for payments

---

## 🎯 Next Steps

1. **Test locally** — Open the HTML file and try it
2. **Choose deployment** — Pick free or paid option
3. **Add data capture** — Formspree for quick start, or custom backend
4. **Custom domain** — Add `audit.restoboom.com` or similar

---

Want me to:
- Help you deploy to a specific platform?
- Set up Formspree for data capture?
- Create a backend server?
- Add payment integration (Stripe)?

Let me know your preference!
