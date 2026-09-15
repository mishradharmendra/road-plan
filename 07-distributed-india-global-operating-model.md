# 07 — Distributed Operating Model: India-Based Principal, Globally Distributed Division

Being based in India while part of the division sits outside India changes the job
**mechanically**, not just socially. Treat it as an architecture problem with constraints.

---

## 1. Time zone strategy

### 1.1 Establish the overlap map (week 1)

| Corridor | Natural overlap with IST | Practical decision window |
|---|---|---|
| India ↔ London (GMT/BST) | ~4–5 hours | 14:00–18:30 IST |
| India ↔ US East | ~2–2.5 hours | 18:30–21:00 IST (07:00–09:30 ET) |
| India ↔ US West | ~1–1.5 hours | 20:30–22:00 IST |
| India ↔ Singapore / HK | ~6 hours | 09:00–17:00 IST, easy |
| India ↔ Sydney | ~4 hours | 06:00–11:00 IST |

### 1.2 Rules
- **Protect the overlap window for decisions and relationships only.** Status goes async, always.
  Burning your only 2 hours of US overlap on a status call is the classic failure.
- **Rotate the pain visibly.** If every call is 21:00 IST and never 07:00 ET, resentment builds
  and you lose your local team. Alternate, and *say out loud* that you are alternating.
- Publish a "core collaboration hours" block per corridor and defend it in your calendar.
- Keep one no-meeting block in IST morning for deep architecture work — otherwise you become
  a full-time meeting attendee with no output.

---

## 2. Async-first architecture practice (non-negotiable for a distributed principal)

Verbal decisions made in a single-region room **will** be re-litigated forever.

| Practice | Rule |
|---|---|
| ADRs | Markdown in the repo. Fixed comment window (5 working days). Silence = consent. |
| Meeting output | Written decision summary within 24 hours, every time, no exceptions. |
| Recording | Record architecture sessions; post recording + written summary together. |
| Single source of truth | One canonical architecture location. Never slides in an inbox. |
| Be first in the thread | Post your position *with rationale* early. In async, first well-reasoned position anchors the outcome. |
| Pre-reads | Mandatory for the forum; the meeting is for disagreement, not for reading. |
| Decision SLA | Publish it (e.g. Tier 2 decided within 7 working days) and honour it. |

> **Metric:** % of decisions recorded in writing within 24h. Target 100%. Also track
> "decisions re-litigated because a region was absent" — target zero.

---

## 3. The "offshore architect" credibility problem

There is a real, rarely-stated dynamic where an India-based architect over a partly US/UK-based
org gets treated as a **delivery lead** rather than a **decision-maker**. Name it and beat it
deliberately.

| Counter-move | Detail |
|---|---|
| **Written, announced decision rights** | Your manager announces your scope division-wide. Ambiguity resolves against the remote party. |
| **Be the deepest domain expert** | Expertise travels across time zones; physical presence does not. |
| **Have opinions early, in writing** | Never be the person who only relays. Anchor the async thread. |
| **Own production reality** | Know the incidents, the runbooks, the cost lines better than anyone at HQ. |
| **Chair the forum yourself initially** | Then rotate — but establish that the chair sits in India. |
| **Never accept "we already decided that on a call"** | Politely require the ADR. Once enforced twice, the behaviour stops. |
| **Build direct relationships with 3–5 HQ engineers** | Bypasses the "offshore team" abstraction. |

### Questions to ask offshore colleagues (month 4+ guild)

| Question | Answer you want |
|---|---|
| What decisions were made in a room I wasn't in? | Async-process failures — fix process, not people |
| Which meetings are consistently at a bad hour for your region? | Rotation fairness audit |
| What context do you routinely lack? | Documentation and broadcast gaps |
| What would make you feel like a peer rather than a downstream team? | A direct, actionable fix list |

---

## 4. Travel

| Item | Guidance |
|---|---|
| First trip | Within the first 90 days, to the main non-India hub |
| Year-one cadence | 2–3 trips |
| Trip composition | 80% one-on-ones and whiteboard sessions, 20% formal presentation |
| Priority targets | Peer principals, the skeptics, the unofficial architects, your exec sponsor |
| Social time | Dinners matter more than demos; book them deliberately |
| Output | Trip report: relationships formed, decisions unblocked, follow-ups owned |

> Two weeks of in-person time buys more trust than six months of video calls.
> If travel is not approved, that is meaningful information about how the role is valued — raise it early and explicitly.

---

## 5. Cross-region data and regulatory constraints

This is a genuine architecture constraint in financial risk, not a checkbox. Resolve it in month 1.

| Question | Why it constrains architecture |
|---|---|
| What data may not leave which jurisdiction? | Determines where compute and storage can physically sit |
| What can India-based engineers see of client data? | Determines support model, debugging access, test data strategy |
| How is MNPI segregated, and does that cross regions? | Information barriers become network and entitlement design |
| Which regulators apply: RBI, SEBI, GDPR, SEC, FCA, MAS? | Each adds retention, residency, and reporting obligations |
| What is the approved cross-border transfer mechanism? | Gates any centralized data platform design |
| Can production access be granted from India, and under what controls? | Directly shapes follow-the-sun operations |
| Where must audit evidence be stored? | Constrains logging and archival architecture |

**Output artifact:** a `Data Residency and Access Constraint Register` — this constrains your
target architecture more than any technology choice will.

---

## 6. Follow-the-sun operations

If overnight risk batches run in one region while support sits in another, **handoff quality is
an MTTR driver** and therefore your architecture problem.

| Action | Detail |
|---|---|
| Formalize handoff runbooks | Structured template: in-flight issues, known risks, decisions pending, who to call |
| Instrument the handoff | Track incidents where handoff added > 30 min to MTTR |
| Design for regional autonomy | Each region must be able to resolve a defined incident class alone |
| Avoid single-region tribal knowledge | Any system where only one region can debug it is an architecture defect |
| Rotate the unpleasant shift | Same fairness principle as meetings |

---

## 7. Cross-region architecture guild (start month 4)

| Element | Design |
|---|---|
| Cadence | Monthly, 60 min |
| Time slot | **Rotating** across corridors, published a quarter ahead |
| Chair | Rotating, explicitly including non-India chairs and India chairs |
| Agenda | 1 architecture topic + 1 incident learning + open floor |
| Output | Written minutes + ADRs within 24h |
| Membership | Principals, eng leads, and 2–3 senior engineers per region |
| Purpose | Make architecture decisions genuinely multi-regional, and make offshore engineers authors rather than recipients |

---

## 8. Distributed-model metrics

| Metric | Target |
|---|---|
| % decisions written up within 24h | 100% |
| % meetings in fair-rotation slot | ≥ 80% |
| Decisions re-litigated due to absent region | 0 |
| Time-to-decision: cross-region vs single-region | Gap < 3 days |
| ADR authorship split by region | Roughly proportional to engineering headcount |
| Incidents where handoff added > 30 min to MTTR | Trending to 0 |
| Cross-region engineers contacting you directly | Growing month over month |
| Your meeting load in unsocial hours per week | Capped and monitored — burnout is a real failure mode here |

---

## 9. Sustainability

A distributed principal role in financial services silently expands to 12-hour days:
India-morning deep work, India-afternoon London, India-evening US, then the overnight batch pages.

- Cap unsocial-hour meetings per week and track it as a metric
- Refuse status meetings in overlap windows without exception
- Delegate a named deputy for the US overlap window by month 6
- Take the on-call rotation once for credibility — not permanently
- If you burn out at month 8, none of the rest of this plan matters
