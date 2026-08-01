"""
Stage 7: PDF export.

Takes a saved analysis (the same dict shape database.get_analysis returns)
and builds a clean, professional PDF report - company name, date, ratios
table, and the AI's plain-language explanations, with a disclaimer.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

# Colors matched loosely to the frontend's "ledger" theme
INK = colors.HexColor("#14231F")
ACCENT = colors.HexColor("#3D6B52")
WATCH = colors.HexColor("#B8863B")
CONCERN = colors.HexColor("#A8432F")
MUTED = colors.HexColor("#6B7570")
RULE = colors.HexColor("#D8D4C8")

CONCERN_COLORS = {
    "healthy": ACCENT,
    "watch": WATCH,
    "concerning": CONCERN,
}


def _format_ratio_name(key: str) -> str:
    return key.replace("_", " ").title()


def generate_pdf(analysis_record: dict) -> bytes:
    """
    Build a PDF report from a saved analysis record (as returned by
    database.get_analysis). Returns the PDF as raw bytes, ready to
    stream back in an HTTP response - no file is written to disk.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], textColor=INK, fontSize=22, spaceAfter=4,
    )
    meta_style = ParagraphStyle(
        "Meta", parent=styles["Normal"], textColor=MUTED, fontSize=9, spaceAfter=20,
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"], textColor=INK, fontSize=12,
        spaceBefore=18, spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], textColor=INK, fontSize=10, leading=15,
    )
    summary_style = ParagraphStyle(
        "Summary", parent=styles["Normal"], textColor=INK, fontSize=11, leading=16,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer", parent=styles["Normal"], textColor=MUTED, fontSize=8, leading=12,
    )

    story = []

    company_name = analysis_record.get("company_name", "Untitled")
    created_at = analysis_record.get("created_at", "")
    try:
        formatted_date = datetime.fromisoformat(created_at).strftime("%B %d, %Y")
    except (ValueError, TypeError):
        formatted_date = created_at

    story.append(Paragraph("Financial Ratio Analysis", title_style))
    story.append(Paragraph(f"{company_name} &nbsp;&nbsp;|&nbsp;&nbsp; {formatted_date}", meta_style))
    story.append(HRFlowable(width="100%", thickness=1, color=RULE, spaceAfter=12))

    # Warnings, if any
    warnings = analysis_record.get("warnings") or []
    if warnings:
        story.append(Paragraph("Worth Double-Checking", section_style))
        for w in warnings:
            story.append(Paragraph(f"• {w}", body_style))
        story.append(Spacer(1, 6))

    # Overall summary
    summary = analysis_record.get("analysis", {}).get("overall_summary", "")
    if summary:
        story.append(Paragraph("Summary", section_style))
        story.append(Paragraph(summary, summary_style))

    # Ratios table
    ratios = analysis_record.get("ratios", {})
    if ratios:
        story.append(Paragraph("Ratios", section_style))
        table_data = [["Ratio", "Value"]]
        for key, value in ratios.items():
            display_value = "N/A" if value is None else str(value)
            table_data.append([_format_ratio_name(key), display_value])

        table = Table(table_data, colWidths=[3.5 * inch, 2.5 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), INK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F5F3")]),
            ("GRID", (0, 0), (-1, -1), 0.5, RULE),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(table)

    # Explanations
    explanations = analysis_record.get("analysis", {}).get("explanations", [])
    if explanations:
        story.append(Paragraph("Ratio by Ratio", section_style))
        for exp in explanations:
            level = exp.get("concern_level", "watch")
            color = CONCERN_COLORS.get(level, WATCH)
            name_style = ParagraphStyle(
                "RatioName", parent=styles["Normal"], textColor=INK,
                fontSize=11, fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=2,
            )
            level_style = ParagraphStyle(
                "Level", parent=styles["Normal"], textColor=color,
                fontSize=8, fontName="Helvetica-Bold", spaceAfter=4,
            )
            story.append(Paragraph(exp.get("ratio_name", ""), name_style))
            story.append(Paragraph(exp.get("explanation", ""), body_style))
            story.append(Paragraph(level.upper(), level_style))

    # Disclaimer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=RULE, spaceAfter=8))
    story.append(Paragraph(
        "This is an AI-generated analysis for informational purposes only, "
        "not professional financial or tax advice.",
        disclaimer_style,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()