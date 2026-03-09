"""RestoBoom Audit Generator — Application Streamlit principale.

Outil de génération d'audits de présence numérique pour les restaurants
à service rapide au Québec. Génère un rapport PDF professionnel de 2 pages.
"""

from __future__ import annotations

import os
import re
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

from config import RestaurantData, ANTHROPIC_API_KEY, GOOGLE_PLACES_API_KEY, SERPAPI_KEY
from google_scraper import fetch_restaurant_data
from ai_analyzer import generate_key_findings, generate_recommendations
from pdf_generator import generate_pdf

# --- Page Configuration ---
st.set_page_config(
    page_title="RestoBoom — Audit de Présence Numérique",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        background-color: #1B4332;
        padding: 20px 30px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 28px;
    }
    .main-header p {
        color: #B7E4C7;
        margin: 5px 0 0 0;
        font-size: 14px;
    }
    .metric-card {
        background: #F8F9FA;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        border-left: 4px solid #2D6A4F;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1B4332;
    }
    .metric-label {
        font-size: 12px;
        color: #6C757D;
    }
    .score-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    .score-green { background: #D4EDDA; color: #155724; }
    .score-amber { background: #FFF3CD; color: #856404; }
    .score-red { background: #F8D7DA; color: #721C24; }
    .stButton > button {
        background-color: #2D6A4F;
        color: white;
        border: none;
        padding: 10px 30px;
        font-size: 16px;
        border-radius: 8px;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #1B4332;
        color: white;
    }
    div[data-testid="stDownloadButton"] > button {
        background-color: #E76F51;
        color: white;
        border: none;
        font-size: 16px;
        border-radius: 8px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def _is_google_maps_url(text: str) -> bool:
    """Vérifie si le texte est une URL Google Maps."""
    patterns = [
        r"google\.\w+/maps",
        r"maps\.google\.\w+",
        r"goo\.gl/maps",
        r"maps\.app\.goo\.gl",
    ]
    return any(re.search(p, text) for p in patterns)


def _get_score_class(score: int, max_score: int = 100) -> str:
    """Retourne la classe CSS pour la couleur du score."""
    pct = (score / max_score) * 100 if max_score > 0 else 0
    if pct >= 70:
        return "score-green"
    elif pct >= 40:
        return "score-amber"
    return "score-red"


def _check_api_keys() -> list[str]:
    """Vérifie la configuration des clés API."""
    warnings = []
    if not GOOGLE_PLACES_API_KEY and not SERPAPI_KEY:
        warnings.append(
            "Aucune clé API de données configurée (GOOGLE_PLACES_API_KEY ou SERPAPI_KEY). "
            "Les données seront simulées."
        )
    if not ANTHROPIC_API_KEY:
        warnings.append(
            "Clé ANTHROPIC_API_KEY non configurée. Les analyses IA utiliseront "
            "des textes génériques."
        )
    return warnings


def _display_metrics_preview(data: RestaurantData):
    """Affiche un aperçu des métriques clés dans Streamlit."""
    st.markdown("### Aperçu des données collectées")

    # Restaurant info
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Restaurant:** {data.name}")
        st.markdown(f"**Adresse:** {data.address}")
    with col2:
        st.markdown(f"**Téléphone:** {data.phone}")
        if data.website:
            st.markdown(f"**Site web:** {data.website}")

    st.divider()

    # Score cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        score_class = _get_score_class(data.total_score, 100)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">SCORE TOTAL</div>
            <div class="metric-value">
                <span class="score-badge {score_class}">{data.total_score}/100</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.metric("Note moyenne", f"{data.rating} ⭐", delta=None)

    with col3:
        st.metric("Nombre d'avis", data.total_reviews)

    with col4:
        st.metric("Taux de réponse", f"{data.response_rate:.0f}%")

    st.divider()

    # Sub-scores
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Complétude GBP:** {data.gbp_score}/50")
        st.progress(data.gbp_score / 50)
    with col2:
        st.markdown(f"**Santé des avis:** {data.review_health_score}/30")
        st.progress(data.review_health_score / 30)
    with col3:
        st.markdown(f"**Présence sociale:** {data.social_score}/20")
        st.progress(data.social_score / 20)

    # GBP Criteria details
    with st.expander("Détail des critères GBP"):
        for name, score in data.gbp_criteria_scores:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.text(name)
            with col_b:
                st.progress(score / 5, text=f"{score}/5")


def main():
    """Point d'entrée principal de l'application Streamlit."""

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>RestoBoom</h1>
        <p>Générateur d'audit de présence numérique pour restaurants</p>
    </div>
    """, unsafe_allow_html=True)

    # API key warnings
    warnings = _check_api_keys()
    for warning in warnings:
        st.warning(warning)

    # --- Input Section ---
    st.markdown("### Informations du restaurant")

    input_method = st.radio(
        "Méthode de recherche:",
        ["Nom du restaurant + Ville", "URL Google Maps"],
        horizontal=True,
        label_visibility="collapsed",
    )

    query = ""
    is_url = False

    if input_method == "URL Google Maps":
        url_input = st.text_input(
            "URL Google Maps",
            placeholder="https://maps.google.com/maps/place/...",
            help="Collez l'URL complète de la fiche Google Maps du restaurant.",
        )
        query = url_input
        is_url = True
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            name_input = st.text_input(
                "Nom du restaurant",
                placeholder="Ex: Pizza Salvatoré",
            )
        with col2:
            city_input = st.text_input(
                "Ville",
                placeholder="Ex: Québec",
            )
        if name_input and city_input:
            query = f"{name_input}, {city_input}, QC, Canada"

    # Social media inputs (manual since not available via Google APIs)
    with st.expander("Réseaux sociaux (optionnel)"):
        col1, col2 = st.columns(2)
        with col1:
            fb_active = st.checkbox(
                "Facebook actif (publication dans les 30 derniers jours)",
                value=False,
            )
        with col2:
            ig_active = st.checkbox(
                "Instagram actif (publication dans les 30 derniers jours)",
                value=False,
            )

    # --- Generate Button ---
    st.markdown("")
    generate_clicked = st.button("Générer l'Audit", type="primary", use_container_width=True)

    if generate_clicked and query:
        with st.spinner("Collecte des données en cours... Veuillez patienter."):
            # Fetch restaurant data
            data = fetch_restaurant_data(query, is_url=is_url)

            # Set social media flags from manual input
            data.facebook_active = fb_active
            data.instagram_active = ig_active

            # Recalculate scores with social data
            from google_scraper import calculate_scores
            data = calculate_scores(data)

        st.success(f"Données collectées pour **{data.name}**")

        # Display metrics preview
        _display_metrics_preview(data)

        # Generate AI analysis
        with st.spinner("Analyse IA en cours..."):
            key_findings = generate_key_findings(data)
            recommendations = generate_recommendations(data)

        # Display findings preview
        st.markdown("### Constats clés")
        for finding in key_findings:
            st.markdown(f"- {finding}")

        st.markdown("### Recommandations prioritaires")
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"**{i}.** {rec}")

        st.divider()

        # Generate PDF
        with st.spinner("Génération du PDF..."):
            pdf_bytes = generate_pdf(data, key_findings, recommendations)

        # Store in session state
        st.session_state["pdf_bytes"] = pdf_bytes
        st.session_state["restaurant_name"] = data.name

    elif generate_clicked and not query:
        st.error("Veuillez entrer un nom de restaurant et une ville, ou une URL Google Maps.")

    # --- Download Button ---
    if "pdf_bytes" in st.session_state:
        safe_name = re.sub(r"[^\w\s-]", "", st.session_state.get("restaurant_name", "restaurant"))
        safe_name = safe_name.strip().replace(" ", "_")
        filename = f"Audit_RestoBoom_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"

        st.download_button(
            label="Télécharger le rapport PDF",
            data=st.session_state["pdf_bytes"],
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
