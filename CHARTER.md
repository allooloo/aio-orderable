# DESIGN CHARTER: GHOST ROUTER (AIO-ORDERABLE.AI)

**Project Code:** Build #1 (Inbound Signal Catch)

**Core Directive:** Catch inbound retail intent, strip prose, and inject a deterministic signal into the Microsoft Power Apps MCP Dashboard.

**Philosophy:** Fast as Fuck (FaF), Lite Token Usage, Zero Reasoning, Hard Tenant Isolation.

---

## 1. MISSION OBJECTIVE

Establish aio-orderable.ai as the **Sovereign Beacon** for the 7SignalStack.

Eliminate "conversational slop" by converting unstructured human/agent messages (WhatsApp, DM, Email) into structured ACM-68000 Ghost Headers that populate the Allooloo Agent Feed in real-time.

---

## 2. TECHNICAL STACK (ALLOOLOO CORP TENANT)

| Component | Technology |
|-----------|------------|
| **Ingress Gateway** | OpenClaw (WhatsApp/Messaging Bridge) |
| **Logic Engine** | Ghost Router (Python/FastAPI) |
| **Terminal** | Microsoft Power Apps Model-Driven App |
| **Protocol** | Model Context Protocol (MCP) via native Dataverse MCP Server |

---

## 3. THE "GHOST" PRINCIPLES (GUARDRAILS)

### Zero Reasoning
No planning. No chatting. Straight keyword-to-schema mapping (GTIN, Cluster, Qty). Ambiguity triggers `acm-451.ai` (Escalate to Human).

### Headless Execution
Silent pipe architecture. No public UI on the router itself.

### Lite Token Footprint
Max 200 tokens per transaction. Uses GPT-4o-mini or Mistral Small for sub-second resolution.

### Hard Tenant Isolation
The Router (Allooloo Tenant) has zero visibility into the Vault (MK Internal Tenant) or SAP credentials. Azure tenants are hard-isolated — no token bleed, no VNET overlap.

---

## 4. DATA FLOW & SCHEMA

| Sequence | Action | Data Payload |
|----------|--------|--------------|
| INPUT | OpenClaw Ingest | Raw Text: "Need 4 pallets diapers Madrid" |
| PROCESS | Normalization | Extract: `GTIN: null`, `Cluster: HYGIENE`, `Qty: 4`, `Loc: ES-MAD` |
| OUTPUT | MCP POST | Structured JSON to `https://<mcp-endpoint>/events` |

### Signal Mapping

| Condition | Signal | State |
|-----------|--------|-------|
| Valid GTIN + Cluster + Qty | `acm-200.ai` | ALLOW |
| Valid Cluster, missing GTIN | `acm-300.ai` | CONDITIONAL |
| Ambiguous / unparseable | `acm-451.ai` | ESCALATE |
| Known spam pattern | `acm-403.ai` | RESTRICT |
| System error | `acm-500.ai` | ERROR |

### Cluster Keywords

| Cluster | Keywords |
|---------|----------|
| HYGIENE | diaper, diapers, nappy, treefree, core, absorbent, incontinence |
| BPC | cosmetic, skincare, beauty, lotion, cream, serum |

### The Deterministic Payload

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
    "quantity": 4,
    "unit": "pallets",
    "region": "ES-MAD"
  },
  "timestamp": "2026-04-10T18:30:00Z",
  "raw_message": "Need 4 pallets diapers Madrid"
}
```

---

## 5. SUCCESS METRICS

| Metric | Target |
|--------|--------|
| **Latency** | Ingest-to-Dashboard pop in < 1000ms |
| **Accuracy** | 98% mapping without "hallucinated helpfulness" |
| **Cost** | Under $0.005 USD per inbound lead |

### Fallback Behavior

```
IF parse fails → acm-451.ai + pass raw message → human reviews
```

### Retry Logic

```
IF MCP POST fails → retry 2x (100ms, 500ms) → log to fallback queue → Teams alert
```

---

## 6. EXECUTION ROADMAP

| Phase | Task | Status |
|-------|------|--------|
| Phase 1 | Define Ghost Router Code Template (FastAPI) | ✅ Complete |
| Phase 2 | Configure Power Apps MCP Endpoint | 🔲 Pending |
| Phase 3 | Establish OpenClaw-to-Router webhook | 🔲 Pending |
| Phase 4 | Live "Signal Bounce" Test | 🔲 Pending |

---

## 7. OPEN SOURCE DEPLOYMENT (ACM-68000 SHOWCASE)

**Purpose:** Demonstrate to the agentic world that the 7SignalStack is real, fast, and deployable by anyone.

**Repository:** `github.com/allooloo/aio-orderable`

### Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI Ghost Router |
| `catalog.json` | GTIN + Cluster config |
| `Dockerfile` | One-command container |
| `deploy-azure.yaml` | Azure Container Apps deploy |
| `deploy-gcp.yaml` | Google Cloud Run deploy |
| `README.md` | 5-minute quickstart |
| `CHARTER.md` | This document |
| `LICENSE` | MIT |

---

## CHARTER SIGN-OFF

This Charter is the **Source of Truth** for Build #1.

Any drift toward LLM "creativity" or complex orchestration is a failure.

---

**Built by Allooloo Technologies Corp. + Claude (Anthropic)**

*First production Ghost Router. April 2026.*

*"Fast as Fuck. Zero Reasoning. Ship SKUs."*
