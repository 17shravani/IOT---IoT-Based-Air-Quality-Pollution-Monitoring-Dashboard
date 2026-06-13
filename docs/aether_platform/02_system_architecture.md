# AETHER Network: System Architecture & Data Flow

This document details the multi-layered system architecture of the **AETHER Network** using the C4 model guidelines, outlining how edge sensors, autonomous agents, event brokers, and frontend layers interact.

---

## 1. System Context Diagram (C4 Level 1)

The context diagram outlines the primary boundaries of the AETHER platform, showing how external organizations, hardware sensors, and operations teams interact with the core engine.

```mermaid
graph TD
    User["Factory Operations Manager"] -- Monitor & Override --> AETHER["AETHER Command Center"]
    ESP32["Edge ESP32 Node Grid"] -- Cryptographic Telemetry --> AETHER
    AETHER -- Automated Mitigation --> HVAC["Defensive HVAC & Valves"]
    AETHER -- Immutable Compliance Proofs --> Ledger["Distributed Audit Log / ESGBook"]
    AETHER -- Alert Notification --> SMS["SMS / Email Gateways"]
```

---

## 2. Container Architecture Diagram (C4 Level 2)

This diagram details the containerized services that make up the AETHER ecosystem, highlighting the tech stack and integration boundaries.

```mermaid
graph TB
    subgraph Frontend Surfaces
        WebApp["Next.js 14 Dashboard\nReact 19, Recharts"]
        CLI["AETHER CLI\nNodeJS, TypeScript"]
    end

    subgraph API & Routing Layer
        Gateway["FastAPI Gateway\nOAuth2, JWT, WebSocket Stream"]
    end

    subgraph Multi-Agent AI Core
        Orch["LangGraph Orchestrator\nStateful Agent Coordination"]
        AgentConsensus["Consensus Engine\nAgent Voting (Raft-adapted)"]
    end

    subgraph High-Performance Data Layer
        Kafka["Apache Kafka Event Bus\nTelemetry Ingestion"]
        ClickHouse["ClickHouse OLAP\nReal-time Analytical Queries"]
        PG["PostgreSQL + TimescaleDB\nAudit Logs & Time-Series"]
        Neo4j["Neo4j Graph Database\nShared Agent Memory Graph"]
    end

    subgraph Physical/Simulation Interface
        ESP32_Nodes["ESP32 Microcontrollers\nMQ135, SDS011, DHT22"]
        Simulator["Digital Twin Engine\nThree.js simulation"]
    end

    %% Flow lines
    ESP32_Nodes -->|MQTT / WS| Gateway
    Simulator -->|WebSockets| WebApp
    Gateway -->|Publish Event| Kafka
    Kafka -->|Stream Processing| ClickHouse
    Kafka -->|Write Log| PG
    Orch -->|Read/Write Context| Neo4j
    Orch -->|Explainability Logs| PG
    Gateway <-->|WS Telemetry| WebApp
    Gateway -->|Invoke Agent swarm| Orch
    Orch -->|Command Override| Gateway
```

---

## 3. Sovereign Multi-Agent Interaction Map

AETHER's intelligence layer operates as a multi-tier agent society. Agents communicate via an asynchronous Event Bus and share access to a persistent Graph Memory.

```mermaid
sequenceDiagram
    autonumber
    participant ESP as ESP32 Telemetry Stream
    participant NX as NEXUS Agent (Orchestration)
    participant SH as SHIELD Agent (Protection)
    participant OR as ORACLE Agent (Prediction)
    participant SV as SOVEREIGN Agent (Decision)
    participant HX as HELIX Agent (Self-Healing)
    
    ESP->>NX: Ingests raw telemetry packet (AQI=210, Gas=1600)
    NX->>SH: Dispatches packet for threat auditing
    Note over SH: Audit reveals threshold breach!
    SH->>NX: Triggers critical alert warning
    NX->>OR: Requests prediction trajectory for next 60m
    OR->>NX: Forecasts: 94% chance of sustained high values
    NX->>SV: Requests mitigation proposal with confidence score
    Note over SV: Sovereign evaluates HVAC vs shutdown options
    SV->>NX: Submits proposal: Trigger HVAC boost (Conf: 98.4%)
    NX->>HX: Dispatches self-healing instruction
    HX->>ESP: Overrides local node actuator to activate air scrubbers
    Note over HX: Self-monitoring confirms parameters recovery
```

---

## 4. Infrastructure & Scaling Strategy

### 100M User / Five-Nines Scaling Blueprint
*   **Edge Processing**: Heavy compression and pre-filtering on local gateways before ingestion into AWS API Gateway.
*   **Event Ingestion**: Scaled Apache Kafka cluster deployed across 3 availability zones in active-active configurations, capable of handling 500,000 requests/sec.
*   **Database Partitioning**:
    *   **TimescaleDB**: Telemetry data partitioned by `timestamp` and `node_id` in 24-hour chunks to prevent index bloat.
    *   **PostgreSQL**: Metadata tables replicated across 5 global regions using AWS Aurora Global Database (sub-second lag).
    *   **ClickHouse**: Cold-data storage for deep compliance queries, compressing raw data at 5:1 ratio.
*   **Edge Execution**: Cloudflare Workers deployed globally as edge brokers, returning static dashboard updates in under 10ms.
