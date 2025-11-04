# 🆚 Free Hosting Comparison for EasyGrant

Compare different free hosting options for deploying EasyGrant.

## TL;DR - Recommended Setup ⭐

**Frontend**: Vercel (no sleep, fast CDN)
**Backend**: Render (persistent storage, no timeout limits)

**Cost**: $0/month
**Setup Time**: ~15 minutes
**Pros**: Best of both platforms, easy to maintain
**Cons**: Two platforms to manage

---

## Architecture Options

### Option 1: Vercel (Frontend) + Render (Backend) ⭐ RECOMMENDED

```
User → Vercel (Frontend) → Render (Backend) → OpenAI API
                                  ↓
                            File Storage (1GB)
                            Vector DB (ChromaDB)
```

**✅ Pros:**
- Frontend never sleeps (Vercel edge network)
- Backend has persistent storage (Render disk)
- No timeout limits on backend
- Each platform used for its strengths
- Free SSL on both
- Auto-deployment from GitHub

**❌ Cons:**
- Backend cold start on Render (~30s after 15min idle)
- Two dashboards to monitor
- Need to configure CORS between services

**Free Tier Limits:**
- Vercel: 100GB bandwidth/month
- Render: 512MB RAM, 1GB disk, 750 hours/month ⚠️

**⚠️ Important**: Render's 750 hours/month means you get ~24/7 uptime ONLY if your service sleeps during idle periods. If constantly active, service stops at 750 hours. See `RENDER_FREE_TIER_SOLUTIONS.md` for workarounds.

**Best For**: Production deployments, this app specifically

---

### Option 2: Render (Full-Stack)

```
User → Render (Frontend + Backend in same container)
              ↓
         File Storage
         Vector DB
```

**✅ Pros:**
- Single platform, one dashboard
- Persistent storage for uploads & vector DB
- No timeout limits
- Simple CORS (same origin)
- Good for monolithic apps

**❌ Cons:**
- Frontend also sleeps after 15min idle
- Slower frontend (not on CDN)
- Limited to 512MB RAM total (shared between frontend & backend)
- Only one container on free tier

**Free Tier Limits:**
- 512MB RAM (shared)
- 1GB disk
- 750 hours/month
- 100GB bandwidth/month

**Best For**: Simple demos, tight resource constraints

---

### Option 3: Vercel (Full-Stack with External Services)

```
User → Vercel (Frontend + Serverless Backend)
                         ↓
              Supabase/S3 (File Storage)
              Pinecone (Vector DB)
              OpenAI API
```

**✅ Pros:**
- No cold starts (instant response)
- Global CDN for everything
- Automatic scaling
- Modern serverless architecture

**❌ Cons:**
- **10-second timeout** (kills long-running operations)
- **Read-only filesystem** (need external storage)
- **Complex setup** (3-4 services to configure)
- **Extra services required**:
  - Supabase/S3 for file storage
  - Pinecone/Weaviate for vector DB
- May exceed free tiers faster

**Free Tier Limits:**
- Vercel: 100GB bandwidth, 10s timeout
- Supabase: 500MB storage, 2GB bandwidth
- Pinecone: 1 index, 100K vectors

**Best For**: High-traffic apps, global distribution, teams familiar with serverless

---

### Option 4: Railway

```
User → Railway (Frontend + Backend)
              ↓
         File Storage
         Vector DB
```

**✅ Pros:**
- $5 free credit/month (not perpetual free tier)
- Persistent storage
- No timeout limits
- Good developer experience
- Easier than Vercel serverless

**❌ Cons:**
- **Not truly free** (credit runs out)
- After free credit: ~$5-10/month
- Smaller free tier than Render
- Less mature than Vercel/Render

**Free Tier:**
- $5 credit/month (covers ~100 hours)
- After credit exhausted: billing required

**Best For**: Paid projects with small budget, teams wanting simplicity

---

### Option 5: Hugging Face Spaces

```
User → Hugging Face Space (Gradio/Streamlit UI + Backend)
                          ↓
                    Persistent Storage
                    Vector DB
```

**✅ Pros:**
- Free persistent storage
- Great for ML/AI demos
- No cold starts on paid tier
- Community visibility
- Docker support

**❌ Cons:**
- **Slower on free tier** (CPU-only)
- Not ideal for React apps (better for Gradio/Streamlit)
- Limited custom domain options
- Would require UI rewrite

**Free Tier:**
- 2 CPU cores
- 16GB RAM
- 50GB storage
- Public repos only

**Best For**: ML demos, research projects, Python-first apps

---

### Option 6: Netlify (Frontend) + Render (Backend)

Similar to Option 1 but with Netlify instead of Vercel.

**✅ Pros:**
- Similar to Vercel+Render approach
- Generous free tier
- Great DX

**❌ Cons:**
- Netlify builds can be slower than Vercel
- Functions have 10s timeout (like Vercel)
- Less optimized for Vite than Vercel

**Free Tier:**
- 100GB bandwidth/month
- 300 build minutes/month

**Best For**: Teams already using Netlify, preference over Vercel

---

## Feature Comparison Matrix

| Feature | Vercel+Render ⭐ | Render Full | Vercel Full | Railway | HF Spaces |
|---------|----------------|-------------|-------------|---------|-----------|
| **Cost** | Free | Free | Free* | $5/mo | Free |
| **Storage** | 1GB (Render) | 1GB | External* | Paid | 50GB |
| **Timeout** | None | None | 10s ⚠️ | None | None |
| **Cold Start** | Frontend: No<br>Backend: 30s | Both: 30s | None | ~5s | None (paid) |
| **Setup** | Medium | Easy | Complex | Easy | Medium |
| **Scalability** | Good | Limited | Excellent | Good | Limited |
| **Custom Domain** | Yes (both) | Yes | Yes | Yes | Limited |
| **SSL** | Auto | Auto | Auto | Auto | Auto |

*Requires paid external services (Supabase, Pinecone)

---

## Decision Tree

```
Do you need persistent file storage & vector DB?
├─ YES → Not Vercel serverless
│   ├─ Want frontend on CDN?
│   │   ├─ YES → Vercel (Frontend) + Render (Backend) ⭐
│   │   └─ NO → Render (Full-Stack) or Railway
│   └─ Can use external services?
│       ├─ YES → Vercel (Full-Stack) + Supabase + Pinecone
│       └─ NO → Render or Railway
└─ NO (stateless API only)
    └─ Vercel serverless functions work great
```

---

## Cost Projections

### Year 1 (Free Tiers)

| Option | Monthly Cost | Annual Cost | Notes |
|--------|--------------|-------------|-------|
| Vercel+Render ⭐ | $0 | $0 | Stay in free tier |
| Render Full | $0 | $0 | Stay in free tier |
| Vercel Full | $0* | $0* | *If external services stay free |
| Railway | $0** | $0** | **After $5 credit: ~$5-10/mo |

### Scaling Up (1000+ users/month)

| Option | Est. Monthly Cost | Upgrade Trigger |
|--------|-------------------|-----------------|
| Vercel+Render | $20 | 100GB bandwidth, need faster backend |
| Render Full | $7-25 | Need more RAM, remove cold starts |
| Vercel Full | $50+ | Supabase/Pinecone limits, function timeout |
| Railway | $20-50 | After free credit runs out |

---

## When to Use Each Option

### Use Vercel + Render if:
- ✅ Building for production
- ✅ Want best performance for free
- ✅ OK with backend cold starts
- ✅ Need persistent storage
- ✅ Want frontend on global CDN

### Use Render Full-Stack if:
- ✅ Want simplest setup
- ✅ OK with slower frontend
- ✅ Low traffic expected
- ✅ Don't mind cold starts

### Use Vercel Full-Stack if:
- ✅ Willing to refactor for serverless
- ✅ Can pay for external services
- ✅ Need global distribution
- ✅ High traffic expected
- ✅ Have serverless experience

### Use Railway if:
- ✅ Can pay ~$5-10/month
- ✅ Want simpler than Vercel serverless
- ✅ Need better performance than Render free

### Use Hugging Face Spaces if:
- ✅ Pure ML/AI demo
- ✅ OK with Gradio/Streamlit UI
- ✅ Want community visibility
- ✅ Open-source project

---

## Migration Path

### Start: Vercel + Render (Free)

As you grow:

**Stage 1**: Stay on free tier (0-1000 users)
- Cost: $0/month
- Bandwidth: <100GB
- No changes needed

**Stage 2**: Remove cold starts (~1000-5000 users)
- Upgrade Render to Starter: $7/month
- No cold starts, same architecture
- Cost: $7/month

**Stage 3**: Scale backend (5000-50,000 users)
- Upgrade Render to Standard: $25/month
- Or migrate to dedicated VPS
- Cost: $25-50/month

**Stage 4**: Enterprise (50,000+ users)
- Vercel Pro: $20/month
- Render Pro: $85/month
- Or self-hosted K8s
- Cost: $100-500/month

---

## EasyGrant-Specific Recommendation

Given your requirements:

1. **File uploads**: Need persistent storage ✅ (Render has this)
2. **Vector database**: Need persistent storage ✅ (Render has this)
3. **PDF processing**: Can take >10s ⚠️ (Vercel timeout kills this)
4. **Low traffic initially**: Cold starts OK ✅
5. **Fast frontend**: Want CDN ✅ (Vercel excels here)

**Verdict**: **Vercel (Frontend) + Render (Backend)** ⭐

This is already documented in `DEPLOYMENT_GUIDE.md` and works perfectly for your use case!

---

## Quick Start Links

- **Recommended Setup**: See `DEPLOYMENT_GUIDE.md`
- **Vercel Only**: See `VERCEL_DEPLOYMENT.md`
- **Quick Checklist**: See `VERCEL_DEPLOYMENT_CHECKLIST.md`

---

## Questions?

**Q: Can I use 100% Vercel for free?**
A: Yes, but requires refactoring to serverless + external storage services.

**Q: Is Render backend slow?**
A: First request after 15min idle takes ~30s. After that, it's fast.

**Q: Can I upgrade later?**
A: Yes! Start free, upgrade Render to $7/mo to remove cold starts.

**Q: What about AWS/GCP/Azure free tiers?**
A: More complex setup, not recommended for MVPs.

**Q: Is there a one-click deploy?**
A: Render supports "Deploy to Render" button. Vercel has similar for frontend.

---

**Last Updated**: October 26, 2025
