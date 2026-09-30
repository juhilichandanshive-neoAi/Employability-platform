"""Generate a real, downloadable PDF from the current session's data."""

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
import re
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from xml.sax.saxutils import escape


def _safe(value: Any) -> str:
    return escape(str(value if value not in (None, "") else "Not provided"))


def generate_session_report(
    app_data: dict[str, Any],
    included_sections: set[str],
) -> tuple[bytes, str]:
    profile = app_data["profile"]
    score = app_data["score"]
    stream = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportSection",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0E7490"),
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportBody",
            parent=styles["BodyText"],
            alignment=TA_LEFT,
            fontSize=9,
            leading=13,
        )
    )
    story = [
        Paragraph("Employability session report", styles["Title"]),
        Paragraph(
            "Generated from the profile and assessment data in this session. "
            "No cohort comparison or salary-model estimate is included.",
            styles["ReportBody"],
        ),
        Spacer(1, 6 * mm),
    ]

    if "Profile summary" in included_sections:
        story.extend(
            [
                Paragraph("Profile summary", styles["ReportSection"]),
                Paragraph(
                    f"Name: {_safe(profile.get('name'))}<br/>"
                    f"Email: {_safe(profile.get('email'))}<br/>"
                    f"Target role: {_safe(profile.get('target_role'))}<br/>"
                    f"Education: {_safe(profile.get('degree'))}<br/>"
                    f"Profile completion: {app_data['profile_completion']}%",
                    styles["ReportBody"],
                ),
            ]
        )

    if "Employability score" in included_sections:
        story.append(Paragraph("Employability score", styles["ReportSection"]))
        if score["overall"] is None:
            story.append(
                Paragraph(
                    "No score is available. Complete and save a profile and submit an assessment.",
                    styles["ReportBody"],
                )
            )
        else:
            story.append(
                Paragraph(
                    f"Score: {score['overall']}/100 · {score['band']} · {score['verdict']}",
                    styles["ReportBody"],
                )
            )
            component_rows = [["Component", "Score / 100"]]
            component_rows.extend(
                [item["label"], str(item["value"])]
                for item in score["breakdown"]
            )
            table = Table(component_rows, repeatRows=1, hAlign="LEFT")
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E0F2FE")),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("PADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.extend([Spacer(1, 3 * mm), table])

    if "Skill gap analysis" in included_sections:
        story.append(Paragraph("Skill gap analysis", styles["ReportSection"]))
        gap_rows = [["Skill", "Recorded level", "Role requirement", "Priority"]]
        gap_rows.extend(
            [row["skill"], row["have"], row["required"], row["priority"]]
            for row in app_data["skill_gap"]["rows"]
        )
        if len(gap_rows) == 1:
            story.append(
                Paragraph("No skill levels have been recorded for comparison.", styles["ReportBody"])
            )
        else:
            table = Table(gap_rows, repeatRows=1, hAlign="LEFT")
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E0F2FE")),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("PADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.append(table)

    if "Assessment details" in included_sections:
        story.append(Paragraph("Assessment details", styles["ReportSection"]))
        assessment = app_data["analytics"]["latest_assessment"]
        if not assessment:
            story.append(Paragraph("No completed assessment is available.", styles["ReportBody"]))
        else:
            story.append(
                Paragraph(
                    f"Assessment: {_safe(assessment.get('domain_name'))} · "
                    f"{_safe(assessment.get('difficulty'))}<br/>"
                    f"Result: {assessment['overall_pct']}% "
                    f"({assessment['correct_count']} of {assessment['total']} correct)",
                    styles["ReportBody"],
                )
            )
            category_rows = [["Area", "Score"]]
            category_rows.extend(
                [item["name"], f"{item['pct']}%"]
                for item in assessment.get("categories", [])
            )
            if len(category_rows) > 1:
                story.append(Spacer(1, 3 * mm))
                story.append(Table(category_rows, repeatRows=1))

    if "Career recommendations" in included_sections:
        story.append(Paragraph("Career recommendations", styles["ReportSection"]))
        if not app_data["career_matches"]:
            story.append(
                Paragraph("Add skill levels to calculate role matches.", styles["ReportBody"])
            )
        else:
            for role in app_data["career_matches"]:
                story.append(
                    Paragraph(
                        f"{_safe(role['role'])}: {role['match']}% calculated fit from recorded "
                        f"skills; {role['row_count']} rows in the dataset snapshot.",
                        styles["ReportBody"],
                    )
                )

    if "Certification recommendations" in included_sections:
        story.append(Paragraph("Certification recommendations", styles["ReportSection"]))
        if not app_data["certification_recommendations"]:
            story.append(
                Paragraph("No certification recommendations are available from the recorded gaps.", styles["ReportBody"])
            )
        else:
            for item in app_data["certification_recommendations"]:
                story.append(
                    Paragraph(
                        f"{_safe(item['name'])} — {_safe(item['provider'])}; "
                        f"addresses: {_safe(', '.join(item['skills']))}. "
                        "Current-source pricing and ratings are not available.",
                        styles["ReportBody"],
                    )
                )

    if "Learning roadmap" in included_sections:
        story.append(Paragraph("Learning roadmap", styles["ReportSection"]))
        if not app_data["roadmap"]["tasks"]:
            story.append(Paragraph("No roadmap tasks are available yet.", styles["ReportBody"]))
        else:
            for index, task in enumerate(app_data["roadmap"]["tasks"], start=1):
                cert = f" Suggested certification: {_safe(task['certification'])}." if task.get("certification") else ""
                story.append(
                    Paragraph(
                        f"{index}. {_safe(task['title'])} — {_safe(task['reason'])}{cert}",
                        styles["ReportBody"],
                    )
                )

    story.extend(
        [
            Spacer(1, 8 * mm),
            Paragraph(
                "Limitations: job-market evidence is a bundled dataset snapshot, not live listings. "
                "The approved salary model artifact is unavailable, so this report contains no "
                "ML salary prediction.",
                styles["Italic"],
            ),
        ]
    )
    document = SimpleDocTemplate(
        stream,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Employability session report",
        author="Employability Platform",
    )
    document.build(story)
    name = re.sub(r"[^a-zA-Z0-9-]+", "-", profile.get("name", "").strip()).strip("-") or "student"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return stream.getvalue(), f"employability-report-{name}-{timestamp}.pdf"