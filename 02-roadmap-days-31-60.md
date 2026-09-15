# 02 — Roadmap: Days 31–60 — Shared Diagnosis and First Visible Win

**Theme:** Convert observations into a diagnosis the division agrees with, then fix one painful
thing — and let someone else present the win.

**Hard rule for this phase:** every document you publish credits the people who told you.
Your name goes last.

---

## A. Questions to ask

### A1. Deep-dive architecture reviews (2–3 systems that dominate the incident record)

Frame these as *"help me understand"*, never as an audit. Sit with the owning team.

| # | Question | What answer you actually want |
|---|---|---|
| 1 | What was the original constraint that made this design correct at the time? | Prevents you from mistaking a reasonable historical trade-off for incompetence. |
| 2 | What breaks when load doubles? | Concrete scaling cliff, with a number. |
| 3 | What happens if this fails halfway through a batch? | Idempotency/replay reality. Usually the answer is "we rerun manually." |
| 4 | Where is state held, and who else reads it directly? | Hidden coupling — the real blocker to any change. |
| 5 | Which dependency here can we not survive losing? | Single points of failure with business impact. |
| 6 | If you had 6 weeks and no new headcount, what would you fix? | The team's own prioritization — usually better than yours, and free buy-in. |
| 7 | What test would have caught the last incident? | Test strategy gaps with evidence. |
| 8 | What would we need to delete to make this simpler? | Surfaces dead code and unused features nobody dares remove. |

### A2. First-win scoping questions

| # | Question | What answer you actually want |
|---|---|---|
| 9 | If we cut this from 6 hours to 2, who benefits and by how much? | A business-language benefit statement you can quote to leadership. |
| 10 | What is the single biggest contributor to the current duration? | Profile-driven, not opinion-driven, prioritization. |
| 11 | Has anyone attempted this before? What stopped them? | Avoids repeating a known dead end. |
| 12 | Who must approve for this to ship? | Approval path mapped before you start, not after. |
| 13 | How will we prove it worked? | Agreed measurement *before* the work starts. Non-negotiable. |
| 14 | Who on this team wants to present this outcome? | Your credit-transfer plan. |

### A3. Boundary contract ratification — peer principals, together

| # | Question | What answer you actually want |
|---|---|---|
| 15 | Does this one-pager describe reality as you see it? | Correction, not agreement. Agreement too fast means they didn't read it. |
| 16 | Which grey zone will bite us first? | Prioritizes which boundary to make concrete. |
| 17 | For inference serving — who gets paged at 2am? | The single most consequential AI/platform boundary question. |
| 18 | For the web layer — BFF or direct service access, and who versions the contract? | Prevents a year of API friction. |
| 19 | What do we take to our shared leader vs decide ourselves? | Escalation protocol agreed in calm conditions. |
| 20 | Can all three of us sign this? | Ratification. Do it by day 60. |

### A4. Solution engineers — sponsorship conversations

| # | Question | What answer you actually want |
|---|---|---|
| 21 | What architecture scope do you want that you don't have? | Sponsorship opportunities. Sponsored people become advocates. |
| 22 | What is blocking your next level? | Aligns your standards work with their promotion path. |
| 23 | Would you own the service template / observability standard? | Named owners other than you = a real practice. |
| 24 | What standard would you actively resist, and why? | Pre-empts the code-review death of your paved road. |

---

## B. Actions / TODO

- [ ] Publish the **Current-State + Pain Map** using their language, their incidents, their names
- [ ] Run 2–3 joint deep-dive architecture reviews; publish findings **co-authored, their name first**
- [ ] Select the first win against explicit criteria (see below) and start it
- [ ] Agree the measurement of the first win *before* work begins
- [ ] Ratify the **Principal Boundary Contract** with both peer principals and the shared leader
- [ ] Start lightweight **ADR practice**: markdown in repo, 5-day async comment window, silence = consent
- [ ] Write the first 3 ADRs yourself to set the format and quality bar
- [ ] Sponsor 2–3 solution engineers into named architecture ownership
- [ ] Instrument anything from the Day-30 baseline that could not be measured
- [ ] Book the offshore travel for the day 60–90 window
- [ ] Attend at least one production incident bridge end to end

### First-win selection criteria (score each candidate 1–5)

| Criterion | Why |
|---|---|
| Breadth of pain | Many people must feel the relief |
| Fixable in 4–8 weeks | Must land inside the credibility window |
| No reorg required | Organisational change is a year-two move |
| Objectively measurable | You need a number, not a vibe |
| Existing team can own it | You are not the hero |
| Low blast radius if wrong | A failed first win is very expensive |

**Realistic candidates in a risk division:**
- Risk batch takes 6 hours, should take 2 (profile it; usually 1–2 stages dominate)
- CI pipeline at 45 minutes, blocking every team daily
- A flaky reconciliation job generating recurring manual work
- Observability gaps making every incident a 90-minute mystery
- One crushing cloud cost line item (idle grid capacity is the classic)
- Environment provisioning that takes days

---

## C. Metrics to capture

### C1. First-win metrics (define before starting)

| Metric | Baseline | Target | Measurement source |
|---|---|---|---|
| Primary outcome metric (e.g. batch wall-clock) | from Day 30 | agreed with team | Scheduler telemetry |
| Secondary: cost impact | from Day 30 | agreed | Cloud cost console |
| Secondary: manual interventions eliminated | from Day 30 | agreed | Ops runbook count |
| Guardrail: no increase in failure rate | from Day 30 | ≤ baseline | Incidents |
| Guardrail: no regression in output correctness | reconciliation breaks | ≤ baseline | Recon dashboard |

### C2. Architecture practice metrics (start tracking now)

| Metric | Target by day 60 |
|---|---|
| ADRs published | ≥ 5 |
| ADRs authored by someone other than you | ≥ 1 |
| Decision cycle time (proposed → decided) | ≤ 10 working days |
| Deep-dive reviews completed | 2–3 |
| Systems with a named architecture owner | +3 vs baseline |

### C3. Trust metrics (private)

| Metric | Signal |
|---|---|
| Corrections received on your pain map | High is **good** — means people read and engaged |
| Design discussions you were invited to early | Rising = trust forming |
| Peer principals referencing your artifacts | Boundary contract is working |
| Unsolicited inbound requests for your input | The strongest single signal |
| People who volunteered to co-author | Practice is becoming shared |

### C4. Anti-metrics — watch for these going the wrong way

| Anti-metric | What it means |
|---|---|
| Meetings where you are the only speaker | You are broadcasting, not building |
| Docs with only your name | Credit hoarding perception forming |
| Decisions escalated to you that teams could make | You are becoming a bottleneck |
| Teams delaying work "until architecture reviews it" | Your process is now a tax |

---

## D. Outcomes to produce (Day 60 deliverables)

| # | Artifact | Definition of done |
|---|---|---|
| 1 | **Current-State + Pain Map** | Published division-wide. Uses their language, cites their incidents, credits sources. Corrections incorporated and version-2 reissued. |
| 2 | **2–3 Deep-Dive Findings Docs** | Co-authored with owning teams, their name first, with agreed remediation options (not mandates). |
| 3 | **Ratified Principal Boundary Contract** | One page, grey zones named, three principal signatures, shared leader ratification, published. |
| 4 | **First win — in flight and measurably trending** | Baseline recorded, target agreed, mid-point measurement showing movement. |
| 5 | **ADR practice live** | Repo location, template, 5-day window, ≥5 ADRs, ≥1 by another author. |
| 6 | **Sponsorship assignments** | 2–3 named solution engineers own named architecture artifacts, agreed with their managers. |
| 7 | **Instrumentation gap closed** | Every Day-30 metric now has an automated source, or an explicit "cannot measure — here's the plan". |
| 8 | **Draft target architecture** | Not published. Circulated to 5 trusted people for demolition. |

**Phase exit test:** Has at least one person who was not in your interview list quoted your pain
map back to you as if it were their own idea? That is the point at which the diagnosis is shared.
