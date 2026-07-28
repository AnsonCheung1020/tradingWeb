# Trading404 — Live Web App (Free Hosting)

A Django web application showcasing trading screeners, quantitative research
(Quant Lab), and blog posts.

🔗 **Live site (after deploy):** `https://<your-username>.pythonanywhere.com`

---

## 💡 Why PythonAnywhere? (Free, no credit card)

This app is **Django** (Python on a server), so it can't go on GitHub Pages
(static-only). Hosts that run Django:

| Host | Free tier? | Card needed? | Auto-deploy from git? |
|------|-----------|--------------|------------------------|
| **PythonAnywhere** ✅ | Yes | **No** | Via a `git pull` button |
| Render | Trial only | **Yes** | Yes |
| Heroku | No | Yes | Yes |

**PythonAnywhere is the only one that's truly free with no card** — perfect for
a CV/portfolio link. The only caveat: the free tier doesn't auto-deploy on push,
so redeploying is a 1-line command (see below).

---

## 🚀 Deploy on PythonAnywhere (≈10 minutes, one-time)

### 1. Create a free account
Go to **https://www.pythonanywhere.com** → **Create a free Beginner account**.
Pick a username — that becomes your URL (`https://<username>.pythonanywhere.com`).

### 2. Open a Bash console and clone this repo
On the PythonAnywhere Dashboard → **Consoles** tab → **Bash**. Run:
```bash
git clone https://github.com/AnsonCheung1020/tradingWeb.git mysite
```

### 3. Install the Python dependencies
In the same Bash console:
```bash
pip3.10 install --user -r ~/mysite/tWeb/requirements.txt
```

### 4. Create the web app
Dashboard → **Web** tab → **Add a new web app** → **Manual configuration** → **Python 3.10**.

### 5. Point it at your code
On the Web tab, set:
- **Source code:** `/home/<your-username>/mysite/tWeb`
- **Working directory:** `/home/<your-username>/mysite/tWeb`
- **WSGI configuration file:** click the link, delete everything in it, and paste
  the contents of `mysite/tWeb/pythonanywhere_wsgi.py`. **Replace `<your-username>`**
  (3 places) with your actual PythonAnywhere username. Save.

### 6. Add static + media file mappings
On the Web tab, **Static files** section → add:
| URL | Directory |
|-----|-----------|
| `/static/` | `/home/<your-username>/mysite/tWeb/assets` |
| `/media/` | `/home/<your-username>/mysite/tWeb/media` |

### 7. Build static files + database
Back in the Bash console:
```bash
cd ~/mysite/tWeb
python3.10 manage.py collectstatic --noinput
python3.10 manage.py migrate
```

### 8. Go live
Web tab → big green **Reload** button. Open `https://<your-username>.pythonanywhere.com`. 🎉

---

## 🔁 How to RE-DEPLOY after changes (your second question)

Because PythonAnywhere's free tier isn't auto-deploy, updating is **3 commands**
in a Bash console on PythonAnywhere:

```bash
cd ~/mysite
git pull                       # 1. fetch your latest changes from GitHub
cd ~/mysite/tWeb
python3.10 manage.py collectstatic --noinput   # 2. refresh static files (if frontend changed)
python3.10 manage.py migrate                   # 3. apply DB migrations (if models changed)
```
Then hit the **Reload** button on the Web tab. Done.

> 💡 **One-line version** (frontend-only change): `cd ~/mysite && git pull && cd tWeb && python3.10 manage.py collectstatic --noinput`

So your workflow is: edit locally → `git push` from your Mac → SSH/console into
PythonAnywhere → the 3 commands above.

---

## 🗂 Deployment files in this repo

| File | Purpose |
|------|---------|
| `tWeb/pythonanywhere_wsgi.py` | **WSGI entry point for PythonAnywhere** (paste into their config) |
| `tWeb/requirements.txt` | Pinned Python dependencies |
| `tWeb/tWeb/settings.py` | Production-aware (reads `SECRET_KEY`/`DEBUG`/`ALLOWED_HOSTS` from env) |
| `render.yaml`, `Procfile` | Kept as fallbacks if you later use Render/Heroku |
| `tWeb/build.sh` | Generic build script (deps + collectstatic + migrate) |

---

## 🧪 Run locally

```bash
cd ~/Desktop/tradingWeb/tWeb
source ../bin/activate
python manage.py runserver
# → http://127.0.0.1:8000
```

---

## ⚠️ Notes
- **Free tier limits:** PythonAnywhere free allows 512 MB storage, 1 web app,
  and ~3 months of CPU. Plenty for a CV demo.
- **External internet (yfinance):** free PythonAnywhere accounts *can* do outbound
  HTTPS, so the screener pages that call Yahoo Finance will work, just slower.
- **SQLite persistence:** on PythonAnywhere the file system is **persistent** (unlike
  Render's ephemeral disk), so your posts/users survive redeploys. 🎉
- **Quant Lab thesis edits:** saved to `tWeb/quant_lab/thesis/*.md` — on
  PythonAnywhere these persist too. Commit them to git to mirror locally.

---

## Author
**Anson Cheung** — [GitHub](https://github.com/AnsonCheung1020)