# Working With the Existing Solution Architect

The single biggest risk to your first 6 months is not technical. It is being seen
by the Solution Architect (SA) as a competitor who arrived to take their seat.
If that happens, every proposal you make will face quiet resistance, and teams
will be forced to pick sides.

Your aim: by Month 3, the SA should describe you as **"the person who makes my
solutions easier to deliver."**

---

## 1. Understand why the overlap exists

Both roles legitimately touch architecture. The difference is the axis.

| Dimension | Solution Architect | Principal Java Architect (you) |
|---|---|---|
| Primary axis | **Vertical** — one business initiative end-to-end | **Horizontal** — one technology stack across all initiatives |
| Core question | "What solution meets this business need, within constraints?" | "How do we build solutions in Java so they are fast, safe, consistent and maintainable?" |
| Typical outputs | Solution designs, integration patterns, vendor/build choices, NFR mapping, estimates, delivery trade-offs | Platform standards, reference implementations, runtime/performance engineering, framework choices, code-level design review, modernisation roadmap |
| Horizon | Project / programme timeline | Multi-year platform health |
| Stakeholders | Product, business, delivery, clients | Engineers, platform/SRE, security, CTO |
| Depth | Broad across tech (cloud, data, vendors, networks) | Deep in JVM, concurrency, performance, Java ecosystem |

Say this back to the SA in your own words in the first meeting and **ask them to
correct it**. The version they correct becomes the working agreement.

---

## 2. Decision rights (RACI) — propose, don't impose

Bring this as a *draft for discussion* in week 2–3. Let the SA edit it. Then take
the agreed version to your shared manager(s) so it's recognised above both of you.

R = Responsible, A = Accountable, C = Consulted, I = Informed

| Decision | SA | You | Engineering lead | CTO / Head of Arch |
|---|---|---|---|---|
| Solution design for a business initiative | **A/R** | C | C | I |
| Build vs buy vs vendor for a capability | **A/R** | C | C | A for > threshold spend |
| Integration pattern between systems (sync/async, protocol) | **A** | C (R for Java-internal) | C | I |
| JDK versions, JVM runtime vendor, GC defaults | C | **A/R** | C | I |
| Approved Java frameworks and libraries | C | **A/R** | C | I |
| Service internals: concurrency model, memory layout, caching in-process | I | **A** | R | — |
| Performance engineering on hot paths (latency, throughput) | C | **A/R** | R | I |
| Java platform standards, golden path template | C | **A/R** | C | I |
| Non-functional requirements for a solution | **A** | C (R for feasibility evidence) | C | I |
| Cross-cutting ADRs (affect > 1 team) | **Co-A** | **Co-A** | C | Tie-break |
| Modernisation roadmap for Java estate | C | **A/R** | C | A for funding |
| Architecture review forum | **Co-chair** | **Co-chair** | Attend | Escalation |

**Grey zones to pre-agree** (these cause 80% of conflict):
1. Messaging technology choice (Kafka vs Solace vs Aeron vs vendor bus) — it's both
   an integration pattern (SA) and a runtime/performance choice (you). Agree: SA owns
   the *pattern*, you own the *client-side implementation standard and performance
   evidence*, joint ADR for the technology.
2. Data store choice for tick/time-series data (kdb+, ClickHouse, Timescale, Iceberg)
   — typically SA leads, you provide JVM integration and performance testing.
3. Cloud vs on-prem for latency-sensitive components — SA leads, you provide the
   latency evidence.
4. Who presents to the CTO/architecture board — default: whoever owns the decision
   presents, the other co-signs.

---

## 3. First 1:1 with the SA — script (Week 1)

Book 60 minutes. Coffee/lunch if possible, not a meeting room.

**Open (5 min)**
> "Before I meet anyone else senior, I wanted to meet you. You know this estate
> and these stakeholders far better than I do, and I'll get a lot wrong in my
> first months if I don't learn from you."

**Their world (25 min)** — listen, take notes, don't counter.
- What are you working on right now, and what's the most important thing on your
  plate this quarter?
- What decisions are in flight that I should be careful not to disturb?
- Where has architecture gone well here? Where has it been painful?
- Who are the people I must earn trust with? Who's been burned before?
- What did you think when you heard this role was being created?
  *(This is the most valuable question. Let silence do the work.)*

**How we split (15 min)**
> "Here's how I understand the split: you own the solution for each business
> problem; I own how we build in Java consistently across all of them — standards,
> runtime, performance, modernisation. Does that match how you see it? Where
> would you draw it differently?"

**Offer (10 min)** — offer to take something off their plate that sits in your remit:
- "Is there anything Java-specific you've been carrying that you'd like someone
  to own — JDK upgrades, library standards, performance issues, code reviews?"

**Close (5 min)**
- Propose the standing 30-min weekly sync.
- "If I ever step on your toes, please tell me directly — I'd much rather hear
  it from you than find out later. I'll do the same."

---

## 4. Operating rules to avoid conflict

| Rule | In practice |
|---|---|
| **Private first, public credit** | Any disagreement with the SA's design goes to them 1:1 first. Any shared win gets their name first in public. |
| **No surprises upward** | Never present anything to the CTO/your manager that the SA would be surprised by. Send drafts 48 hours ahead. |
| **Don't go around them** | If a product owner or business stakeholder asks you about a solution the SA owns, answer the Java question and loop the SA in: "Let me bring [SA] in, they own the overall design." |
| **Bring evidence, not opinion** | When you disagree, disagree with a benchmark, a profile, an incident, or a cost — not a preference. "JMH shows X" beats "I prefer Y". |
| **Make them look good** | Your standards and golden path should make their solution designs faster to deliver. Say so explicitly and let them announce adoption on their projects. |
| **Co-author, don't review** | For designs that touch your remit, ask to co-author the relevant section rather than "review" it. Reviewers are gatekeepers; co-authors are allies. |
| **Disagree and commit, in writing** | If a decision goes their way over your objection, record your concern in the ADR "Consequences" section, then support it fully. No "I told you so". |
| **Respect their stakeholders** | Their relationships with product and clients took years. Don't build parallel relationships in their territory in the first 90 days. |

---

## 5. Conflict early-warning signs and responses

| Signal | Likely cause | Response |
|---|---|---|
| You're not invited to design reviews on projects that touch Java | SA feels reviewed/judged, or process doesn't have a slot for you | Ask SA directly: "Would it help if I only joined for the Java runtime parts?" Offer a narrower scope |
| SA's designs start specifying JVM/framework details you'd own | Old habits, or testing boundaries | Don't correct in public. 1:1: "I noticed the design picks X for Y — happy to own that part so you're not carrying it. Here's the standard I'm proposing." |
| Engineers bring you the SA's design and ask for your opinion | Teams triangulating, or unhappy with the design | "Have you raised this with [SA]? Let's take it to them together." Never give a verdict without the SA present |
| Your manager asks you to "sort out" something the SA owns | Leadership impatience with the SA | Clarify with manager: "Is this a change of ownership? If so, can we tell [SA] together?" Never accept silent transfers |
| SA pushes back on your standards | Standards add cost to their projects | Ask which specific clause hurts their delivery. Add a waiver process with an expiry date. Standards must have an exit ramp |
| Two of you give contradicting answers to a team | RACI not clear in that area | Fix it same day: joint message to the team, then update the RACI |

### Escalation path (agree it in advance with the SA)

1. Discuss 1:1, with evidence, time-boxed to one week.
2. Write a joint ADR with both options and both recommendations.
3. Take the ADR to the agreed tie-breaker (CTO / Head of Architecture) **together**.
4. Both commit to the outcome.

Pre-agreeing the path turns a conflict into a process, which depersonalises it.

---

## 6. If the relationship is already strained on arrival

Sometimes the SA was a candidate for your role, or was not consulted. Signs: short
answers, missed 1:1s, "we already tried that".

- Acknowledge it without naming it: "I know a new role in the middle of things can
  be disruptive. I want to make your work easier, not harder."
- Ask for their help on something real and visible — e.g. "Would you present the
  context diagram with me? You know it better."
- Give them first right of refusal on the most interesting cross-cutting work.
- Do not escalate relationship issues to your manager in the first 60 days unless
  it's blocking delivery. Escalating early makes you look like you can't influence.
- If by Day 60 it hasn't improved, ask your manager to facilitate a
  3-way conversation on the RACI — framed as clarifying roles, not complaining.
