# Make.com Automation Scenarios

Complete blueprints for the Make.com (formerly Integromat) scenarios that power ReplyAI.

---

## Scenario 1: Daily Review Scraper

**Trigger:** Scheduled — runs every 24 hours at 6:00 AM EST

### Flow

```
[Schedule Trigger]
    → [HTTP: Call Apify Actor]
        → [Iterator: Loop through new reviews]
            → [Airtable: Search for existing review]
                → [Filter: Only new reviews]
                    → [Airtable: Create new review record]
```

### Step-by-Step Configuration

#### 1. Schedule Trigger
- Interval: Every 24 hours
- Time: 06:00 EST
- Days: Every day

#### 2. HTTP Module — Call Apify Actor
- URL: `https://api.apify.com/v2/acts/compass~google-maps-reviews-scraper/run-sync-get-dataset-items`
- Method: POST
- Headers:
  ```
  Content-Type: application/json
  Authorization: Bearer {{APIFY_API_TOKEN}}
  ```
- Body (JSON):
  ```json
  {
    "startUrls": [
      {"url": "{{CLIENT_GOOGLE_MAPS_URL}}"}
    ],
    "maxReviews": 50,
    "reviewsSort": "newest",
    "language": "en",
    "personalData": true
  }
  ```
- Note: Run this module once per client. Use a sub-scenario or router to handle multiple clients.

#### 3. Iterator
- Source: HTTP response array
- Map each review to extract:
  - `reviewerName`: `{{item.name}}`
  - `rating`: `{{item.stars}}`
  - `reviewText`: `{{item.text}}`
  - `reviewDate`: `{{item.publishedAtDate}}`
  - `reviewId`: `{{item.reviewId}}`
  - `platform`: `"Google"`

#### 4. Airtable: Search Records
- Base: ReplyAI Operations
- Table: Reviews
- Formula: `{review_id} = "{{reviewId}}"`
- Purpose: Deduplicate — skip reviews already in the database

#### 5. Filter
- Condition: Airtable search returned 0 results (new review)

#### 6. Airtable: Create Record
- Base: ReplyAI Operations
- Table: Reviews
- Fields:
  ```
  client_id: {{CLIENT_ID}}
  reviewer_name: {{reviewerName}}
  star_rating: {{rating}}
  review_text: {{reviewText}}
  review_date: {{reviewDate}}
  review_id: {{reviewId}}
  platform: "Google"
  status: "NEW"
  response_text: (empty)
  created_at: {{now}}
  ```

---

## Scenario 2: AI Response Generator

**Trigger:** Airtable — watch for new records with status "NEW"

### Flow

```
[Airtable: Watch Records (status = NEW)]
    → [Airtable: Get Client Record]
        → [OpenAI: Generate Response]
            → [Filter: Check for flagging conditions]
                → [Router]
                    Route 1: Normal → [Airtable: Update with response, status = READY]
                    Route 2: Flagged → [Airtable: Update with response, status = NEEDS_REVIEW]
                        → [Email/Slack: Notify owner]
```

### Step-by-Step Configuration

#### 1. Airtable: Watch Records
- Base: ReplyAI Operations
- Table: Reviews
- Trigger field: `created_at`
- Filter formula: `{status} = "NEW"`
- Polling interval: Every 15 minutes

#### 2. Airtable: Get Client Record
- Base: ReplyAI Operations
- Table: Clients
- Record ID: `{{client_id}}` from the review record
- Returns: business_name, business_type, city, province, owner_name, language, brand_tone

#### 3. OpenAI: Create Chat Completion
- Model: `gpt-4o`
- System Message:
  ```
  You are a professional customer service manager for {{business_name}},
  a {{business_type}} located in {{city}}, {{province}}. Your job is to
  write responses to online customer reviews.

  Rules:
  - Respond in {{language}}
  - Address the reviewer by their first name
  - Acknowledge their specific feedback — never write a generic response
  - Keep the response under 100 words
  - Use a warm, professional tone
  - If the review is positive, express genuine gratitude and invite them back
  - If the review is negative, apologize sincerely and offer to make it right
  - Never be defensive or argumentative
  - Never offer specific compensation unless instructed
  ```
- User Message:
  ```
  Review from {{reviewer_name}} ({{star_rating}}/5 stars):
  "{{review_text}}"

  Write a response signed by {{owner_name}}.
  ```
- Max Tokens: 200
- Temperature: 0.7

#### 4. Filter: Flagging Check
Check these conditions and flag if any are true:
- `star_rating` <= 1
- `review_text` contains: "lawyer", "lawsuit", "health inspector", "avocat", "poursuite"
- `review_text` contains: "food poisoning", "sick", "allergic", "intoxication"
- `review_text` contains profanity (maintain a blocklist)

#### 5. Router

**Route 1 — Normal (not flagged):**
- Airtable: Update Record
  - `response_text`: OpenAI output
  - `status`: "READY"
  - `generated_at`: `{{now}}`

**Route 2 — Flagged:**
- Airtable: Update Record
  - `response_text`: OpenAI output
  - `status`: "NEEDS_REVIEW"
  - `flag_reason`: (matched condition)
  - `generated_at`: `{{now}}`
- Email/Slack: Send notification
  - To: Client owner email
  - Subject: "[ReplyAI] Review needs your attention — {{reviewer_name}}"
  - Body: Include the review text, AI-generated response, and a link to the Airtable record

---

## Scenario 3: Response Delivery

**Trigger:** Airtable — watch for records with status "APPROVED" or "READY" (if auto-approve is enabled)

### Flow

```
[Airtable: Watch Records (status = APPROVED or READY + auto_approve)]
    → [Email: Send response to client]
        → [Airtable: Update status to DELIVERED]
```

### Step-by-Step Configuration

#### 1. Airtable: Watch Records
- Filter: `OR({status} = "APPROVED", AND({status} = "READY", {auto_approve} = TRUE()))`
- Polling: Every 15 minutes

#### 2. Email: Send to Client
- To: `{{client_email}}`
- Subject: "New review response ready — {{reviewer_name}} ({{star_rating}}★)"
- Body:
  ```
  Hi {{owner_name}},

  A new {{star_rating}}-star review from {{reviewer_name}} on {{platform}}
  has been responded to. Here's the response ready to post:

  ---
  {{response_text}}
  ---

  To post this response:
  1. Go to your {{platform}} business page
  2. Find the review from {{reviewer_name}}
  3. Click "Reply" and paste the response above

  Or reply to this email if you'd like any changes.

  — ReplyAI
  ```

#### 3. Airtable: Update Record
- `status`: "DELIVERED"
- `delivered_at`: `{{now}}`

---

## Scenario 4: Client Onboarding (Manual Trigger)

**Trigger:** Webhook — triggered when a new client signs up via Stripe

### Flow

```
[Webhook: New Stripe subscription]
    → [Airtable: Create Client Record]
        → [Apify: Test scrape first reviews]
            → [Email: Welcome email to client]
```

### Configuration

#### 1. Webhook
- Listen for Stripe `customer.subscription.created` event
- Extract: customer email, name, subscription plan, metadata (business URL)

#### 2. Airtable: Create Client
- Table: Clients
- Fields: business_name, google_maps_url, owner_name, email, language, business_type, brand_tone, auto_approve, subscription_status, created_at

#### 3. Apify: Test Scrape
- Run the Google review scraper for the new client's URL
- Pull the 5 most recent reviews as a test

#### 4. Welcome Email
- Send onboarding email with:
  - How the service works
  - What to expect (daily email with responses)
  - How to approve/modify responses
  - Support contact

---

## Operations Budget per Scenario

| Scenario | Make.com Operations/Run | Runs/Day | Monthly Operations |
|----------|------------------------|----------|--------------------|
| Review Scraper | ~5 per client | 1/day | 150/client |
| AI Response | ~4 per review | ~3/day avg | 360/client |
| Delivery | ~3 per review | ~3/day avg | 270/client |
| **Total per client** | | | **~780/month** |

Make.com free tier: 1,000 ops/month (enough for 1 client)
Make.com Core ($9/mo): 10,000 ops/month (enough for ~12 clients)
Make.com Pro ($16/mo): 10,000 ops + priority (enough for ~12 clients)

**At 40+ clients**, upgrade to Teams plan ($29/mo for 10,000 ops) and optimize scenarios to reduce operations per run.
