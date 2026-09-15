# 04 — Roadmap: Months 4–6 — Execute and Institutionalize

**Theme:** Deliver horizon-1, land one structural decision with a multi-year shadow, and make the
architecture practice survive your absence.

**Hard rule for this phase:** your name should be *absent* from the credit on delivered work,
and *present* on exactly one hard structural decision nobody else wanted to make.

---

## A. Questions to ask

### A1. Structural decision questions (grid/compute, data platform, streaming backbone, JDK strategy)

| # | Question | What answer you actually want |
|---|---|---|
| 1 | What is the 3-year cost of staying where we are? | Cost-of-inaction number — the only way to fund structural work. |
| 2 | What is the reversal cost if this decision is wrong in 18 months? | Distinguishes a one-way door from a two-way door. |
| 3 | What capability does this unlock that we cannot offer today? | Links infrastructure to business capability. |
| 4 | Who has tried this at comparable scale in this firm? | Internal precedent beats vendor references. |
| 5 | What is the migration path for the 5 largest existing workloads? | Migration realism check — kills most attractive-looking options. |
| 6 | What do we sunset as a result? | A decision with no decommissioning is additive complexity. |
| 7 | Which regulator or auditor cares about this? | Compliance blast radius. |
| 8 | What does this do to cost per risk run? | Your headline efficiency metric. |

### A2. Delivery health questions (recurring, with each horizon-1 team)

| # | Question | What answer you actually want |
|---|---|---|
| 9 | What is the actual blocker this week? | Real impediments you can remove with your seniority. |
| 10 | What did we assume in the roadmap that turned out false? | Roadmap correction signal — collect it honestly, republish. |
| 11 | Is the golden path helping or taxing you? | Adoption truth, not adoption statistics. |
| 12 | What decision are you waiting on from me? | Your decision-SLA compliance. |

### A3. Institutionalization questions

| # | Question | What answer you actually want |
|---|---|---|
| 13 | If I were unavailable for a month, which decisions would stall? | Your single points of failure. Delegate each one. |
| 14 | Who is ready to run the forum? | Succession — a practice with one owner is not a practice. |
| 15 | Which standard is being followed only because I'm watching? | Standards needing enforcement are badly designed; redesign them. |
| 16 | What have we learned that should change the roadmap? | Forces a real 6-month roadmap revision rather than a stale doc. |

### A4. Cross-region guild questions

| # | Question | What answer you actually want |
|---|---|---|
| 17 | What decisions were made in a room you weren't in? | Async-practice failures. Fix the process, not the people. |
| 18 | Which meetings are consistently at a bad hour for your region? | Rotation fairness audit. |
| 19 | What context do you routinely lack? | Documentation and broadcast gaps. |
| 20 | What would make you feel like a peer rather than a downstream team? | Direct fix list for the distributed-trust problem. |

---

## B. Actions / TODO

- [ ] Deliver horizon-1 items with real teams; publish outcomes with **their** names
- [ ] Land **one structural decision** — grid/compute strategy, data platform convergence, streaming backbone, or JDK/framework strategy
- [ ] Produce a full options analysis for that decision: 3 options, cost, risk, migration path, reversal cost, sunset plan
- [ ] Run the **cross-region architecture guild** monthly (see file 07)
- [ ] Publish the **NFR/SLO contract** per critical risk pipeline, with named owners
- [ ] Get the SLO dashboard reviewed in a recurring leadership meeting
- [ ] Fund at least one tech-debt item using the cost-attached register
- [ ] Run a **roadmap revision** at month 6 based on what was learned — publish the changes and why
- [ ] Hand the Architecture Forum chair to a rotating owner for at least one session
- [ ] Delegate at least 3 decision types permanently downward (document them as Tier 3)
- [ ] Complete second offshore trip or host offshore peers in India
- [ ] Run a hiring-bar calibration session; define the senior/staff architecture competency
- [ ] Write the 6-month self-assessment against the written success contract from day 30

---

## C. Metrics to capture

### C1. Outcome metrics — now you commit to targets

| Metric | Day-90 value | Month-6 target | Owner |
|---|---|---|---|
| Risk batch completion p95 | | −40% vs day 0 | Platform lead |
| Cutoff SLO breaches / month | | ≤ 1 | Ops |
| Reconciliation breaks (count, aging) | | −50%, none > 5 days | Data lead |
| Sev1/Sev2 per quarter | | −30% | SRE |
| Repeat-root-cause % | | < 15% | SRE |
| MTTR p90 | | −30% | SRE |
| Change failure rate | | < 15% | Delivery |
| Lead time commit→prod | | −40% | Delivery |
| CI p95 duration | | < 15 min | Platform |
| Cloud cost per risk run | | −25% | Platform + Finance |
| Golden path adoption | | ≥ 30% of services | Sponsored SE |
| Critical CVE age | | none > 30 days | Security champion |
| JDK versions in prod | | ≤ 2 | Platform |
| Services with named owner | | 100% | Eng managers |

### C2. Practice-maturity metrics

| Metric | Month-6 target |
|---|---|
| Cumulative ADRs | ≥ 30 |
| % ADRs authored by non-you | ≥ 60% |
| Decision cycle time p90 | ≤ 7 working days |
| Forum sessions chaired by non-you | ≥ 2 |
| Initiatives with pre-build architecture review | ≥ 90% |
| Tech-debt items funded from the register | ≥ 2 |
| Architecture decisions reversed due to late discovery | ≤ 1 |

### C3. Influence metrics (private but tracked)

| Metric | Month-6 signal of health |
|---|---|
| Invited-early vs shown-finished ratio | > 70% early |
| Voluntary golden-path adoptions | > mandated adoptions |
| Peer principals initiating joint work with you | ≥ 3 instances |
| People who cite you as a sponsor/mentor | ≥ 3 |
| Cross-region engineers who contact you directly | growing |

### C4. Anti-metrics and stall signals

| Signal | Interpretation | Response |
|---|---|---|
| You authored > 60% of ADRs | Practice is you, not a practice | Force rotation, coach authors |
| Roadmap unchanged after 6 months | Not learning, or not executing | Public revision with rationale |
| Golden path adoption flat | Paved road is harder than dirt | Re-scope template; interview non-adopters |
| Forum agenda thin | Teams route around you | Reduce tiers, speed decisions |
| Every offshore decision made in HQ hours | Async model failing | Escalate; enforce rotation |
| You are on every escalation | Delegation failed | Publish Tier-3 list again, publicly decline |

---

## D. Outcomes to produce (Month-6 deliverables)

| # | Artifact | Definition of done |
|---|---|---|
| 1 | **Horizon-1 delivered** | Named items shipped, before/after metrics published, delivering teams credited. |
| 2 | **One structural decision, decided and documented** | Full options analysis, ADR, funding, migration plan, sunset plan, exec endorsement. |
| 3 | **NFR/SLO contracts per critical pipeline** | Published, owned, alerting wired, reviewed in a leadership forum. |
| 4 | **Leadership-visible SLO dashboard in active use** | Referenced in a recurring management meeting, not just existing. |
| 5 | **Tech-debt register driving funding** | ≥ 2 items funded because of the attached cost case. |
| 6 | **Revised roadmap (v2)** | Changes from v1 explicit, with reasons, published. |
| 7 | **Cross-region architecture guild, operating** | Monthly, rotating chair and time slot, written minutes, decisions as ADRs. |
| 8 | **Distributed architecture practice** | 60% of ADRs by others, forum chaired by others, Tier-3 decisions delegated and documented. |
| 9 | **Talent artifacts** | Architecture competency definition, hiring bar calibration done, 3 sponsored engineers with named scope. |
| 10 | **6-month self-assessment** | Written against the day-30 success contract, shared with your manager before they ask. |

**Phase exit test:** Could you take four weeks off without stalling any decision? If not, name
every stalled decision and delegate it in month 7. That list is the definition of your remaining work.
