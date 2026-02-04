from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

def generate_pdf_report(filename, overall_score, summary, clauses, entities=None, language="en"):
    """
    Generates a professional PDF report for the contract analysis.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    
    # Custom Bold Heading Style
    bold_heading_style = ParagraphStyle(
        'BoldHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        fontSize=22,
        textColor=colors.HexColor("#6C5CE7"),
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    
    story = []
    
    # --- HEADER SECTION ---
    story.append(Paragraph(f"Contract Risk Audit Report", title_style))
    story.append(Paragraph(f"Document: {filename}", styles['Heading3']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
    story.append(Spacer(1, 12))
    story.append(Table([[""]], colWidths=[500], rowHeights=[1], style=[('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor("#6C5CE7"))]))
    story.append(Spacer(1, 20))
    
    # --- DOCUMENT OVERVIEW SECTION ---
    story.append(Paragraph("<b>1. Document Overview</b>", bold_heading_style))
    if entities:
        overview_data = [
            ["<b>Parties Identified:</b>", ", ".join(entities.get("PARTIES", [])) or "None detected"],
            ["<b>Key Dates:</b>", ", ".join(entities.get("DATES", [])) or "None detected"],
            ["<b>Financial Terms:</b>", ", ".join(entities.get("MONEY", [])) or "None detected"],
            ["<b>Jurisdiction/GPE:</b>", ", ".join(entities.get("GPE", [])) or "None detected"]
        ]
        t_overview = Table(overview_data, colWidths=[150, 350])
        t_overview.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(t_overview)
    else:
        story.append(Paragraph("No specific entities extracted.", normal_style))
    story.append(Spacer(1, 20))
    
    # --- EXECUTIVE SUMMARY SECTION ---
    story.append(Paragraph("<b>2. Executive Summary</b>", bold_heading_style))
    
    # Risk Score Visual Representation (Simple color coded box)
    score_color = colors.green if overall_score > 80 else (colors.orange if overall_score > 50 else colors.red)
    score_data = [[f"Overall Health Score: {overall_score}/100"]]
    t_score = Table(score_data, colWidths=[200])
    t_score.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), score_color),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(t_score)
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Assessment:</b> {summary}", normal_style))
    story.append(Spacer(1, 20))
    
    # --- RISK ANALYTICS ---
    story.append(Paragraph("<b>3. Risk Analytics</b>", bold_heading_style))
    high_risks = sum(1 for c in clauses if c['analysis']['risk_score'] > 7)
    med_risks = sum(1 for c in clauses if 4 < c['analysis']['risk_score'] <= 7)
    low_risks = sum(1 for c in clauses if c['analysis']['risk_score'] <= 4)
    
    analytics_data = [
        ["Risk Level", "Count", "Severity"],
        ["CRITICAL / HIGH", str(high_risks), "IMMEDIATE ATTENTION"],
        ["MEDIUM", str(med_risks), "REVIEW SUGGESTED"],
        ["LOW / SAFE", str(low_risks), "STANDARD"]
    ]
    t_analytics = Table(analytics_data, colWidths=[150, 100, 250])
    t_analytics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#6C5CE7")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (1, 1), (1, 1), colors.lightpink if high_risks > 0 else colors.whitesmoke),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_analytics)
    story.append(Spacer(1, 20))

    # --- DETAILED FINDINGS SECTION ---
    story.append(Paragraph("<b>4. Detailed Risk Findings & Mitigation</b>", bold_heading_style))
    
    def clean_text(text):
        """Removes non-latin characters to prevent PDF crash on default fonts."""
        return text.encode('ascii', 'ignore').decode('ascii')
    
    # Prepare Table Data
    data = [['Clause Snippet', 'Risk', 'Mitigation Strategy']]
    
    for c in clauses:
        if c['analysis']['risk_score'] > 4: # Filter for medium/high risk
            snippet = clean_text(c['text'][:120]) + "..." 
            risk_val = c['analysis']['risk_score']
            risk_label = f"HIGH ({risk_val})" if risk_val > 7 else f"MED ({risk_val})"
            mitigation = clean_text(f"{c['analysis']['explanation']}\n\nSUGGESTION: {c['analysis']['suggestion']}")
            
            data.append([
                Paragraph(snippet, styles['Normal']), 
                risk_label, 
                Paragraph(mitigation, styles['Normal'])
            ])
            
    if len(data) > 1:
        t_risks = Table(data, colWidths=[180, 80, 240])
        t_risks.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t_risks)
    else:
        story.append(Paragraph("No significant risks requiring mitigation were detected in the scanned clauses.", normal_style))
    
    story.append(Spacer(1, 40))
    story.append(Paragraph("<i>This report is AI-generated and intended for informational purposes only. It does not constitute legal advice.</i>", styles['Italic']))
    
    # --- FOOTER ---
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawString(inch, 0.75 * inch, f"Legal Co-Pilot AI - Confidential Audit Report - Page {doc.page}")
        canvas.drawRightString(letter[0] - inch, 0.75 * inch, "Powered by Google Gemini")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)
    return buffer
