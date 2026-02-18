# ReplyAI — AI Review Response SaaS for Local Businesses

> Automated AI-powered Google/Yelp review response tool for local businesses. Built for the Quebec restaurant and service industry market.

## Overview

ReplyAI solves a universal problem: local businesses are drowning in online reviews they ignore or respond to poorly. Google's algorithm rewards businesses that respond — owners know this but have no time. ReplyAI generates professional, personalized responses in under 60 seconds using AI.

**Target:** $100/day recurring revenue within 90 days.

## Revenue Model

| Metric | Value |
|--------|-------|
| Price per location | $79/month |
| Break-even clients | 2 (covers ~$100/mo overhead) |
| $100/day target | 38 clients |
| Scale target | 150+ clients = $11,850/month |

## Tech Stack

| Tool | Purpose | Cost |
|------|---------|------|
| [Make.com](https://make.com) | Automation backbone | $9/mo |
| [OpenAI API](https://platform.openai.com) (GPT-4o) | AI review responses | ~$0.01/response |
| [Apify](https://apify.com) | Scrape Google reviews | $49/mo |
| [Airtable](https://airtable.com) | Client dashboard/CRM | Free tier |
| [Stripe](https://stripe.com) | Payments | 2.9% + $0.30 |
| [Softr](https://softr.io) or [Carrd](https://carrd.co) | Landing page + client portal | $19-49/mo |

**Total monthly overhead:** ~$80-100

## Project Structure

```
restoboom/
├── README.md                          # This file
├── docs/
│   ├── business-plan.md               # Full 30-day launch plan
│   ├── pricing-and-onboarding.md      # Pricing tiers + client onboarding
│   └── airtable-schema.md             # Database schema for Airtable
├── prompts/
│   ├── review-response.md             # Core AI prompt templates
│   ├── prompt-variations.md           # Industry-specific variations
│   └── quality-guidelines.md          # Response quality standards
├── automation/
│   ├── make-scenarios.md              # Make.com scenario blueprints
│   ├── apify-config.json              # Apify Google review scraper config
│   └── webhook-handler.py             # Optional webhook handler script
├── outreach/
│   ├── cold-email-sequences.md        # 5-email cold outreach sequence
│   ├── loom-script.md                 # 2-minute demo video script
│   └── linkedin-messages.md           # LinkedIn DM templates
├── landing-page/
│   └── copy.md                        # Landing page copy and structure
└── scripts/
    ├── review-responder.py            # Standalone review response generator
    ├── batch-processor.py             # Batch process reviews from CSV
    └── requirements.txt               # Python dependencies
```

## Quick Start

1. **Test the AI locally** — Run the standalone review responder:
   ```bash
   cd scripts/
   pip install -r requirements.txt
   export OPENAI_API_KEY="your-key-here"
   python review-responder.py
   ```

2. **Set up the automation** — Follow `automation/make-scenarios.md`

3. **Get your first clients** — Use the templates in `outreach/`

4. **Scale** — See `docs/business-plan.md` for the full 30-day plan

## Target Market

- **Primary:** Quebec restaurant owners (French + English bilingual)
- **Secondary:** Salons, clinics, retail shops in Quebec
- **Scale target:** Franchise networks (20+ locations per deal)

## License

Proprietary — All rights reserved.
