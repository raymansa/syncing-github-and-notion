import os
import base64
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


# Important: Adjust path to import from the shared module
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.secrets import get_secret
from shared.notion_client import NotionClient
from shared.email_client import EmailClient
from shared.messaging_client import MessagingClient

def run():
    """Main function for the Reporting & Comms Worker."""
    print("--- Reporting & Comms Worker Started ---")
    
    # --- 1. Initialization ---
    gcp_project_id = os.getenv("GCP_PROJECT_ID")
    
    notion = NotionClient(api_key=get_secret("NOTION_API_KEY", project_id=gcp_project_id))
    email_client = EmailClient(
        api_key=get_secret("BREVO_API_KEY", project_id=gcp_project_id),
        sender_email=get_secret("SENDER_EMAIL", project_id=gcp_project_id)
    )
    messaging_client = MessagingClient(
        account_sid=get_secret("TWILIO_ACCOUNT_SID", project_id=gcp_project_id),
        auth_token=get_secret("TWILIO_AUTH_TOKEN", project_id=gcp_project_id),
        from_number=get_secret("TWILIO_WHATSAPP_FROM", project_id=gcp_project_id)
    )

    # --- 2. Fetch Data ---
    print("Fetching data from Notion...")
    dashboard_data = notion.get_all_dashboard_data()
    # In a real scenario, you'd fetch stakeholder contacts here.
    # For now, we'll use a mock list.
    stakeholders = [
        {"name": "Sarah Jones", "email": "rendaniramano@icloud.com", "phone": "+27713971240"},
        {"name": "Alex Chen", "email": "raymansa@gmail.com", "phone": "+27713971240"},
    ]
    
    # --- 3. Generate PDF Report ---
    print("Generating PDF report...")
    template_env = Environment(loader=FileSystemLoader('templates/'))
    template = template_env.get_template('report_template.html')
    
    current_date = datetime.now().strftime("%B %d, %Y")
    html_out = template.render(data=dashboard_data, generation_date=current_date)
    
    pdf_bytes = HTML(string=html_out).write_pdf()
    pdf_name = f"Neuroflux_Weekly_Report_{datetime.now().strftime('%Y-%m-%d')}.pdf"
    
    # We must base64 encode the bytes for the Brevo API attachment
    encoded_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

    # --- 4. Distribute Report ---
    print("Distributing report to stakeholders...")
    for stakeholder in stakeholders:
        subject = f"Neuroflux Weekly Status Report - {current_date}"
        
        if stakeholder.get("email"):
            email_client.send_email_with_attachment(
                to_email=stakeholder["email"],
                subject=subject,
                pdf_data=encoded_pdf,
                pdf_name=pdf_name
            )
        
        if stakeholder.get("phone"):
            message = f"Hi {stakeholder['name']}, the Neuroflux weekly report for {current_date} has been sent to your email."
            messaging_client.send_whatsapp_notification(
                to_phone=stakeholder["phone"],
                message=message
            )
            
    print("--- Reporting & Comms Worker Finished ---")

if __name__ == "__main__":
    run()