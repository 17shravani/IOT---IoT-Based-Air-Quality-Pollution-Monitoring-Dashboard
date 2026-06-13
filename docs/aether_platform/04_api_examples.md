# AETHER Network: Production API Specifications & SDKs

This document contains production-ready API endpoint specifications, WebSocket event payloads, GraphQL schemas, and SDK consumption examples.

---

## 1. REST API Endpoints (FastAPI Spec)

### Ingest Telemetry Packet
*   **Method**: `POST`
*   **URL**: `/api/v1/telemetry/ingest`
*   **Authentication**: Bearer Token (JWT / API Key)
*   **Request Body**:
```json
{
  "node_id": "8f3b92c4-2a6f-4d92-bf3e-8c347ad19ff2",
  "temperature": 28.5,
  "humidity": 62.4,
  "gas_raw": 450,
  "pm25": 42.10,
  "pm10": 67.36,
  "aqi": 115,
  "category": "Moderate",
  "mode": "normal",
  "timestamp": "2026-06-13T12:30:00Z"
}
```
*   **Response** (`202 Accepted`):
```json
{
  "status": "success",
  "packet_id": "0x7E1B39D4C2F8A",
  "processed_by": "NEXUS_Agent",
  "audit_trail_created": true
}
```

### Fetch Agent Decision Logs
*   **Method**: `GET`
*   **URL**: `/api/v1/agents/decisions?station_id=12c3f4e5-9a8b-7c6d-5e4f-3a2b1c0d`
*   **Response** (`200 OK`):
```json
[
  {
    "id": "7ae8f427-2394-4dcc-9a30-bd327de500f7",
    "timestamp": "2026-06-13T12:28:45Z",
    "trigger_type": "Anomaly",
    "initiating_agent": "SHIELD",
    "decision_payload": {
      "metric_breached": "aqi",
      "value": 245,
      "limit": 200
    },
    "confidence_score": 98.40,
    "rationale": "Sustained high AQI values detected at station. Automatic activation of air scrubbers initiated to restore normal breathing atmosphere.",
    "mitigation_executed": true,
    "audit_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  }
]
```

---

## 2. WebSockets Telemetry Channel

### Subscription Endpoint
*   **URL**: `wss://api.aether.network/v1/telemetry/ws?client_id=SovereignClient_7e1b`

### Outgoing Server Event (Broadcast)
*   **Channel**: `telemetry:update`
```json
{
  "event": "telemetry:update",
  "city": "Delhi",
  "data": {
    "aqi": 115,
    "category": "Moderate",
    "gas_raw": 450,
    "pm25": 42.1,
    "pm10": 67.3,
    "temperature": 28.5,
    "humidity": 62.4,
    "timestamp": "12:30:00 PM"
  },
  "agents": {
    "oracle": { "status": "Stable", "action": "Analyzing trends" },
    "shield": { "status": "Guarding", "action": "Verifying limits" }
  }
}
```

---

## 3. GraphQL Query (ESG Reporting)

For enterprise auditors generating PDF compliance logs.

```graphql
query GetESGComplianceReport($stationId: ID!, $startDate: DateTime!) {
  complianceReport(stationId: $stationId, startDate: $startDate) {
    stationCity
    averageAQI
    maxAQI
    totalViolations
    explainabilityLogs {
      timestamp
      agent
      rationale
      confidence
      auditHash
    }
  }
}
```

---

## 4. Python Developer SDK Usage Example

```python
from aether_sdk import AetherClient

# Initialize secure connection
client = AetherClient(api_key="ae_prod_99f38c3e...")

# Fetch live environment metrics
metrics = client.stations.get_metrics(city="Delhi")
print(f"Current Delhi AQI: {metrics.aqi} ({metrics.category})")

# Inject manual audit verification override
client.agents.dispatch_override(
    agent_name="SHIELD",
    override_action="FORCE_VENTILATION",
    duration_minutes=30,
    reason="Scheduled physical system test"
)
```
