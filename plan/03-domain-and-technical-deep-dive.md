# Domain and Technical Deep Dive

What to assess during Weeks 1–6, organised by area. For each: what good looks
like, questions to ask, and red flags. Use these to fill the scorecard in
`05-artefacts-and-templates.md`.

---

## 1. Market Data Platform

### Typical shape

```
Vendor/exchange feeds          Ingest & normalise         Distribute            Consumers
(Bloomberg B-PIPE, LSEG     ->  feed handlers         ->  pub/sub bus       ->  client APIs (WS/FIX/REST),
 RTDS/RDP, ICE, CME MDP3,       symbology mapping          conflation            desktop apps, risk engines,
 direct exchange ITCH/OUCH)     validation, cleansing      entitlements          internal analytics
                                                           snapshot/cache
                                    |
                                    v
                             Tick store / history  (kdb+, ClickHouse, Timescale, Parquet/Iceberg)
                             EOD golden copy, corrections, bitemporal
```

### What good looks like

- Clear latency tiers: real-time (sub-ms to low-ms), near-real-time (conflated,
  100ms–1s), delayed (15 min for licensing), end-of-day.
- Per-consumer back-pressure and conflation — one slow client can't slow others.
- Symbology service is a single source of truth (FIGI/ISIN/CUSIP/SEDOL/RIC/ticker
  mapping with effective dates).
- **Entitlements enforced at distribution and auditable** — every delivery can be
  attributed to a licensed user for vendor reporting.
- Corrections and late ticks handled; history is bitemporal (valid time vs
  known-at time) so you can reproduce "what did we publish at 14:32:05".
- Hot/warm failover for feed handlers with measured failover time; gap detection
  and recovery (sequence numbers, snapshot + replay).
- Clock sync meets requirement (PTP where MiFID II RTS 25 granularity applies).

### Questions to ask

1. What is p99 and p99.9 tick-to-client latency at market open, and on the worst
   day of the last year (e.g. major macro release)?
2. What happens when a consumer is slow? Show me the code path.
3. How long does feed handler failover take, and when was it last tested?
4. How are entitlements enforced, and how do we produce vendor usage reports?
   When was the last vendor audit and what did it find?
5. How do we handle a vendor correction to a price already distributed?
6. Can we replay a trading day deterministically for incident analysis?
7. What's the market data vendor spend, and do we know which consumers use which
   feeds? (Unused feeds are a frequent cost win.)

### Red flags

- GC pauses correlated with latency spikes at market open.
- Single-threaded fan-out; unbounded queues per consumer.
- Entitlements checked only at login, not per instrument/feed.
- "We don't store what we published, only what we received."
- Failover never tested in production hours.
- Symbology mapping duplicated in several services.

### Java-specific levers on the hot path

| Lever | When appropriate | Caution |
|---|---|---|
| ZGC (generational, JDK 21+) | Sub-ms pause target on large heaps without rewriting code | Higher CPU overhead; measure throughput |
| Azul Prime (Falcon JIT, C4 GC) | Latency tier where rewriting to zero-GC is uneconomic | Licence cost; vendor lock-in |
| Zero-allocation hot path (Agrona buffers, flyweights, object pools) | Feed handlers, normalisers, fan-out | Harder to maintain; restrict to hot path only |
| LMAX Disruptor | Single-producer/multi-consumer pipelines with predictable latency | Busy-spin wait strategies burn cores |
| Aeron (+ Aeron Cluster) | Low-latency UDP/IPC messaging, replicated state machines | Operational expertise required |
| Chronicle Queue / Map | Persisted low-latency journals, replay | Commercial licence for some features |
| SBE (Simple Binary Encoding) | Wire format on hot path | Schema evolution discipline needed |
| CPU pinning, isolcpus, NUMA awareness | Dedicated hosts for latency tier | Not available/meaningful on most shared cloud VMs |
| Virtual threads (JDK 21) | I/O-bound services: client REST APIs, entitlement lookups, reference data | **Not** for the latency-critical hot path; watch pinning with `synchronized` on JDK < 24 |

---

## 2. Risk and Analytics Platform

### Typical shape

```
Positions/portfolios + Market data snapshot + Reference data + Models/config
                          |
                    Job orchestration (overnight batch + intraday on-demand)
                          |
                    Compute grid (in-house, Spark, Hazelcast/Ignite/Coherence, K8s jobs, cloud batch)
                          |
             Pricing & sensitivities (Greeks), VaR (historical / Monte Carlo), stress,
             FRTB SA / IMA, XVA, performance attribution, factor models
                          |
                    Results store -> aggregation -> client reports / APIs / UI
```

### What good looks like

- **Reproducibility:** any historic run can be reproduced from stored immutable
  inputs (positions snapshot, market data snapshot, model version, config version).
- **Determinism:** same inputs produce identical outputs. Watch floating-point
  reduction order in parallel aggregation, `HashMap` iteration order, time-zone
  and holiday calendar sources, random seeds in Monte Carlo.
- Batch SLA met on high-volatility days, not just average days.
- Partial failure handled: failed tasks retry idempotently; the run doesn't restart
  from zero.
- Model governance: models versioned, validated, and model changes go through
  controlled release (clients may be subject to SR 11-7 / PRA SS1/23 model risk
  expectations and will ask).
- Lineage: every output number traceable to inputs (BCBS 239 expectations for bank
  clients).
- Clear numeric policy: `double` for risk maths, `BigDecimal` (or scaled long) for
  money/booking/settlement amounts, documented rounding rules.

### Questions to ask

1. How many nights in the last 6 months did batch breach SLA? What was common to
   those nights?
2. If a client disputes a VaR number from 3 months ago, how long to reproduce it?
3. What's the task granularity on the grid, and where is time actually spent —
   compute, serialisation, data loading, or waiting?
4. How are pricing libraries integrated — pure Java (e.g. OpenGamma Strata),
   in-house, or native (QuantLib/C++ via JNI/JNA or the FFM API)?
5. How do model changes reach production, and who signs off?
6. What's compute cost per run, and how much is idle capacity?

### Red flags

- "It's non-deterministic, we reconcile manually."
- Market data loaded per task instead of broadcast/cached per node.
- Java serialisation (`ObjectOutputStream`) across the grid.
- A single mega-job that restarts from scratch on any failure.
- Model code and infrastructure code in the same release train with no separation.
- Results aggregated with naive parallel `double` sums and compared by equality.

---

## 3. Java Estate Health

### Inventory to build (Week 2–3)

For every service/repo: JDK version, JVM vendor, framework + version (Spring Boot,
Quarkus, Micronaut, Dropwizard, plain), build tool, test count and runtime,
critical/high CVE count, last deploy date, owning team, on-call.

A simple script against your SCM (parse `pom.xml` / `build.gradle(.kts)` /
`.java-version` / Dockerfile base images) gets you 80% of this in a day.

### Benchmarks for "healthy" in late 2026

| Item | Healthy | Watch | Act now |
|---|---|---|---|
| JDK | 21 or 25 LTS | 17 | 8 or 11 (11 is past most free public updates; 8 blocks modern libraries and GCs) |
| Spring Boot | 3.x current | 3.x older minor | 2.x (OSS support ended 2023; also forces `javax` → `jakarta` migration) |
| JVM vendor | Temurin / Corretto / Zulu / Microsoft (supported contract where needed) | Mixed without policy | Oracle JDK without a licence review |
| Build time (CI, main service) | < 10 min | 10–20 min | > 20 min |
| Dependency updates | Automated (Renovate/Dependabot), SBOM in CI | Manual quarterly | No process |
| Observability | OpenTelemetry traces, Micrometer metrics, JFR, structured logs | Metrics only | Logs only |
| Tests | Fast unit + contract + integration with Testcontainers | Integration heavy, slow | Mostly manual/UAT |

### Questions to ask

1. What's blocking JDK upgrades — libraries, app server, native dependencies, fear?
2. Is there a shared internal framework/library ("platform-commons")? Who owns it?
   Internal frameworks are often the real upgrade blocker.
3. How are Java dependency CVEs detected and how fast are criticals patched?
   (Log4Shell response time is a good historic question.)
4. Which services have performance tests, and are they run in CI?

---

## 4. Cross-cutting: Resilience, Security, Regulation

| Topic | Why it matters here | What to check |
|---|---|---|
| **DORA** (EU, since Jan 2025) | Bank clients must manage ICT third-party risk; as their vendor you will get questionnaires, audit rights, exit-plan and incident-reporting obligations | Incident classification and reporting timelines; resilience testing evidence; exit/portability documentation |
| **UK operational resilience** | Clients define impact tolerances for important business services that depend on you | Are your SLAs and recovery times mapped to client impact tolerances? |
| **BCBS 239** | Bank clients need lineage and accuracy of risk data | Lineage capability; reconciliation controls |
| **SOC 2 Type II / ISO 27001** | Commercial prerequisite for most clients | Change management evidence from CI/CD; access reviews |
| **Market data licensing** | Vendor audits can produce large back-billing | Entitlement audit trail; derived-data policy |
| **Software supply chain** | Clients increasingly ask for SBOMs | CycloneDX/SPDX generation; signed artefacts (Sigstore); base image policy |
| **Secrets and keys** | Vendor feed credentials, client API keys | Vault/KMS usage; no credentials in config repos |

---

## 5. Emerging Topics to Have a View On (not to push in the first 90 days)

Have a considered, evidence-based opinion ready when asked; don't lead with them.

- **Virtual threads and structured concurrency** — likely big simplification for
  I/O-bound client APIs; not for hot paths.
- **Foreign Function & Memory API (JDK 22+ final)** — replacement for JNI for native
  pricing libraries; safer and faster to integrate.
- **Vector API (incubating)** — potential for risk maths; don't bet production on
  an incubator API without a fallback.
- **GraalVM native image / CRaC** — startup-time wins for elastic grid workers and
  serverless; check reflection-heavy libraries.
- **AI/LLM features on analytics** — clients will ask. Your position: governance of
  data entitlements and sensitive data first; Java integration via Spring AI /
  LangChain4j is straightforward, the hard part is entitlements and auditability.
