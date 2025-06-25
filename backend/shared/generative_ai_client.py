import google.generativeai as genai

class GenerativeAIClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_meeting_agenda(self, prompt: str) -> str:
        """Generates text content based on a given prompt."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating content with Gemini: {e}")
            return f"Error: Could not generate agenda. Details: {e}"