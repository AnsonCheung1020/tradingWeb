# Trading404 — Live Web App

A Django web application showcasing trading screeners, quantitative research
(Quant Lab), and blog posts. Hosted free on **Render** with auto-deploy from GitHub.

🔗 **Live site:** `https://tradingweb.onrender.com` *(once deployed — see below)*

---

## Why Render (not GitHub Pages)?

GitHub Pages can **only host static sites** (plain HTML/CSS/JS). This app is
**Django** — it runs Python on the server (database, views, quant_lab catalog).
That needs a real application server. **Render** is the modern Heroku-style host
that:

- ✅ Has a free tier (sufficient for a CV/portfolio demo)
- ✅ Auto-deploys every time you `git push` to GitHub
- ✅ Gives you a public HTTPS URL like `https://tradingweb.onrender.com`
- ✅ Reads this repo's `render.yaml` blueprint automatically

---

## 🚀 First-time deployment (≈5 minutes, one-time)

### Step 1 — Push this code to a GitHub repo
*(I do this for you in the steps below — repo name: `tradingWeb`)*

### Step 2 — Connect Render to GitHub
1. Go to **https://render.com** → sign up / log in (use the GitHub button).
2. Click **New +** → **Blueprint**.
3. Select the **`tradingWeb`** repo. Render detects `render.yaml` and shows the
   service config.
4. Click **Apply**. Render will:
   - Build: install Python deps + compile TA-Lib + `collectstatic` + `migrate`
   - Start: `gunicorn tWeb.wsgi:application`
5. Wait ~3–5 min for the first build. When it says **Live**, open the URL. 🎉

That's it. Your CV link is `https://tradingweb.onrender.com`.

### Step 3 (recommended) — Set a strong secret
In Render → your service → **Environment** → confirm `SECRET_KEY` was auto-generated
(it is, via `generateValue: true` in `render.yaml`). Leave `DEBUG=0`.

---

## 🔁 How to RE-HOST / redeploy after changes

This is the best part — **you don't re-host, you just push.**

```bash
# 1. Make your changes (frontend templates, backend views, anything)

# 2. Commit them
cd ~/Desktop/tradingWeb
git add -A
git commit -m "Describe your change"

# 3. Push to GitHub
git push
```

**Render auto-detects the push and redeploys automatically** (typically 2–4 min).
Refresh your live URL and the changes are live. No manual steps.

> If you ever change `requirements.txt` (add a new Python package), the rebuild
> will reinstall everything — still automatic.

---

## 🗂 Deployment files in this repo

| File | Purpose |
|------|---------|
| `render.yaml` | Render Blueprint — tells Render how to build & run the app |
| `Procfile` | Fallback start command for other PaaS hosts (Heroku-style) |
| `tWeb/requirements.txt` | Pinned Python dependencies |
| `tWeb/build.sh` | Build script: installs deps, compiles TA-Lib C lib, collects static, migrates |
| `tWeb/tWeb/settings.py` | Production-aware (reads `SECRET_KEY`/`DEBUG`/`ALLOWED_HOSTS` from env) |
| `.gitignore` | Excludes the venv, db, bytecode, secrets |

---

## 🧪 Run locally

```bash
cd ~/Desktop/tradingWeb/tWeb
source ../bin/activate            # local venv
python manage.py migrate
python manage.py runserver
# → http://127.0.0.1:8000
```

---

## ⚠️ Notes

- **Free tier cold starts:** the service sleeps after 15 min idle; the first
  request after sleep takes ~30s to wake. For a CV link this is fine. Upgrade to
  a paid plan only if you need always-on.
- **SQLite on Render:** the free tier uses an ephemeral disk — the database
  resets on each deploy. For a read-only portfolio demo this is acceptable. If
  you later need persistent posts/users, add a Render PostgreSQL database and
  update `DATABASES` in `settings.py`.
- **Quant Lab thesis edits:** saved to `tWeb/quant_lab/thesis/*.md` on disk —
  note these reset on redeploy on the free tier. Commit them to git to persist.

---

## Author
**Anson Cheung** — [GitHub](https://github.com/AnsonCheung1020)