# 🏗️ EasyGrant Deployment Architectures

Visual diagrams showing different deployment options.

---

## Option 1: Vercel + Render (RECOMMENDED) ⭐

```
┌─────────────────────────────────────────────────────────────┐
│                         INTERNET                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTPS
                       │
                       ▼
         ┌─────────────────────────┐
         │   USER'S BROWSER        │
         │  (Chrome, Firefox...)   │
         └─────────────────────────┘
                       │
         ┌─────────────┴──────────────┐
         │                            │
         ▼                            ▼
┌──────────────────┐         ┌──────────────────┐
│  VERCEL          │         │  RENDER          │
│  (Frontend)      │         │  (Backend)       │
│                  │         │                  │
│  React + Vite    │ API     │  FastAPI         │
│  Static Files    │ Calls   │  Python 3.11     │
│  Global CDN      │────────▶│  Uvicorn         │
│                  │ JSON    │                  │
│  ✅ Always On    │         │  ⚠️ Sleeps after  │
│  ✅ Fast         │         │     15min idle   │
│  ✅ Edge Network │         │                  │
└──────────────────┘         └────────┬─────────┘
                                      │
                                      │ Reads/Writes
                                      │
                    ┌─────────────────┴─────────────┐
                    │                               │
                    ▼                               ▼
          ┌──────────────────┐         ┌─────────────────────┐
          │  FILE STORAGE    │         │  VECTOR DATABASE    │
          │  (1GB Disk)      │         │  (ChromaDB)         │
          │                  │         │                     │
          │  /data/uploads/  │         │  /vector/           │
          │  - PDFs          │         │  - Embeddings       │
          │  - DOCX files    │         │  - Metadata         │
          │  - User docs     │         │  - Citations        │
          └──────────────────┘         └─────────────────────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │  OPENAI API      │
                          │  (External)      │
                          │                  │
                          │  - GPT-4o        │
                          │  - GPT-4o-mini   │
                          │  - Embeddings    │
                          └──────────────────┘

💰 COST: $0/month
⚡ PERFORMANCE: Fast frontend, 30s backend cold start
🔒 STORAGE: 1GB persistent on Render
⏱️ TIMEOUT: No limits on backend
🛠️ SETUP: Easy (15 minutes)
```

---

## Option 2: Vercel Serverless (Full-Stack)

```
┌─────────────────────────────────────────────────────────────┐
│                         INTERNET                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTPS
                       │
                       ▼
         ┌─────────────────────────┐
         │   USER'S BROWSER        │
         │  (Chrome, Firefox...)   │
         └─────────────────────────┘
                       │
                       ▼
            ┌──────────────────────────┐
            │       VERCEL             │
            │                          │
            │  Frontend (CDN)          │
            │  ├─ React + Vite        │
            │  └─ Static files        │
            │                          │
            │  Backend (Serverless)    │
            │  ├─ FastAPI functions   │
            │  ├─ /api/* routes       │
            │  └─ ⚠️ 10s timeout       │
            │                          │
            │  ✅ Always on            │
            │  ✅ Auto-scaling         │
            │  ✅ Global edge          │
            └────────┬─────────────────┘
                     │
                     │ API Calls
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌─────────┐  ┌──────────────┐  ┌─────────────┐
│SUPABASE │  │  PINECONE    │  │  OPENAI     │
│Storage  │  │  Vector DB   │  │  API        │
│         │  │              │  │             │
│- Files  │  │- Embeddings  │  │- GPT-4o     │
│- Uploads│  │- Similarity  │  │- GPT-4o-mini│
│         │  │  Search      │  │- Embeddings │
│         │  │              │  │             │
│500MB    │  │100K vectors  │  │Pay per use  │
│Free ✅  │  │Free ✅       │  │             │
└─────────┘  └──────────────┘  └─────────────┘

💰 COST: $0/month (if within free tiers)
⚡ PERFORMANCE: Instant, no cold starts
🔒 STORAGE: External (Supabase, S3)
⏱️ TIMEOUT: ⚠️ 10 seconds (can kill long operations)
🛠️ SETUP: Complex (2-3 hours, requires refactoring)
```

---

## Option 3: Render Full-Stack

```
┌─────────────────────────────────────────────────────────────┐
│                         INTERNET                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTPS
                       │
                       ▼
         ┌─────────────────────────┐
         │   USER'S BROWSER        │
         │  (Chrome, Firefox...)   │
         └─────────────────────────┘
                       │
                       ▼
            ┌──────────────────────────┐
            │       RENDER             │
            │   (Single Container)     │
            │                          │
            │  Docker Container        │
            │  ├─ Frontend (built)     │
            │  │  └─ Served by FastAPI │
            │  └─ Backend (FastAPI)    │
            │                          │
            │  File Storage (1GB)      │
            │  ├─ /data/uploads        │
            │  └─ /vector              │
            │                          │
            │  Vector Database         │
            │  └─ ChromaDB             │
            │                          │
            │  ✅ Persistent storage   │
            │  ⚠️ Sleeps after 15min   │
            │  ⚠️ Frontend not on CDN  │
            └────────┬─────────────────┘
                     │
                     ▼
            ┌──────────────────┐
            │  OPENAI API      │
            │  (External)      │
            │                  │
            │  - GPT-4o        │
            │  - GPT-4o-mini   │
            │  - Embeddings    │
            └──────────────────┘

💰 COST: $0/month
⚡ PERFORMANCE: ⚠️ Slower frontend (not on CDN), 30s cold start
🔒 STORAGE: 1GB persistent
⏱️ TIMEOUT: No limits
🛠️ SETUP: Easiest (single platform)
```

---

## Request Flow Comparison

### Vercel + Render (Option 1)

```
First Request After 15min Idle:
User → Vercel (instant) → Render (30s wake) → Response
Total: ~30 seconds

Subsequent Requests:
User → Vercel (instant) → Render (50-100ms) → Response
Total: ~100 milliseconds

Page Load:
User → Vercel CDN (20-50ms) → Page displayed
Very fast! ⚡
```

### Vercel Serverless (Option 2)

```
Every Request:
User → Vercel Edge (10-20ms) → External APIs (50-100ms) → Response
Total: ~100 milliseconds

But: ⚠️ 10-second timeout can kill long operations
```

### Render Full-Stack (Option 3)

```
First Request After 15min Idle:
User → Render (30s wake + 100ms) → Response
Total: ~30 seconds

Subsequent Requests:
User → Render Origin (100-200ms) → Response
Total: ~200 milliseconds

Page Load:
User → Render Origin (100-200ms) → Page displayed
Slower than CDN ⚠️
```

---

## Data Flow for Document Upload

### Vercel + Render (Option 1)

```
1. User selects PDF file
2. Frontend (Vercel) sends multipart upload
3. Backend (Render) receives file
4. File saved to /data/uploads (persistent disk)
5. PDF parsed by PyMuPDF
6. Text sent to OpenAI for embeddings
7. Embeddings stored in ChromaDB (/vector)
8. Response sent to frontend

✅ All data persists between requests
✅ No file size limits (within 1GB total)
⚠️ First upload after idle: ~30s wait
```

### Vercel Serverless (Option 2)

```
1. User selects PDF file
2. Frontend (Vercel) sends multipart upload
3. Serverless function receives file
4. File uploaded to Supabase Storage (external API)
5. PDF parsed (must complete within 10s!)
6. Text sent to OpenAI for embeddings
7. Embeddings sent to Pinecone (external API)
8. Response sent to frontend

⚠️ Must complete in 10 seconds
⚠️ Multiple external API calls (slower)
✅ No cold starts
```

---

## Scaling Comparison

### At 1,000 Users/Month

| Metric | Vercel+Render | Vercel Full | Render Full |
|--------|---------------|-------------|-------------|
| **Bandwidth** | 20GB | 25GB | 30GB |
| **Storage** | 200MB | 100MB* | 200MB |
| **Cost** | $0 ✅ | $0 ✅ | $0 ✅ |
| **Performance** | Good | Excellent | OK |

*External storage (Supabase)

### At 10,000 Users/Month

| Metric | Vercel+Render | Vercel Full | Render Full |
|--------|---------------|-------------|-------------|
| **Bandwidth** | 80GB ✅ | 90GB ✅ | 150GB ❌ |
| **Storage** | 800MB ✅ | 600MB* ❌ | 800MB ✅ |
| **Cost** | $0 or $7** | $10-20*** | $7-25** |

*May exceed Supabase free tier (500MB)
**Upgrade Render to remove cold starts
***May need Supabase/Pinecone paid tier

### At 100,000 Users/Month

| Metric | Vercel+Render | Vercel Full | Render Full |
|--------|---------------|-------------|-------------|
| **Cost** | $25-50/mo | $50-100/mo | $50-85/mo |
| **Recommended** | ✅ Yes | ⚠️ Maybe | ❌ No |

Need enterprise tier or self-hosted at this scale.

---

## Decision Matrix

### Choose Vercel + Render if:
- ✅ You want best free tier experience
- ✅ You need persistent storage
- ✅ You have long-running operations
- ✅ You're OK with 30s cold starts
- ✅ You want fast frontend
- ✅ You're building for production

### Choose Vercel Serverless if:
- ✅ You can refactor to serverless
- ✅ You're OK with external dependencies
- ✅ You need global distribution
- ✅ Your operations finish in <10 seconds
- ✅ You want zero cold starts
- ✅ You have serverless experience

### Choose Render Full-Stack if:
- ✅ You want simplest setup
- ✅ You're OK with slower frontend
- ✅ You're building a demo/MVP
- ✅ You prefer single platform
- ✅ You have tight budget ($0)
- ✅ You don't need fast page loads

---

## Environment Variables

### Vercel + Render

**Vercel (Frontend)**:
```
VITE_API_URL=https://easygrant-xxxx.onrender.com
```

**Render (Backend)**:
```
OPENAI_API_KEY=sk-...
PORT=8000
PYTHON_VERSION=3.11
```

### Vercel Serverless

**Vercel (Full-Stack)**:
```
VITE_API_URL=
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://...
SUPABASE_KEY=...
PINECONE_API_KEY=...
PINECONE_ENV=...
```

---

**Summary**: For EasyGrant, **Option 1 (Vercel + Render)** is the clear winner! ⭐
