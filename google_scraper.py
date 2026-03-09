"""Module de collecte de données Google Business Profile.

Utilise l'API Google Places et/ou SerpAPI pour récupérer les informations
d'un restaurant à partir d'une URL Google Maps ou d'un nom + ville.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from typing import Any

import googlemaps
import requests

from config import (
    GOOGLE_PLACES_API_KEY,
    SERPAPI_KEY,
    RATING_THRESHOLDS,
    RESPONSE_RATE_THRESHOLDS,
    RestaurantData,
)

logger = logging.getLogger(__name__)


def extract_place_id_from_url(url: str) -> str | None:
    """Extrait le Place ID ou le terme de recherche d'une URL Google Maps."""
    # Pattern: /place/.../@... or /maps/place/...
    place_match = re.search(r"/place/([^/@]+)", url)
    if place_match:
        return place_match.group(1).replace("+", " ").replace("%20", " ")

    # Pattern with place_id in the URL
    pid_match = re.search(r"place_id[=:]([A-Za-z0-9_-]+)", url)
    if pid_match:
        return pid_match.group(1)

    # CID pattern
    cid_match = re.search(r"cid=(\d+)", url)
    if cid_match:
        return cid_match.group(1)

    return None


def search_place_google(query: str) -> dict[str, Any] | None:
    """Recherche un lieu via l'API Google Places."""
    if not GOOGLE_PLACES_API_KEY:
        logger.warning("Clé API Google Places non configurée")
        return None

    try:
        gmaps = googlemaps.Client(key=GOOGLE_PLACES_API_KEY)
        results = gmaps.places(query=query, language="fr")

        if results.get("results"):
            place_id = results["results"][0]["place_id"]
            details = gmaps.place(
                place_id=place_id,
                fields=[
                    "name",
                    "formatted_address",
                    "formatted_phone_number",
                    "rating",
                    "user_ratings_total",
                    "opening_hours",
                    "photos",
                    "website",
                    "types",
                    "business_status",
                    "reviews",
                    "url",
                ],
                language="fr",
            )
            return details.get("result", {})
    except Exception as e:
        logger.error("Erreur Google Places API: %s", e)

    return None


def search_place_serpapi(query: str) -> dict[str, Any] | None:
    """Recherche un lieu via SerpAPI pour des données enrichies."""
    if not SERPAPI_KEY:
        logger.info("Clé SerpAPI non configurée, utilisation de Google Places uniquement")
        return None

    try:
        params = {
            "engine": "google_maps",
            "q": query,
            "api_key": SERPAPI_KEY,
            "hl": "fr",
            "gl": "ca",
        }
        response = requests.get(
            "https://serpapi.com/search", params=params, timeout=30
        )
        response.raise_for_status()
        data = response.json()

        if data.get("local_results"):
            place = data["local_results"][0]
            place_id = place.get("place_id", "")

            # Fetch detailed info
            detail_params = {
                "engine": "google_maps",
                "place_id": place_id,
                "api_key": SERPAPI_KEY,
                "hl": "fr",
            }
            detail_response = requests.get(
                "https://serpapi.com/search", params=detail_params, timeout=30
            )
            detail_response.raise_for_status()
            return detail_response.json()

        return data

    except Exception as e:
        logger.error("Erreur SerpAPI: %s", e)
        return None


def fetch_serpapi_reviews(place_id: str) -> list[dict[str, Any]]:
    """Récupère les avis via SerpAPI."""
    if not SERPAPI_KEY or not place_id:
        return []

    try:
        params = {
            "engine": "google_maps_reviews",
            "place_id": place_id,
            "api_key": SERPAPI_KEY,
            "hl": "fr",
            "sort_by": "newestFirst",
            "num": "20",
        }
        response = requests.get(
            "https://serpapi.com/search", params=params, timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data.get("reviews", [])
    except Exception as e:
        logger.error("Erreur récupération avis SerpAPI: %s", e)
        return []


def parse_google_data(google_data: dict[str, Any]) -> RestaurantData:
    """Parse les données de l'API Google Places dans RestaurantData."""
    data = RestaurantData()

    data.name = google_data.get("name", "Non disponible")
    data.address = google_data.get("formatted_address", "Non disponible")
    data.phone = google_data.get("formatted_phone_number", "Non disponible")
    data.rating = float(google_data.get("rating", 0.0))
    data.total_reviews = int(google_data.get("user_ratings_total", 0))
    data.website = google_data.get("website", "")
    data.categories = google_data.get("types", [])
    data.has_description = bool(google_data.get("editorial_summary", {}).get("overview", ""))
    data.description = google_data.get("editorial_summary", {}).get("overview", "")

    # Photos
    photos = google_data.get("photos", [])
    data.photo_count = len(photos)

    # Hours
    hours = google_data.get("opening_hours", {})
    if hours:
        data.business_hours = {
            "weekday_text": hours.get("weekday_text", []),
            "open_now": hours.get("open_now", False),
        }
        weekday_text = hours.get("weekday_text", [])
        data.hours_complete = len(weekday_text) >= 7

    # Reviews from Google Places API
    reviews = google_data.get("reviews", [])
    parsed_reviews = []
    for review in reviews[:5]:
        parsed_reviews.append({
            "text": review.get("text", ""),
            "rating": review.get("rating", 0),
            "date": review.get("relative_time_description", ""),
            "author": review.get("author_name", "Anonyme"),
            "responded": bool(review.get("owner_response")),
        })
    data.recent_reviews = parsed_reviews

    return data


def parse_serpapi_data(serpapi_data: dict[str, Any]) -> RestaurantData:
    """Parse les données SerpAPI dans RestaurantData."""
    data = RestaurantData()

    place_info = serpapi_data.get("place_results", serpapi_data)

    data.name = place_info.get("title", place_info.get("name", "Non disponible"))
    data.address = place_info.get("address", "Non disponible")
    data.phone = place_info.get("phone", "Non disponible")
    data.rating = float(place_info.get("rating", 0.0))
    data.total_reviews = int(place_info.get("reviews", place_info.get("user_ratings_total", 0)))
    data.website = place_info.get("website", "")
    data.description = place_info.get("description", "")
    data.has_description = bool(data.description)

    # Categories
    data.categories = place_info.get("types", [])
    if place_info.get("type"):
        data.categories = [place_info["type"]] + data.categories

    # Photos
    photos = place_info.get("photos", [])
    data.photo_count = place_info.get("photos_count", len(photos))

    # Hours
    hours = place_info.get("operating_hours", place_info.get("hours", {}))
    if hours:
        data.business_hours = hours
        data.hours_complete = len(hours) >= 7

    # Menu / order link
    data.has_menu = bool(place_info.get("menu"))
    data.has_order_link = bool(place_info.get("order_online_link") or place_info.get("reservations_link"))

    # Posts
    if place_info.get("posts"):
        posts = place_info["posts"]
        if posts:
            last_post = posts[0]
            data.last_post_date = last_post.get("date", "")
            # Check if post is within last 30 days (heuristic)
            data.has_recent_post = True

    # FAQ
    data.has_faq = bool(place_info.get("questions_and_answers"))

    # Attributes
    data.has_attributes = bool(place_info.get("service_options") or place_info.get("amenities"))

    # Reviews from SerpAPI
    place_id = place_info.get("place_id", "")
    serpapi_reviews = fetch_serpapi_reviews(place_id)

    parsed_reviews = []
    unresponded = 0
    star_dist = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

    for review in serpapi_reviews:
        stars = int(review.get("rating", review.get("extracted_snippet", {}).get("rating", 0)))
        if 1 <= stars <= 5:
            star_dist[stars] += 1

        responded = bool(review.get("response"))
        if not responded:
            unresponded += 1

        if len(parsed_reviews) < 5:
            parsed_reviews.append({
                "text": review.get("snippet", review.get("text", "")),
                "rating": stars,
                "date": review.get("date", review.get("iso_date_of_last_edit", "")),
                "author": review.get("user", {}).get("name", "Anonyme"),
                "responded": responded,
            })

    data.recent_reviews = parsed_reviews if parsed_reviews else data.recent_reviews
    data.unresponded_reviews = unresponded
    data.star_distribution = star_dist

    if data.total_reviews > 0 and serpapi_reviews:
        reviewed_count = len(serpapi_reviews)
        responded_count = reviewed_count - unresponded
        data.response_rate = (responded_count / reviewed_count) * 100 if reviewed_count > 0 else 0.0

    return data


def merge_data(google_data: RestaurantData, serpapi_data: RestaurantData) -> RestaurantData:
    """Fusionne les données Google Places et SerpAPI, en privilégiant les données les plus complètes."""
    merged = RestaurantData()

    # Prendre la meilleure valeur pour chaque champ
    merged.name = serpapi_data.name if serpapi_data.name != "Non disponible" else google_data.name
    merged.address = serpapi_data.address if serpapi_data.address != "Non disponible" else google_data.address
    merged.phone = serpapi_data.phone if serpapi_data.phone != "Non disponible" else google_data.phone
    merged.rating = serpapi_data.rating or google_data.rating
    merged.total_reviews = max(serpapi_data.total_reviews, google_data.total_reviews)
    merged.website = serpapi_data.website or google_data.website
    merged.description = serpapi_data.description or google_data.description
    merged.has_description = serpapi_data.has_description or google_data.has_description
    merged.categories = serpapi_data.categories or google_data.categories
    merged.photo_count = max(serpapi_data.photo_count, google_data.photo_count)
    merged.business_hours = serpapi_data.business_hours or google_data.business_hours
    merged.hours_complete = serpapi_data.hours_complete or google_data.hours_complete
    merged.has_menu = serpapi_data.has_menu or google_data.has_menu
    merged.has_order_link = serpapi_data.has_order_link or google_data.has_order_link
    merged.has_faq = serpapi_data.has_faq or google_data.has_faq
    merged.has_attributes = serpapi_data.has_attributes or google_data.has_attributes
    merged.has_recent_post = serpapi_data.has_recent_post or google_data.has_recent_post
    merged.last_post_date = serpapi_data.last_post_date or google_data.last_post_date

    # Reviews: SerpAPI a plus de données
    merged.recent_reviews = serpapi_data.recent_reviews or google_data.recent_reviews
    merged.unresponded_reviews = serpapi_data.unresponded_reviews or google_data.unresponded_reviews
    merged.response_rate = serpapi_data.response_rate or google_data.response_rate
    merged.star_distribution = serpapi_data.star_distribution if any(serpapi_data.star_distribution.values()) else google_data.star_distribution

    # Social (non disponible via ces APIs, sera mis à jour manuellement ou par scraping)
    merged.facebook_active = False
    merged.instagram_active = False

    return merged


def calculate_scores(data: RestaurantData) -> RestaurantData:
    """Calcule tous les scores de l'audit."""
    criteria_scores: list[tuple[str, int]] = []

    # 1. NAP accuracy
    nap_score = 0
    if data.name != "Non disponible":
        nap_score += 2
    if data.address != "Non disponible":
        nap_score += 2
    if data.phone != "Non disponible":
        nap_score += 1
    criteria_scores.append(("NAP (Nom / Adresse / Téléphone)", nap_score))

    # 2. Business categories
    cat_score = 5 if data.categories else 0
    criteria_scores.append(("Catégories d'entreprise", cat_score))

    # 3. Hours complete
    hours_score = 5 if data.hours_complete else (2 if data.business_hours else 0)
    criteria_scores.append(("Heures d'ouverture complètes", hours_score))

    # 4. Photos
    if data.photo_count >= 5:
        photo_score = 5
    elif data.photo_count >= 3:
        photo_score = 3
    else:
        photo_score = 1 if data.photo_count > 0 else 0
    criteria_scores.append(("Photos du profil", photo_score))

    # 5. Description
    desc_score = 5 if data.has_description else 0
    criteria_scores.append(("Description de l'entreprise", desc_score))

    # 6. Menu / Products
    menu_score = 5 if data.has_menu else 0
    criteria_scores.append(("Menu / Produits ajoutés", menu_score))

    # 7. FAQ
    faq_score = 5 if data.has_faq else 0
    criteria_scores.append(("FAQ / Questions-Réponses", faq_score))

    # 8. Google Posts
    post_score = 5 if data.has_recent_post else 0
    criteria_scores.append(("Google Posts (30 derniers jours)", post_score))

    # 9. Attributes
    attr_score = 5 if data.has_attributes else 0
    criteria_scores.append(("Attributs et services", attr_score))

    # 10. Order/reservation link
    order_score = 5 if data.has_order_link else 0
    criteria_scores.append(("Lien commande / réservation", order_score))

    data.gbp_criteria_scores = criteria_scores
    data.gbp_score = sum(score for _, score in criteria_scores)

    # Review Health Score (/30)
    # Rating score (/10)
    rating_score = 1
    for threshold, score in RATING_THRESHOLDS:
        if data.rating >= threshold:
            rating_score = score
            break

    # Response rate score (/10)
    response_score = 1
    for threshold, score in RESPONSE_RATE_THRESHOLDS:
        if data.response_rate >= threshold:
            response_score = score
            break

    # Review volume trend (/10) - heuristic based on total count
    if data.total_reviews >= 100:
        volume_score = 10
    elif data.total_reviews >= 50:
        volume_score = 7
    elif data.total_reviews >= 20:
        volume_score = 4
    else:
        volume_score = 1

    data.review_health_score = rating_score + response_score + volume_score

    # Social Presence Score (/20)
    social = 0
    if data.facebook_active:
        social += 10
    if data.instagram_active:
        social += 10
    data.social_score = social

    # Total
    data.total_score = data.gbp_score + data.review_health_score + data.social_score

    return data


def fetch_restaurant_data(query: str, is_url: bool = False) -> RestaurantData:
    """Point d'entrée principal: récupère et score les données d'un restaurant.

    Args:
        query: URL Google Maps ou 'nom du restaurant, ville'.
        is_url: True si query est une URL Google Maps.

    Returns:
        RestaurantData avec toutes les données et scores calculés.
    """
    search_query = query
    if is_url:
        extracted = extract_place_id_from_url(query)
        search_query = extracted if extracted else query

    google_data = RestaurantData()
    serpapi_data = RestaurantData()

    # Essayer Google Places API
    google_result = search_place_google(search_query)
    if google_result:
        google_data = parse_google_data(google_result)

    # Essayer SerpAPI pour données enrichies
    serpapi_result = search_place_serpapi(search_query)
    if serpapi_result:
        serpapi_data = parse_serpapi_data(serpapi_result)

    # Fusionner les résultats
    if google_result and serpapi_result:
        merged = merge_data(google_data, serpapi_data)
    elif serpapi_result:
        merged = serpapi_data
    elif google_result:
        merged = google_data
    else:
        # Aucune donnée — retourner un objet vide avec le nom de la recherche
        merged = RestaurantData()
        merged.name = search_query if not is_url else "Restaurant non trouvé"

    # Estimate unresponded reviews from Google Places data if SerpAPI not available
    if not serpapi_result and google_result:
        reviews = google_data.recent_reviews
        if reviews:
            unresponded = sum(1 for r in reviews if not r.get("responded", False))
            total_sample = len(reviews)
            if total_sample > 0:
                merged.response_rate = ((total_sample - unresponded) / total_sample) * 100
                # Extrapolate unresponded count
                if merged.total_reviews > 0:
                    merged.unresponded_reviews = int(
                        (unresponded / total_sample) * merged.total_reviews
                    )

    # Calculer les scores
    merged = calculate_scores(merged)

    return merged
