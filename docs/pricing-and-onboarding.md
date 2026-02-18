# Pricing Tiers & Client Onboarding

---

## Pricing Structure

### Single Location — $79/month
- 1 Google Business listing monitored
- Daily review scraping (all new reviews)
- AI-generated responses for every review
- Email delivery of responses for approval
- Auto-approve option for 4-5 star reviews
- Flagging for sensitive reviews (1-star, legal, health)
- Email support

### Multi-Location 3 — $199/month ($66/location)
- Everything in Single Location
- 3 Google Business listings
- Consistent brand voice across all locations
- Single dashboard view of all locations
- Priority email support

### Multi-Location 10 — $499/month ($50/location)
- Everything in Multi-Location 3
- Up to 10 Google Business listings
- Monthly reputation report (PDF)
- Dedicated onboarding setup
- Priority support via email + WhatsApp

### Enterprise / Franchise — Custom pricing
- 10+ locations
- White-label option (branded as client's own tool)
- Custom AI tone training per brand
- API access for integration with existing systems
- Dedicated account manager
- Contact: hello@replyai.ca

### All Plans Include
- **30-day free trial** — no credit card required
- Cancel anytime, no contracts
- Setup assistance included

---

## Stripe Product Setup

Create these products in Stripe Dashboard:

```
Product: ReplyAI Single Location
  Price: $79/month (recurring)
  Trial period: 30 days
  Metadata:
    plan_type: single
    locations: 1

Product: ReplyAI Multi-Location 3
  Price: $199/month (recurring)
  Trial period: 30 days
  Metadata:
    plan_type: multi-3
    locations: 3

Product: ReplyAI Multi-Location 10
  Price: $499/month (recurring)
  Trial period: 30 days
  Metadata:
    plan_type: multi-10
    locations: 10
```

Payment link setup:
1. Create a Payment Link for each product in Stripe
2. Add custom fields: Business Name, Google Maps URL, Preferred Language
3. Embed the payment link on your Carrd landing page CTA buttons

---

## Client Onboarding Process

### Step 1: Client Signs Up (Automated)

Client clicks payment link on landing page → Stripe creates subscription with 30-day trial → Webhook triggers Make.com Scenario 4 → Airtable client record created automatically.

### Step 2: Welcome Email (Automated)

Sent via Make.com immediately after signup.

**Subject:** "Welcome to ReplyAI — here's what happens next"

```
Hi {{OWNER_NAME}},

Welcome to ReplyAI! Here's what's happening right now:

1. We're connecting to your Google Business listing
2. We're pulling your most recent reviews
3. Within 24 hours, you'll receive your first AI-generated
   review responses via email

What you need to do:
- Nothing right now. We'll email you when your first batch
  of responses is ready.
- When you get the email, review the responses and post them
  as replies on Google.

Quick settings:
- Your responses will be in {{LANGUAGE}}
- Your brand tone is set to: {{BRAND_TONE}}
- Auto-approve is: {{AUTO_APPROVE_STATUS}}

Want to change any of these? Just reply to this email.

Questions? Reply anytime — I read every message.

{{YOUR_NAME}}
ReplyAI
```

### Step 3: Initial Review Scrape (Automated)

Make.com runs Apify scraper for the new client's Google Maps URL. First batch of reviews added to Airtable.

### Step 4: First Responses Generated (Automated)

AI generates responses for the initial batch. Responses emailed to client.

### Step 5: Day 3 Check-In (Manual)

Send a personal message:

```
Hi {{OWNER_NAME}},

Just checking in — how are the review responses looking?
Do they match the tone you'd use yourself?

If anything feels off, let me know and I'll adjust the AI
to better match your style.

{{YOUR_NAME}}
```

### Step 6: Day 25 — Trial Ending Reminder (Automated)

```
Hi {{OWNER_NAME}},

Your free trial of ReplyAI ends in 5 days. Since you started:

- We've responded to {{REVIEW_COUNT}} reviews
- Your average response time went from {{OLD_RESPONSE_TIME}} to {{NEW_RESPONSE_TIME}}
- {{APPROVAL_RATE}}% of responses were approved without changes

To keep your reviews managed automatically, your subscription
will start at ${{PRICE}}/month on {{BILLING_START_DATE}}.

No action needed if you want to continue. To cancel, just
reply to this email.

{{YOUR_NAME}}
ReplyAI
```

---

## Churn Prevention

### Warning Signs
- Client hasn't opened delivery emails in 7+ days
- Client manually edited 50%+ of responses (tone mismatch)
- Client has 0 reviews in a 2-week period (low volume concern)

### Prevention Actions
| Signal | Action |
|--------|--------|
| Unopened emails (7+ days) | Personal check-in: "Hey, just making sure our emails aren't going to spam" |
| High edit rate | Adjust prompts: "I noticed you're tweaking the responses — let me update the AI to better match your style" |
| Low review volume | Reframe value: "Even at low volume, consistent responses improve your ranking over time" |
| Approaching renewal | Send results summary 5 days before billing |

### Cancellation Save Offer
If a client requests cancellation:
```
Hi {{OWNER_NAME}},

I'm sorry to see you go. Before I process the cancellation,
would any of these help?

- 50% off for the next 3 months ($39.50/month)
- Pause your account for 1-2 months (no charge)
- A quick call to adjust the AI to better fit your needs

If not, no worries — I'll cancel immediately and you won't
be charged again.

{{YOUR_NAME}}
```
