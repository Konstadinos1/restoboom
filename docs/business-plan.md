# ReplyAI — 30-Day Launch Plan

Complete execution plan from zero to first paying clients.

---

## Week 1: Build (Days 1-7)

### Day 1-2: Core Automation Setup
- [ ] Create Airtable base with Clients and Reviews tables (see `docs/airtable-schema.md`)
- [ ] Sign up for Make.com (Core plan, $9/mo)
- [ ] Sign up for Apify (Personal plan, $49/mo)
- [ ] Get OpenAI API key (pay-as-you-go)
- [ ] Build Make.com Scenario 1: Daily Review Scraper (see `automation/make-scenarios.md`)
- [ ] Build Make.com Scenario 2: AI Response Generator

### Day 3-4: Test With Your Own Business
- [ ] Add your Bellepros location as first client in Airtable
- [ ] Run the review scraper on your own Google listing
- [ ] Generate AI responses for your last 10 reviews
- [ ] Review quality — adjust prompts as needed (see `prompts/review-response.md`)
- [ ] Build Make.com Scenario 3: Response Delivery (email)

### Day 5-6: Client-Facing Setup
- [ ] Build landing page on Carrd (see `landing-page/copy.md`)
- [ ] Set up Stripe with $79/month product + 30-day free trial
- [ ] Connect Stripe to Make.com webhook (Scenario 4)
- [ ] Record 2-minute Loom demo video (see `outreach/loom-script.md`)

### Day 7: Launch Prep
- [ ] Test the full flow end-to-end: new review → AI response → email delivery
- [ ] Fix any automation errors
- [ ] Prepare outreach list of 50 local businesses (see Week 2)

---

## Week 2: First Clients (Days 8-14)

### Target: 5 clients on free trial

### Warm Outreach (Days 8-10)
- [ ] Message 10 contacts from your Bellepros/RestoBoom network
- [ ] Post in 3-5 Quebec restaurant owner Facebook groups
- [ ] Send personalized Loom video to 20 restaurant owners you know
- [ ] Offer: "Free 30-day trial — I'll set everything up for you"

### Cold Outreach (Days 11-14)
- [ ] Build a list of 50 restaurants in Quebec with 3+ unanswered Google reviews
- [ ] Start Email Sequence (see `outreach/cold-email-sequences.md`) for all 50
- [ ] Send 10 LinkedIn connection requests per day to restaurant owners
- [ ] Follow up with anyone who opened Email 1 but didn't reply

### Conversion Targets
| Channel | Contacts | Expected Response Rate | Expected Conversions |
|---------|----------|----------------------|---------------------|
| Warm network | 30 | 30-40% | 5-10 trials |
| Cold email | 50 | 5-10% | 3-5 trials |
| Facebook groups | ~100 views | 2-3% | 2-3 trials |
| LinkedIn | 40 | 10-15% | 2-4 trials |

Conservative target: **5 paying clients** by end of Week 2.

---

## Week 3: Optimize (Days 15-21)

### Operations
- [ ] Monitor all 5 clients' review responses daily
- [ ] Fix any prompt quality issues — iterate on the AI prompts
- [ ] Check Make.com for automation errors
- [ ] Ensure response delivery emails aren't going to spam

### Client Success
- [ ] Check in with each client via email or WhatsApp
- [ ] Ask: "Are the responses matching your voice? Anything to adjust?"
- [ ] Document any client feedback for prompt improvements
- [ ] Track: response rate, approval rate, client satisfaction

### Content
- [ ] Ask your best client for a testimonial
- [ ] Screenshot before/after Google review response rates
- [ ] Prepare a simple case study (3 paragraphs)

---

## Week 4: Scale (Days 22-30)

### Convert Trials to Paid
- [ ] Email all trial clients 5 days before trial ends
- [ ] Offer: "Your trial ends in 5 days — here's what you'd lose"
- [ ] Target: 80%+ trial-to-paid conversion

### Scale Outreach
- [ ] Double cold email volume to 100 new contacts
- [ ] Use case study in Email 3 of the sequence
- [ ] Target franchise operators and multi-location owners
- [ ] Post case study on LinkedIn with results

### Systems
- [ ] Document your daily operations workflow (should be under 1 hour/day)
- [ ] Create a simple client onboarding checklist
- [ ] Set up Stripe to auto-charge after trial period

---

## Month 2-3: Growth Phase

### Revenue Targets
| Month | Clients | MRR | Daily Average |
|-------|---------|-----|---------------|
| 1 | 5 | $395 | $13 |
| 2 | 20 | $1,580 | $53 |
| 3 | 40 | $3,160 | **$105** |

### Growth Tactics
- **Referral program**: Offer 1 month free for every referral that converts
- **Franchise play**: Pitch franchisor → get 10-20 locations in one deal
- **Platform expansion**: Add Yelp, TripAdvisor, Facebook reviews
- **Upsell**: Monthly reputation report ($29/mo add-on)

### When to Hire
- At 30+ clients: consider a part-time VA for client onboarding
- At 50+ clients: consider upgrading Make.com plan and Apify plan
- At 100+ clients: consider building a custom dashboard (replace Airtable + Softr)

---

## Daily Operations Checklist (Once Running)

Time: ~45 minutes/day

| Time | Task | Duration |
|------|------|----------|
| 9:00 AM | Check Airtable for flagged reviews (NEEDS_REVIEW) | 10 min |
| 9:10 AM | Review and approve flagged responses | 10 min |
| 9:20 AM | Check Make.com for automation errors | 5 min |
| 9:25 AM | Send 5-10 outreach emails / LinkedIn messages | 15 min |
| 9:40 AM | Reply to client messages (WhatsApp/email) | 5 min |

---

## Key Metrics to Track

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Trial signup rate | 10% of cold contacts | Stripe dashboard |
| Trial-to-paid conversion | 80% | Stripe dashboard |
| Monthly churn rate | <5% | Stripe dashboard |
| Average response quality | 90%+ approval rate | Airtable (approved / total) |
| Response delivery time | <4 hours from review | Airtable timestamps |
| Client satisfaction | 4.5+/5 | Monthly check-in survey |
| Google rating improvement | +0.2 in 60 days | Track client ratings monthly |

---

## Budget (First 30 Days)

| Expense | Monthly Cost |
|---------|-------------|
| Make.com Core | $9 |
| Apify Personal | $49 |
| OpenAI API (est. 500 reviews) | $5 |
| Carrd landing page | $2 (annual plan) |
| Stripe fees (on revenue) | ~2.9% + $0.30/transaction |
| Loom (free tier) | $0 |
| **Total fixed costs** | **~$65/month** |

Break-even: **1 client at $79/month** covers your costs.
