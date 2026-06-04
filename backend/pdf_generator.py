import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf(report_data, mode, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    def safe_str(item):
        if isinstance(item, dict):
            return " - ".join(str(v) for v in item.values())
        return str(item)
    
    story = []
    
    if mode == 'medical':
        story.append(Paragraph("Medical Consultation Report (SOAP Note)", title_style))
        story.append(Spacer(1, 12))
        
        # Subjective
        story.append(Paragraph("Subjective", heading_style))
        story.append(Paragraph(f"<b>Patient Complaint:</b> {report_data.get('patient_complaint', 'N/A')}", normal_style))
        
        symptoms = report_data.get('symptoms', [])
        if symptoms:
            story.append(Paragraph("<b>Symptoms:</b>", normal_style))
            sym_items = [ListItem(Paragraph(safe_str(sym), normal_style)) for sym in symptoms]
            story.append(ListFlowable(sym_items, bulletType='bullet'))
        story.append(Spacer(1, 12))
        
        # Assessment
        story.append(Paragraph("Assessment", heading_style))
        diagnoses = report_data.get('diagnosis_possibilities', [])
        if diagnoses:
            story.append(Paragraph("<b>Possible Diagnoses:</b>", normal_style))
            diag_items = [ListItem(Paragraph(safe_str(diag), normal_style)) for diag in diagnoses]
            story.append(ListFlowable(diag_items, bulletType='bullet'))
        story.append(Spacer(1, 12))
        
        # Plan
        story.append(Paragraph("Plan", heading_style))
        meds = report_data.get('medications_prescribed', [])
        if meds:
            story.append(Paragraph("<b>Medications Prescribed:</b>", normal_style))
            med_items = [ListItem(Paragraph(safe_str(med), normal_style)) for med in meds]
            story.append(ListFlowable(med_items, bulletType='bullet'))
            
        follow_up = report_data.get('follow_up_instructions', '')
        if follow_up:
            story.append(Paragraph(f"<b>Follow-up Instructions:</b> {follow_up}", normal_style))

    elif mode == 'meeting':
        story.append(Paragraph(report_data.get('meeting_title', 'Meeting Minutes'), title_style))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph(f"<b>Date:</b> {report_data.get('date', 'Unknown')}", normal_style))
        
        attendees = report_data.get('attendees', [])
        if attendees:
            story.append(Paragraph("<b>Attendees:</b>", normal_style))
            att_items = [ListItem(Paragraph(safe_str(att), normal_style)) for att in attendees]
            story.append(ListFlowable(att_items, bulletType='bullet'))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Key Discussion Points", heading_style))
        points = report_data.get('key_discussion_points', [])
        if points:
            point_items = [ListItem(Paragraph(safe_str(pt), normal_style)) for pt in points]
            story.append(ListFlowable(point_items, bulletType='bullet'))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Decisions Made", heading_style))
        decisions = report_data.get('decisions_made', [])
        if decisions:
            dec_items = [ListItem(Paragraph(safe_str(dec), normal_style)) for dec in decisions]
            story.append(ListFlowable(dec_items, bulletType='bullet'))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Action Items", heading_style))
        actions = report_data.get('action_items', [])
        if actions:
            act_items = []
            for act in actions:
                task = act.get('task', '')
                assignee = act.get('assigned_to', 'Unassigned')
                deadline = act.get('deadline', 'No deadline')
                text = f"{task} - <b>{assignee}</b> (Due: {deadline})"
                act_items.append(ListItem(Paragraph(text, normal_style)))
            story.append(ListFlowable(act_items, bulletType='bullet'))
        story.append(Spacer(1, 12))
        
        next_meeting = report_data.get('next_meeting', {})
        if isinstance(next_meeting, dict):
            nm_date = next_meeting.get('date', '')
            nm_details = next_meeting.get('details', '')
            if nm_date or nm_details:
                story.append(Paragraph("Next Meeting", heading_style))
                story.append(Paragraph(f"{nm_date} - {nm_details}", normal_style))
        elif isinstance(next_meeting, str):
            story.append(Paragraph("Next Meeting", heading_style))
            story.append(Paragraph(next_meeting, normal_style))
            
    doc.build(story)
    return output_path
