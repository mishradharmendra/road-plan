# 06 — Stakeholder and Politics Playbook

Surviving the first-few-months hustle in a large division that already has a Principal AI,
a Principal Web Engineer, and many solution engineers.

**Core premise:** peer principals are simultaneously the biggest risk to your success and your
biggest asset. Territory is decided in the first 60 days, by default if not by design.

---

## 1. Peer principals (Principal AI, Principal Web Engineer)

### 1.1 Week-one de-escalation
They are watching for one thing: are you a land-grabber. Say out loud, early, in writing:

> "My scope is the JVM platform and the risk compute, data, and serving backbone.
> I will bring things *to* you, not *around* you."

### 1.2 Questions to ask them (and the answer you want)

| Question | Answer you want |
|---|---|
| Where do we currently step on each other? | Named grey zones in their words |
| Where do you wish the line were clearer? | Their preferred boundary — usually cheap to grant |
| What do you need from the Java platform that you don't get today? | A concrete gift to deliver in month 2 |
| What has a previous architect done here that annoyed you? | The behaviour to avoid, given for free |
| How do you want to be involved in decisions I own? | Protocol agreed before the first conflict |
| For inference serving, who gets paged at 2am? | The single most consequential AI/platform boundary |
| BFF or direct service access, and who versions the contract? | Prevents a year of API friction with web |

### 1.3 The grey zones that cause real conflict

| Grey zone | Typical failure if unresolved |
|---|---|
| Feature/embedding pipeline runtime | AI owns semantics, nobody owns uptime |
| Model inference serving SLAs | Platform is paged for model latency it cannot fix |
| Model rollback vs service rollback | Conflicting deployment authority during an incident |
| BFF layer ownership | Web builds a shadow backend; contracts fragment |
| API gateway, auth, session | Two auth models, one audit finding |
| Data schema governance | Three teams each "own" the risk data model |
| Shared infra cost allocation | Finance attributes everything to your platform |

### 1.4 Rules of engagement
- **Never surprise a peer in a meeting.** Raise concerns 1:1 first, every single time.
- Co-author anything that crosses a boundary; joint authorship beats negotiation.
- Escalate to the shared leader jointly, framed as "we need a tie-break," never as a complaint.
- Review the boundary contract quarterly — reality drifts.

### 1.5 Output artifact
`Principal Boundary Contract` — one page, grey zones named explicitly, three signatures,
ratified by the shared leader, published. **Deadline: day 60.**

---

## 2. Solution engineers and senior/lead engineers

### 2.1 The dynamic to expect
Many will read a new Principal as a threat to their autonomy or a blocker on their promotion path.
Some of them have been doing informal architecture for years and were possibly passed over for
your role. Assume this is true of at least two people and behave accordingly.

### 2.2 Counter-moves that actually work
- **Sponsor, don't supervise.** Hand named architecture ownership to 2–3 of them:
  the service template, the observability standard, the API contract standard.
- Put their name first on co-authored documents.
- Make them presenters at the architecture forum, not the audience.
- Give them the visible outcome of the first win.
- Define an architecture competency ladder so your standards work *helps* their promotion case.

### 2.3 The unofficial architects
Every large division has 2–3 senior engineers whose opinion everyone quietly checks before
committing. Identify them from the "who should I talk to that I haven't?" question.

> If they are bought in, adoption is free. If they are not, your standards die silently in code review.

Make them co-authors, not reviewers.

---

## 3. Your manager and executive sponsor

### 3.1 Questions to ask in week one

| Question | Answer you want |
|---|---|
| What does success look like at 6 and 12 months? | Written, confirmable definition |
| What one fix would make this hire obviously worth it? | Sanctioned first-win target |
| What are my decision rights, and who announces them? | Public announcement by *them*, not you |
| Which relationships must I not damage? | Minefield map |
| What is my budget and travel envelope? | How the role is actually valued |
| Who else wanted this role or this scope? | Names the person most likely to resist you |

### 3.2 The written success contract
Write down their answers, send it back, get confirmation. Review it at month 3 and month 6.
Most principal failures are not competence failures — they are goal-mismatch failures.

### 3.3 Decision rights must be announced by leadership
For a principal who is remote from part of the org, ambiguity in decision rights **always**
resolves against the remote party. Get it in writing, announced division-wide, by your manager.

---

## 4. Risk, compliance, audit, quant stakeholders

These are the most under-courted and highest-leverage stakeholders for a risk architect.

| Move | Payoff |
|---|---|
| Automate one painful piece of audit evidence | Permanent ally in a powerful function |
| Ask "what number do you wait for, and by when?" | Real SLOs, in business language |
| Bring compliance into Tier-1 architecture reviews early | No late vetoes |
| Quantify manual reconciliation hours | A funding case in FTE terms |
| Learn the next regulatory deadline with a tech dependency | An immovable anchor for your roadmap |

Debt with a regulator attached is the easiest funding to obtain in a financial firm. Use it.

---

## 5. Timing rules

| Window | Rule |
|---|---|
| Days 1–30 | Propose nothing structural. Accuracy earns credit; opinions do not. |
| Days 31–60 | Boundaries must be set. After day 60 they get set by accident and cost a year to undo. |
| Days 61–90 | Nothing new in a large forum. Pre-brief everyone individually. |
| Months 4–6 | Give away credit on delivery; take ownership of exactly one hard structural decision. |
| Always | Never surprise a peer. Never say "at my last firm" more than twice. |

---

## 6. Traps and how to avoid them

| Trap | Symptom | Escape |
|---|---|---|
| **Approval gate** | Everything needs your sign-off | Publish Tier 1/2/3 decision rights; publicly decline Tier-3 |
| **Rewrite reflex** | You propose replacing a system in month 2 | Postpone all rewrite talk to day 90+, with cost of inaction attached |
| **Credit hoarding** | Your name on every doc | Name goes last for two quarters |
| **Sacred cow** | You criticise a system built by someone now three levels up | Always ask "what's the history here?" before "why is this like this?" |
| **Ivory tower** | Never seen in an incident, never in the code | Take an on-call rotation; join a real bridge call |
| **Governance theatre** | Heavy forum, low attendance, teams route around it | Light tiers, fast decision SLA, rotating chairs |
| **Modernization framing** | Roadmap items with no business outcome | Every item tied to cutoff, regulation, cost, or incident rate |
| **Goal mismatch** | You deliver beautifully and nobody cares | Written success contract, reconfirmed quarterly |
| **Peer war** | Public disagreement with the Principal AI or Web | 1:1 first, joint escalation only, boundary contract signed |
| **Remote invisibility** | Decisions happen in HQ hours without you | Written decision rights, async-first ADRs, be first in the thread |

---

## 7. The 30-second version

1. Understand the domain more deeply than anyone expects, faster than anyone expects.
2. Set boundaries with peer principals explicitly, in writing, by day 60.
3. Fix one painful thing and let someone else take the bow.
4. Make standards paved roads, not gates.
5. Sponsor the people who could have resisted you.
6. Get your decision rights announced by leadership, not claimed by you.
7. Take no credit for two quarters. Authority is granted by peers, not by title.
