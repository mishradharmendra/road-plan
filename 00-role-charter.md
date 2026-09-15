# 00 — Role Charter: Principal Java Architect, Risk Intelligence

The calendar version of the role, not the job-description version.

---

## 1. What the role owns

### 1.1 Platform architecture for risk compute
Risk Intelligence typically spans: market & credit risk engines, VaR / stress / scenario
computation, limits and exposure monitoring, trade surveillance, AML/fraud signalling, and
regulatory reporting. The JVM layer sits in **compute orchestration, enrichment, aggregation,
and data serving** — not in the quant model math.

You own:
- How grid/batch compute, streaming enrichment, and low-latency serving fit together
- Job orchestration, scheduling, dependency graphs, replay/idempotency
- Aggregation and slice-and-dice serving layer for risk consumers
- Integration contracts with market data, reference data, position, and trade systems

### 1.2 Non-functional ownership
- Latency and throughput SLOs for risk runs and risk APIs
- Correctness under partial failure; idempotent, replayable overnight batch
- Capacity planning and **cost per risk run**
- Resiliency, failover, DR, and regional isolation

> When the 04:00 risk batch misses the 07:00 trader cutoff, it is your architecture on the bridge call.

### 1.3 Data correctness and lineage
In risk, a *wrong number delivered confidently* is worse than *no number*.
- Reconciliation and break-management patterns
- Golden-source discipline and mastering
- As-of / bitemporal data handling (critical for restatement and audit)
- BCBS 239-grade lineage — an architecture property, not a documentation exercise

### 1.4 Technical standards across many delivery teams
- JDK/JVM version strategy, GC and memory profile standards
- Framework strategy (Spring Boot vs Quarkus vs plain), build & dependency management
- Service templates / paved road, API contract standards, versioning
- Observability baseline, test strategy, resilience library set

Leverage comes from **paved roads**, not code-review volume.

### 1.5 Boundary negotiation with peer principals
The highest-risk, highest-value part of this specific role.
- **With Principal AI** — where the model boundary sits, feature stores, embedding/vector
  infrastructure, inference serving SLAs, model governance vs platform governance,
  who owns drift monitoring and who owns uptime
- **With Principal Web Engineer** — API contracts, BFF vs direct service access, auth/session,
  streaming/push to UI, backward compatibility and versioning policy

### 1.6 Risk, security, regulatory posture
- Threat modelling for risk platforms
- Data classification: PII, MNPI, client-confidential, restricted-list handling
- Crypto and key management, secrets, entitlement models
- Data residency across India / US / EU
- Change governance and audit evidence production

### 1.7 Talent and technical judgment
- Hiring bar for senior/lead/staff engineers
- Mentoring and sponsoring solution engineers into architecture scope
- Arbitrating design disputes across teams
- Deciding what the division will **not** build

### 1.8 Build-vs-buy and vendor strategy
Compute grids, market data vendors, streaming platforms, observability vendors, cloud services.
Multi-million decisions land here.

---

## 2. What the role does NOT own

Pretending otherwise is the most common way a new principal fails.

| Not yours | Whose it is |
|---|---|
| Sprint-level delivery of every team | Engineering managers / tech leads |
| Being the top committer | Senior engineers |
| Quant model mathematics | Quant research / model risk |
| Escalation path for every production incident | SRE / on-call rotation |
| Approving every design change | Tiered review model (see phase 3) |
| People management of the division | Engineering leadership |

---

## 3. Boundary map vs peer principals

Draft this in week 1–2, ratify by day 60. The grey zones must be **named explicitly**.

| Capability | Principal Java (you) | Principal AI | Principal Web | Grey zone — must decide |
|---|---|---|---|---|
| Risk compute grid / batch | Own | Consult | — | Model-heavy batch jobs |
| Feature / embedding pipelines | Platform + SLA | Semantics + schema | — | **Who owns the pipeline runtime** |
| Model inference serving | Runtime, scaling, SLO | Model, eval, drift | — | **Who is paged at 2am** |
| Risk data serving APIs | Own | Consumer | Consumer | **BFF vs direct** |
| API gateway / auth | Co-own | — | Co-own | **Token/session ownership** |
| Streaming to UI | Own transport | — | Own contract | Push protocol choice |
| Data platform / lakehouse | Co-own | Co-own | — | **Schema governance authority** |
| Observability standard | Own | Adopt | Adopt | Model-specific telemetry |
| Cost attribution | Own | Own model spend | Own CDN/front spend | Shared infra allocation |

**Output artifact:** `Principal Boundary Contract` — one page, three signatures, ratified by the
shared leader. Do this by day 60; after that boundaries get set by accident and cost a year to undo.

---

## 4. Decision rights model (publish this)

| Tier | Scope | Process | Decider |
|---|---|---|---|
| **Tier 1** | Cross-division, regulatory impact, >$X cost, new vendor, data residency | Architecture Forum + written ADR + exec sign-off | Forum, principals accountable |
| **Tier 2** | Cross-team service/API/schema change, new persistent store, framework deviation | ADR + 1 principal + 1 senior reviewer, 5-day async window | Architecture practice |
| **Tier 3** | Team-local design, internal refactor, within paved road | No review; team decides | Team |

Without published tiers, you become an approval gate and the division's bottleneck inside 90 days.

---

## 5. Signals you are succeeding in the role

- You are invited to designs **early**, not shown finished designs
- Other people author ADRs without you asking
- Teams adopt the paved road because it is easier, not because it is mandated
- Peer principals bring you into their decisions unprompted
- Risk/compliance stakeholders come to you before the auditors do

## 6. Signals you are failing

- Every meeting you attend is a status meeting
- You are the sole ADR author after month 4
- Designs arrive "for sign-off" fully built
- Teams route around your forum
- You are described as "the person who says no"
