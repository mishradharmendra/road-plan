# Scorecard, Risks and Anti-patterns

## 1. How you will actually be judged at Month 6

Leaders rarely read your documents in full. They judge on a few impressions.
Make sure each is true and backed by a number.

| Impression leadership forms | Evidence you need |
|---|---|
| "Engineers trust them" | Engineering leads ask for your input unprompted; office hours are used; guild attendance |
| "They work well with the SA" | Joint ADRs; SA co-presents with you; no escalations between you |
| "They delivered something" | Two quick wins with before/after numbers; one strategic metric moved |
| "They reduced risk" | CVE count down; JDK EOL exposure down; recurring incident class eliminated |
| "They saved money" | Licence cost avoided (JDK, unused market data feeds), compute cost per run down |
| "They raised the bar" | Standards v1 adopted by N teams; golden path used by new services |

### Personal scorecard — fill monthly

| Metric | Baseline (Wk 3) | M2 | M3 | M4 | M5 | M6 target |
|---|---|---|---|---|---|---|
| Services on JDK 17+ (%) | | | | | | +30 pts |
| Services on JDK 21+ (%) | | | | | | new services 100% |
| Critical/high dependency CVEs | | | | | | −50% |
| Median CI build time, top 5 repos | | | | | | −30% |
| Recurring P1/P2 incident class addressed | | | | | | ≥ 1 eliminated |
| Market data p99.9 at open (if chosen) | | | | | | initiative target |
| Batch within SLA (% nights) (if chosen) | | | | | | initiative target |
| Teams adopting standards v1 | 0 | | | | | ≥ 3 |
| ADRs written by teams (not you) | | | | | | ≥ 10 |
| Annual cost avoided / saved | 0 | | | | | a number finance agrees with |

Adjust targets once you have real baselines. Targets agreed with your manager in
Month 2 beat ambitious targets you set alone.

---

## 2. Top risks and mitigations

| Risk | Early signal | Mitigation |
|---|---|---|
| **Seen as the SA's rival** | Excluded from design reviews; SA goes quiet | Follow `02-solution-architect-alignment.md`; co-author; private-first disagreement; give credit publicly |
| **Ivory tower** — standards nobody follows | Standards doc has views but no adoption | Ship the golden path template, not just a document; pair with one team to adopt first; waiver process |
| **Boiling the ocean** | Your list has 25 priorities | Only 2 quick wins + 1 initiative. Everything else is "Next" or "Later" |
| **Proposing a rewrite too early** | You find yourself drafting "Target State 2028" in Month 1 | Hard rule: no replacement proposals before Day 60; no re-platforming proposals before Month 6 review |
| **Losing hands-on credibility** | You haven't read a PR in two weeks | Protect 1 hour/day hands-on; profile a real service yourself; write the first JMH benchmark yourself |
| **Becoming a bottleneck** | Teams wait for your approval | Decisions within a team are theirs; you only review cross-team and standards waivers; publish principles so teams can self-serve |
| **Mis-reading the politics** | A proposal lands badly and you don't know why | Pre-wire every significant proposal with the 3–4 most affected people 1:1 before any group meeting |
| **Under-estimating regulation** | A change hits an audit or client contract constraint | Involve compliance/security early; check client contract SLAs before touching latency/availability |
| **Market data licensing blind spot** | A distribution change alters who receives what data | Every change to distribution or entitlement goes through the data licensing owner |
| **Numbers you can't defend** | Someone challenges your baseline in a meeting | Source every number; share the spreadsheet; let team leads validate their numbers first |

---

## 3. Anti-patterns — what gets principal architects sidelined

1. **"At my last firm..."** Every mention implies this firm is worse. Reframe as
   options with evidence.
2. **Critiquing legacy in public.** The people who built it are often in the room,
   and they made sensible choices under constraints you don't yet know.
3. **Picking a technology fight early** (Spring vs Quarkus, Kafka vs Solace, Gradle
   vs Maven). Unless it causes measurable harm, the switching cost almost always
   exceeds the benefit in year one.
4. **Architecture by PowerPoint.** Diagrams without a prototype, benchmark or
   running template don't change engineering behaviour.
5. **Owning everything.** Principals scale through standards, templates, reviews
   and mentoring, not through doing the work themselves.
6. **Hiding disagreements.** Unrecorded disagreement resurfaces as blame. Record
   dissent in ADRs and move on.
7. **Ignoring the business calendar.** Don't schedule risky changes near quarter
   end, index rebalances, major central-bank dates, or client reporting cycles.
   Ask for the change-freeze calendar in Week 1.
8. **Optimising what isn't the bottleneck.** Profile first. In risk grids the
   bottleneck is frequently data loading or serialisation, not maths; in market
   data it's often fan-out and back-pressure, not parsing.

---

## 4. Month-by-month checkpoint questions (ask yourself)

**End of Month 1**
- Does the SA see me as an ally? How do I know?
- Can I draw the market data and risk flows from memory, with latency and SLA numbers?
- Do I know the top 3 recurring incident causes?

**End of Month 2**
- Are two wins in flight with teams that want them?
- Has my observations document landed without anyone feeling ambushed?
- Have I agreed my Month 6 targets with my manager?

**End of Month 3**
- Is Standards v1 published and being adopted, with a waiver process?
- Is the design review co-chaired with the SA and producing ADRs?
- Have I chosen the strategic initiative, and does it have a sponsor?

**End of Month 4**
- Has the riskiest assumption of the initiative been tested with a spike?
- Are weekly metric updates going out?

**End of Month 5**
- Is shadow-mode data showing the target is achievable? If not, have I said so early?

**End of Month 6**
- Did a headline metric move in production?
- Can my manager describe my impact in one sentence?
- What's the bigger proposal for the next 6 months — and have the SA and key leads
  already seen it?
