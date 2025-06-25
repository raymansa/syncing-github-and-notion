from twilio.rest import Client

class MessagingClient:
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.client = Client(account_sid, auth_token)
        # self.from_number = from_number
        self.from_number = +14155238886

    def send_whatsapp_notification(self, to_phone: str, message: str):
        """Sends a WhatsApp notification."""
        # Architectural Note: Sending a PDF directly via Twilio requires a public URL.
        # For simplicity in this internal tool, we will just send a text notification
        # that the report has been emailed.
        try:
            self.client.messages.create(
                body=message,
                from_=f'whatsapp:{self.from_number}',
                # content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
                # content_variables='{"1":"12/1","2":"3pm"}',
                to=f'whatsapp:{to_phone}'
            )
            print(f"WhatsApp notification sent to {to_phone}.")
        except Exception as e:
            print(f"Failed to send WhatsApp to {to_phone}. Error: {e}")