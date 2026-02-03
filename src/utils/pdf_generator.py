from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO

def generate_pdf_report(filename, overall_score, summary, clauses):
    """
    Generates a PDF report for the contract analysis.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph(f"Contract Risk Audit Report: {filename}", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    story.append(Paragraph(f"Overall Risk Score: {overall_score}/100", styles['Normal']))
    story.append(Paragraph(f"Summary: {summary}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Critical Risks Table
    story.append(Paragraph("Critical Risk Findings", styles['Heading2']))
    
    # Prepare Table Data
    data = [['Clause Snippet', 'Risk Level', 'Issue & Suggestion']]
    
    def clean_text(text):
        """Removes non-latin characters to prevent PDF crash on default fonts."""
        return text.encode('ascii', 'ignore').decode('ascii')
    
    for c in clauses:
        if c['analysis']['risk_score'] > 4: # Filter for medium/high risk
            # Use English explanation as snippet if original is risky (likely Hindi/Non-ASCII)
            # OR just clean the snippet
            snippet = clean_text(c['text'][:100]) + "..." 
            risk = "HIGH" if c['analysis']['risk_score'] > 7 else "MEDIUM"
            explanation = clean_text(f"{c['analysis']['explanation']}\n\nSuggestion: {c['analysis']['suggestion']}")
            
            data.append([snippet, risk, explanation])
            
    if len(data) > 1:
        t = Table(data, colWidths=[200, 60, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No significant risks detected.", styles['Normal']))
        
    doc.build(story)
    buffer.seek(0)
    return buffer
