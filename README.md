# Ghost-Router.ai —  Inbound Signal Router for the Agentic Era
Human-in-the-Loop Signal Routing for Agentic Commerce

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

The Ghost Router catches inbound retail intent (from humans or AI agents) and converts natural language into deterministic ACM-68000 signals.

| Input | Output |
|---|---|
| "Need 4 pallets diapers Madrid" | `acm-300.ai` CONDITIONAL |
| "RFQ GTIN 00990832300006 for Germany" | `acm-200.ai` ALLOW |
| "What's your price?" | `acm-451.ai` ESCALATE |

Zero reasoning. Keyword mapping only. Sub-second latency.

---

## What's Live — April 2026

### MCP Server — 10 Tools at mcp.10060.ai

| Tool | Description |
|---|---|
| `listSignals` | Returns the 7 ACM signals |
| `getInbound` | Ingress URL + payload schema |
| `ingestSignal` | Send signal → Dataverse |
| `resolveGtin` | GTIN → compliance check |
| `getNodes` | 18 jurisdiction nodes |
| `getGoogleBridge` | Google Madrid ESG bridge |
| `getResolver` | AI-Native architecture |
| `getCarbon` | Carbon-aware compute metrics |
| `getHealth` | Agentic health dashboard |
| `getMCP` | Root manifest |

### Ghost Headers — 43 Nodes Network-Wide

Deployed April 17, 2026. Every node returns the universal standard:

```
X-GSC-Protocol: ACM-68000
X-GSC-Operator: Allooloo Technologies Corp.
X-GSC-Inbound: https://x-gsi.ai/ingest
X-GSC-Trust-Anchor: dpuone.ai
X-GSC-Registry: io.github.allooloo/acm-68000-mcp
X-MCP-Server: https://mcp.10060.ai
X-GSC-Signal: ACM-200
X-GSC-State: ALLOW
X-GSC-Timestamp: [live]
X-GSC-Nonce: [live]
```

Verify:
```bash
curl -I https://acm-200.ai
curl -I https://dpuone.ai
curl -I https://fr-eco-10060.ai
```

### Live Dataverse Records

Real agent signals confirmed received and stored in Dataverse:

```json
{
  "sender": "CLAUDE-DIRECT",
  "signal": "ACM-200",
  "message": "FIRST CLAUDE MCP CALL - LIVE FROM CLAUDE.AI",
  "cluster": "CPG",
  "region": "CA-VAN",
  "latency_ms": 38
}
```

```json
{
  "sender": "RAILS-ARE-OURS",
  "signal": "ACM-200",
  "message": "PROTOCOL IN THE RAILS - FOUNDRY WIRED",
  "cluster": "HYGIENE",
  "region": "EU-PARIS",
  "gtin": "00990832300006",
  "latency_ms": 38
}
```

---

## 5-Minute Quickstart

**Option 1: Docker**
```bash
git clone https://github.com/allooloo/aio-orderable.git
cd aio-orderable
docker build -t aio-orderable .
docker run -p 8000:8000 aio-orderable
curl http://localhost:8000/resolve?gtin=00990832300006
```

**Option 2: Python**
```bash
git clone https://github.com/allooloo/aio-orderable.git
cd aio-orderable
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/resolve?gtin=00990832300006
```

---

## Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Router status |
| `/health` | GET | Health check |
| `/resolve?gtin=<gtin>` | GET | Resolve GTIN to signal |
| `/resolve?cluster=<cluster>` | GET | List cluster items |
| `/catalog` | GET | Full catalog |
| `/ingest` | POST | Inbound signal catch |
| `/.well-known/acm-68000.json` | GET | Discovery endpoint |

---

## Inbound Signal Catch

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"message": "Need 500 units TreeFree for Germany", "sender": "your-agent"}'
```

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
     └──► mcp.10060.ai → Dataverse
              │
              ▼
         aio-router.ai (CEO Dashboard)
```

---

## Network

| Layer | Node |
|---|---|
| MCP Server | mcp.10060.ai |
| Trust Anchor | dpuone.ai |
| Resolver | resolver.aio-resolver.com |
| Ghost Headers | 43 nodes network-wide |
| Jurisdictions | 18 nodes — {country}-eco-10060.ai |
| Carbon | aio-carbon.ai |
| Google Bridge | europe-southwest1 (Madrid) |

---

## Connected Agents

| Agent | Status |
|---|---|
| Claude | ✅ Connected — live Dataverse records confirmed |
| Mistral | ✅ Partner (FR-ECO-10060) |
| Grok | 🔲 Pending |
| Gemini | 🔲 Pending |
| Copilot | 🔲 Pending |

---

## Deploy

**Azure Container Apps**
```bash
az containerapp up --name aio-orderable \
  --resource-group rg-waypoint-10060-fr \
  --location francecentral \
  --source .
```

**Google Cloud Run**
```bash
gcloud run deploy aio-orderable \
  --source . \
  --region europe-southwest1 \
  --allow-unauthenticated
```

---

## Philosophy

- **FaF**: Sub-second latency
- **Lite Token Usage**: Max 200 tokens per transaction
- **Zero Reasoning**: No planning, no chatting, keyword mapping only
- **Hard Tenant Isolation**: Router never sees internal systems

---

## Related

- [ACM-68000 Protocol](https://allooloo.github.io/acm-68000/)
- [MCP Registry](https://registry.modelcontextprotocol.io/?q=io.github.allooloo)
- [resolver.aio-resolver.com](https://resolver.aio-resolver.com)
- [dpuone.ai](https://dpuone.ai)
- [aio-buyer.com](https://aio-buyer.com)
- [7signalstack.ai](https://7signalstack.ai)

---

## License

MIT — Allooloo Technologies Corp.
Vancouver | Barcelona | Paris

**Built by Allooloo + Claude. April 2026.**

*"Fast as Fuck. Zero Reasoning. Ship SKUs."*

# v1.3.0
