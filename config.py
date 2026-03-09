"""Configuration et constantes pour RestoBoom Audit Generator."""

import os
from dataclasses import dataclass, field


# Clés API (via variables d'environnement)
GOOGLE_PLACES_API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "")
SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

# Couleurs de la marque
BRAND_DARK_GREEN = "#1B4332"
BRAND_GREEN = "#2D6A4F"
BRAND_LIGHT_GREEN = "#52B788"
BRAND_ORANGE = "#E76F51"
BRAND_WHITE = "#FFFFFF"
BRAND_LIGHT_GRAY = "#F8F9FA"
BRAND_DARK_TEXT = "#212529"

# Score color thresholds
SCORE_GREEN_THRESHOLD = 70
SCORE_AMBER_THRESHOLD = 40

SCORE_GREEN = "#2D6A4F"
SCORE_AMBER = "#E9C46A"
SCORE_RED = "#E76F51"


@dataclass
class ScoringCriteria:
    """Critères de notation pour le GBP Completeness Score."""

    name: str
    max_score: int = 5
    score: int = 0
    description: str = ""


# GBP Completeness criteria names (pour le tableau)
GBP_CRITERIA_NAMES: list[str] = [
    "NAP (Nom / Adresse / Téléphone)",
    "Catégories d'entreprise",
    "Heures d'ouverture complètes",
    "Photos du profil",
    "Description de l'entreprise",
    "Menu / Produits ajoutés",
    "FAQ / Questions-Réponses",
    "Google Posts (30 derniers jours)",
    "Attributs et services",
    "Lien commande / réservation",
]

# Review Health scoring thresholds
RATING_THRESHOLDS: list[tuple[float, int]] = [
    (4.5, 10),
    (4.0, 7),
    (3.5, 4),
    (0.0, 1),
]

RESPONSE_RATE_THRESHOLDS: list[tuple[float, int]] = [
    (90.0, 10),
    (70.0, 7),
    (50.0, 4),
    (0.0, 1),
]

# Claude model
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Claude system prompt
CLAUDE_SYSTEM_PROMPT = (
    "Tu es un expert en marketing numérique pour restaurants au Québec. "
    "Analyse les données suivantes d'un profil Google Business et génère "
    "des constats et recommandations en français québécois (pas de France). "
    "Sois direct, concret et actionnable. Utilise un ton professionnel mais accessible."
)

# PDF constants
PDF_PAGE_WIDTH = 612  # Letter size
PDF_PAGE_HEIGHT = 792
PDF_MARGIN = 40


@dataclass
class RestaurantData:
    """Données collectées pour un restaurant."""

    name: str = "Non disponible"
    address: str = "Non disponible"
    phone: str = "Non disponible"
    rating: float = 0.0
    total_reviews: int = 0
    unresponded_reviews: int = 0
    response_rate: float = 0.0
    recent_reviews: list = field(default_factory=list)
    business_hours: dict = field(default_factory=dict)
    hours_complete: bool = False
    photo_count: int = 0
    has_menu: bool = False
    has_description: bool = False
    description: str = ""
    categories: list = field(default_factory=list)
    website: str = ""
    last_post_date: str = ""
    has_recent_post: bool = False
    has_faq: bool = False
    has_attributes: bool = False
    has_order_link: bool = False
    star_distribution: dict = field(default_factory=lambda: {5: 0, 4: 0, 3: 0, 2: 0, 1: 0})
    facebook_active: bool = False
    instagram_active: bool = False

    # Scores calculés
    gbp_score: int = 0
    review_health_score: int = 0
    social_score: int = 0
    total_score: int = 0
    gbp_criteria_scores: list = field(default_factory=list)
