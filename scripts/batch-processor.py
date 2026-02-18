"""
ReplyAI — Batch Review Processor

Process a CSV file of reviews and generate AI responses for each one.
Outputs a new CSV with the original data plus a 'response' column.

Usage:
    export OPENAI_API_KEY="your-key-here"
    python batch-processor.py input.csv output.csv

Input CSV format:
    reviewer_name,star_rating,review_text,platform
    "Marie-Claude",5,"Excellent repas!","Google"
    "David",2,"Waited too long...","Google"

Business settings are configured via environment variables or .env file.
"""

import csv
import os
import sys
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Business configuration — set via environment variables or .env
BUSINESS_NAME = os.environ.get("REPLYAI_BUSINESS_NAME", "My Restaurant")
BUSINESS_TYPE = os.environ.get("REPLYAI_BUSINESS_TYPE", "restaurant")
CITY = os.environ.get("REPLYAI_CITY", "Montréal")
PROVINCE = os.environ.get("REPLYAI_PROVINCE", "QC")
OWNER_NAME = os.environ.get("REPLYAI_OWNER_NAME", "The Management")
LANGUAGE = os.environ.get("REPLYAI_LANGUAGE", "the same language as the review")
BRAND_TONE = os.environ.get("REPLYAI_BRAND_TONE", "warm, professional")

SYSTEM_PROMPT = f"""You are a professional customer service manager for {BUSINESS_NAME}, \
a {BUSINESS_TYPE} located in {CITY}, {PROVINCE}. Your job is to write responses to online customer reviews.

Rules:
- Respond in {LANGUAGE}
- Address the reviewer by their first name
- Acknowledge their specific feedback — never write a generic response
- Keep the response under 100 words
- Use a {BRAND_TONE} tone
- If the review is positive (4-5 stars), express genuine gratitude and invite them back
- If the review is negative (1-2 stars), apologize sincerely, acknowledge the issue, and offer to make it right
- If the review is mixed (3 stars), acknowledge the positives and address the concerns
- Never be defensive or argumentative
- Never offer specific compensation unless instructed
- Do not use emojis
- Do not fabricate details not mentioned in the review
- Sign the response with: {OWNER_NAME}"""


def process_reviews(input_path: str, output_path: str):
    """Read reviews from CSV, generate responses, write output CSV."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)

    client = OpenAI()

    # Read input CSV
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reviews = list(reader)

    if not reviews:
        print("No reviews found in input file.")
        sys.exit(1)

    # Validate required columns
    required_cols = {"reviewer_name", "star_rating", "review_text"}
    actual_cols = set(reviews[0].keys())
    missing = required_cols - actual_cols
    if missing:
        print(f"Error: Input CSV missing required columns: {missing}")
        print(f"Found columns: {actual_cols}")
        sys.exit(1)

    print(f"Processing {len(reviews)} reviews...")
    print(f"Business: {BUSINESS_NAME} ({CITY}, {PROVINCE})")
    print("-" * 40)

    results = []
    errors = 0

    for i, review in enumerate(reviews, 1):
        reviewer_name = review["reviewer_name"]
        star_rating = review["star_rating"]
        review_text = review["review_text"]
        platform = review.get("platform", "Google")

        print(f"[{i}/{len(reviews)}] {reviewer_name} ({star_rating} stars)...", end=" ")

        user_prompt = f"""Review from {reviewer_name} ({star_rating}/5 stars) on {platform}:
"{review_text}"

Write a response."""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=200,
                temperature=0.7,
            )
            ai_response = response.choices[0].message.content
            print("Done.")
        except Exception as e:
            ai_response = f"ERROR: {e}"
            errors += 1
            print(f"Error: {e}")

        result = dict(review)
        result["response"] = ai_response
        results.append(result)

        # Rate limiting — avoid hitting API limits
        if i < len(reviews):
            time.sleep(0.5)

    # Write output CSV
    fieldnames = list(results[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("-" * 40)
    print(f"Done. {len(results)} responses generated ({errors} errors).")
    print(f"Output saved to: {output_path}")


def create_sample_csv(path: str):
    """Create a sample input CSV for testing."""
    sample_data = [
        {
            "reviewer_name": "Marie-Claude",
            "star_rating": "5",
            "review_text": "Excellent repas en famille! Le service était impeccable et la poutine était la meilleure que j'ai mangée.",
            "platform": "Google",
        },
        {
            "reviewer_name": "David",
            "star_rating": "2",
            "review_text": "Food was decent but we waited 45 minutes for our main course. Server seemed overwhelmed.",
            "platform": "Google",
        },
        {
            "reviewer_name": "Sophie",
            "star_rating": "4",
            "review_text": "Great atmosphere and friendly staff. The pasta was delicious. Only reason for 4 stars is parking is difficult.",
            "platform": "Yelp",
        },
        {
            "reviewer_name": "Jean-Philippe",
            "star_rating": "3",
            "review_text": "L'ambiance est super et le staff est gentil. Par contre, les portions sont petites pour le prix.",
            "platform": "Google",
        },
        {
            "reviewer_name": "Sarah",
            "star_rating": "1",
            "review_text": "Terrible experience. Cold food, rude waiter, and they got our order wrong twice. Will not return.",
            "platform": "Google",
        },
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["reviewer_name", "star_rating", "review_text", "platform"])
        writer.writeheader()
        writer.writerows(sample_data)

    print(f"Sample CSV created: {path}")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--sample":
        create_sample_csv("sample-reviews.csv")
    elif len(sys.argv) == 3:
        process_reviews(sys.argv[1], sys.argv[2])
    else:
        print("Usage:")
        print("  python batch-processor.py input.csv output.csv")
        print("  python batch-processor.py --sample  (create sample CSV)")
        print()
        print("Environment variables:")
        print("  OPENAI_API_KEY          (required)")
        print("  REPLYAI_BUSINESS_NAME   (default: My Restaurant)")
        print("  REPLYAI_BUSINESS_TYPE   (default: restaurant)")
        print("  REPLYAI_CITY            (default: Montréal)")
        print("  REPLYAI_PROVINCE        (default: QC)")
        print("  REPLYAI_OWNER_NAME      (default: The Management)")
        print("  REPLYAI_LANGUAGE        (default: same as review)")
        print("  REPLYAI_BRAND_TONE      (default: warm, professional)")
