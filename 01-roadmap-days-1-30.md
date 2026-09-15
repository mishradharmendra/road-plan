# 01 — Roadmap: Days 1–30 — Learn the Terrain

**Theme:** Become the person who understands how money and risk actually flow, faster than anyone expects.

**Hard rule for this phase:** propose nothing structural. You get enormous credit for accuracy
and zero credit for premature opinions.

---

## A. Questions to ask

### A1. Engineers, tech leads, solution engineers (target ~25 people, 30 min each)

| # | Question | What answer you actually want |
|---|---|---|
| 1 | Walk me through what happens between a trade booking and a risk number on a trader's screen. | Their *mental model* and where it goes vague — the vagueness marks an ownership gap. |
| 2 | What breaks most often? | A short list of repeat offenders. If 5+ people name the same system, that is your first-win candidate. |
| 3 | What takes longest that shouldn't? | Cycle-time pain: builds, environments, data refresh, approvals. |
| 4 | What decision is currently stuck waiting on someone? | Your fastest, cheapest early value: unblock a stalled decision in week 2. |
| 5 | If you had one architecture wish granted, what is it? | Ranked latent demand. Cluster the answers. |
| 6 | What did we try before that failed, and why? | Prevents you from re-proposing a dead initiative. Highest-signal question in the set. |
| 7 | Which system is nobody willing to touch? | The true core risk. Usually undocumented and owned by one person. |
| 8 | Who should I talk to that I haven't? | Builds the influence graph. Repeated names = real decision-makers. |
| 9 | What would make your job worse if I changed it? | Surfaces sacred cows before you step on one. |
| 10 | How do you find out you broke something? | Observability maturity in one answer. |

### A2. Risk managers, quants, front-office consumers (target ~8)

| # | Question | What answer you actually want |
|---|---|---|
| 11 | What number are you waiting for, and by when? | The real SLOs. Usually differs from the documented ones. |
| 12 | When the number is late or wrong, what do you do? | Manual workaround inventory = hidden operational risk. |
| 13 | Which risk measure do you distrust, and why? | Data-quality hot spots, prioritized by business pain. |
| 14 | What analysis do you want but cannot get today? | Roadmap horizon-3 material and your differentiation story. |
| 15 | How much of your day is spent reconciling numbers by hand? | Quantifies a business case in hours/FTE. |

### A3. Compliance, internal audit, model risk, regulatory reporting (target ~5)

| # | Question | What answer you actually want |
|---|---|---|
| 16 | What are the open audit findings against this division? | Non-negotiable roadmap items with dates. |
| 17 | What is our next regulatory deadline that has technology dependency? | An immovable date to anchor the roadmap. |
| 18 | Where is our lineage story weakest (BCBS 239)? | Architecture debt with a regulator attached — the easiest funding to obtain. |
| 19 | What evidence do you need at audit time that is painful to produce today? | Automatable evidence = quick credibility with a powerful stakeholder. |
| 20 | What data must not leave which jurisdiction? | Hard constraint on target architecture (see file 07). |

### A4. Peer principals — Principal AI and Principal Web (week 1, individually)

| # | Question | What answer you actually want |
|---|---|---|
| 21 | Where do we currently step on each other? | Named grey zones, in their words. |
| 22 | Where do you wish the line were clearer? | Their preferred boundary — usually reasonable and cheap to grant. |
| 23 | What do you need from the Java platform that you don't get? | A concrete gift you can deliver in month 2. |
| 24 | What has a previous architect done here that annoyed you? | The behaviour to avoid, stated for free. |
| 25 | How do you want to be involved in decisions I own? | Sets the collaboration protocol before the first conflict. |

> Follow up in writing within 48 hours with a summary of what you heard, sent to them for
> correction. That single document positions you as a collaborator rather than a competitor.

### A5. Your manager / CTO / division head

| # | Question | What answer you actually want |
|---|---|---|
| 26 | What does success look like for me at 6 and 12 months? | Written, confirmed success definition. Most principals fail by optimizing for a goal nobody had. |
| 27 | What is the one thing that, if fixed, makes this hire obviously worth it? | Your first-win target, sanctioned from above. |
| 28 | What are my decision rights, and who announces them? | Critical for a remote-from-HQ principal. Ambiguity resolves against the remote party. |
| 29 | Which relationships must I not damage? | Political minefield map. |
| 30 | What is the budget and travel envelope for this role? | Tells you how the role is actually valued. |

### A6. Ops / SRE / production support

| # | Question | What answer you actually want |
|---|---|---|
| 31 | Show me the last 5 Sev1/Sev2 postmortems. | Ground truth on architecture weakness. |
| 32 | What is the most common manual intervention during the batch cycle? | Automation candidates with immediate ROI. |
| 33 | How does handoff work between regions at end of shift? | Follow-the-sun quality — usually a hidden MTTR driver. |
| 34 | What alert do you routinely ignore? | Alert fatigue = observability redesign scope. |

---

## B. Actions / TODO

- [ ] Complete 40–50 listening interviews across all six audiences above
- [ ] Build the **influence graph** — who is actually consulted, separate from the org chart
- [ ] Read every Sev1/Sev2 postmortem from the last 12 months
- [ ] Read all open audit findings and regulatory commitments
- [ ] Map the **risk value chain** on one page: trade capture → position → market data → model/calc → aggregation → limits/alerts → reporting → consumer
- [ ] Mark on that map: where JVM lives, where AI lives, where the web layer lives, where data lives, where the seams are
- [ ] **Sit through one full overnight/EOD risk cycle end to end** — watch the batch, read the runbook, sit in the support channel
- [ ] Obtain read access to everything: repos, CI, Grafana/Splunk/Datadog, cloud cost console, Jira, Confluence, incident tooling
- [ ] Personally inspect: build times, deploy frequency, incident counts, cloud spend trend, JDK/framework version spread
- [ ] Clone and build the 3 most critical repos yourself; note how long it takes a newcomer
- [ ] Draft (do not publish) the Principal Boundary Contract
- [ ] Confirm your written success definition with your manager

### What NOT to do in days 1–30
- Do not propose a rewrite
- Do not criticise a framework choice in public
- Do not say "at my last firm" more than twice — after that it permanently costs you
- Do not accept a standing approval-gate role
- Do not commit to any outcome metric

---

## C. Metrics to capture (baseline only — no targets yet)

These are **baselines**, recorded for later comparison. Record the number and the date observed.

| Metric | Where to get it | Why it matters |
|---|---|---|
| Risk batch wall-clock time (p50/p95) | Scheduler / orchestration logs | The headline SLO of the division |
| Batch cutoff breach count, last 90 days | Incident + scheduler records | Business pain, quantified |
| Sev1 / Sev2 count, last 12 months | Incident tooling | Stability baseline |
| % incidents with repeat root cause | Postmortem review | Measures whether learning happens |
| MTTR (p50/p90) | Incident tooling | Operational maturity |
| Deploy frequency per team | CI/CD | DORA baseline |
| Change failure rate | CI/CD + incidents | DORA baseline |
| Lead time: commit → prod | CI/CD | DORA baseline |
| CI build duration (p50/p95) | CI | Direct developer tax |
| Test flakiness rate | CI | Trust in the pipeline |
| Cloud cost: total, and per risk run | Cost console | Your strongest funding lever |
| Reconciliation break count + aging | Ops dashboards / manual | Data correctness baseline |
| Data freshness lag per critical feed | Pipeline telemetry | Correctness + SLO baseline |
| p99 latency, top 5 risk APIs | APM | Serving layer baseline |
| Count of distinct JDK versions in prod | SBOM / build scan | Standardization debt |
| Count of distinct frameworks/patterns | Repo scan | Fragmentation baseline |
| Critical + high CVEs open, and age | Security scanner | Regulatory exposure |
| Open audit findings with tech dependency | Audit register | Immovable roadmap items |
| Number of services with no named owner | CMDB / repo metadata | Orphan risk |
| Manual interventions per batch cycle | Ops interview + runbooks | Toil baseline |

**Private trust metrics (track in your own notes, never publish):**
- Interviews completed / target
- Distinct people who have proactively contacted you
- Number of design discussions you were invited to *before* the design was done
- Number of times a peer principal referenced your input

---

## D. Outcomes to produce (Day 30 deliverables)

| # | Artifact | Definition of done |
|---|---|---|
| 1 | **Risk Value Chain Map** (1 page) | End-to-end flow with system names, ownership, and seams marked. Reviewed by 3 engineers for accuracy. |
| 2 | **"What I've Learned So Far" memo** | 8–10 observations, explicitly labelled as *hypotheses*, circulated division-wide for correction. **No recommendations.** |
| 3 | **Influence graph** (private) | Named list of the 10–15 people whose opinion actually moves decisions. |
| 4 | **Baseline metrics sheet** | Every metric in section C populated with a number and a date. |
| 5 | **Written success contract** | Your manager's 6- and 12-month success definition, confirmed in writing by them. |
| 6 | **Peer principal summary notes** | One doc per peer, sent to them for correction, on boundaries and grey zones. |
| 7 | **Constraint register** | Regulatory deadlines, audit findings, data residency rules, sacred cows. |
| 8 | **First-win shortlist** | 3 candidate problems, scored on: pain breadth, fixability in 4–8 weeks, measurability, no reorg needed. |

**Phase exit test:** Can you explain the end-to-end risk flow, including its three worst failure
modes, to a room of the division's engineers — and have them agree you got it right?
