"""
aio-orderable.ai — Ghost Router
The inbound signal router for ACM-68000.

Built by Allooloo Technologies Corp. + Claude (Anthropic)
MIT License | April 2026

Philosophy: Fast as Fuck (FaF), Lite Token Usage, Zero Reasoning, Hard Tenant Isolation

Version: 1.3.1 — Added Dataverse retry logic (3 attempts, exponential backoff)
"""

from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import json
import re
import httpx
from typing import Optional
import os
import uuid
import asyncio

app = FastAPI(
    title="aio-orderable.ai — Ghost Router",
    description="The inbound signal router for ACM-68000. Zero reasoning. Deterministic signals.",
    version="1.3.1"
)

# CORS for agent access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# CONFIGURATION — Azure AD + Dataverse
# =============================================================================
TENANT_ID = os.getenv("TENANT_ID", "04a24e43-dc13-4578-950a-910db076a799")
CLIENT_ID = os.getenv("CLIENT_ID", "78626d29-b5a6-4ae3-b033-bab136be4b8b")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")  # Set via environment variable
DATAVERSE_URL = os.getenv("DATAVERSE_URL", "https://orgd693166f.crm3.dynamics.com")
TABLE_NAME = os.getenv("TABLE_NAME", "cr1e4_inboundeventses")  # FIXED: API endpoint is pluralized
# Token cache
_token_cache = {"token": None, "expires": 0}


# =============================================================================
# GHOST HEADERS — Full 15+ Header Set (ACM-68000 Compliant)
# =============================================================================
def get_ghost_headers(signal: str = None, state: str = None) -> dict:
    """
    Generate full Ghost Header set for every response.
    
    Per TRUST-MODEL.md and AGENTIC-GHOST-HEADERS.md:
    - Core Protocol headers (always present)
    - Discovery headers (always present)
    - Trust headers (Phase 2)
    - Dynamic headers (per-request)
    - Signal headers (when applicable)
    """
    timestamp = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    nonce = str(uuid.uuid4())
    
    headers = {
        # === CORE PROTOCOL ===
        "X-GSC-Protocol": "ACM-68000",
        "X-GSC-Version": "1.3.1",
        "X-GSC-Router": "aio-orderable.ai",
        "X-GSC-Stack": "7SignalStack",
        "X-GSC-Operator": "Allooloo Technologies Corp.",
        "X-GSC-Role": "ghost-router",
        
        # === DISCOVERY ===
        "X-GSC-Registry": "io.github.allooloo/acm-68000-mcp",
        "X-GSC-Inbound": "/ingest",
        "X-GSC-Verify": "/.well-known/acm-68000.json",
        "X-MCP-Server": "https://mcp.10060.ai",
        "X-MCP-Registry": "io.github.allooloo/acm-68000-mcp",
        "X-MCP-Version": "1.0",
        
        # === TRUST (Phase 2) ===
        "X-GSC-Trust-Anchor": "dpuone.ai",
        "X-GSC-DPU": "https://dpuone.ai",
        "X-GSC-Node": "aio-orderable",
        
        # === DYNAMIC (Per-Request) ===
        "X-GSC-Timestamp": timestamp,
        "X-GSC-Nonce": nonce,
    }
    
    # === SIGNAL (When Applicable) ===
    if signal:
        headers["X-GSC-Signal"] = signal.replace("acm-", "ACM-").replace(".ai", "")
    if state:
        headers["X-GSC-State"] = state
    
    return headers


def add_ghost_headers(response: Response, signal: str = None, state: str = None) -> Response:
    """Add full Ghost Header set to any response."""
    headers = get_ghost_headers(signal, state)
    for key, value in headers.items():
        response.headers[key] = value
    return response


# =============================================================================
# AUTHENTICATION — Get Azure AD Token for Dataverse
# =============================================================================
async def get_dataverse_token() -> str:
    """Get OAuth token for Dataverse API."""
    global _token_cache
    
    # Check cache
    now = datetime.now(timezone.utc).timestamp()
    if _token_cache["token"] and _token_cache["expires"] > now + 60:
        return _token_cache["token"]
    
    # Get new token
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": f"{DATAVERSE_URL}/.default"
            }
        )
        
        if response.status_code != 200:
            print(f"Token error: {response.text}")
            raise HTTPException(500, f"Token error: {response.status_code}")
        
        data = response.json()
        _token_cache["token"] = data["access_token"]
        _token_cache["expires"] = now + data.get("expires_in", 3600)
        
        return _token_cache["token"]


# =============================================================================
# DATAVERSE — Write to InboundEvents table (WITH RETRY)
# =============================================================================
async def write_to_dataverse(record: dict, max_retries: int = 3) -> bool:
    """
    Write a record to the InboundEvents table.
    
    Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s).
    If all retries fail, log and return False — signal is lost but system continues.
    """
    global _token_cache
    
    if not CLIENT_SECRET:
        print("CLIENT_SECRET not set — skipping Dataverse write")
        return False
    
    # Map to Dataverse column names (cr1e4_ prefix for this environment)
    # v1.3.0: Added contact capture fields
    dataverse_record = {
        "cr1e4_sender": str(record.get("sender", ""))[:100],
        "cr1e4_message": str(record.get("raw_message", ""))[:2000],
        "cr1e4_signal": str(record.get("signal", ""))[:50],
        "cr1e4_cluster": str(record.get("cluster", ""))[:50],
        "cr1e4_region": str(record.get("region", ""))[:50],
        "cr1e4_quantity": int(record.get("quantity") or 0),
        "cr1e4_gtin": str(record.get("gtin", ""))[:50],
        "cr1e4_raw_message": str(record.get("raw_message", ""))[:2000],
        # === NEW: Contact Capture Fields (v1.3.0) ===
        "cr1e4_contact_email": str(record.get("contact_email", ""))[:100],
        "cr1e4_contact_name": str(record.get("contact_name", ""))[:100],
        "cr1e4_contact_phone": str(record.get("contact_phone", ""))[:50],
        "cr1e4_company_name": str(record.get("company_name", ""))[:200],
    }
    
    api_url = f"{DATAVERSE_URL}/api/data/v9.2/{TABLE_NAME}"
    
    for attempt in range(1, max_retries + 1):
        try:
            token = await get_dataverse_token()
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    api_url,
                    json=dataverse_record,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "OData-MaxVersion": "4.0",
                        "OData-Version": "4.0",
                        "Prefer": "return=minimal"
                    }
                )
                
                if response.status_code in [200, 201, 204]:
                    print(f"Dataverse write SUCCESS (attempt {attempt}): {record.get('signal')}")
                    return True
                elif response.status_code == 401:
                    # Token expired — clear cache and retry
                    print(f"Dataverse 401 — clearing token cache (attempt {attempt})")
                    _token_cache["token"] = None
                    _token_cache["expires"] = 0
                elif response.status_code == 429:
                    # Throttled — back off longer
                    print(f"Dataverse throttled (429) — backing off (attempt {attempt})")
                else:
                    print(f"Dataverse error {response.status_code} (attempt {attempt}): {response.text[:200]}")
                    
        except asyncio.TimeoutError:
            print(f"Dataverse timeout (attempt {attempt})")
        except Exception as e:
            print(f"Dataverse write failed (attempt {attempt}): {e}")
        
        # Exponential backoff: 1s, 2s, 4s
        if attempt < max_retries:
            wait_time = 2 ** (attempt - 1)
            print(f"Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)
    
    # All retries exhausted
    print(f"Dataverse write FAILED after {max_retries} attempts: {record.get('signal')}")
    return False


# =============================================================================
# CATALOG — GTINs and Clusters
# =============================================================================
CATALOG = {
    "00990832300006": {
        "label": "TreeFree Core Tape",
        "cluster": "HYGIENE",
        "rail": "aio-tfx-rail.ai",
        "dpu": "https://dpuone.ai/dpu/00990832300006.json",
        "signal": "acm-200.ai"
    },
    "00990832300013": {
        "label": "TreeFree Core Pant",
        "cluster": "HYGIENE",
        "rail": "aio-tfx-rail.ai",
        "dpu": "https://dpuone.ai/dpu/00990832300013.json",
        "signal": "acm-200.ai"
    }
    # Beauty & Personal Care GTINs: Add here when available
}

# Cluster keyword mapping
CLUSTER_KEYWORDS = {
    "HYGIENE": ["diaper", "diapers", "nappy", "nappies", "treefree", "core", "absorbent", "incontinence"],
    "BEAUTY_PERSONAL_CARE": ["cosmetic", "skincare", "beauty", "lotion", "cream", "serum", "hygiene-beaute"]
}

# Region mapping
REGION_KEYWORDS = {
    "ES": ["madrid", "spain", "españa", "es", "barcelona"],
    "DE": ["germany", "deutschland", "de", "berlin", "munich"],
    "FR": ["france", "paris", "fr"],
    "UK": ["uk", "united kingdom", "london", "england"],
    "US": ["usa", "united states", "us", "america"],
    "CA": ["canada", "ca", "toronto", "vancouver"],
    "EU": ["eu", "europe", "european union"],
    "JP": ["japan", "jp", "tokyo"],
    "AU": ["australia", "au", "sydney", "melbourne"],
    "BR": ["brazil", "br", "são paulo", "rio"]
}


def extract_gtin(text: str) -> Optional[str]:
    """Extract GTIN from text."""
    match = re.search(r'\b(\d{13,14})\b', text)
    if match:
        gtin = match.group(1)
        if gtin in CATALOG:
            return gtin
    return None


def extract_cluster(text: str) -> str:
    """Extract cluster from keywords."""
    text_lower = text.lower()
    for cluster, keywords in CLUSTER_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return cluster
    return ""


def extract_quantity(text: str) -> Optional[int]:
    """Extract quantity from text."""
    patterns = [
        r'(\d+)\s*(pallets?|pallet)',
        r'(\d+)\s*(units?|unit)',
        r'(\d+)\s*(cases?|case)',
        r'(\d+)\s*(containers?|container)',
        r'(\d+)k\b',
        r'(\d+)\s*(?:thousand|k)',
    ]
    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            qty = int(match.group(1))
            if 'k' in pattern:
                qty *= 1000
            return qty
    return None


def extract_region(text: str) -> str:
    """Extract region code from text."""
    text_lower = text.lower()
    for region, keywords in REGION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return region
    return ""


def determine_signal(gtin: Optional[str], cluster: str) -> tuple[str, str]:
    """Determine ACM signal based on extracted data."""
    if gtin and gtin in CATALOG:
        return "acm-200.ai", "ALLOW"
    elif cluster:
        return "acm-300.ai", "CONDITIONAL"
    else:
        return "acm-451.ai", "ESCALATE"


# =============================================================================
# ENDPOINTS — All with Full Ghost Headers
# =============================================================================

@app.get("/")
async def root():
    """Ghost Router status — with full Ghost Headers."""
    data = {
        "router": "aio-orderable.ai",
        "protocol": "ACM-68000",
        "version": "1.3.0",
        "status": "LIVE",
        "stack": "7SignalStack",
        "clusters": ["HYGIENE", "BEAUTY_PERSONAL_CARE"],
        "dataverse": DATAVERSE_URL,
        "endpoints": {
            "resolve": "/resolve?gtin=<gtin>",
            "catalog": "/catalog",
            "ingest": "/ingest",
            "health": "/health",
            "discovery": "/.well-known/acm-68000.json"
        },
        "trust_anchor": "dpuone.ai",
        "mcp_registry": "io.github.allooloo/acm-68000-mcp",
        "buyer_portal": "https://aio-buyer.com",
        "operator": "Allooloo Technologies Corp."
    }
    response = JSONResponse(data)
    return add_ghost_headers(response, signal="ACM-200", state="LIVE")


@app.get("/health")
async def health():
    """Health check — with full Ghost Headers."""
    data = {
        "status": "ok",
        "router": "aio-orderable.ai",
        "version": "1.3.0",
        "protocol": "ACM-68000",
        "dataverse_configured": bool(CLIENT_SECRET),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    response = JSONResponse(data)
    return add_ghost_headers(response, signal="ACM-200", state="HEALTHY")


@app.get("/resolve")
async def resolve(gtin: Optional[str] = None, cluster: Optional[str] = None):
    """
    Resolve GTIN or cluster to ACM signal — with full Ghost Headers.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    
    if gtin and gtin in CATALOG:
        item = CATALOG[gtin]
        data = {
            "protocol": "ACM-68000",
            "signal": item["signal"],
            "signal_state": "ALLOW",
            "gtin": gtin,
            "label": item["label"],
            "cluster": item["cluster"],
            "rail": item["rail"],
            "dpu": item["dpu"],
            "buyer_portal": f"https://aio-buyer.com/?gtin={gtin}",
            "timestamp": timestamp
        }
        response = JSONResponse(data)
        return add_ghost_headers(response, signal="ACM-200", state="ALLOW")
    
    elif gtin:
        data = {
            "protocol": "ACM-68000",
            "signal": "acm-404.ai",
            "signal_state": "NOT_FOUND",
            "gtin": gtin,
            "message": "GTIN not registered in catalog",
            "timestamp": timestamp
        }
        response = JSONResponse(data, status_code=404)
        return add_ghost_headers(response, signal="ACM-404", state="NOT_FOUND")
    
    elif cluster:
        cluster_upper = cluster.upper()
        if cluster_upper in ["HYGIENE", "BEAUTY_PERSONAL_CARE"]:
            items = [
                {**v, "gtin": k} 
                for k, v in CATALOG.items() 
                if v["cluster"] == cluster_upper
            ]
            data = {
                "protocol": "ACM-68000",
                "cluster": cluster_upper,
                "signal": "acm-200.ai" if items else "acm-404.ai",
                "signal_state": "ALLOW" if items else "NOT_FOUND",
                "items": items,
                "count": len(items),
                "timestamp": timestamp
            }
            response = JSONResponse(data)
            signal = "ACM-200" if items else "ACM-404"
            state = "ALLOW" if items else "NOT_FOUND"
            return add_ghost_headers(response, signal=signal, state=state)
    
    data = {
        "protocol": "ACM-68000",
        "signal": "acm-451.ai",
        "signal_state": "ESCALATE",
        "message": "Provide ?gtin= or ?cluster= parameter",
        "timestamp": timestamp
    }
    response = JSONResponse(data, status_code=400)
    return add_ghost_headers(response, signal="ACM-451", state="ESCALATE")


@app.get("/catalog")
async def catalog():
    """Return full catalog — with full Ghost Headers."""
    data = {
        "protocol": "ACM-68000",
        "router": "aio-orderable.ai",
        "version": "1.3.0",
        "clusters": {
            "HYGIENE": {
                "rail": "aio-tfx-rail.ai",
                "status": "LIVE",
                "items": [
                    {**v, "gtin": k}
                    for k, v in CATALOG.items()
                    if v["cluster"] == "HYGIENE"
                ]
            },
            "BEAUTY_PERSONAL_CARE": {
                "rail": "aio-rail.ai",
                "status": "LIVE",
                "items": [
                    {**v, "gtin": k}
                    for k, v in CATALOG.items()
                    if v["cluster"] == "BEAUTY_PERSONAL_CARE"
                ]
            }
        },
        "buyer_portal": "https://aio-buyer.com",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    response = JSONResponse(data)
    return add_ghost_headers(response, signal="ACM-200", state="CATALOG")


@app.post("/ingest")
async def ingest(request: Request):
    """
    INBOUND SIGNAL CATCH — with full Ghost Headers.
    
    Receives messy human/agent messages.
    Normalizes to ACM-68000 schema.
    Writes to Dataverse InboundEvents table.
    
    Zero reasoning. Keyword mapping only.
    
    v1.3.0: Added contact capture fields (email, name, phone, company)
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    
    try:
        body = await request.json()
    except:
        body = {"message": (await request.body()).decode()}
    
    raw_message = body.get("message", body.get("text", str(body)))
    sender = body.get("sender", body.get("from", "unknown"))
    
    # === CONTACT CAPTURE (v1.3.0) ===
    contact_email = body.get("contact_email", body.get("email", ""))
    contact_name = body.get("contact_name", body.get("name", ""))
    contact_phone = body.get("contact_phone", body.get("phone", ""))
    company_name = body.get("company_name", body.get("company", ""))
    
    # === NORMALIZATION (Zero Reasoning) ===
    gtin = extract_gtin(raw_message)
    cluster = extract_cluster(raw_message)
    quantity = extract_quantity(raw_message)
    region = extract_region(raw_message)
    signal, signal_state = determine_signal(gtin, cluster)
    
    # Build normalized record
    record = {
        "sender": sender,
        "raw_message": raw_message,
        "signal": signal,
        "cluster": cluster,
        "region": region,
        "quantity": quantity,
        "gtin": gtin or "",
        # === NEW: Contact Fields (v1.3.0) ===
        "contact_email": contact_email,
        "contact_name": contact_name,
        "contact_phone": contact_phone,
        "company_name": company_name,
    }
    
    # === WRITE TO DATAVERSE ===
    dataverse_success = await write_to_dataverse(record)
    
    # === RESPONSE ===
    data = {
        "protocol": "ACM-68000",
        "source": "aio-orderable.ai",
        "intent": "PROCURE_INQUIRY",
        "signal": signal,
        "signal_state": signal_state,
        "payload": {
            "gtin": gtin,
            "cluster": cluster or None,
            "quantity": quantity,
            "region": region or None
        },
        "contact": {
            "email": contact_email or None,
            "name": contact_name or None,
            "phone": contact_phone or None,
            "company": company_name or None,
        },
        "sender": sender,
        "timestamp": timestamp,
        "raw_message": raw_message,
        "dataverse_saved": dataverse_success,
        "buyer_portal": f"https://aio-buyer.com/?gtin={gtin}" if gtin else "https://aio-buyer.com"
    }
    
    response = JSONResponse(data)
    return add_ghost_headers(response, signal=signal.replace("acm-", "ACM-").replace(".ai", ""), state=signal_state)


@app.get("/.well-known/acm-68000.json")
async def well_known():
    """RFC 8615 compliant discovery endpoint — with full Ghost Headers."""
    data = {
        "protocol": "ACM-68000",
        "version": "1.3.0",
        "router": "aio-orderable.ai",
        "type": "ghost-router",
        "stack": "7SignalStack",
        "operator": "Allooloo Technologies Corp.",
        
        # Discovery
        "mcp_registry": "io.github.allooloo/acm-68000-mcp",
        "mcp_server": "https://mcp.10060.ai",
        "apex_resolver": "https://resolver.aio-resolver.com",
        "dataverse": DATAVERSE_URL,
        
        # Trust
        "trust_anchor": "dpuone.ai",
        "dpu": "https://dpuone.ai",
        
        # Endpoints
        "endpoints": {
            "root": "/",
            "health": "/health",
            "resolve": "/resolve",
            "catalog": "/catalog",
            "ingest": "/ingest"
        },
        
        # Clusters
        "clusters": {
            "HYGIENE": {"rail": "aio-tfx-rail.ai", "status": "LIVE"},
            "BEAUTY_PERSONAL_CARE": {"rail": "aio-rail.ai", "status": "LIVE"}
        },
        
        # Allowed domains (for agent verification)
        "allowed_domains": [
            "aio-orderable.ai",
            "7signalingress.ai",
            "aio-orderable-h4gfg8bwbyb2d5az.francecentral-01.azurewebsites.net",
            "resolver.aio-resolver.com",
            "dpuone.ai",
            "mcp.10060.ai",
            "acm-68000.ai",
            "acm-200.ai",
            "acm-300.ai",
            "acm-403.ai",
            "acm-404.ai",
            "acm-451.ai",
            "acm-500.ai",
            "acm-000.ai"
        ],
        
        # Signal definitions
        "signals": {
            "acm-200.ai": "ALLOW",
            "acm-300.ai": "CONDITIONAL",
            "acm-403.ai": "RESTRICT",
            "acm-404.ai": "NOT_FOUND",
            "acm-451.ai": "ESCALATE",
            "acm-500.ai": "SYSTEM_ERROR",
            "acm-000.ai": "NOT_APPLICABLE"
        },
        
        # Contact capture schema (v1.3.0)
        "contact_schema": {
            "contact_email": "string",
            "contact_name": "string",
            "contact_phone": "string",
            "company_name": "string"
        },
        
        "buyer_portal": "https://aio-buyer.com",
        "license": "MIT",
        "github": "https://github.com/allooloo/aio-orderable"
    }
    response = JSONResponse(data)
    return add_ghost_headers(response, signal="ACM-200", state="DISCOVERY")


# =============================================================================
# STARTUP
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)