# Vercel Keep-Alive Pattern

**For projects hosted on Vercel**

## Problem

Vercel serverless functions experience cold starts after inactivity, causing:
- Increased latency on first request
- Poor user experience
- Potential timeout issues for complex initialization

## Solution: Heartbeat Pattern

Implement a periodic health check to keep functions warm.

## Implementation Guide

### 1. Create Health Endpoint

**File: `app/api/health/route.ts` (Next.js App Router)**

```typescript
export async function GET() {
  return Response.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
}
```

**OR File: `pages/api/health.ts` (Pages Router)**

```typescript
import type { NextApiRequest, NextApiResponse } from 'next';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
}
```

### 2. Configure Vercel Cron

**File: `vercel.json`**

```json
{
  "crons": [
    {
      "path": "/api/health",
      "schedule": "*/5 * * * *"
    }
  ]
}
```

**Schedule options:**
- `*/5 * * * *` - Every 5 minutes (recommended for production)
- `*/10 * * * *` - Every 10 minutes (light usage)
- `*/2 * * * *` - Every 2 minutes (high traffic apps)

### 3. Add Monitoring (Optional)

Track heartbeat execution:

```typescript
// app/api/health/route.ts
import { track } from '@vercel/analytics';

export async function GET() {
  track('heartbeat', {
    timestamp: Date.now()
  });
  
  return Response.json({ status: 'ok' });
}
```

### 4. Create Lug for Maintenance

Track this as a maintenance item in your wheel:

```bash
WAI lug create \
  --title "Vercel Keep-Alive Heartbeat" \
  --type maintenance \
  --priority medium \
  --impact medium \
  --value 7 \
  --tags vercel infrastructure monitoring \
  --justification "Prevent cold starts and ensure consistent response times"
```

**OR** create manually in `WAI-Spoke/WAI-Lugs.jsonl`:

```json
{
  "title": "Vercel Keep-Alive Heartbeat",
  "type": "maintenance",
  "status": "open",
  "priority": "medium",
  "impact": "medium",
  "value": 7,
  "policy_tags": ["vercel", "infrastructure", "monitoring"],
  "justification": "Prevent cold starts on Vercel serverless functions",
  "extras": {
    "implementation_checklist": [
      "Create /api/health endpoint",
      "Configure vercel.json cron job",
      "Optimize Vercel project settings",
      "Test cron execution in Vercel dashboard",
      "Add monitoring/alerts if needed",
      "Document in project README"
    ],
    "vercel_cron_schedule": "*/5 * * * *",
    "monitoring_url": "https://vercel.com/[team]/[project]/logs"
  }
}
```

## Verification

### Test Locally

```bash
curl http://localhost:3000/api/health
# Should return: {"status":"ok","timestamp":"...","uptime":...}
```

### Verify Cron in Vercel

1. Deploy to Vercel
2. Go to Project Settings → Cron Jobs
3. Confirm job appears and runs successfully
4. Check logs: `vercel logs --follow`

## Best Practices

### DO
- ✅ Keep endpoint lightweight (< 100ms response)
- ✅ Return JSON with timestamp
- ✅ Use appropriate schedule (every 5-10 min)
- ✅ Monitor execution in Vercel dashboard
- ✅ Track as maintenance lug in your wheel

### DON'T
- ❌ Make expensive DB queries in health endpoint
- ❌ Run too frequently (< 2 min intervals)
- ❌ Forget to test after deployment
- ❌ Leave unmonitored (check logs periodically)

## Costs

Vercel Cron Jobs are included in:
- **Pro Plan**: 100 cron executions/day included
- **Enterprise**: Custom limits

Running every 5 minutes = 288 executions/day

## Alternatives

If Vercel Cron is unavailable:

1. **External Ping Service**
   - UptimeRobot (free tier available)
   - Pingdom
   - StatusCake

2. **GitHub Actions**
   ```yaml
   name: Keep Alive
   on:
     schedule:
       - cron: '*/5 * * * *'
   jobs:
     ping:
       runs-on: ubuntu-latest
       steps:
         - run: curl https://your-app.vercel.app/api/health
   ```

## Related Documentation

- [Vercel Cron Jobs](https://vercel.com/docs/cron-jobs)
- [Vercel Serverless Functions](https://vercel.com/docs/functions/serverless-functions)
- [Next.js API Routes](https://nextjs.org/docs/api-routes/introduction)

---

**Pattern Type:** Platform-Specific Customization  
**Applies To:** Projects hosted on Vercel  
**Detected During:** `WAI init` (automatic detection)  
**Tracked In:** Project-specific Lugs (WAI-Spoke/WAI-Lugs.jsonl)
