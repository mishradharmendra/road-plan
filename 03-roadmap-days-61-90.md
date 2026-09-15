# 03 — Roadmap: Days 61–90 — Target Architecture and Operating Model

**Theme:** Publish a target architecture and roadmap that is already boring — because everyone
has seen it before the meeting.

**Hard rule for this phase:** surprise in a large forum is how architects get vetoed.
Pre-brief every stakeholder one-on-one and change the document based on what they say.

---

## A. Questions to ask

### A1. Pre-socialization 1:1s (every principal, every eng lead, risk, compliance, finance)

| # | Question | What answer you actually want |
|---|---|---|
| 1 | What in this target state is wrong or naive? | Real objections, in private, where they are cheap to fix. |
| 2 | What have I missed that will embarrass me in the forum? | Direct request for protection — people usually give it. |
| 3 | Which horizon-1 item do you disagree with? | Lets you drop or re-sequence before public commitment. |
| 4 | What would you need to see to support this publicly? | Converts a neutral into an advocate, with a price named. |
| 5 | Whose objection matters most here? | Routes you to the one person who can kill it. |
| 6 | Can I cite you as a contributor? | Shared ownership before launch. |

### A2. Roadmap sequencing questions (leadership and finance)

| # | Question | What answer you actually want |
|---|---|---|
| 7 | Which regulatory deadline constrains sequencing? | Immovable anchors, so the roadmap is date-real. |
| 8 | What funding cycle must this hit? | Determines when the doc must be final, not when it's ready. |
| 9 | What can I stop doing to fund this? | Forces trade-off conversation rather than additive wishlisting. |
| 10 | If I deliver only one thing in 12 months, which one? | The true priority. Ask everyone; compare answers. |
| 11 | What headcount/vendor spend is realistically available? | Prevents a fantasy roadmap. |
| 12 | How will this be measured at the exec level? | Aligns your scorecard with theirs (see file 05). |

### A3. Golden path / paved road design questions (engineering community)

| # | Question | What answer you actually want |
|---|---|---|
| 13 | What would make you use a shared service template voluntarily? | The adoption condition. Build to it. |
| 14 | What does the template need to *not* do? | Over-opinionated templates die. |
| 15 | Which library set do you already trust? | Standardize on existing convergence, don't invent. |
| 16 | What is the first thing you'd have to fight to adopt this? | Migration friction, identified before rollout. |
| 17 | What would you need on day one of an incident from observability? | Designs the telemetry baseline from the consumer backwards. |

### A4. Architecture forum design questions

| # | Question | What answer you actually want |
|---|---|---|
| 18 | What was wrong with previous governance forums here? | Every firm has a failed one. Do not rebuild it. |
| 19 | What review would you happily route around? | Tells you exactly which tier to make lighter. |
| 20 | Who besides the principals should have a vote? | Legitimacy beyond the principal trio. |
| 21 | How fast must a decision come back to be useful? | Sets your SLA for decisions — publish and honour it. |

---

## B. Actions / TODO

- [ ] Finalize **Target Architecture** with three horizons:
  - **Horizon 1 (0–6 mo): Stabilize** — batch reliability, observability, cost, critical CVEs, recon breaks
  - **Horizon 2 (6–12 mo): Consolidate** — platform convergence, golden path adoption, data/lineage, streaming backbone
  - **Horizon 3 (12–18 mo): Differentiate** — near-real-time risk, self-service scenario analysis, AI-assisted surveillance
- [ ] Tie **every** roadmap item to a business outcome: cutoff time, regulatory deadline, cost, incident rate. Never "modernization."
- [ ] Pre-brief every principal, eng lead, and key stakeholder **individually** before any group presentation
- [ ] Revise the doc visibly after pre-briefs; show a changelog crediting who changed what
- [ ] Present to the division — it should feel like a formality
- [ ] Stand up the **Architecture Review Forum**: fortnightly, 45 min, 2 topics, mandatory pre-read, decisions as ADRs, rotating presenters
- [ ] Publish the **tiered decision-rights model** (Tier 1/2/3 from file 00)
- [ ] Publish the **Golden Path v1**: service template, observability baseline, standard build/deploy, approved library set
- [ ] Ensure the golden path is genuinely easier than the alternative — measure time-to-first-deploy for a new service
- [ ] Complete the offshore trip (if not already done) — 80% 1:1s and whiteboards, 20% formal presentation
- [ ] Take one on-call rotation, or be on the bridge for a real incident
- [ ] Close out or hand over the first win with a published before/after number
- [ ] Publish the **tech-debt register with cost attached**

---

## C. Metrics to capture

### C1. Establish the SLO baseline dashboard (leadership-visible)

| Domain | Metric | Baseline | 6-mo target |
|---|---|---|---|
| Batch | Risk batch completion time (p50/p95) | day-30 value | −40% or to cutoff −60 min |
| Batch | Cutoff SLO breaches / month | day-30 value | ≤ 1 |
| Data | Feed freshness lag, critical feeds | day-30 value | within stated SLO 99% of days |
| Data | Reconciliation breaks: count + aging | day-30 value | −50% count, zero >5 days old |
| Serving | p99 latency, top 5 risk APIs | day-30 value | within published SLO |
| Reliability | Sev1/Sev2 per quarter | day-30 value | −30% |
| Reliability | Repeat-root-cause % | day-30 value | < 15% |
| Reliability | MTTR p50/p90 | day-30 value | −30% |
| Delivery | Deploy frequency | day-30 value | +50% |
| Delivery | Change failure rate | day-30 value | < 15% |
| Delivery | Lead time commit→prod | day-30 value | −40% |
| Delivery | CI duration p95 | day-30 value | < 15 min |
| Cost | Cloud cost per risk run | day-30 value | −25% |
| Security | Critical/high CVEs open + age | day-30 value | zero critical > 30 days |
| Standards | Golden path adoption % of services | 0% | 30% by 6 mo |
| Standards | JDK/framework version skew | day-30 value | ≤ 2 supported JDKs |

### C2. Architecture practice metrics

| Metric | Day-90 target |
|---|---|
| ADRs published (cumulative) | ≥ 12 |
| % ADRs authored by non-you | ≥ 40% |
| Decision cycle time p90 | ≤ 10 working days |
| Major initiatives reviewed **before** build started | ≥ 80% |
| Forum attendance and pre-read completion | ≥ 80% |
| Tier-3 decisions escalated to you unnecessarily | trending to zero |
| Rework attributable to late architecture change | baselined |

### C3. First-win closeout metric

Publish a single before/after line, in business language:
> "EOD risk batch: 5h50m → 2h10m. Trader cutoff now met with 90 minutes of buffer.
> Delivered by [team names]. Cloud cost for the run down 31%."

### C4. Anti-metrics

| Anti-metric | Meaning |
|---|---|
| Forum agenda filled only by you | No shared ownership |
| Roadmap items with no business outcome attached | Will be defunded at the first budget squeeze |
| Golden path adoption at 0% after 60 days of availability | The paved road is harder than the dirt track |
| Any ADR open > 15 days | Your process is slower than shipping around it |

---

## D. Outcomes to produce (Day 90 deliverables)

| # | Artifact | Definition of done |
|---|---|---|
| 1 | **Target Architecture (current → target, 1 diagram + narrative)** | Every component mapped to an owner and a horizon. |
| 2 | **12–18 month roadmap, 3 horizons** | Every item has: business outcome, metric, owner, rough cost, dependency. |
| 3 | **Pre-socialization record** | Evidence of 1:1s with every key stakeholder, plus a changelog of what changed because of them. |
| 4 | **Architecture Review Forum, operating** | Charter, cadence, membership (incl. non-principals), pre-read rule, ADR output, published decision SLA. |
| 5 | **Published decision-rights tiers** | Tier 1/2/3 announced by your manager, not only by you. |
| 6 | **Golden Path v1** | Service template repo, observability baseline, build/deploy standard, approved library set, and a measured time-to-first-deploy. |
| 7 | **SLO baseline dashboard** | Live, leadership-visible, owned, with named metric owners. |
| 8 | **Tech-debt register with cost** | Each item: risk, business impact, estimated cost to fix, cost of not fixing. |
| 9 | **First win, closed and published** | Before/after number, credited to the delivering team. |
| 10 | **Offshore trip completed** | Trip report: relationships formed, decisions unblocked, follow-ups owned. |

**Phase exit test:** In the roadmap presentation, does anyone learn something for the first time?
If yes, your pre-socialization failed. The goal is a room full of people who already agree.
