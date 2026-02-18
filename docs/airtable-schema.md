# Airtable Database Schema

Two tables power the entire operation: **Clients** and **Reviews**.

---

## Table 1: Clients

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `client_id` | Auto Number | Unique identifier | 1, 2, 3... |
| `business_name` | Single Line Text | Business display name | "Chez Marcel" |
| `business_type` | Single Select | Industry category | restaurant, salon, clinic, retail, hotel, auto |
| `google_maps_url` | URL | Google Maps listing URL | https://maps.google.com/... |
| `owner_name` | Single Line Text | Owner/manager name for signatures | "Marcel Gagnon" |
| `email` | Email | Client contact email | marcel@chezmarcel.ca |
| `phone` | Phone | Client phone number | +1-418-555-0123 |
| `city` | Single Line Text | City | "Québec" |
| `province` | Single Line Text | Province | "QC" |
| `language` | Single Select | Preferred response language | fr, en, bilingual |
| `brand_tone` | Single Select | Response tone preference | casual-friendly, formal-professional, warm-family |
| `auto_approve` | Checkbox | Auto-approve 4-5 star responses | true/false |
| `subscription_status` | Single Select | Current status | trial, active, paused, cancelled |
| `stripe_customer_id` | Single Line Text | Stripe customer reference | cus_abc123 |
| `stripe_subscription_id` | Single Line Text | Stripe subscription reference | sub_xyz789 |
| `monthly_plan` | Single Select | Pricing tier | single ($79), multi-3 ($199), multi-10 ($499) |
| `onboarded_at` | Date | When the client was fully set up | 2026-02-15 |
| `notes` | Long Text | Internal notes | "Referred by Bellepros network" |
| `created_at` | Created Time | Record creation timestamp | Auto |

### Views

- **Active Clients** — Filter: `subscription_status` = "active" or "trial"
- **Needs Onboarding** — Filter: `onboarded_at` is empty
- **By Plan** — Group by `monthly_plan`
- **Churned** — Filter: `subscription_status` = "cancelled"

---

## Table 2: Reviews

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `review_id` | Single Line Text | Unique ID from the platform | "ChdDSUhNMG9..." |
| `client_id` | Link to Clients | Reference to the client | Link to Clients table |
| `platform` | Single Select | Review source | Google, Yelp, TripAdvisor, Facebook |
| `reviewer_name` | Single Line Text | Reviewer's display name | "Marie-Claude T." |
| `star_rating` | Number (1-5) | Star rating | 4 |
| `review_text` | Long Text | Full review content | "Excellent repas en famille..." |
| `review_date` | Date | When the review was posted | 2026-02-14 |
| `response_text` | Long Text | AI-generated response | "Merci Marie-Claude..." |
| `status` | Single Select | Processing status | NEW, GENERATING, READY, NEEDS_REVIEW, APPROVED, DELIVERED, POSTED |
| `flag_reason` | Single Line Text | Why it was flagged (if applicable) | "1-star review", "legal language detected" |
| `auto_approved` | Checkbox | Was this auto-approved? | true/false |
| `generated_at` | Date | When the AI response was created | 2026-02-14 |
| `delivered_at` | Date | When it was sent to the client | 2026-02-14 |
| `posted_at` | Date | When the client posted it (manual tracking) | 2026-02-15 |
| `created_at` | Created Time | Record creation timestamp | Auto |

### Views

- **Needs Response** — Filter: `status` = "NEW"
- **Needs Review** — Filter: `status` = "NEEDS_REVIEW"
- **Ready to Send** — Filter: `status` = "READY" or "APPROVED"
- **Today's Activity** — Filter: `created_at` is today
- **By Client** — Group by `client_id`
- **Flagged Reviews** — Filter: `flag_reason` is not empty

### Status Flow

```
NEW → GENERATING → READY → DELIVERED → POSTED
                     ↓
              NEEDS_REVIEW → APPROVED → DELIVERED → POSTED
```

- **NEW**: Review scraped, awaiting AI processing
- **GENERATING**: OpenAI API call in progress
- **READY**: Response generated, auto-approve eligible (4-5 stars + client opted in)
- **NEEDS_REVIEW**: Flagged for human review (1 star, legal, health, profanity)
- **APPROVED**: Owner approved the response
- **DELIVERED**: Response sent to owner via email
- **POSTED**: Owner confirmed they posted it (optional manual tracking)

---

## Table 3: Activity Log (Optional)

For debugging and client reporting.

| Field Name | Type | Description |
|------------|------|-------------|
| `log_id` | Auto Number | Unique ID |
| `client_id` | Link to Clients | Client reference |
| `action` | Single Select | What happened |
| `details` | Long Text | Event details |
| `timestamp` | Created Time | When it happened |

Actions: `review_scraped`, `response_generated`, `response_flagged`, `response_delivered`, `client_onboarded`, `client_cancelled`, `error`

---

## Airtable Setup Checklist

1. [ ] Create a new Airtable base called "ReplyAI Operations"
2. [ ] Create the Clients table with all fields above
3. [ ] Create the Reviews table with all fields above
4. [ ] Set up the views listed under each table
5. [ ] Create an API key in Airtable settings (Settings → API)
6. [ ] Note the Base ID (in the URL: airtable.com/BASE_ID/...)
7. [ ] Test: manually create one Client record and one Review record
8. [ ] Connect to Make.com using the Airtable module with your API key and Base ID
