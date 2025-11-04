# ❓ Deployment FAQ - Common Questions

## Render Free Tier Questions

### Q: Does Render provide true 24/7 uptime on the free tier?

**A: No.** Render's free tier has two limitations:

1. **Sleep after 15 minutes idle**: Service automatically stops when inactive
2. **750 hours/month limit**: Only enough for ~31 days of continuous runtime

**Reality**: You get "mostly 24/7" IF your app sleeps during idle periods. Active apps will hit the 750-hour limit mid-month.

**Solution**: 
- For demos/MVPs: Accept the limitation or use keep-alive ping
- For production: Upgrade to Render Starter ($7/month) for true 24/7

See: `RENDER_FREE_TIER_SOLUTIONS.md`

---

### Q: What happens when I hit 750 hours?

**A:** Your service stops completely until the next billing cycle (1st of next month).

**What you'll see:**
- All API requests return 503 errors
- Render dashboard shows: "Free tier hours exceeded"
- Frontend will show connection errors

**Your options:**
1. Wait until next month (service is down)
2. Upgrade to paid tier (service resumes immediately)

---

### Q: How can I avoid hitting the 750-hour limit?

**A:** Let your service sleep when idle:

**Don't** use keep-alive pings if you want to maximize free tier usage.

**Typical usage pattern:**
- Active hours: ~8-12 hours/day (when users are online)
- Monthly: ~240-360 hours
- Well within 750-hour limit ✅

**If you use keep-alive:**
- Active hours: 24 hours/day
- Monthly: ~720 hours
- Very close to limit ⚠️

---

### Q: Is the 30-second cold start acceptable?

**A:** Depends on your use case:

**Acceptable for:**
- ✅ Personal projects
- ✅ Internal tools
- ✅ Demos/portfolios
- ✅ Low-traffic apps (<100 users/day)

**Not acceptable for:**
- ❌ Production apps with paying customers
- ❌ High-traffic websites
- ❌ Time-sensitive applications
- ❌ Apps where first impression matters

**User experience:**
```
Without cold start: Click → 1 second → Response ✅
With cold start: Click → 30 seconds → Response ❌
```

---

## Vercel Questions

### Q: Does Vercel have similar sleep limitations?

**A: No.** Vercel's frontend hosting is always on with no sleep.

However, if you use Vercel serverless functions, there are different limits:
- ⏱️ 10-second execution timeout (free tier)
- 💾 No persistent storage

For EasyGrant, we recommend Vercel for frontend only.

---

### Q: Can I deploy my entire app (frontend + backend) to Vercel for free?

**A: Technically yes, but not recommended** for EasyGrant because:

1. **Serverless functions have 10-second timeout** → Kills long-running PDF processing
2. **No persistent file storage** → Need external services (Supabase, S3)
3. **No persistent vector database** → Need cloud service (Pinecone)
4. **Complex setup** → Requires significant refactoring

See `VERCEL_DEPLOYMENT.md` Option 2 for details.

---

## Cost Questions

### Q: What's the minimum cost to run EasyGrant in production?

**A: $7/month** (Render Starter + Vercel free)

**Breakdown:**
- Vercel (frontend): $0/month ✅
- Render Starter (backend): $7/month
- **Total: $7/month**

This gives you:
- ✅ No cold starts
- ✅ Always-on backend
- ✅ Fast global frontend
- ✅ Professional user experience

---

### Q: Can I run it completely free for production?

**A: Technically yes, but user experience will suffer:**

**Free setup:**
- Vercel (frontend): $0
- Render free tier (backend): $0
- **Total: $0/month**

**Tradeoffs:**
- ⚠️ 30-second delay on first request after idle
- ⚠️ Service may stop if you hit 750 hours
- ⚠️ Users may think app is broken

**Recommendation**: 
- Start free for testing
- Upgrade to $7/month when you have real users

---

### Q: What happens when I exceed free tier limits?

**Vercel:**
- Bandwidth >100GB: Site continues but you get upgrade prompts
- Builds continue to work
- No hard limits on free tier

**Render:**
- Hours >750: Service stops completely ⚠️
- Must upgrade or wait for next billing cycle
- Hard limit enforced

---

## Alternative Platforms

### Q: Are there better free options than Render?

**A: Depends on your needs:**

**For similar functionality:**
- **Railway**: $5 credit/month (not perpetual free)
- **Fly.io**: 3 free VMs (256MB each, no sleep)
- **Koyeb**: 1 free service (with sleep)

**For always-on free:**
- **Fly.io** is best alternative (256MB RAM limit)

**Comparison:**

| Platform | Free Tier | Sleep | Persistent Storage |
|----------|-----------|-------|-------------------|
| Render | 750 hrs/mo | Yes (15min) | 1GB ✅ |
| Railway | $5 credit | No | Yes ✅ |
| Fly.io | 3 VMs | No | 3GB ✅ |
| Koyeb | 1 service | Yes (30min) | Limited |

See `HOSTING_COMPARISON.md` for detailed analysis.

---

### Q: Should I migrate from Render to another platform?

**A: Only if:**
- ❌ You can't afford $7/month AND
- ❌ You need true 24/7 uptime AND
- ❌ You're willing to spend time migrating

**Otherwise**: Render + $7/month is the easiest path.

**Migration effort:**
- Render → Railway: ~30 minutes
- Render → Fly.io: ~1-2 hours
- Render → Self-hosted: ~4-8 hours

---

## Technical Questions

### Q: Can I use a keep-alive service to prevent sleep?

**A: Yes, but be careful:**

**How it works:**
- External service pings your backend every 5-14 minutes
- Keeps service awake
- Prevents cold starts

**⚠️ Warning:**
- Uses your 750 hours/month
- May hit limit if you have traffic spikes
- Only works if total hours <750

**Free services:**
- UptimeRobot (recommended)
- Cron-Job.org
- GitHub Actions

See `RENDER_FREE_TIER_SOLUTIONS.md` for setup.

---

### Q: How do I monitor my Render usage?

**A: Render Dashboard:**

1. Go to https://dashboard.render.com
2. Click **Account** (top right)
3. Click **Usage**
4. See current month's hours

**Set up alerts:**
- Render doesn't provide usage alerts on free tier
- Monitor manually weekly
- Consider upgrading before hitting 750

---

### Q: What's the best free tier strategy?

**A: Tiered approach:**

**Stage 1: Development (Free)**
- Accept sleep
- 30s cold start is fine
- Focus on building features

**Stage 2: Beta Testing (Free + Keep-Alive)**
- Use UptimeRobot
- Monitor usage
- Get user feedback

**Stage 3: Production (Paid)**
- Upgrade to $7/month
- Professional UX
- Scale with confidence

---

## Recommendation Summary

### For Personal Projects:
✅ Render Free + Vercel Free
- Cost: $0
- Accept cold starts
- Monitor usage

### For Serious MVPs:
✅ Render Free + UptimeRobot + Vercel Free
- Cost: $0
- Minimal cold starts
- Watch 750-hour limit

### For Production:
⭐ Render Starter ($7) + Vercel Free
- Cost: $7/month
- No cold starts
- Best UX
- **RECOMMENDED**

---

## Quick Decision Tree

```
Do you have paying customers?
├─ YES → Upgrade to Render Starter ($7/mo)
└─ NO → Is this a serious project?
    ├─ YES → Use UptimeRobot + monitor usage
    └─ NO → Accept free tier limitations
```

---

## Additional Resources

- 📘 [Render Pricing](https://render.com/pricing)
- 📘 [Render Free Tier Solutions](RENDER_FREE_TIER_SOLUTIONS.md)
- 📘 [Hosting Comparison](HOSTING_COMPARISON.md)
- 📘 [Deployment Guide](DEPLOYMENT_GUIDE.md)

---

**Bottom Line**: Render free tier is great for getting started, but plan to upgrade to $7/month for production. It's worth it! ☕
