# Roadmap — Day 1 to Month 6

Five phases. Each phase has **deliverables** and **exit criteria**. Do not move to
the next phase's behaviour (e.g. proposing change) until the exit criteria of the
current phase are met, even if you are tempted.

```
Phase 0  Pre-joining          (2 weeks before)   Prepare, don't opine
Phase 1  Listen & map         (Weeks 1-4)        Earn context
Phase 2  Diagnose & quick win (Weeks 5-8)        Earn credibility
Phase 3  Standardise          (Weeks 9-13)       Earn authority
Phase 4  Strategic initiative (Months 4-6)       Earn mandate
```

---

## Phase 0 — Pre-joining (2 weeks before Day 1)

**Goal:** arrive with domain vocabulary and a question list, not opinions.

| Action | Concrete output |
|---|---|
| Read the firm's public product pages, API docs, SLAs, status page history, last 2 annual reports / investor decks | 1-page note: products, customer segments (buy-side, sell-side, corporates), which products are revenue-critical |
| Read their public engineering blog / GitHub / job ads for the last 12 months | List of stack signals (Kafka? kdb+? Spring? Coherence? AWS/Azure/on-prem?). Job ads tell you what's hurting — repeated "low latency", "migration", "modernisation" = known pain |
| Refresh regulatory context relevant to a data/risk vendor | Notes on: BCBS 239 (risk data aggregation and lineage), FRTB (if they sell risk to banks), DORA (EU ICT resilience, in force Jan 2025 — vendors to banks are "ICT third-party providers"), UK operational resilience (impact tolerances), MiFID II RTS 25 (clock sync), SOC 2 / ISO 27001 |
| Refresh market data vendor licensing basics | Know what "redistribution", "derived data", "non-display use" and "entitlement reporting" mean — licensing breaches are a board-level cost risk |
| Ask your hiring manager for 3 things by email | (1) Org chart for technology, (2) the top 3 outcomes they expect from you in 6 months, (3) the name and background of the Solution Architect(s) and how they see the split |

**Exit criteria:** you can explain in 2 minutes what the firm sells, to whom, and
what your manager thinks success looks like at Month 6.

---

## Phase 1 — Listen & Map (Weeks 1–4)

**Goal:** build an accurate map of systems, people and pain. Change nothing.

### Week 1 — Access and first conversations

- Day 1–2: get access to source control, CI, wiki/Confluence, Jira, observability
  (Grafana/Datadog/Splunk/ELK), incident tracker, architecture repository, cloud
  consoles (read-only). Track blockers in a list — your manager will want to know.
- Day 1–3: **1:1 with the Solution Architect** using the script in
  `02-solution-architect-alignment.md`. This is the most important meeting of
  your first month. Do it before you meet their stakeholders.
- Day 2–5: 1:1s with your manager, Head of Engineering/CTO, heads of Market Data,
  Risk/Analytics, Platform/SRE, Security. Use question sets in `04-...md`.
- Read: last 6 months of **P1/P2 postmortems**. Nothing tells you more, faster.

**Deliverable (Friday Week 1):** private notes doc: people met, top pains quoted
verbatim, open questions.

### Week 2 — System walkthroughs

- Ask each team lead for a **60-minute whiteboard walkthrough** of their system:
  inputs, outputs, SLAs, data stores, deployment, what wakes them up at night.
- Sit in on: one on-call handover, one sprint planning, one architecture review
  (if it exists), one release.
- Clone the top 5 revenue-critical Java repos. Build them locally. Time the build.
  Note JDK version, framework versions, test count, test runtime, flaky tests.

**Deliverable:** first-draft **context diagram** (C4 level 1 and 2) of the
market-data and risk flows. Share with the SA as "can you correct this?" — this
positions you as a learner and gives them ownership of accuracy.

### Week 3 — Data and numbers

Pull a baseline. You will need these numbers in every proposal for the next year.

| Area | Metric to baseline |
|---|---|
| Market data | Tick-to-client p50/p99/p99.9 latency; messages/sec at peak (market open, US data releases); gap/stale-data incidents per month; feed failover time |
| Risk/analytics | Overnight batch start/end times and variance; % nights batch finished within SLA; intraday recalculation time; compute cost per run |
| Delivery | Deploy frequency, lead time for change, change failure rate, MTTR (DORA metrics) per team |
| Java estate | Services by JDK version (8/11/17/21); Spring Boot versions; count of critical/high CVEs in dependencies; Oracle JDK usage (licence cost exposure) |
| Reliability | P1/P2 incidents per month by system; top 3 recurring root causes |
| Cost | Cloud/infra spend by system; market data vendor spend (often the single largest non-people line) |

**Deliverable:** baseline spreadsheet, sources noted for every number.

### Week 4 — Synthesis

- Fill the **system assessment scorecard** (`05-...md`) for each major system.
- Write down 10 candidate problems. For each: evidence, affected users, cost of
  doing nothing, effort, who owns it today.
- Review the list with the SA *before* your manager. Ask: "Which of these are
  already on your radar or in flight? I don't want to duplicate."

**Exit criteria for Phase 1:**
- You have met at least 25 people, including 2 customers-facing people (sales
  engineering / client support) and at least 1 client call listened to.
- Context diagram reviewed and corrected by at least 2 team leads and the SA.
- Baseline numbers exist for latency, batch, delivery, JDK/CVEs.
- The SA has seen your candidate problem list before anyone else senior.

---

## Phase 2 — Diagnose & Quick Wins (Weeks 5–8)

**Goal:** publish a diagnosis and deliver 1–2 wins that engineers feel.

### Pick quick wins with these filters

A good first win is: (a) visible to many engineers, (b) low risk to production,
(c) not owned by anyone else or explicitly handed to you, (d) completable in
4 weeks, (e) measurable before/after.

Typical high-probability candidates in a Java risk/market-data shop:

| Candidate | Why it works as a first win | Measure |
|---|---|---|
| **JDK licensing and runtime consolidation** — move Oracle JDK to Temurin/Corretto/Azul Zulu | Oracle's 2023 per-employee Java SE licensing can be a 6–7 figure annual cost. Finance and CTO both notice | Annual licence cost avoided; # services migrated |
| **Build time reduction** on the largest monorepo/multi-module build (Gradle build cache / Maven parallel + remote cache, test parallelisation, flaky test quarantine) | Every engineer feels it daily | Median CI time before/after; flaky test count |
| **Dependency/CVE hygiene** — SBOM (CycloneDX) in CI, Renovate/Dependabot, a policy for critical CVEs | Security and audit (SOC 2, DORA) will love it; low production risk | Critical/high CVE count; mean time to patch |
| **JVM observability baseline** — JFR continuous recording, GC logs, async-profiler on demand, standard Micrometer metrics | Converts future performance arguments into data | # services with JFR + GC dashboards |
| **Fix one recurring incident root cause** from the postmortem review (e.g. GC pauses during market open, connection pool exhaustion, Kafka consumer lag during batch) | Directly reduces pages; on-call engineers become your advocates | Incidents/month of that class |

Pick **one engineering-productivity win and one production-reliability win**.
Run them *with* a team, not for them; the team presents the result.

### Week 5–6 — Diagnosis document

Write **"Architecture Observations — First 45 Days"** (outline in `05-...md`).
Rules:
- Strengths section first and real — name specific people and systems.
- Every observation has evidence and a number.
- No "rewrite" recommendations. Recommendations are sized as: *now (≤1 quarter)*,
  *next (2–3 quarters)*, *later (options only)*.
- Co-review with SA; offer co-authorship of any section touching solution design.

### Week 7–8 — Deliver and show

- Ship the two wins. Demo them in the engineering all-hands or guild meeting.
- Present the observations doc to your manager + CTO, SA in the room.

**Exit criteria for Phase 2:**
- Two wins shipped with before/after numbers.
- Diagnosis doc accepted by your manager; SA publicly agrees with it (or their
  disagreements are captured as open questions in the doc, not in hallways).
- You have a named list of "Now" items with owners agreed.

---

## Phase 3 — Standardise (Weeks 9–13)

**Goal:** turn your judgement into reusable assets so your impact scales beyond
the meetings you attend.

| Deliverable | Content | Owner / co-owner |
|---|---|---|
| **Java Platform Standards v1** | Supported JDKs (target 21 LTS, 17 allowed, 8/11 with dated exit), approved frameworks, GC defaults per workload class, logging/metrics/tracing conventions, error handling, config, dependency policy, testing pyramid, JMH for perf-critical code. Skeleton in `05-...md` | You own; SA reviews for solution-fit |
| **Golden path service template** | A repo template/archetype that bakes in the standards: build, CI, SBOM, JFR, OpenTelemetry, health checks, Dockerfile, Helm chart | You + Platform team |
| **ADR process** | Lightweight ADRs in each repo + an index. Define which decisions need cross-team review | Co-owned with SA — explicitly |
| **Architecture review rhythm** | Fortnightly design review, 45 min, published agenda, written pre-reads, decisions recorded as ADRs | Co-chair with SA |
| **Java modernisation roadmap** | Per-service path off JDK 8/11 and old Spring; dated milestones; risk-ranked | You; teams commit dates |
| **Community of practice** | Monthly Java guild: 1 internal talk + 1 "how we fixed X" story | You start it; hand over chairing by Month 6 |

**Exit criteria for Phase 3:**
- Standards v1 published, with at least 3 teams signed up to adopt in the next
  quarter.
- Golden path used by at least 1 new service.
- ADRs being written by teams without you prompting.
- Design review running with SA as co-chair.

---

## Phase 4 — Strategic Initiative (Months 4–6)

**Goal:** own one problem of real business consequence end-to-end and move a
headline metric.

### Choosing the initiative

Choose from your Phase 1 candidate list using this scoring (1–5 each):
business impact, evidence strength, sponsor exists, fits your remit (Java/runtime/
platform depth), does **not** overlap an SA-owned solution in flight.

Likely candidates for this type of firm:

**A. Market data distribution: latency and resilience**
- Problem shape: p99/p99.9 spikes at market open, slow failover, head-of-line
  blocking for slow consumers, uncontrolled fan-out.
- Typical levers: conflation per consumer tier, back-pressure, moving hot path to
  off-heap/zero-GC (Agrona, Chronicle Queue, Aeron, LMAX Disruptor), ZGC or Azul
  Prime for the tier that can't be zero-GC, CPU pinning/isolation, busy-spin vs
  park trade-offs, deterministic replay for incident analysis.
- Target example: "p99.9 tick-to-client from X ms to Y ms during market open;
  feed failover from X s to < Y s; zero stale-price incidents for 60 days."

**B. Risk calculation grid: throughput and determinism**
- Problem shape: overnight batch breaching SLA on high-volatility days, poor
  reproducibility (same inputs different outputs), expensive idle compute.
- Typical levers: task granularity and data locality, avoiding double-serialisation,
  vectorisation (Vector API incubator — use cautiously), elastic scaling on
  Kubernetes/batch, caching of market data snapshots, bitemporal inputs so any run
  can be reproduced, checkpoint/restart for partial failure.
- Target example: "batch completes within SLA on 99% of nights including
  top-decile volatility days; compute cost per run down 25%; any historic run
  reproducible bit-for-bit from stored inputs."

**C. Data lineage and reproducibility for regulated clients (BCBS 239 / DORA)**
- Problem shape: clients' auditors ask "where did this number come from" and it
  takes days.
- Levers: bitemporal storage, immutable input snapshots, lineage IDs propagated
  through calc, OpenLineage events.

### Execution plan for the chosen initiative

| Month | Activities | Output |
|---|---|---|
| Month 4 | Problem statement with baseline; 2–3 options with trade-offs; spike/prototype on the riskiest assumption; JMH or load-test evidence | Initiative ADR approved; sponsor named; team assigned |
| Month 5 | Build in production-shadow mode (dual-run, compare outputs); weekly metric update; risk log | Shadow results showing target is achievable |
| Month 6 | Controlled rollout (one client tier / one asset class first); runbooks; hand ownership to team | Metric moved in production; team owns it; you present outcome to leadership |

### Month 6 review — prepare this pack

1. Baselines vs now (every metric from Week 3).
2. Wins delivered, with named team contributors.
3. Standards adoption: % services on target JDK, on golden path, with SBOM.
4. Initiative outcome vs target.
5. Next 6 months proposal — now you have the credibility to propose bigger
   structural change (this is when a re-platforming proposal, if warranted, lands).

**Exit criteria for Phase 4:** a headline metric moved in production and your
manager can describe your impact in one sentence without your help.

---

## Weekly personal rhythm (all phases)

| Day | Habit |
|---|---|
| Monday | Review week's goals against phase exit criteria |
| Tuesday–Thursday | At least 1 hour hands-on: reading code, reviewing PRs, profiling, prototyping. A Java principal who stops reading code loses the room in 6 months |
| Wednesday | 30-min sync with the SA (standing) |
| Friday | Write a 5-bullet weekly note to your manager: done, learned, next, blockers, risk |
