import brevo_python
from brevo_python.rest import ApiException
from brevo_python.models import SendSmtpEmail, SendSmtpEmailAttachment

class EmailClient:
    def __init__(self, api_key: str, sender_email: str):
        configuration = brevo_python.Configuration()
        configuration.api_key['api-key'] = api_key
        self.api_instance = brevo_python.TransactionalEmailsApi(brevo_python.ApiClient(configuration))
        self.sender = {"email": sender_email, "name": "Neuroflux Reports"}

    def send_email_with_attachment(self, to_email: str, subject: str, pdf_data: str, pdf_name: str):
        to = [{"email": to_email}]
        attachment = SendSmtpEmailAttachment(
            content=pdf_data,
            name=pdf_name
        )
        send_smtp_email = SendSmtpEmail(
            sender=self.sender,
            to=to,
            subject=subject,
            html_content="<p>Please find the weekly status report attached.</p>",
            attachment=[attachment]
        )
        try:
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            print(f"Email sent to {to_email}. Response: {api_response}")
        except ApiException as e:
            print(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}\n")