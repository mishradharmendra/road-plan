# 05 — Metrics Scorecard

The full metric catalogue for a Principal Java Architect in Risk Intelligence, with what each
metric proves, how to get it, and when to commit to a target.

**Rule: do not commit to outcome targets before day 90.** In months 1–3 commit only to
*learning and diagnosis deliverables*. Committing to a latency number before you understand the
system is the most common way a new principal loses credibility.

---

## 1. Business / risk-domain metrics (what the division is actually judged on)

| Metric | Definition | Source | Why it matters |
|---|---|---|---|
| Risk batch completion time | Wall clock, p50/p95, per critical run | Scheduler/orchestrator | The headline division SLO |
| Cutoff SLO breach count | Runs missing the trader/regulatory cutoff | Scheduler + incidents | Direct business impact |
| Time-to-risk-number | Trade booked → visible in risk view | Distributed trace / event timestamps | The consumer-facing latency |
| Data freshness lag per critical feed | Now − latest good data timestamp | Pipeline telemetry | Correctness precondition |
| Reconciliation break count and aging | Open breaks, by age bucket | Recon platform | "Wrong number" risk, quantified |
| Restatement count | Published risk numbers later corrected | Ops/finance | The worst-case failure, measured |
| Manual interventions per batch cycle | Human touches to complete a run | Runbooks + ops log | Toil and operational risk |
| Scenario/what-if turnaround | Request → result for an ad-hoc scenario | App telemetry | Differentiation capability |
| Regulatory report on-time rate | Submitted by deadline | Compliance | Existential |
| Open audit findings with tech dependency | Count + age | Audit register | Non-negotiable backlog |

---

## 2. Reliability and operations

| Metric | Target direction | Source |
|---|---|---|
| Sev1 / Sev2 count per quarter | ↓ 30% in 6 mo | Incident tool |
| Repeat-root-cause % | < 15% | Postmortem tagging |
| MTTR p50 / p90 | ↓ 30% | Incident tool |
| MTTD (detect) | ↓ | Monitoring vs incident open time |
| % incidents detected by monitoring vs by a human | > 80% by monitoring | Incident tool |
| Alert noise ratio (alerts : actioned alerts) | ↓ | Alerting platform |
| Failed/retried batch jobs per week | ↓ | Scheduler |
| Cross-region handoff misses | → 0 | Shift handover log |
| DR test success and RTO/RPO achieved | meets stated targets | DR exercise |

---

## 3. Delivery (DORA) — the engineering-velocity core

| Metric | Baseline at day 30 | Month-6 target |
|---|---|---|
| Deploy frequency (per team, per week) | measure | +50% |
| Lead time: commit → production | measure | −40% |
| Change failure rate | measure | < 15% |
| MTTR (service restore) | measure | −30% |
| CI pipeline duration p95 | measure | < 15 min |
| Test flakiness rate | measure | < 2% |
| PR cycle time (open → merge) | measure | < 24h p50 |
| Time-to-first-deploy for a new service (golden path) | measure | < 1 day |
| Environment provisioning time | measure | < 1 hour |

---

## 4. Cost and efficiency

| Metric | Why it is your lever |
|---|---|
| Total division cloud spend, trend | Context |
| **Cost per risk run** | The single most persuasive architecture metric in a risk division |
| Cost per million calculations | Normalizes across changing volumes |
| Idle grid/compute capacity % | Classic large, easy saving |
| Storage cost by tier and data age | Retention policy opportunity |
| Vendor/licence spend vs utilisation | Build-vs-buy evidence |
| Cost attributable to untagged resources | Governance maturity |

---

## 5. Security, compliance, data governance

| Metric | Target |
|---|---|
| Critical / high CVEs open, and max age | Zero critical > 30 days |
| % services with SBOM produced | 100% |
| Secrets in code findings | 0 |
| % data assets with owner + classification | > 90% |
| Lineage coverage for regulatory-reported metrics (BCBS 239) | 100% for reported figures |
| Access reviews completed on time | 100% |
| Cross-border data transfer exceptions | tracked and approved, count ↓ |
| Time to produce audit evidence | ↓ (automate it) |

---

## 6. Standardization and platform adoption

| Metric | Meaning |
|---|---|
| Golden path adoption % of services | Is your paved road real |
| Distinct JDK versions in production | Fragmentation debt |
| Distinct frameworks/patterns for the same job | Complexity tax |
| % services meeting observability baseline | Incident readiness |
| % services with named owner | Orphan risk |
| % APIs with published, versioned contracts | Integration health |
| Deprecated component removal rate | Are you actually decommissioning |

---

## 7. Architecture practice health

| Metric | 90 days | 6 months |
|---|---|---|
| ADRs published (cumulative) | ≥ 12 | ≥ 30 |
| % ADRs authored by someone other than you | ≥ 40% | ≥ 60% |
| Decision cycle time (proposed → decided), p90 | ≤ 10 days | ≤ 7 days |
| Initiatives reviewed **before** build started | ≥ 80% | ≥ 90% |
| Forum pre-read completion rate | ≥ 80% | ≥ 80% |
| Forum sessions chaired by non-you | 0 | ≥ 2 |
| Rework caused by late architecture change | baselined | ↓ |
| Architecture decisions later reversed | baselined | ≤ 1 |

---

## 8. Influence and trust (private — never publish these)

| Metric | Healthy signal |
|---|---|
| Invited-early vs shown-finished ratio | > 70% early by month 6 |
| Unsolicited inbound requests for your input | Growing month over month |
| Voluntary vs mandated golden-path adoptions | Voluntary dominant |
| Peer principals initiating joint work | ≥ 3 instances by month 6 |
| Corrections received on your published docs | High early is **good** |
| People naming you as sponsor/mentor | ≥ 3 by month 6 |
| Cross-region engineers contacting you directly | Growing — proves you're not "the India architect" |

---

## 9. Distributed / cross-region specific metrics

| Metric | Why |
|---|---|
| % decisions recorded in writing within 24h of the meeting | Async discipline |
| % meetings in the fair-rotation slot | Prevents one region always taking the pain |
| Decisions re-litigated because a region was absent | Should trend to zero |
| Time-to-decision for cross-region topics vs single-region | Gap reveals async friction |
| Cross-region handoff quality (incidents where handoff added > 30 min to MTTR) | Follow-the-sun health |
| Offshore/onshore split of ADR authorship | Is architecture genuinely distributed |

---

## 10. Anti-metrics — actively watch for these

| Anti-metric | What it really means |
|---|---|
| Number of approvals you personally give | Higher = you are a bottleneck, not an architect |
| Meetings where you are the only speaker | Broadcasting, not building |
| Documents with only your name | Credit hoarding perception |
| Lines of code you wrote | Wrong job |
| Number of standards published | Vanity; adoption is the metric |
| Roadmap items with no business outcome attached | First to be defunded |
| "Modernization" as a stated goal | Unfundable and unmeasurable |

---

## 11. Reporting cadence

| Cadence | Audience | Content |
|---|---|---|
| Weekly | You (private) | Trust metrics, blockers, decision backlog |
| Fortnightly | Architecture Forum | ADR throughput, decision cycle time, upcoming Tier-1 items |
| Monthly | Engineering leadership | SLO dashboard, DORA, cost per risk run, incident trend |
| Quarterly | Division exec / CTO | Roadmap progress vs business outcomes, structural decisions, tech-debt funded, risk posture |
| Quarterly | Peer principals | Boundary contract review — has reality drifted from the doc |

---

## 12. Target-setting rules

1. No outcome target before you own the baseline and the instrumentation.
2. Every target has a named owner who is **not** you.
3. Every improvement target has a paired guardrail metric (speed ↑ must not push failure rate ↑).
4. Business language in the headline, engineering language in the detail.
5. If a metric has not changed a decision in two quarters, delete it.
