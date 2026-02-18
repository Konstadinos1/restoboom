# Response Quality Guidelines

Standards for AI-generated review responses before they go live.

---

## Quality Checklist

Every generated response must pass these checks:

### Must Have
- [ ] Addresses reviewer by first name
- [ ] References specific details from the review (not generic)
- [ ] Matches the requested language (French/English)
- [ ] Under 100 words
- [ ] Signed with the owner/manager name
- [ ] Appropriate tone for the star rating

### Must NOT Have
- [ ] Generic phrases like "Thank you for your feedback" without specifics
- [ ] Defensive or argumentative language
- [ ] Specific compensation offers (unless pre-approved by client)
- [ ] Emojis (unless client style guide allows)
- [ ] Fabricated details not in the original review
- [ ] Medical/health information (for clinic clients)
- [ ] Mention of competitors
- [ ] Excessive exclamation marks (max 2 per response)

---

## Response Tone by Star Rating

| Rating | Tone | Key Elements |
|--------|------|-------------|
| 5 stars | Enthusiastic gratitude | Thank, highlight what they loved, invite back |
| 4 stars | Warm appreciation | Thank, acknowledge positive points, subtle acknowledgment of room to grow |
| 3 stars | Balanced, constructive | Thank for honesty, acknowledge positives, address concerns, invite back |
| 2 stars | Empathetic, solution-oriented | Apologize, acknowledge specific issues, offer to make it right |
| 1 star | Serious, concerned | Sincere apology, take ownership, direct contact invitation |

---

## Flagging Rules

Automatically flag for human review when:

1. **1-star reviews** — Always flag for owner review before responding
2. **Legal language** — Review mentions lawsuits, lawyers, health inspectors, or regulatory bodies
3. **Employee names** — Review names a specific employee negatively
4. **Health/safety** — Review mentions food poisoning, allergic reactions, injuries
5. **Profanity** — Review contains excessive profanity or threats
6. **Repeat reviewer** — Same person has left multiple negative reviews

Flag in Airtable by setting `status` to `NEEDS_REVIEW` and adding a `flag_reason`.

---

## Language Quality (French-Specific)

For Quebec French responses:

- Use Quebec French conventions, not France French
- "Merci beaucoup" not "Je vous remercie" (unless formal tone)
- Appropriate use of "tu" vs "vous" based on brand tone:
  - Casual/friendly brands: "tu"
  - Formal/professional brands: "vous"
- Common Quebec expressions are acceptable for casual brands:
  - "On a bien hâte de te revoir"
  - "Ça nous fait plaisir"
  - "C'est notre fierté"
- Avoid France-specific expressions like "c'est top" or "génial"

---

## Response Length Guidelines

| Platform | Ideal Length | Max Length |
|----------|-------------|-----------|
| Google | 50-80 words | 100 words |
| Yelp | 60-100 words | 120 words |
| TripAdvisor | 60-100 words | 120 words |
| Facebook | 40-70 words | 80 words |

Shorter is better. Owners who write essays look desperate. Concise, specific responses look professional.
