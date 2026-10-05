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
            textColor=colors.HexColor("#7C3AED"),
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
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDE9FE")),
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
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDE9FE")),
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


def generate_development_plan_pdf(app_data: dict[str, Any]) -> tuple[bytes, str]:
    """Generate a comprehensive, professionally styled PDF Development Plan."""
    profile = app_data["profile"]
    assessment = app_data["analytics"]["latest_assessment"]
    skill_gap = app_data["skill_gap"]
    roadmap = app_data["roadmap"]
    careers = app_data["career_matches"]

    stream = BytesIO()
    styles = getSampleStyleSheet()

    primary = colors.HexColor("#7C3AED")
    dark = colors.HexColor("#211C36")
    body_col = colors.HexColor("#3F3A52")
    border_col = colors.HexColor("#E5E1EE")
    bg_light = colors.HexColor("#F9F8FC")

    title_style = ParagraphStyle(
        "PlanTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=primary,
        spaceAfter=2,
    )
    subtitle_style = ParagraphStyle(
        "PlanSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=dark,
        spaceAfter=10,
    )
    h2_style = ParagraphStyle(
        "PlanH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=primary,
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "PlanBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=body_col,
    )
    table_cell = ParagraphStyle(
        "PlanTableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=dark,
    )
    table_header = ParagraphStyle(
        "PlanTableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white,
    )

    story = [
        Paragraph("EMPLOYAAI", title_style),
        Paragraph("PERSONALIZED EMPLOYABILITY DEVELOPMENT PLAN", subtitle_style),
        Paragraph(
            f"Generated on {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')} · Verified Assessment & Skill Gap Evidence",
            body_style,
        ),
        Spacer(1, 4 * mm),
    ]

    # 1. Candidate Profile
    story.append(Paragraph("1. Candidate Profile", h2_style))
    skills_str = ", ".join(f"{s['name']} ({s['level']}/5)" for s in profile.get("skills", [])) or "No skills recorded"
    profile_table_data = [
        [
            Paragraph("<b>Full Name:</b>", table_cell),
            Paragraph(_safe(profile.get("name")), table_cell),
            Paragraph("<b>Target Role:</b>", table_cell),
            Paragraph(_safe(profile.get("target_role")), table_cell),
        ],
        [
            Paragraph("<b>Email:</b>", table_cell),
            Paragraph(_safe(profile.get("email")), table_cell),
            Paragraph("<b>Degree / Major:</b>", table_cell),
            Paragraph(_safe(profile.get("degree")), table_cell),
        ],
        [
            Paragraph("<b>Semester:</b>", table_cell),
            Paragraph(_safe(profile.get("semester")), table_cell),
            Paragraph("<b>CGPA:</b>", table_cell),
            Paragraph(str(profile.get("cgpa") or "Not provided"), table_cell),
        ],
        [
            Paragraph("<b>Recorded Skills:</b>", table_cell),
            Paragraph(_safe(skills_str), table_cell),
            "",
            "",
        ],
    ]
    t1 = Table(profile_table_data, colWidths=[28 * mm, 58 * mm, 30 * mm, 58 * mm])
    t1.setStyle(
        TableStyle(
            [
                ("SPAN", (1, 3), (3, 3)),
                ("BACKGROUND", (0, 0), (-1, -1), bg_light),
                ("GRID", (0, 0), (-1, -1), 0.5, border_col),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t1)
    story.append(Spacer(1, 4 * mm))

    # 2. Assessment Summary
    story.append(Paragraph("2. Assessment Summary", h2_style))
    if not assessment:
        story.append(Paragraph("No assessment has been completed in this session yet.", body_style))
    else:
        score_val = f"{assessment['overall_pct']}% ({assessment['correct_count']} of {assessment['total']} correct)"
        story.append(
            Paragraph(
                f"<b>Domain:</b> {_safe(assessment.get('domain_name'))} ({_safe(assessment.get('difficulty'))}) · <b>Overall Score:</b> {score_val}",
                body_style,
            )
        )
        cat_scores = assessment.get("categories", [])
        strengths = [c["name"] for c in cat_scores if c.get("pct", 0) >= 70]
        improvements = [f"{c['name']} ({c.get('pct', 0)}%)" for c in cat_scores if c.get("pct", 0) < 70]
        summary_text = (
            f"<b>Strengths:</b> {', '.join(strengths) if strengths else 'None above 70%'}<br/>"
            f"<b>Improvement Areas:</b> {', '.join(improvements) if improvements else 'None below 70%'}"
        )
        story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 4 * mm))

    # 3. Skill Gap Analysis
    story.append(Paragraph("3. Skill Gap Analysis", h2_style))
    gap_rows = skill_gap.get("rows", [])
    if not gap_rows:
        story.append(Paragraph("No skill gaps measured against current target role requirements.", body_style))
    else:
        gap_table_data = [
            [
                Paragraph("Skill / Competency", table_header),
                Paragraph("Current Level (0-5)", table_header),
                Paragraph("Required Level (1-10)", table_header),
                Paragraph("Gap Analysis", table_header),
                Paragraph("Priority", table_header),
            ]
        ]
        for row in gap_rows[:8]:
            curr_level = row.get("have") or f"{row.get('student_level_0_to_5', 0)}/5"
            req_level = row.get("required") or f"{row.get('required_level_1_to_10', 0)}/10"
            gap_analysis = row.get("action") or f"Gap: {row.get('gap_0_to_5', 0)}"
            gap_table_data.append(
                [
                    Paragraph(_safe(row.get("skill", "Skill")), table_cell),
                    Paragraph(_safe(curr_level), table_cell),
                    Paragraph(_safe(req_level), table_cell),
                    Paragraph(_safe(gap_analysis), table_cell),
                    Paragraph(_safe(row.get("priority", "Medium")), table_cell),
                ]
            )
        t_gap = Table(gap_table_data, colWidths=[40 * mm, 32 * mm, 34 * mm, 40 * mm, 28 * mm])
        t_gap.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), primary),
                    ("GRID", (0, 0), (-1, -1), 0.5, border_col),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, bg_light]),
                ]
            )
        )
        story.append(t_gap)
    story.append(Spacer(1, 4 * mm))

    # 4. Personalized Learning Roadmap
    story.append(Paragraph("4. Personalized Learning Roadmap", h2_style))
    tasks = roadmap.get("tasks", [])
    if not tasks:
        story.append(Paragraph("No learning actions generated. Complete an assessment or add skills to generate your roadmap.", body_style))
    else:
        for index, task in enumerate(tasks[:6], start=1):
            cert_note = f" · <i>Recommended Certification:</i> {_safe(task['certification'])}" if task.get("certification") else ""
            story.append(
                Paragraph(
                    f"<b>Step {index}: {_safe(task['title'])}</b> [Priority: {_safe(task['priority'])}]<br/>"
                    f"&bull; <i>Why Recommended:</i> {_safe(task['reason'])}<br/>"
                    f"&bull; <i>Learning Action:</i> Complete structured modular practice and project implementation{cert_note}",
                    body_style,
                )
            )
            story.append(Spacer(1, 2 * mm))
    story.append(Spacer(1, 2 * mm))

    # 5. Career Recommendations
    story.append(Paragraph("5. Career Recommendations & Market Fit", h2_style))
    if not careers:
        story.append(Paragraph("Add skills to calculate role fit percentages.", body_style))
    else:
        career_table_data = [
            [
                Paragraph("Target Role", table_header),
                Paragraph("Calculated Fit", table_header),
                Paragraph("Sampled Benchmark", table_header),
                Paragraph("Salary Range (Dataset)", table_header),
            ]
        ]
        for role in careers[:4]:
            career_table_data.append(
                [
                    Paragraph(_safe(role["role"]), table_cell),
                    Paragraph(f"{role['match']}%", table_cell),
                    Paragraph(f"{role['row_count']} job postings", table_cell),
                    Paragraph(_safe(role.get("salary", "N/A")), table_cell),
                ]
            )
        t_car = Table(career_table_data, colWidths=[54 * mm, 30 * mm, 45 * mm, 45 * mm])
        t_car.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), primary),
                    ("GRID", (0, 0), (-1, -1), 0.5, border_col),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, bg_light]),
                ]
            )
        )
        story.append(t_car)
    story.append(Spacer(1, 4 * mm))

    # 6. Recommended Next Actions
    story.append(Paragraph("6. Recommended Next Actions", h2_style))
    actions_list = [
        "1. Focus on High Priority skill gaps identified above before applying to entry-level openings.",
        "2. Complete practical hands-on projects demonstrating competence in missing frameworks.",
        "3. Pursue suggested industry certifications to provide verified third-party evidence.",
        "4. Retake the domain assessment to measure improved competency and update your score.",
    ]
    for action in actions_list:
        story.append(Paragraph(action, body_style))
    story.append(Spacer(1, 4 * mm))

    # 7. Progress / Review Section
    story.append(Paragraph("7. Student Progress & Verification Review", h2_style))
    review_data = [
        [
            Paragraph("Milestone", table_header),
            Paragraph("Target Date", table_header),
            Paragraph("Status", table_header),
            Paragraph("Verified By", table_header),
        ],
        [
            Paragraph("Core Skill Gap Remediation", table_cell),
            Paragraph("Within 30 days", table_cell),
            Paragraph("[  ] Pending", table_cell),
            Paragraph("Faculty / Mentor", table_cell),
        ],
        [
            Paragraph("Hands-on Project Portfolio", table_cell),
            Paragraph("Within 60 days", table_cell),
            Paragraph("[  ] Pending", table_cell),
            Paragraph("GitHub Repository", table_cell),
        ],
        [
            Paragraph("Domain Re-Assessment (>= 80%)", table_cell),
            Paragraph("Within 90 days", table_cell),
            Paragraph("[  ] Pending", table_cell),
            Paragraph("EmployaAI Assessment", table_cell),
        ],
    ]
    t_rev = Table(review_data, colWidths=[54 * mm, 38 * mm, 38 * mm, 44 * mm])
    t_rev.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), primary),
                ("GRID", (0, 0), (-1, -1), 0.5, border_col),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, bg_light]),
            ]
        )
    )
    story.append(t_rev)

    # Build document
    doc = SimpleDocTemplate(
        stream,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="EmployaAI Development Plan",
        author="EmployaAI Platform",
    )
    doc.build(story)

    clean_name = re.sub(r"[^a-zA-Z0-9-]+", "-", profile.get("name", "").strip()).strip("-") or "student"
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return stream.getvalue(), f"employability-plan-{clean_name}-{ts}.pdf"