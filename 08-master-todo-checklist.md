# 08 — Master TODO Checklist

Single flat checklist across all phases. Each item links to the phase file for detail.

---

## Days 1–30 — Learn the terrain ([detail](01-roadmap-days-1-30.md))

- [ ] Complete 40–50 listening interviews across engineers, risk/quant, compliance/audit, principals, leadership, ops
- [ ] Build the influence graph (who is actually consulted, vs the org chart)
- [ ] Read every Sev1/Sev2 postmortem from the last 12 months
- [ ] Read all open audit findings and regulatory commitments with tech dependency
- [ ] Map the risk value chain end to end on one page, with seams and ownership marked
- [ ] Sit through one full overnight/EOD risk cycle — batch, runbook, support channel
- [ ] Get read access to repos, CI, monitoring, cloud cost console, Jira, incident tooling
- [ ] Personally baseline: batch times, incidents, DORA, CI duration, cloud cost, version skew, CVEs
- [ ] Clone and build the 3 most critical repos yourself; time it as a newcomer would
- [ ] Meet Principal AI and Principal Web individually in week 1; send written summaries for correction
- [ ] Get written 6- and 12-month success definition from your manager
- [ ] Get decision rights clarified and agree who announces them
- [ ] Establish data residency / cross-border access constraints ([detail](07-distributed-india-global-operating-model.md))
- [ ] Publish the Day-30 "What I've Learned So Far" memo — observations only, no recommendations
- [ ] Produce the first-win shortlist (3 scored candidates)
- [ ] Do NOT: propose a rewrite, criticise a framework publicly, or say "at my last firm" more than twice

## Days 31–60 — Shared diagnosis and first win ([detail](02-roadmap-days-31-60.md))

- [ ] Publish the Current-State + Pain Map, in their language, citing their incidents, crediting sources
- [ ] Reissue a v2 incorporating corrections received
- [ ] Run 2–3 joint deep-dive architecture reviews; publish co-authored findings, their name first
- [ ] Select the first win against the scoring criteria and agree measurement **before** starting
- [ ] Deliver the first win with the existing team; plan who will present it (not you)
- [ ] Ratify the Principal Boundary Contract — three signatures + shared leader, grey zones named
- [ ] Start the ADR practice: repo location, template, 5-day async window, silence = consent
- [ ] Write the first 3 ADRs yourself to set the quality bar
- [ ] Sponsor 2–3 solution engineers into named architecture ownership
- [ ] Close instrumentation gaps from the Day-30 baseline
- [ ] Book the offshore trip for the day 60–90 window
- [ ] Attend at least one production incident bridge end to end
- [ ] Circulate a draft target architecture privately to 5 trusted people for demolition

## Days 61–90 — Target architecture and operating model ([detail](03-roadmap-days-61-90.md))

- [ ] Finalize the target architecture with 3 horizons: stabilize / consolidate / differentiate
- [ ] Tie every roadmap item to a business outcome — never "modernization"
- [ ] Pre-brief every principal, eng lead, and key stakeholder individually
- [ ] Revise the doc visibly and publish a changelog crediting who changed what
- [ ] Present to the division — it should feel like a formality
- [ ] Stand up the Architecture Review Forum: fortnightly, 45 min, 2 topics, pre-read, rotating presenters
- [ ] Publish the tiered decision-rights model (Tier 1/2/3), announced by your manager
- [ ] Publish Golden Path v1: service template, observability baseline, build/deploy standard, library set
- [ ] Measure time-to-first-deploy on the golden path; make it genuinely easier than the alternative
- [ ] Stand up the leadership-visible SLO baseline dashboard with named metric owners
- [ ] Publish the tech-debt register **with cost attached**
- [ ] Close out the first win with a published before/after number, credited to the team
- [ ] Complete the offshore trip — 80% 1:1s and whiteboards; write a trip report
- [ ] Take one on-call rotation or be on a real incident bridge

## Months 4–6 — Execute and institutionalize ([detail](04-roadmap-months-4-6.md))

- [ ] Deliver horizon-1 items with real teams; publish outcomes with **their** names
- [ ] Land one structural decision (grid/compute, data platform, streaming backbone, or JDK strategy)
- [ ] Produce full options analysis: 3 options, cost, risk, migration path, reversal cost, sunset plan
- [ ] Publish NFR/SLO contracts per critical pipeline, with named owners and alerting
- [ ] Get the SLO dashboard into a recurring leadership meeting
- [ ] Fund ≥ 2 tech-debt items using the cost-attached register
- [ ] Run the cross-region architecture guild monthly, with rotating chair and rotating time slot
- [ ] Hand the Architecture Forum chair to someone else for ≥ 1 session
- [ ] Permanently delegate ≥ 3 decision types downward; document them as Tier 3
- [ ] Publish roadmap v2 at month 6 with explicit changes and reasons
- [ ] Complete a second offshore trip or host offshore peers in India
- [ ] Run hiring-bar calibration; define the architecture competency ladder
- [ ] Write the 6-month self-assessment against the day-30 success contract, before being asked

---

## Standing behaviours (every week, all phases)

- [ ] Never surprise a peer principal in a meeting — 1:1 first, every time
- [ ] Write up every decision within 24 hours
- [ ] Put your name last on shared documents for the first two quarters
- [ ] Ask "what's the history here?" before "why is this like this?"
- [ ] Protect overlap windows for decisions, never for status
- [ ] Rotate the unsocial-hours pain visibly across regions
- [ ] Track your private trust metrics weekly ([detail](05-metrics-scorecard.md))
- [ ] Cap your unsocial-hour meeting load — burnout at month 8 invalidates the whole plan

---

## Phase exit tests

| Phase | Exit test |
|---|---|
| Day 30 | Can you explain the end-to-end risk flow and its three worst failure modes to the division's engineers — and have them agree you got it right? |
| Day 60 | Has someone who was *not* in your interview list quoted your pain map back to you as their own idea? |
| Day 90 | In the roadmap presentation, does anyone learn something for the first time? (If yes, pre-socialization failed.) |
| Month 6 | Could you take four weeks off without stalling any decision? |

---

## The 15-item short version

1. 40+ listening interviews; map the influence graph, not the org chart
2. Read every postmortem and audit finding from the last year
3. Sit through a full risk batch cycle end to end
4. Write the boundary contract with Principal AI and Principal Web; ratify it by day 60
5. Get an explicit success definition from your manager, in writing
6. Publish current-state + pain map at day 30 — observations, no verdicts
7. Pick one visible, bounded pain and fix it by day 60 — credit the team
8. Establish lightweight ADR practice + tiered review model
9. Stand up an architecture forum with rotating, non-you presenters
10. Publish target architecture + 3-horizon roadmap at day 90, fully pre-socialized
11. Instrument SLO / DORA / cost baselines on a leadership dashboard
12. Lock in the cross-region async operating rhythm and rotate meeting pain
13. Take one on-call rotation or join a live incident bridge
14. Get one offshore trip done inside 90 days
15. Sponsor 2–3 solution engineers into named architecture ownership
