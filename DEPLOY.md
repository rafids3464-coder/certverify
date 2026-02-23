# CertVerify — Free Cloud Deployment Guide

> **Stack:** Vercel (frontend) + Render free (backend) + MongoDB Atlas (database)
> **Cost:** $0/month · GPU: CPU-only inference

---

## Architecture

```
User → Vercel (Next.js) ──→ Render (FastAPI/Docker, CPU)
                                       │
                                MongoDB Atlas (free 512MB)
                                       │
                                model.pth (bundled via Git LFS)
```

---

## Prerequisites

Install on your machine before starting:
```bash
# Git LFS (for model.pth)
winget install GitHub.GitLFS    # Windows
# or: brew install git-lfs      # Mac

# Vercel CLI (optional, for CLI deploy)
npm install -g vercel
```

---

## Step 1 — Set up Git LFS for model.pth

```bash
cd "C:\Users\rafid\Desktop\Fake certificate"

git lfs install
git lfs track "*.pth"
git add .gitattributes
git add models/model.pth
git commit -m "Add model.pth via Git LFS"
git push origin main
```

> **GitHub free** gives 1 GB LFS storage and 1 GB/month bandwidth — more than enough for a 20 MB model.

---

## Step 2 — MongoDB Atlas (free cluster)

1. Go to **[mongodb.com/atlas](https://www.mongodb.com/atlas)** → Create free account
2. Create a free **M0 cluster** (512 MB, shared, free forever)
3. **Database Access** → Add user: `certverify` with a strong password
4. **Network Access** → Add IP `0.0.0.0/0` (allow all, needed for Render)
5. **Connect** → Drivers → copy the connection string:
   ```
   mongodb+srv://certverify:<password>@cluster0.xxxxx.mongodb.net/
   ```
6. Save this — you'll need it in Step 3.

---

## Step 3 — Deploy Backend on Render

### 3a. Create Render account
Go to **[render.com](https://render.com)** → sign up (free, no card needed).

### 3b. Deploy via Blueprint (easiest)
1. Render Dashboard → **New → Blueprint**
2. Connect your GitHub repo
3. Render detects `render.yaml` automatically
4. Click **Apply**

### 3c. Set secret environment variables
In Render → your service → **Environment**:

| Key | Value |
|-----|-------|
| `MONGO_URI` | `mongodb+srv://certverify:PASSWORD@cluster0.xxxxx.mongodb.net/` |
| `JWT_SECRET` | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ADMIN_PASSWORD` | Your chosen admin password |
| `ALLOWED_ORIGINS` | `https://YOUR-APP.vercel.app` (fill after Step 4) |

### 3d. First deploy
- Build takes ~5–10 min (downloads CPU PyTorch, ~800 MB image)
- Check **Logs** tab — wait for: `API ready.` and `✔ CNN model warm-loaded`
- Test: `https://certverify-backend.onrender.com/api/health`

> ⚠️ Free tier **spins down after 15 min** inactivity. First request after sleep takes ~30s.

---

## Step 4 — Deploy Frontend on Vercel

### 4a. Update vercel.json
Edit `frontend/vercel.json` — replace the Render URL with your actual service URL:
```json
"destination": "https://YOUR-SERVICE-NAME.onrender.com/api/:path*"
```
Also update the `NEXT_PUBLIC_API_URL` field.

### 4b. Deploy
```bash
cd frontend

# Option A: Vercel CLI
vercel --prod

# Option B: Vercel Dashboard
# → New Project → Import GitHub repo → Framework: Next.js
# → Environment Variables → add NEXT_PUBLIC_API_URL=https://YOUR.onrender.com
# → Deploy
```

### 4c. Set environment variable in Vercel dashboard
| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://certverify-backend.onrender.com` |

---

## Step 5 — Update CORS (after you have Vercel URL)

Go back to Render → Environment → update `ALLOWED_ORIGINS`:
```
https://certverify.vercel.app,https://www.certverify.vercel.app
```
Then **Manual Deploy → Deploy latest commit**.

---

## Step 6 — Verify Everything Works

```bash
# 1. Health check
curl https://certverify-backend.onrender.com/api/health

# 2. Sign up a user
curl -X POST https://certverify-backend.onrender.com/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"Test1234"}'

# 3. Admin login (default creds)
curl -X POST https://certverify-backend.onrender.com/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"YOUR_ADMIN_PASSWORD"}'

# 4. Upload a certificate
curl -X POST https://certverify-backend.onrender.com/api/upload \
  -F "file=@path/to/certificate.jpg"
```

---

## Production Limits & Notes

| Item | Free Tier Limit | Solution |
|------|----------------|----------|
| RAM | 512 MB | CLIP disabled — CNN+ELA only |
| CPU | Shared | `torch.set_num_threads(2)` |
| Sleep | 15 min idle | Keep-alive ping (optional) |
| MongoDB | 512 MB | Unlimited uploads till full |
| Vercel | 100 GB bandwidth | More than enough |
| Git LFS | 1 GB storage | ~50× model.pth headroom |

### Inference speed (CPU, no CLIP)
| Format | Approx. time |
|--------|-------------|
| JPEG (warm) | 8–15 s |
| JPEG (cold) | 25–40 s |
| PDF | 15–25 s |

---

## Optional: Keep-Alive Ping

Add to Vercel as a Cron Job to prevent Render from sleeping:

Create `frontend/pages/api/keepalive.js`:
```js
export default async function handler(req, res) {
  await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/health`);
  res.status(200).json({ ok: true });
}
```

Then in `vercel.json` add:
```json
"crons": [{ "path": "/api/keepalive", "schedule": "*/10 * * * *" }]
```

---

## Upgrading (when needed)

| If you need | Upgrade to | Cost |
|-------------|-----------|------|
| CLIP enabled | Render Starter | $7/mo (2 GB RAM) |
| No sleep | Render Starter | $7/mo |
| GPU inference | RunPod / Lambda Labs | ~$0.20/hr |
| More DB storage | MongoDB Atlas M2 | $9/mo |

To enable CLIP on Render Starter: set `DISABLE_CLIP=false` in environment.
