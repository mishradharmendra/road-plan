# Stakeholders and Operating Cadence

## 1. Who to meet, in what order

Order matters. Meeting the SA's business stakeholders before the SA signals that
you're going around them. Meeting executives before engineers signals you're
managing up.

| Week | Who | Why this order |
|---|---|---|
| 1 | Your manager; Solution Architect(s); Head of Engineering / CTO | Establish mandate and the SA relationship first |
| 1–2 | Engineering leads: Market Data, Risk/Analytics, Client APIs, Platform/SRE | They own the systems; you need their trust for anything to happen |
| 2 | Security / CISO delegate; Head of SRE / on-call leads | Understand constraints and incident reality |
| 2–3 | 5–8 senior engineers, including the most tenured Java engineer | Tenured engineers know why things are the way they are. Future allies or future blockers |
| 3 | Product managers for market data and risk products (with SA's intro) | Understand roadmap pressure — through the SA, not around them |
| 3–4 | Client support / sales engineering; listen to 1 client call | Hear real client pain in their words |
| 4 | Finance / procurement contact for technology spend | Needed for licensing and cost wins |
| 4–6 | Risk quants / model owners; data governance / compliance | Model release and regulatory constraints |

Target: 25–35 conversations in the first 30 days.

---

## 2. Question sets per stakeholder

**Your manager**
1. What are the 3 outcomes that would make you say hiring me was right, at Month 6?
2. Why was this role created now? What triggered it?
3. What should I absolutely not touch in the first 90 days?
4. How do you see the split between me and the Solution Architect?
5. How do you like updates — written weekly, 1:1s, or both?

**CTO / Head of Engineering**
1. What's the biggest technology risk to the business in the next 12 months?
2. Where are we spending money that we shouldn't be?
3. What would you like the Java platform to look like in 2 years?
4. Which client commitments or regulatory deadlines constrain us this year?

**Engineering leads**
1. Walk me through your system on a whiteboard. What wakes you up at night?
2. What have you asked for repeatedly that hasn't happened?
3. What's the one thing slowing your team down most?
4. What standards or decisions from "architecture" have helped you? Hurt you?
5. How can I be useful to you in the next month?

**Senior / tenured engineers**
1. What's the history of this system — why is it built this way?
2. What was tried before and failed? Why?
3. What should I read in the code to understand how things really work?
4. If you had 3 months with no roadmap, what would you fix?

**SRE / on-call**
1. Top 3 alert sources by volume in the last quarter?
2. Which incidents recur? What's stopped them being fixed?
3. How do we test failover and DR, and when was the last test?

**Product managers** (with SA)
1. What are clients asking for that we can't deliver today because of technology?
2. Which competitor capability worries you most?
3. What latency / freshness / coverage commitments are in client contracts?

**Security**
1. How are Java dependency vulnerabilities tracked and remediated?
2. What findings from the last pen test / audit are still open?
3. What client security questionnaires cause us most trouble?

**Client support / sales engineering**
1. What do clients complain about most?
2. Which issues cause client escalations to senior management?
3. What do we lose deals on?

---

## 3. Stakeholder map — maintain privately

Keep a private table, updated monthly:

| Name | Role | Influence (H/M/L) | Current stance (advocate / neutral / sceptic) | What they care about | What I can do for them | Next touchpoint |
|---|---|---|---|---|---|---|

Aim by Month 3: every high-influence person is at least neutral; at least 3
engineering leads are advocates; the SA is an advocate.

---

## 4. Operating cadence

### Recurring meetings you set up

| Meeting | Frequency | Length | Attendees | Purpose |
|---|---|---|---|---|
| SA sync | Weekly | 30 min | You + SA | Align on in-flight decisions; no surprises |
| Manager 1:1 | Weekly | 30–45 min | You + manager | Progress vs phase exit criteria |
| Design review | Fortnightly (from Week 9) | 45 min | Co-chaired with SA; open to engineers | Cross-team designs; outputs are ADRs |
| Java guild | Monthly (from Week 8) | 60 min | Open | One talk, one war story, one standards update |
| Office hours | Weekly (from Week 5) | 60 min | Open drop-in | Any engineer can bring a design, profile, or PR |
| Lead skip-levels | Monthly per team | 30 min | You + each engineering lead | Pulse check; find problems early |

### Written communication rhythm

| Artefact | Frequency | Audience |
|---|---|---|
| Weekly 5-bullet note | Weekly | Manager (cc SA if it touches their area) |
| Architecture observations | Once, Week 6–8 | Manager, CTO, SA |
| Standards changelog | Per change | All engineering |
| Initiative status (Months 4–6) | Weekly | Sponsor, SA, involved teams |
| Monthly metrics snapshot | Monthly | Manager, CTO |

### Meeting discipline

- Don't attend more than ~50% of your week in meetings; protect hands-on time.
- In any meeting where the SA is presenting, your default is to ask clarifying
  questions, not to propose alternatives. Alternatives go 1:1 afterwards.
- Write decisions down at the end of every meeting you chair, within 24 hours.
