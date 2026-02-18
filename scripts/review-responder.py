"""
ReplyAI — Standalone Review Response Generator

Generates AI-powered responses to customer reviews using OpenAI GPT-4o.
Use this to test prompt quality, demo to clients, or process one-off reviews.

Usage:
    export OPENAI_API_KEY="your-key-here"
    python review-responder.py

Or with a .env file:
    OPENAI_API_KEY=your-key-here
    python review-responder.py
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SYSTEM_PROMPT_TEMPLATE = """You are a professional customer service manager for {business_name}, \
a {business_type} located in {city}, {province}. Your job is to write responses to online customer reviews.

Rules:
- Respond in {language}
- Address the reviewer by their first name
- Acknowledge their specific feedback — never write a generic response
- Keep the response under 100 words
- Use a {brand_tone} tone
- If the review is positive (4-5 stars), express genuine gratitude and invite them back
- If the review is negative (1-2 stars), apologize sincerely, acknowledge the issue, and offer to make it right
- If the review is mixed (3 stars), acknowledge the positives and address the concerns
- Never be defensive or argumentative
- Never offer specific compensation (discounts, free items) unless instructed
- Do not use emojis
- Do not fabricate details not mentioned in the review
- Sign the response with the name: {owner_name}"""

USER_PROMPT_TEMPLATE = """Review from {reviewer_name} ({star_rating}/5 stars) on {platform}:
"{review_text}"

Write a response."""


def generate_response(
    review_text: str,
    reviewer_name: str,
    star_rating: int,
    platform: str = "Google",
    business_name: str = "Our Business",
    business_type: str = "restaurant",
    city: str = "Montréal",
    province: str = "QC",
    owner_name: str = "The Management",
    language: str = "the same language as the review",
    brand_tone: str = "warm, professional",
) -> str:
    """Generate an AI response to a customer review."""
    client = OpenAI()

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        business_name=business_name,
        business_type=business_type,
        city=city,
        province=province,
        language=language,
        brand_tone=brand_tone,
        owner_name=owner_name,
    )

    user_prompt = USER_PROMPT_TEMPLATE.format(
        reviewer_name=reviewer_name,
        star_rating=star_rating,
        platform=platform,
        review_text=review_text,
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=200,
        temperature=0.7,
    )

    return response.choices[0].message.content


def interactive_mode():
    """Run in interactive mode — enter reviews manually."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    print("=" * 60)
    print("ReplyAI — Review Response Generator")
    print("=" * 60)

    # Collect business info
    print("\nBusiness Setup (press Enter to use defaults):\n")

    business_name = input("Business name [My Restaurant]: ").strip() or "My Restaurant"
    business_type = input("Business type [restaurant]: ").strip() or "restaurant"
    city = input("City [Montréal]: ").strip() or "Montréal"
    province = input("Province [QC]: ").strip() or "QC"
    owner_name = input("Owner/manager name [The Management]: ").strip() or "The Management"
    language = input("Response language [same as review]: ").strip() or "the same language as the review"
    brand_tone = input("Brand tone [warm, professional]: ").strip() or "warm, professional"

    print("\n" + "=" * 60)
    print(f"Generating responses for: {business_name}")
    print("Type 'quit' to exit.\n")

    while True:
        print("-" * 40)
        review_text = input("\nPaste the review text (or 'quit'): ").strip()
        if review_text.lower() == "quit":
            break

        reviewer_name = input("Reviewer name: ").strip() or "Customer"

        rating_input = input("Star rating (1-5): ").strip()
        try:
            star_rating = int(rating_input)
            if star_rating < 1 or star_rating > 5:
                raise ValueError
        except ValueError:
            print("Invalid rating. Using 3.")
            star_rating = 3

        platform = input("Platform [Google]: ").strip() or "Google"

        print("\nGenerating response...\n")

        try:
            response = generate_response(
                review_text=review_text,
                reviewer_name=reviewer_name,
                star_rating=star_rating,
                platform=platform,
                business_name=business_name,
                business_type=business_type,
                city=city,
                province=province,
                owner_name=owner_name,
                language=language,
                brand_tone=brand_tone,
            )
            print("--- GENERATED RESPONSE ---")
            print(response)
            print("-" * 26)
        except Exception as e:
            print(f"Error generating response: {e}")


def demo_mode():
    """Run with sample reviews to demonstrate the tool."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    sample_reviews = [
        {
            "review_text": "Excellent repas en famille! Le service était impeccable et la poutine était la meilleure que j'ai mangée. On va revenir c'est sûr!",
            "reviewer_name": "Marie-Claude",
            "star_rating": 5,
            "platform": "Google",
        },
        {
            "review_text": "Food was decent but we waited 45 minutes for our main course. Server seemed overwhelmed and never checked on us. Disappointing for the price point.",
            "reviewer_name": "David",
            "star_rating": 2,
            "platform": "Google",
        },
        {
            "review_text": "L'ambiance est super et le staff est gentil. Par contre, les portions sont petites pour le prix. Le dessert était bon mais pas mémorable.",
            "reviewer_name": "Jean-Philippe",
            "star_rating": 3,
            "platform": "Yelp",
        },
    ]

    business = {
        "business_name": "Chez Marcel",
        "business_type": "restaurant québécois",
        "city": "Québec",
        "province": "QC",
        "owner_name": "Marcel",
        "language": "the same language as the review",
        "brand_tone": "warm, friendly",
    }

    print("=" * 60)
    print("ReplyAI — Demo Mode")
    print(f"Business: {business['business_name']}")
    print("=" * 60)

    for i, review in enumerate(sample_reviews, 1):
        print(f"\n--- Review {i} ({review['star_rating']}/5 stars from {review['reviewer_name']}) ---")
        print(f'"{review["review_text"]}"')
        print("\nGenerating response...\n")

        try:
            response = generate_response(**review, **business)
            print(">>> RESPONSE:")
            print(response)
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 60)
    print("Demo complete.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_mode()
    else:
        interactive_mode()
