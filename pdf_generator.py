"""Module de génération PDF pour l'audit RestoBoom.

Crée un rapport PDF professionnel de 2 pages au format Letter
avec les données d'audit et les recommandations IA.
"""

from __future__ import annotations

import io
import math
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Circle, String, Rect, Line
from reportlab.graphics import renderPDF

from config import (
    BRAND_DARK_GREEN,
    BRAND_GREEN,
    BRAND_LIGHT_GREEN,
    BRAND_ORANGE,
    BRAND_WHITE,
    BRAND_LIGHT_GRAY,
    BRAND_DARK_TEXT,
    SCORE_GREEN,
    SCORE_AMBER,
    SCORE_RED,
    SCORE_GREEN_THRESHOLD,
    SCORE_AMBER_THRESHOLD,
    PDF_PAGE_WIDTH,
    PDF_PAGE_HEIGHT,
    PDF_MARGIN,
    RestaurantData,
)

# Color conversions
def hex_to_color(hex_color: str) -> colors.Color:
    """Convertit un code hex en couleur ReportLab."""
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return colors.Color(r, g, b)


# Brand colors as ReportLab colors
C_DARK_GREEN = hex_to_color(BRAND_DARK_GREEN)
C_GREEN = hex_to_color(BRAND_GREEN)
C_LIGHT_GREEN = hex_to_color(BRAND_LIGHT_GREEN)
C_ORANGE = hex_to_color(BRAND_ORANGE)
C_WHITE = colors.white
C_LIGHT_GRAY = hex_to_color(BRAND_LIGHT_GRAY)
C_DARK_TEXT = hex_to_color(BRAND_DARK_TEXT)


def _get_score_color(score: int, max_score: int = 100) -> colors.Color:
    """Retourne la couleur appropriée selon le score."""
    pct = (score / max_score) * 100 if max_score > 0 else 0
    if pct >= SCORE_GREEN_THRESHOLD:
        return hex_to_color(SCORE_GREEN)
    elif pct >= SCORE_AMBER_THRESHOLD:
        return hex_to_color(SCORE_AMBER)
    return hex_to_color(SCORE_RED)


def _draw_score_circle(canvas, x: float, y: float, score: int, max_score: int = 100, radius: float = 40):
    """Dessine un cercle de score avec couleur dynamique."""
    score_color = _get_score_color(score, max_score)

    # Outer circle (background)
    canvas.setFillColor(colors.Color(0.93, 0.93, 0.93))
    canvas.circle(x, y, radius, fill=1, stroke=0)

    # Inner circle with score color
    canvas.setFillColor(score_color)
    canvas.circle(x, y, radius - 4, fill=1, stroke=0)

    # Score text
    canvas.setFillColor(C_WHITE)
    canvas.setFont("Helvetica-Bold", 22)
    score_text = f"{score}"
    canvas.drawCentredString(x, y + 5, score_text)
    canvas.setFont("Helvetica", 10)
    canvas.drawCentredString(x, y - 12, f"/ {max_score}")


def _draw_bar(canvas, x: float, y: float, score: int, max_score: int = 5, width: float = 80, height: float = 8):
    """Dessine une barre de progression."""
    # Background bar
    canvas.setFillColor(colors.Color(0.9, 0.9, 0.9))
    canvas.rect(x, y, width, height, fill=1, stroke=0)

    # Score bar
    if max_score > 0:
        fill_width = (score / max_score) * width
        score_color = _get_score_color(score, max_score)
        canvas.setFillColor(score_color)
        canvas.rect(x, y, fill_width, height, fill=1, stroke=0)


def _draw_star_rating(canvas, x: float, y: float, rating: float, size: float = 10):
    """Dessine des étoiles pour la notation."""
    canvas.setFont("Helvetica", size)
    for i in range(5):
        if rating >= i + 1:
            canvas.setFillColor(colors.Color(1, 0.84, 0))  # Gold
            canvas.drawString(x + i * (size + 2), y, "★")
        elif rating >= i + 0.5:
            canvas.setFillColor(colors.Color(1, 0.84, 0))
            canvas.drawString(x + i * (size + 2), y, "★")
        else:
            canvas.setFillColor(colors.Color(0.8, 0.8, 0.8))
            canvas.drawString(x + i * (size + 2), y, "★")


def generate_pdf(
    data: RestaurantData,
    key_findings: list[str],
    recommendations: list[str],
) -> bytes:
    """Génère le PDF d'audit complet de 2 pages.

    Args:
        data: Données du restaurant avec scores calculés.
        key_findings: 3 constats clés générés par Claude.
        recommendations: 3 recommandations prioritaires générées par Claude.

    Returns:
        Contenu du PDF en bytes.
    """
    buffer = io.BytesIO()

    from reportlab.pdfgen import canvas as canvas_module

    c = canvas_module.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = PDF_MARGIN
    content_width = width - 2 * margin
    audit_date = datetime.now().strftime("%d %B %Y")

    # ============================================================
    # PAGE 1
    # ============================================================
    _draw_page1(c, width, height, margin, content_width, data, key_findings, audit_date)

    c.showPage()

    # ============================================================
    # PAGE 2
    # ============================================================
    _draw_page2(c, width, height, margin, content_width, data, recommendations, audit_date)

    c.save()
    buffer.seek(0)
    return buffer.read()


def _draw_page1(c, width, height, margin, content_width, data, key_findings, audit_date):
    """Dessine la page 1 du rapport."""
    # --- Header Banner ---
    banner_height = 70
    c.setFillColor(C_DARK_GREEN)
    c.rect(0, height - banner_height, width, banner_height, fill=1, stroke=0)

    # Logo text
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(margin, height - 45, "RESTOBOOM")

    # Subtitle
    c.setFont("Helvetica", 11)
    c.drawString(margin, height - 62, "AUDIT DE PRÉSENCE NUMÉRIQUE")

    # Date on right
    c.setFont("Helvetica", 9)
    c.drawRightString(width - margin, height - 45, audit_date)

    # --- Client Info Box ---
    y = height - banner_height - 15
    box_height = 55
    c.setFillColor(C_LIGHT_GRAY)
    c.roundRect(margin, y - box_height, content_width, box_height, 5, fill=1, stroke=0)

    c.setFillColor(C_DARK_TEXT)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin + 10, y - 18, data.name)
    c.setFont("Helvetica", 9)
    c.drawString(margin + 10, y - 32, f"Adresse: {data.address}")
    c.drawString(margin + 10, y - 44, f"Date de l'audit: {audit_date}  |  Préparé par: Konsta — RestoBoom")

    # Website on right side
    if data.website:
        c.setFont("Helvetica", 8)
        c.setFillColor(C_GREEN)
        display_url = data.website[:50] + "..." if len(data.website) > 50 else data.website
        c.drawRightString(width - margin - 10, y - 18, display_url)
        c.setFillColor(C_DARK_TEXT)

    # --- Global Score Circle ---
    y = y - box_height - 15
    score_section_height = 100

    # Section title
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(C_DARK_GREEN)
    c.drawString(margin, y - 5, "SCORE GLOBAL")

    # Draw score circle
    circle_x = margin + 55
    circle_y = y - 60
    _draw_score_circle(c, circle_x, circle_y, data.total_score, 100, radius=38)

    # Sub-scores next to the circle
    sub_x = margin + 120
    sub_y = y - 25

    c.setFont("Helvetica", 9)
    c.setFillColor(C_DARK_TEXT)

    # GBP Score
    c.drawString(sub_x, sub_y, f"Complétude GBP:")
    c.setFont("Helvetica-Bold", 10)
    gbp_color = _get_score_color(data.gbp_score, 50)
    c.setFillColor(gbp_color)
    c.drawString(sub_x + 105, sub_y, f"{data.gbp_score}/50")
    _draw_bar(c, sub_x + 150, sub_y + 1, data.gbp_score, 50, width=120, height=7)

    # Review Health Score
    sub_y -= 20
    c.setFont("Helvetica", 9)
    c.setFillColor(C_DARK_TEXT)
    c.drawString(sub_x, sub_y, f"Santé des avis:")
    c.setFont("Helvetica-Bold", 10)
    review_color = _get_score_color(data.review_health_score, 30)
    c.setFillColor(review_color)
    c.drawString(sub_x + 105, sub_y, f"{data.review_health_score}/30")
    _draw_bar(c, sub_x + 150, sub_y + 1, data.review_health_score, 30, width=120, height=7)

    # Social Score
    sub_y -= 20
    c.setFont("Helvetica", 9)
    c.setFillColor(C_DARK_TEXT)
    c.drawString(sub_x, sub_y, f"Présence sociale:")
    c.setFont("Helvetica-Bold", 10)
    social_color = _get_score_color(data.social_score, 20)
    c.setFillColor(social_color)
    c.drawString(sub_x + 105, sub_y, f"{data.social_score}/20")
    _draw_bar(c, sub_x + 150, sub_y + 1, data.social_score, 20, width=120, height=7)

    # --- GBP Scorecard Table ---
    y = y - score_section_height - 10
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(C_DARK_GREEN)
    c.drawString(margin, y, "FICHE D'ÉVALUATION GBP")

    y -= 10
    row_height = 20
    col_criteria_w = 250
    col_score_w = 50
    col_bar_w = content_width - col_criteria_w - col_score_w - 20

    # Table header
    y -= row_height
    c.setFillColor(C_DARK_GREEN)
    c.rect(margin, y, content_width, row_height, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin + 5, y + 6, "CRITÈRE")
    c.drawString(margin + col_criteria_w + 5, y + 6, "SCORE")
    c.drawString(margin + col_criteria_w + col_score_w + 10, y + 6, "NIVEAU")

    # Table rows
    for i, (criteria_name, criteria_score) in enumerate(data.gbp_criteria_scores):
        y -= row_height
        # Alternate row background
        if i % 2 == 0:
            c.setFillColor(C_LIGHT_GRAY)
            c.rect(margin, y, content_width, row_height, fill=1, stroke=0)

        c.setFillColor(C_DARK_TEXT)
        c.setFont("Helvetica", 8)
        c.drawString(margin + 5, y + 6, criteria_name)

        c.setFont("Helvetica-Bold", 8)
        score_color = _get_score_color(criteria_score, 5)
        c.setFillColor(score_color)
        c.drawString(margin + col_criteria_w + 15, y + 6, f"{criteria_score}/5")

        # Bar
        _draw_bar(c, margin + col_criteria_w + col_score_w + 10, y + 5, criteria_score, 5, width=col_bar_w, height=7)

    # --- Key Findings Box ---
    y -= 25
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(C_DARK_GREEN)
    c.drawString(margin, y, "CONSTATS CLÉS")

    y -= 8
    findings_box_height = 12 + len(key_findings) * 25
    # Orange border box
    c.setStrokeColor(C_ORANGE)
    c.setLineWidth(2)
    c.setFillColor(colors.Color(1, 0.97, 0.95))  # Light orange bg
    c.roundRect(margin, y - findings_box_height, content_width, findings_box_height, 5, fill=1, stroke=1)
    c.setLineWidth(1)

    c.setFillColor(C_DARK_TEXT)
    c.setFont("Helvetica", 8)
    finding_y = y - 15
    for finding in key_findings[:3]:
        # Truncate if too long
        if len(finding) > 120:
            finding = finding[:117] + "..."
        c.drawString(margin + 12, finding_y, f"•  {finding}")
        finding_y -= 22

    # Footer line
    c.setStrokeColor(C_DARK_GREEN)
    c.setLineWidth(0.5)
    c.line(margin, 30, width - margin, 30)
    c.setFont("Helvetica", 7)
    c.setFillColor(C_GREEN)
    c.drawCentredString(width / 2, 18, "RestoBoom — Votre partenaire en marketing numérique pour restaurants | restoboom.com")


def _draw_page2(c, width, height, margin, content_width, data, recommendations, audit_date):
    """Dessine la page 2 du rapport."""
    # --- Header Banner (simplified) ---
    banner_height = 40
    c.setFillColor(C_DARK_GREEN)
    c.rect(0, height - banner_height, width, banner_height, fill=1, stroke=0)

    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, height - 28, "RESTOBOOM")
    c.setFont("Helvetica", 9)
    c.drawRightString(width - margin, height - 28, f"Audit — {data.name}")

    y = height - banner_height - 20

    # --- Review Analysis Section ---
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(C_DARK_GREEN)
    c.drawString(margin, y, "ANALYSE DES AVIS")

    y -= 20
    # Metrics row
    metrics = [
        ("Note moyenne", f"{data.rating}/5.0"),
        ("Total avis", str(data.total_reviews)),
        ("Sans réponse", str(data.unresponded_reviews)),
        ("Taux de réponse", f"{data.response_rate:.0f}%"),
    ]

    metric_width = content_width / 4
    for i, (label, value) in enumerate(metrics):
        mx = margin + i * metric_width
        # Metric box
        c.setFillColor(C_LIGHT_GRAY)
        c.roundRect(mx + 2, y - 35, metric_width - 6, 35, 3, fill=1, stroke=0)

        c.setFillColor(C_DARK_TEXT)
        c.setFont("Helvetica", 7)
        c.drawCentredString(mx + metric_width / 2, y - 12, label)
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(C_GREEN)
        c.drawCentredString(mx + metric_width / 2, y - 30, value)

    # --- Star Distribution ---
    y -= 55
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(C_DARK_GREEN)
    c.drawString(margin, y, "Distribution des étoiles")

    y -= 5
    total_star_reviews = sum(data.star_distribution.values())
    bar_max_width = 200

    for stars in range(5, 0, -1):
        y -= 16
        count = data.star_distribution.get(stars, 0)
        pct = (count / total_star_reviews * 100) if total_star_reviews > 0 else 0

        c.setFillColor(C_DARK_TEXT)
        c.setFont("Helvetica", 8)
        c.drawString(margin, y + 2, f"{stars} ★")

        # Bar
        bar_width = (count / total_star_reviews * bar_max_width) if total_star_reviews > 0 else 0
        c.setFillColor(colors.Color(0.9, 0.9, 0.9))
        c.rect(margin + 35, y + 1, bar_max_width, 10, fill=1, stroke=0)

        if stars >= 4:
            bar_color = hex_to_color(SCORE_GREEN)
        elif stars == 3:
            bar_color = hex_to_color(SCORE_AMBER)
        else:
            bar_color = hex_to_color(SCORE_RED)
        c.setFillColor(bar_color)
        c.rect(margin + 35, y + 1, bar_width, 10, fill=1, stroke=0)

        c.setFillColor(C_DARK_TEXT)
        c.setFont("Helvetica", 7)
        c.drawString(margin + 35 + bar_max_width + 5, y + 2, f"{count} ({pct:.0f}%)")

    # --- Top 3 Unresponded Reviews ---
    y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(C_DARK_GREEN)
    c.drawString(margin, y, "Avis récents sans réponse")

    unresponded_reviews = [r for r in data.recent_reviews if not r.get("responded", False)][:3]

    if not unresponded_reviews:
        y -= 15
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(C_DARK_TEXT)
        c.drawString(margin + 10, y, "Aucun avis sans réponse trouvé dans les données récentes.")
    else:
        for review in unresponded_reviews:
            y -= 5
            box_h = 40
            c.setStrokeColor(colors.Color(0.85, 0.85, 0.85))
            c.setFillColor(colors.Color(0.99, 0.99, 0.99))
            c.roundRect(margin, y - box_h, content_width, box_h, 3, fill=1, stroke=1)

            c.setFillColor(C_DARK_TEXT)
            c.setFont("Helvetica-Bold", 8)
            stars_text = "★" * review.get("rating", 0) + "☆" * (5 - review.get("rating", 0))
            c.drawString(margin + 8, y - 12, f"{stars_text}  —  {review.get('author', 'Anonyme')}  ({review.get('date', '')})")

            c.setFont("Helvetica", 7)
            text = review.get("text", "")[:150]
            if len(review.get("text", "")) > 150:
                text += "..."
            c.drawString(margin + 8, y - 25, f'"{text}"')

            c.setFont("Helvetica-Bold", 7)
            c.setFillColor(C_ORANGE)
            c.drawRightString(width - margin - 8, y - 12, "❌ Sans réponse")

            y -= box_h

    # --- Social Media Snapshot ---
    y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(C_DARK_GREEN)
    c.drawString(margin, y, "Aperçu des réseaux sociaux")

    y -= 20
    social_items = [
        ("Facebook", data.facebook_active),
        ("Instagram", data.instagram_active),
    ]

    for platform, active in social_items:
        status = "Actif (publication dans les 30 jours)" if active else "Inactif / Non vérifié"
        icon = "✅" if active else "❌"
        c.setFillColor(C_DARK_TEXT)
        c.setFont("Helvetica", 8)
        c.drawString(margin + 10, y, f"{icon}  {platform}: {status}")
        y -= 15

    # --- Combined Total Score ---
    y -= 10
    c.setFillColor(C_LIGHT_GRAY)
    c.roundRect(margin, y - 30, content_width, 30, 5, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(C_DARK_GREEN)
    c.drawString(margin + 10, y - 20, "SCORE TOTAL COMBINÉ:")
    score_color = _get_score_color(data.total_score, 100)
    c.setFillColor(score_color)
    c.setFont("Helvetica-Bold", 18)
    c.drawRightString(width - margin - 15, y - 22, f"{data.total_score} / 100")

    # --- Priority Recommendations ---
    y -= 50
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(C_DARK_GREEN)
    c.drawString(margin, y, "RECOMMANDATIONS PRIORITAIRES")

    y -= 10
    rec_box_height = 15 + len(recommendations) * 28
    c.setStrokeColor(C_GREEN)
    c.setLineWidth(2)
    c.setFillColor(colors.Color(0.94, 0.99, 0.96))
    c.roundRect(margin, y - rec_box_height, content_width, rec_box_height, 5, fill=1, stroke=1)
    c.setLineWidth(1)

    c.setFillColor(C_DARK_TEXT)
    rec_y = y - 18
    for i, rec in enumerate(recommendations[:3], 1):
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(C_GREEN)
        c.drawString(margin + 10, rec_y, f"{i}.")
        c.setFont("Helvetica", 8)
        c.setFillColor(C_DARK_TEXT)
        # Truncate if needed
        if len(rec) > 110:
            rec = rec[:107] + "..."
        c.drawString(margin + 25, rec_y, rec)
        rec_y -= 25

    # --- Bottom CTA Bar ---
    cta_height = 50
    c.setFillColor(C_DARK_GREEN)
    c.rect(0, 0, width, cta_height, fill=1, stroke=0)

    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(width / 2, cta_height - 18, "Prêt à corriger tout ça?")

    c.setFont("Helvetica", 9)
    c.drawCentredString(
        width / 2,
        cta_height - 35,
        "Contactez RestoBoom  |  info@restoboom.com  |  Partenaires Fondateurs: 149$/mois",
    )

    # Footer line above CTA
    c.setStrokeColor(C_LIGHT_GREEN)
    c.setLineWidth(2)
    c.line(0, cta_height, width, cta_height)
