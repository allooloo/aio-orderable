# aio-orderable.ai — Ghost Router

![ACM-68000](https://img.shields.io/badge/Protocol-ACM--68000-blue)
![MCP Registry](https://img.shields.io/badge/MCP-io.github.allooloo-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Deploy](https://img.shields.io/badge/Deploy-5%20min-brightgreen)

**The inbound signal router for ACM-68000.**

```
Outbound: resolver.aio-resolver.com → World
Inbound:  World → aio-orderable.ai → You
```

Built by [Allooloo Technologies Corp.](https://allooloo.ai) + [Claude](https://anthropic.com) (Anthropic).

---

## What It Does

The Ghost Router catches inbound retail intent (from humans or AI agents) and converts messy natural language into deterministic ACM-68000 signals.

| Input | Output |
|-------|--------|
| "Need 4 pallets diapers Madrid" | `acm-300.ai` CONDITIONAL |
| "RFQ GTIN 00990832300006 for Germany" | `acm-200.ai` ALLOW |
| "What's your price?" | `acm-451.ai` ESCALATE |

**Zero reasoning. Keyword mapping only. Sub-second latency.**

---

## 5-Minute Quickstart

### Option 1: Docker (Recommended)

```bash
# Clone
git clone https://github.com/allooloo/aio-orderable.git
cd aio-orderable

# Run
docker build -t aio-orderable .
docker run -p 8000:8000 aio-orderable

# Test
curl http://localhost:8000/resolve?gtin=00990832300006
```

### Option 2: Python

```bash
# Clone
git clone https://github.com/allooloo/aio-orderable.git
cd aio-orderable

# Install
pip install -r requirements.txt

# Run
uvicorn main:app --host 0.0.0.0 --port 8000

# Test
curl http://localhost:8000/resolve?gtin=00990832300006
```

---

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Router status |
| `/health` | GET | Health check |
| `/resolve?gtin=<gtin>` | GET | Resolve GTIN to signal |
| `/resolve?cluster=<cluster>` | GET | List cluster items |
| `/catalog` | GET | Full catalog |
| `/ingest` | POST | **Inbound signal catch** |
| `/.well-known/acm-68000.json` | GET | Discovery endpoint |

---

## Ghost Headers

Every response includes ACM-68000 Ghost Headers:

```http
X-GSC-Protocol: ACM-68000
X-GSC-Router: aio-orderable.ai
X-GSC-Stack: 7SignalStack
X-GSC-Signal: ACM-200
X-GSC-State: ALLOW
X-GSC-Registry: io.github.allooloo/acm-68000-mcp
X-GSC-Operator: Allooloo Technologies Corp.
```

---

## Inbound Signal Catch

POST to `/ingest` with raw message:

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"message": "Need 500 units TreeFree for Germany", "sender": "+1-555-123-4567"}'
```

Response:

```json
{
  "protocol": "ACM-68000",
  "source": "aio-orderable.ai",
  "intent": "PROCURE_INQUIRY",
  "signal": "acm-300.ai",
  "signal_state": "CONDITIONAL",
  "payload": {
    "gtin": null,
    "cluster": "HYGIENE",
    "quantity": 500,
    "unit": "units",
    "region": "DE"
  },
  "sender": "+1-555-123-4567",
  "timestamp": "2026-04-10T18:30:00Z",
  "raw_message": "Need 500 units TreeFree for Germany",
  "buyer_portal": "https://aio-buyer.com"
}
```

---

## Clusters

| Cluster | Rail | Status | GTINs |
|---------|------|--------|-------|
| HYGIENE | aio-tfx-rail.ai | 🟢 LIVE | 2 |
| BPC | aio-rail.ai | 🟢 LIVE | TBD |

---

## Deploy

### Azure Container Apps

```bash
az containerapp up --name aio-orderable \
  --resource-group allooloo-rg \
  --location francecentral \
  --source .
```

### Google Cloud Run

```bash
gcloud run deploy aio-orderable \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated
```

---

## Connect to Power Apps MCP

Set environment variables:

```bash
export MCP_ENDPOINT="https://<region>.api.powerapps.com/providers/Microsoft.MCP/events"
export MCP_TOKEN="<your-token>"
```

The Ghost Router will POST normalized signals to your Power Apps dashboard.

---

## Architecture

```
Agent or Human
     │
     │ POST /ingest
     │ "Need 500 units TreeFree for DE"
     ▼
aio-orderable.ai (Ghost Router)
     │
     │ Normalize → Signal
     │
     ├──► Ghost Headers (response)
     │
     └──► Power Apps MCP (dashboard)
              │
              ▼
         YOU SEE IT
```

---

## Philosophy

- **Fast as Fuck (FaF)**: Sub-second latency
- **Lite Token Usage**: Max 200 tokens per transaction
- **Zero Reasoning**: No planning, no chatting, keyword mapping only
- **Hard Tenant Isolation**: Router never sees internal systems

---

## Related

- [ACM-68000 Protocol](https://allooloo.github.io/acm-68000/)
- [MCP Registry](https://registry.modelcontextprotocol.io/?q=io.github.allooloo)
- [resolver.aio-resolver.com](https://resolver.aio-resolver.com)
- [aio-buyer.com](https://aio-buyer.com) — Human interface

---

## License

MIT License — Allooloo Technologies Corp.

---

**Built by Allooloo + Claude. April 2026.**

*"Fast as Fuck. Zero Reasoning. Ship SKUs."*
# v1.2.0 
