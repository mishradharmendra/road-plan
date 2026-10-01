# Artefacts and Templates

Ready-to-fill templates for the deliverables in the roadmap.

---

## 1. System Assessment Scorecard (Weeks 3–4)

Score each major system 1–5. Keep it private until reviewed with the owning team
lead and the SA — scores published without consultation feel like an audit.

| Dimension | 1 (poor) | 3 (adequate) | 5 (strong) | Score | Evidence |
|---|---|---|---|---|---|
| Business criticality | Internal tool | Important product | Revenue-critical, client-contracted SLA | | |
| Reliability | Frequent P1/P2, recurring causes | Occasional incidents, RCAs done | Rare incidents, causes eliminated | | |
| Performance vs SLA | Regularly breached | Met on average days | Met on worst days with headroom | | |
| Observability | Logs only | Metrics + logs | Traces, metrics, JFR, SLO dashboards, alerts on SLOs | | |
| Delivery speed | Monthly+ releases, manual | Weekly, partly automated | On-demand, automated, low change failure rate | | |
| Tech currency | JDK 8, EOL frameworks | JDK 17, supported frameworks | JDK 21+, current frameworks, automated updates | | |
| Security posture | Open critical CVEs | Tracked, patched in weeks | SBOM, patched in days, signed artefacts | | |
| Testability | Mostly manual | Unit + some integration | Fast pyramid, contract tests, perf tests in CI | | |
| Operability | Tribal knowledge | Runbooks exist | Runbooks tested, failover drilled | | |
| Knowledge concentration | 1 person knows it | 2–3 people | Whole team, documented | | |
| Regulatory/audit readiness | Can't evidence controls | Evidence with effort | Evidence automated (lineage, change control) | | |

**Summary line per system:** *"[System] is [strong/adequate/at risk]; the biggest
risk is [X]; the cheapest meaningful improvement is [Y]."*

---

## 2. Architecture Observations — First 45 Days (outline)

Target length: 6–10 pages. Co-reviewed with SA before circulation.

1. **Purpose and method** — who I spoke to (count, roles), what I read, what I
   measured. One paragraph.
2. **What's working well** — 4–6 specific strengths, naming systems and teams.
   (This section is not optional or token. It's what makes the rest credible.)
3. **Baseline metrics** — the Week 3 table with sources.
4. **Observations** — 6–10 items, each with:
   - Observation (one sentence)
   - Evidence (numbers, incidents, code references)
   - Impact (client, cost, risk, engineering time)
   - Confidence (high/medium/low)
5. **Recommendations** grouped:
   - *Now* (this quarter, low risk, named owners)
   - *Next* (2–3 quarters, need funding or planning)
   - *Later* (options to investigate; no commitment)
6. **What I'm not recommending, and why** — explicitly defuses fear of big rewrites.
7. **Open questions** — including any points where SA and I see things differently.
8. **Proposed next 90 days** for my own work.

---

## 3. ADR Template

Store in each repo under `docs/adr/NNNN-title.md`. Cross-team ADRs in a central
architecture repo with an index.

```markdown
# NNNN. <Decision title>

- Status: Proposed | Accepted | Superseded by NNNN | Deprecated
- Date: YYYY-MM-DD
- Deciders: <names>   (for cross-team: SA + Principal Java Architect + affected leads)
- Consulted: <names>
- Scope: <systems / teams affected>

## Context
What problem, what constraints (SLA, regulation, cost, deadline), what evidence.

## Options considered
### Option A — <name>
Pros / cons / cost / risk / evidence (benchmarks, spikes).
### Option B — <name>
...

## Decision
What we chose, in one paragraph.

## Consequences
Positive, negative, and follow-up work. Record dissent here if any
("<Name> preferred Option B because ...; we will revisit if <trigger>").

## Validation
How we'll know it worked (metric + target + date).
```

---

## 4. Java Platform Standards v1 — Skeleton (Weeks 9–13)

Keep v1 short (≤ 10 pages). Every rule states the **reason** and a **waiver
process**. Standards without an exit ramp create conflict.

```
1. Scope and waiver process
   - Applies to: new services immediately; existing services at next major change
   - Waiver: ADR with expiry date, approved by Principal Java Architect; SA consulted
     if the waiver affects a solution design

2. Runtime
   - Supported JDKs: 21 LTS (default), 25 LTS (allowed, target for new latency tier),
     17 (maintenance only, exit by <date>), 8/11 (exit plan required by <date>)
   - JVM distribution: <Temurin/Corretto/Zulu>; commercial JVM (e.g. Azul Prime)
     only for named latency-tier services
   - Container base images: <approved list>, rebuilt weekly

3. GC and JVM flags by workload class
   - Latency tier (market data hot path): ZGC generational or commercial low-pause;
     fixed heap (Xms=Xmx); AlwaysPreTouch; documented CPU allocation
   - Request/response services: G1 default; container-aware sizing via
     MaxRAMPercentage
   - Batch / risk grid workers: Parallel GC or G1 tuned for throughput
   - All: JFR continuous recording on; GC logging on; heap dump on OOM

4. Frameworks and libraries
   - Service framework: <Spring Boot 3.x | Quarkus> — one default, one allowed alternative
   - Messaging clients: <Kafka / Solace / Aeron> with the internal wrapper version X
   - Serialisation: <Protobuf/Avro for services, SBE for hot path>; no Java serialisation
   - HTTP client, JSON, testing libraries: named defaults
   - Banned: <e.g. Log4j 1.x, Java serialisation across network, unmaintained libs>

5. Concurrency
   - Virtual threads: default for I/O-bound request handling on JDK 21+
   - Hot path: explicit threading model documented per service; no blocking calls
   - Shared mutable state: documented ownership; prefer immutable value objects

6. Numerics
   - double for risk/pricing maths; BigDecimal or scaled long for monetary amounts
   - Rounding modes documented per domain; parallel aggregation order-deterministic
     where reproducibility is required

7. Observability
   - OpenTelemetry tracing with correlation IDs propagated across messaging
   - Micrometer metrics: standard names and tags; no high-cardinality labels
     (no instrument IDs, client IDs as metric labels)
   - Structured JSON logs; no sensitive data (client positions, credentials) in logs

8. Build and supply chain
   - <Gradle | Maven> with shared conventions plugin / parent POM
   - SBOM (CycloneDX) generated on every build; critical CVEs block release
   - Automated dependency updates (Renovate); signed artefacts

9. Testing
   - Unit, contract (e.g. Pact / schema registry compatibility), integration
     (Testcontainers)
   - JMH benchmarks required for hot-path changes; perf regression gate in CI
     for latency-tier services

10. Reproducibility and data (risk and market data services)
   - Inputs to calculations are immutable, versioned snapshots
   - Time: all timestamps UTC, java.time only, clock injected (no System.currentTimeMillis
     in business logic)
```

---

## 5. Initiative Charter (Month 4)

```markdown
# Initiative: <name>

Sponsor: <exec name>          Co-owner: <SA name, if solution impact>
Lead: <you>                   Team(s): <names>

## Problem
<2-3 sentences, with baseline numbers>

## Target
| Metric | Baseline | Target | By |
|---|---|---|---|

## Scope
In: ...   Out: ...

## Approach
Options considered (link ADR). Chosen approach. Riskiest assumption and how the
spike will test it.

## Rollout
Shadow / dual-run -> one tier or asset class -> full. Rollback plan.

## Risks
| Risk | Likelihood | Impact | Mitigation | Owner |

## Governance
Weekly status to sponsor. Decision log. Go/no-go criteria per stage.
```

---

## 6. Weekly Note to Manager (5 bullets)

```
Week N — <date>
1. Done: ...
2. Learned: ...          (one insight about the org or system)
3. Next week: ...
4. Blockers / asks: ...
5. Risk I'm watching: ...
```
