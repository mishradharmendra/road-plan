# 09 — Interview Question Bank

Every question worth asking in the first 90 days, grouped by audience, with **what answer you are
actually listening for**. Use 8–10 per 30-minute conversation; never run the full list.

**Technique notes**
- Ask about *specific past events*, not opinions: "tell me about the last time X broke" beats "is X reliable".
- Silence after the answer usually produces the real answer.
- Always close with "who should I talk to that I haven't?"
- Send a written summary back within 48 hours for correction. This single habit builds more trust than anything else.

---

## 1. Engineers, tech leads, solution engineers

| Question | Listening for |
|---|---|
| Walk me through trade booking → risk number on a screen. | Their mental model, and where it turns vague — vagueness marks an ownership gap |
| What breaks most often? | Repeat offenders; 5+ mentions = first-win candidate |
| What takes longest that shouldn't? | Cycle-time pain: builds, environments, data refresh, approvals |
| What decision is stuck waiting on someone? | Cheapest early value — unblock it in week 2 |
| If you had one architecture wish, what is it? | Ranked latent demand |
| What did we try before that failed, and why? | Prevents re-proposing a dead initiative — highest-signal question in the bank |
| Which system is nobody willing to touch? | True core risk, usually undocumented |
| How do you find out you broke something? | Observability maturity in one answer |
| What test would have caught the last incident? | Test strategy gap with evidence |
| What would make your job worse if I changed it? | Sacred cows, surfaced before you step on one |
| What would you delete if you were allowed? | Dead code and unused features |
| Who reviews your design before you build? | Whether any real architecture practice exists |
| Who should I talk to that I haven't? | Influence graph |

## 2. Risk managers, quants, front-office consumers

| Question | Listening for |
|---|---|
| What number are you waiting for, and by when? | The real SLOs — usually differ from documented ones |
| When the number is late or wrong, what do you do? | Manual workaround inventory = hidden operational risk |
| Which risk measure do you distrust, and why? | Data-quality hot spots ranked by business pain |
| What analysis do you want but cannot get today? | Horizon-3 roadmap material |
| How much of your day goes to reconciling numbers by hand? | Business case in FTE hours |
| What has to be true for you to trust a new number? | Acceptance criteria for any new capability |
| Which report would you stop receiving if you could? | Decommissioning candidates |

## 3. Compliance, internal audit, model risk, regulatory reporting

| Question | Listening for |
|---|---|
| What are the open audit findings against this division? | Non-negotiable roadmap items with dates |
| What is the next regulatory deadline with a technology dependency? | An immovable anchor for sequencing |
| Where is our lineage story weakest (BCBS 239)? | Debt with a regulator attached — easiest funding to obtain |
| What evidence is painful to produce at audit time? | Automatable evidence = fast credibility with a powerful function |
| What data must not leave which jurisdiction? | Hard architecture constraint |
| What change would require re-approval or re-certification? | Governance blast radius of any redesign |
| What has a regulator asked about recently? | Leadership's current fear |

## 4. Peer principals (AI, Web)

| Question | Listening for |
|---|---|
| Where do we currently step on each other? | Named grey zones in their words |
| Where do you wish the line were clearer? | Their preferred boundary — usually cheap to grant |
| What do you need from the Java platform that you don't get? | A concrete gift to deliver in month 2 |
| What has a previous architect done here that annoyed you? | Behaviour to avoid, given free |
| How do you want to be involved in decisions I own? | Collaboration protocol before the first conflict |
| For model inference, who gets paged at 2am? | The single most consequential AI/platform boundary |
| BFF or direct service access — who versions the contract? | Prevents a year of API friction |
| What do we escalate vs decide between ourselves? | Escalation protocol agreed while calm |
| Can all three of us sign this one-pager? | Ratification |

## 5. Manager, CTO, division leadership

| Question | Listening for |
|---|---|
| What does success look like at 6 and 12 months? | Written success contract |
| What one fix would make this hire obviously worth it? | Sanctioned first-win target |
| What are my decision rights, and who announces them? | Critical for a remote-from-HQ principal |
| Which relationships must I not damage? | Political minefield map |
| Who else wanted this role or this scope? | Most likely source of resistance |
| What is the budget and travel envelope? | How the role is actually valued |
| If I deliver only one thing in 12 months, which one? | True priority — ask several people and compare |
| What can I stop doing to fund this? | Forces trade-offs instead of additive wishlists |
| What funding cycle must the roadmap hit? | When the doc must be final, not when it's ready |

## 6. Ops, SRE, production support

| Question | Listening for |
|---|---|
| Show me the last 5 Sev1/Sev2 postmortems. | Ground truth on architecture weakness |
| What is the most common manual intervention during the batch? | Automation with immediate ROI |
| How does handoff work between regions at end of shift? | Follow-the-sun quality — a hidden MTTR driver |
| Which alert do you routinely ignore? | Observability redesign scope |
| What happens if the batch fails at 60%? | Idempotency/replay reality |
| What is the worst night you've had here? | The failure mode that actually matters |
| What would you fix with 6 weeks and no new headcount? | Team-sourced prioritization, free buy-in |

## 7. Deep-dive architecture reviews (days 31–60)

| Question | Listening for |
|---|---|
| What was the original constraint that made this design correct then? | Stops you mistaking a reasonable trade-off for incompetence |
| What breaks when load doubles? | The scaling cliff, with a number |
| Where is state held, and who reads it directly? | Hidden coupling — the real blocker to change |
| Which dependency can we not survive losing? | SPOFs with business impact |
| What happens on partial failure mid-batch? | Recovery design reality |
| What would we need to delete to make this simpler? | Simplification candidates |
| If you had 6 weeks, what would you fix? | Their prioritization — usually better than yours |

## 8. Target-architecture pre-socialization (days 61–90)

| Question | Listening for |
|---|---|
| What in this is wrong or naive? | Objections in private, where they're cheap |
| What have I missed that will embarrass me in the forum? | A direct request for protection — usually granted |
| Which horizon-1 item do you disagree with? | Re-sequence before public commitment |
| What would you need to support this publicly? | Converts a neutral into an advocate, with a price named |
| Whose objection matters most here? | The one person who can kill it |
| Can I cite you as a contributor? | Shared ownership before launch |

## 9. Golden path / standards design

| Question | Listening for |
|---|---|
| What would make you use a shared template voluntarily? | The adoption condition — build to it |
| What must the template *not* do? | Over-opinionated templates die |
| Which library set do you already trust? | Standardize on existing convergence; don't invent |
| What would you have to fight to adopt this? | Migration friction, found before rollout |
| What do you need from observability on day one of an incident? | Design telemetry from the consumer backwards |
| What standard would you actively resist, and why? | Pre-empts death-by-code-review |

## 10. Governance forum design

| Question | Listening for |
|---|---|
| What was wrong with previous governance forums here? | Every firm has a failed one — don't rebuild it |
| Which review would you happily route around? | Exactly which tier to make lighter |
| Who besides the principals should have a vote? | Legitimacy beyond the principal trio |
| How fast must a decision come back to be useful? | Your published decision SLA |

## 11. Cross-region / distributed (month 4+)

| Question | Listening for |
|---|---|
| What decisions were made in a room I wasn't in? | Async-process failures — fix process, not people |
| Which meetings are consistently at a bad hour for your region? | Rotation fairness audit |
| What context do you routinely lack? | Documentation and broadcast gaps |
| What would make you feel like a peer rather than a downstream team? | Direct, actionable fix list |
| What can your region resolve alone during an incident, and what can't it? | Regional autonomy gaps |

## 12. Structural decision questions (months 4–6)

| Question | Listening for |
|---|---|
| What is the 3-year cost of staying where we are? | Cost of inaction — the only way to fund structural work |
| What is the reversal cost if this is wrong in 18 months? | One-way door vs two-way door |
| What capability does this unlock that we can't offer today? | Links infrastructure to business capability |
| Who has done this at comparable scale inside this firm? | Internal precedent beats vendor references |
| What is the migration path for the 5 largest workloads? | Kills most attractive-looking options |
| What do we sunset as a result? | No decommissioning = additive complexity |
| What does this do to cost per risk run? | Headline efficiency metric |
| Which regulator or auditor cares about this? | Compliance blast radius |

## 13. Institutionalization questions (month 6)

| Question | Listening for |
|---|---|
| If I were unavailable for a month, which decisions would stall? | Your single points of failure — delegate each |
| Who is ready to run the forum? | Succession; a practice with one owner is not a practice |
| Which standard is followed only because I'm watching? | Badly designed standard — redesign it |
| What have we learned that should change the roadmap? | Forces a genuine roadmap v2 |
