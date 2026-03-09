"""Module d'analyse IA via l'API Claude d'Anthropic.

Génère les constats clés et recommandations prioritaires en français québécois
à partir des données du profil Google Business d'un restaurant.
"""

from __future__ import annotations

import logging
from typing import Any

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_SYSTEM_PROMPT, RestaurantData

logger = logging.getLogger(__name__)


def _build_data_summary(data: RestaurantData) -> str:
    """Construit un résumé textuel des données pour Claude."""
    # Identifier les critères faibles
    weak_criteria = [
        name for name, score in data.gbp_criteria_scores if score <= 2
    ]
    strong_criteria = [
        name for name, score in data.gbp_criteria_scores if score >= 4
    ]

    unresponded_pct = 100 - data.response_rate if data.response_rate > 0 else 100

    summary = f"""
RESTAURANT: {data.name}
ADRESSE: {data.address}
TÉLÉPHONE: {data.phone}
SITE WEB: {data.website or 'Aucun'}

SCORES:
- Score GBP Complétude: {data.gbp_score}/50
- Score Santé des Avis: {data.review_health_score}/30
- Score Présence Sociale: {data.social_score}/20
- SCORE TOTAL: {data.total_score}/100

PROFIL GOOGLE BUSINESS:
- Note moyenne: {data.rating}/5.0
- Nombre total d'avis: {data.total_reviews}
- Avis sans réponse: {data.unresponded_reviews} ({unresponded_pct:.0f}% non répondus)
- Taux de réponse aux avis: {data.response_rate:.0f}%
- Nombre de photos: {data.photo_count}
- Heures d'ouverture complètes: {'Oui' if data.hours_complete else 'Non'}
- Description présente: {'Oui' if data.has_description else 'Non'}
- Menu/Produits ajoutés: {'Oui' if data.has_menu else 'Non'}
- FAQ présente: {'Oui' if data.has_faq else 'Non'}
- Google Posts récents: {'Oui' if data.has_recent_post else 'Non'}
- Attributs configurés: {'Oui' if data.has_attributes else 'Non'}
- Lien commande/réservation: {'Oui' if data.has_order_link else 'Non'}
- Facebook actif: {'Oui' if data.facebook_active else 'Non'}
- Instagram actif: {'Oui' if data.instagram_active else 'Non'}

CRITÈRES FAIBLES (score ≤ 2/5): {', '.join(weak_criteria) if weak_criteria else 'Aucun'}
CRITÈRES FORTS (score ≥ 4/5): {', '.join(strong_criteria) if strong_criteria else 'Aucun'}

DISTRIBUTION DES ÉTOILES:
- 5 étoiles: {data.star_distribution.get(5, 0)}
- 4 étoiles: {data.star_distribution.get(4, 0)}
- 3 étoiles: {data.star_distribution.get(3, 0)}
- 2 étoiles: {data.star_distribution.get(2, 0)}
- 1 étoile: {data.star_distribution.get(1, 0)}
"""

    # Ajouter les avis récents
    if data.recent_reviews:
        summary += "\nAVIS RÉCENTS:\n"
        for i, review in enumerate(data.recent_reviews[:5], 1):
            responded_text = "✅ Répondu" if review.get("responded") else "❌ Sans réponse"
            summary += (
                f"{i}. {review.get('rating', '?')}⭐ — {review.get('author', 'Anonyme')} "
                f"({review.get('date', 'Date inconnue')}) [{responded_text}]\n"
                f"   \"{review.get('text', '')[:200]}\"\n"
            )

    return summary


def generate_key_findings(data: RestaurantData) -> list[str]:
    """Génère 3 constats clés via Claude analysant les métriques les plus faibles.

    Returns:
        Liste de 3 constats en français québécois.
    """
    if not ANTHROPIC_API_KEY:
        return _fallback_key_findings(data)

    data_summary = _build_data_summary(data)

    prompt = f"""Voici les données d'audit du restaurant:

{data_summary}

Génère exactement 3 constats clés (key findings) qui analysent les points les plus faibles de ce profil.
Chaque constat doit être UNE phrase concise et percutante.
Concentre-toi sur les problèmes les plus critiques qui affectent la visibilité en ligne.

Format ta réponse EXACTEMENT comme suit (une phrase par ligne, sans numérotation, sans tiret):
Constat 1
Constat 2
Constat 3"""

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=500,
            system=CLAUDE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()
        findings = [line.strip() for line in text.split("\n") if line.strip()]
        return findings[:3] if len(findings) >= 3 else findings + _fallback_key_findings(data)[len(findings):]

    except Exception as e:
        logger.error("Erreur Claude API (constats): %s", e)
        return _fallback_key_findings(data)


def generate_recommendations(data: RestaurantData) -> list[str]:
    """Génère 3 recommandations prioritaires via Claude.

    Returns:
        Liste de 3 recommandations numérotées en français québécois.
    """
    if not ANTHROPIC_API_KEY:
        return _fallback_recommendations(data)

    data_summary = _build_data_summary(data)

    prompt = f"""Voici les données d'audit du restaurant:

{data_summary}

Génère exactement 3 recommandations prioritaires et actionnables pour améliorer la présence numérique de ce restaurant.
Chaque recommandation doit être concrète, spécifique et réalisable rapidement.
Ordonne-les par impact potentiel (la plus importante en premier).

Format ta réponse EXACTEMENT comme suit (sans autre texte):
1. Recommandation un
2. Recommandation deux
3. Recommandation trois"""

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=500,
            system=CLAUDE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        # Clean numbering if present
        recommendations = []
        for line in lines:
            cleaned = line.lstrip("0123456789.").strip()
            if cleaned:
                recommendations.append(cleaned)

        return recommendations[:3] if len(recommendations) >= 3 else recommendations + _fallback_recommendations(data)[len(recommendations):]

    except Exception as e:
        logger.error("Erreur Claude API (recommandations): %s", e)
        return _fallback_recommendations(data)


def _fallback_key_findings(data: RestaurantData) -> list[str]:
    """Constats de secours générés sans IA."""
    findings = []

    if data.response_rate < 50:
        findings.append(
            f"Le taux de réponse aux avis est critique à {data.response_rate:.0f}%, "
            f"ce qui nuit à la confiance des clients potentiels."
        )

    if data.photo_count < 5:
        findings.append(
            f"Avec seulement {data.photo_count} photo(s), le profil manque d'attrait visuel "
            f"et perd des opportunités de conversion."
        )

    if not data.has_description:
        findings.append(
            "L'absence de description d'entreprise réduit la visibilité dans les "
            "recherches locales et le référencement naturel."
        )

    if not data.has_menu:
        findings.append(
            "Le menu n'est pas ajouté au profil Google, ce qui diminue l'engagement "
            "des clients qui cherchent des options de restauration."
        )

    if not data.has_recent_post:
        findings.append(
            "Aucun Google Post récent n'a été publié, ce qui signale à Google un profil inactif."
        )

    if data.rating < 4.0:
        findings.append(
            f"La note moyenne de {data.rating}/5.0 est en dessous du seuil de confiance "
            f"des consommateurs et nécessite une attention immédiate."
        )

    # Return top 3
    return findings[:3] if findings else [
        "Le profil Google Business nécessite une optimisation globale.",
        "La présence en ligne du restaurant est insuffisante pour le marché actuel.",
        "Des améliorations rapides peuvent significativement augmenter la visibilité locale.",
    ]


def _fallback_recommendations(data: RestaurantData) -> list[str]:
    """Recommandations de secours générées sans IA."""
    recommendations = []

    if data.response_rate < 70:
        recommendations.append(
            "Répondre à tous les avis Google dans les 24 heures — cela améliore "
            "le référencement local et montre que vous êtes à l'écoute."
        )

    if data.photo_count < 10:
        recommendations.append(
            "Ajouter au minimum 10 photos de qualité (plats, intérieur, équipe) "
            "pour augmenter l'engagement de 35%."
        )

    if not data.has_recent_post:
        recommendations.append(
            "Publier un Google Post par semaine (promotion, nouvel item, événement) "
            "pour signaler à Google que votre profil est actif."
        )

    if not data.has_description:
        recommendations.append(
            "Rédiger une description d'entreprise optimisée avec les mots-clés "
            "principaux de votre type de cuisine et votre quartier."
        )

    if not data.has_menu:
        recommendations.append(
            "Ajouter votre menu complet avec photos et prix dans la section "
            "Menu de Google Business Profile."
        )

    return recommendations[:3] if recommendations else [
        "Optimiser la fiche Google Business Profile avec toutes les informations manquantes.",
        "Mettre en place une stratégie de réponse systématique aux avis clients.",
        "Créer un calendrier de publications Google Posts hebdomadaires.",
    ]
