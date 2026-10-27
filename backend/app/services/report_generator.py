import os
import uuid
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.site import HeritageSite
from app.models.evidence import EvidenceRecord
from app.models.audit import AuditLog
from app.services.gap_analysis import compute_gap_analysis, SAFETY_DISCLAIMER

def generate_pdf_dossier(site_id: str, db: Session) -> str:
    """
    Generates an archival PDF dossier report using ReportLab.
    Returns the absolute path to the generated PDF.
    """
    site = HeritageSite.find_by_identifier(site_id, db)
    if not site:
        raise ValueError(f"Site '{site_id}' not found")

    gap_data = compute_gap_analysis(site.id, db)
    evidence_records = db.query(EvidenceRecord).filter(EvidenceRecord.site_id == site.id).all()
    evidence_ids = [e.id for e in evidence_records]

    # Query audit logs related to this site or its evidence
    audit_logs = db.query(AuditLog).filter(
        (AuditLog.entity_id == site.id) | (AuditLog.entity_id.in_(evidence_ids))
    ).order_by(AuditLog.created_at.desc()).limit(10).all()

    os.makedirs(settings.REPORT_DIR, exist_ok=True)
    report_id = str(uuid.uuid4())
    pdf_filename = f"HeritageProof_Dossier_{site.name.replace(' ', '_')}_{report_id[:8]}.pdf"
    pdf_path = os.path.join(settings.REPORT_DIR, pdf_filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom typography
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1C1917'),
        alignment=0
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#78716C')
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#C25E3E'),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#292524')
    )
    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#9A3412')
    )

    elements = []

    # 1. Header Banner
    elements.append(Paragraph("HERITAGEPROOF ARCHIVAL DOSSIER & VERIFICATION REPORT", subtitle_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(site.name, title_style))
    elements.append(Paragraph(f"Historical Era: {site.historical_period or 'Unrecorded'} | Site Type: {site.site_type.title()} | Region: {site.city or ''}, {site.state or ''}, {site.country}", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#C25E3E'), spaceAfter=14))

    # 2. Site Overview & Coordinates
    overview_data = [
        [
            Paragraph("<b>Monument Entity:</b>", body_style),
            Paragraph(site.name, body_style),
            Paragraph("<b>Latitude / Longitude:</b>", body_style),
            Paragraph(f"{site.latitude:.4f} N, {site.longitude:.4f} E", body_style)
        ],
        [
            Paragraph("<b>Alternate Names:</b>", body_style),
            Paragraph(site.alternate_names or "None recorded", body_style),
            Paragraph("<b>Dossier Timestamp:</b>", body_style),
            Paragraph(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), body_style)
        ]
    ]
    overview_table = Table(overview_data, colWidths=[110, 160, 110, 150])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FBF9F5')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E7E5E4')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E7E5E4')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 14))

    # 3. Documentation Completeness Score & Mandatory Safety Disclaimer
    elements.append(Paragraph("DOCUMENTATION COMPLETENESS SCORE", section_style))
    score_val = gap_data.get("completeness_score", 0.0)
    score_data = [
        [
            Paragraph(f"<font size=22 color='#C25E3E'><b>{score_val}%</b></font><br/><font size=8 color='#78716C'>Archival Coverage</font>", body_style),
            Paragraph(f"<b>CRITICAL NOTICE:</b><br/>{SAFETY_DISCLAIMER}", disclaimer_style)
        ]
    ]
    score_table = Table(score_data, colWidths=[100, 430])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFBEB')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#FDE68A')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 14))

    # 4. Canonical 7-Category Documentation Checklist Table
    elements.append(Paragraph("Documentation Categories Checklist", section_style))
    check_rows = [["Category", "Archival Requirement", "Status", "Identified Gap / Task"]]
    for item in gap_data.get("checklist", []):
        status_text = "<font color='#16A34A'><b>FULFILLED</b></font>" if item["is_fulfilled"] else "<font color='#DC2626'><b>GAP DETECTED</b></font>"
        check_rows.append([
            Paragraph(f"<b>{item['category'].replace('_', ' ').title()}</b>", body_style),
            Paragraph(item["item_name"], body_style),
            Paragraph(status_text, body_style),
            Paragraph(item["gap_description"] or "Verified in archives", body_style)
        ])
    check_table = Table(check_rows, colWidths=[90, 160, 80, 200])
    check_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E7E5E4')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D6D3D1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(check_table)
    elements.append(Spacer(1, 14))

    # 5. Verified Evidence Records & Facts with Citations
    elements.append(Paragraph("Verified Archival Evidence & Facts", section_style))
    verified_evidence = [e for e in evidence_records if e.verification_status == "verified"]
    if verified_evidence:
        ev_rows = [["Fact / Extracted Claim", "Source File", "Page/Slide", "Verifier Status"]]
        for ev in verified_evidence:
            ev_rows.append([
                Paragraph(ev.claim_statement or ev.raw_extracted_text[:120], body_style),
                Paragraph(ev.document.original_filename if ev.document else "Archival File", body_style),
                Paragraph(f"Page {ev.page_or_slide_number}", body_style),
                Paragraph("<font color='#16A34A'><b>VERIFIED (Human)</b></font>", body_style)
            ])
        ev_table = Table(ev_rows, colWidths=[230, 140, 60, 100])
        ev_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E7E5E4')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D6D3D1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(ev_table)
    else:
        elements.append(Paragraph("<i>No human-verified claims yet for this monument. Claims are pending researcher review.</i>", body_style))
    elements.append(Spacer(1, 14))

    # 6. Auto-Generated Missing-Evidence Tasks
    elements.append(Paragraph("Auto-Generated Archival Action Tasks", section_style))
    tasks = gap_data.get("missing_tasks", [])
    if tasks:
        task_rows = [["Priority", "Category", "Actionable Field / Archival Recommendation"]]
        for t in tasks:
            pri_color = "#DC2626" if t["priority"] == "HIGH" else "#D97706"
            task_rows.append([
                Paragraph(f"<font color='{pri_color}'><b>{t['priority']}</b></font>", body_style),
                Paragraph(t["category"].replace('_', ' ').title(), body_style),
                Paragraph(t["actionable_task"], body_style)
            ])
        task_table = Table(task_rows, colWidths=[60, 110, 360])
        task_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E7E5E4')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D6D3D1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(task_table)
        elements.append(Spacer(1, 14))

    # 7. Verification Audit Trail & Provenance Sign-Off
    elements.append(Paragraph("Verification Audit Trail & Provenance Sign-Off", section_style))
    if audit_logs:
        audit_rows = [["Timestamp (UTC)", "Action", "Verifier", "Verification Notes"]]
        for log in audit_logs:
            details = log.details or {}
            timestamp_str = log.created_at.strftime("%Y-%m-%d %H:%M") if log.created_at else "Recent"
            verifier_str = f"{details.get('verifier_username', 'Verifier')} ({details.get('verifier_role', 'Human')})"
            notes_str = details.get("notes") or "Verified against primary archive."
            audit_rows.append([
                Paragraph(timestamp_str, body_style),
                Paragraph(f"<b>{log.action}</b>", body_style),
                Paragraph(verifier_str, body_style),
                Paragraph(notes_str, body_style)
            ])
        audit_table = Table(audit_rows, colWidths=[100, 110, 130, 190])
        audit_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E7E5E4')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D6D3D1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(audit_table)
    else:
        elements.append(Paragraph("<i>No audit log entries recorded yet for this monument's records.</i>", body_style))

    # Running Footer with Page Numbers
    def add_footer(canvas, document):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#78716C'))
        canvas.drawString(40, 20, "HeritageProof Archival Verification Framework - Confidential Historical Dossier")
        canvas.drawRightString(document.pagesize[0] - 40, 20, f"Page {document.page}")
        canvas.setStrokeColor(colors.HexColor('#E7E5E4'))
        canvas.setLineWidth(0.5)
        canvas.line(40, 30, document.pagesize[0] - 40, 30)
        canvas.restoreState()

    # Build Document with running footers
    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    return pdf_path
