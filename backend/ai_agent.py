import google.generativeai as genai
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set. AI features will not work.")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')

    async def generate_response(self, prompt: str) -> str:
        """
        Generates a response using Google's Gemini model.
        """
        if not self.api_key:
            return "Error: API Key not configured."

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return f"Error analyzing data: {str(e)}"

    async def analyze_market_data(self, idea: str, search_data: str, social_data: str, email_data: str) -> str:
        """
        Synthesizes gathered data to analyze a business idea.
        """
        prompt = f"""
        You are an expert Business Market Analyst.

        Task: Analyze the viability of the following business idea based on the provided data.

        Business Idea: {idea}

        Data Sources:
        1. Online Search Results:
        {search_data}

        2. Social Media & Forums (Reddit/Twitter/etc):
        {social_data}

        3. Email Feedback/Responses:
        {email_data}

        Please provide a comprehensive report including:
        - Market Demand Assessment
        - Potential Competitors (based on search data)
        - Public Sentiment (based on social data)
        - Direct Feedback Analysis (based on emails)
        - Final Verdict: Viable or Risky?

        Cite specific sources from the data where possible.
        """
        return await self.generate_response(prompt)

    async def generate_business_idea(self, niche: str, search_data: str, social_data: str) -> str:
        """
        Generates a new business idea based on a niche and market trends.
        """
        prompt = f"""
        You are a Creative Business Strategist.

        Task: Generate a unique and profitable business idea for the niche: "{niche}".

        Use the following market signals to ensure the idea is relevant:

        Market Trends (Search):
        {search_data}

        Social Discourse (Forums/Socials):
        {social_data}

        Output Format:
        - Business Name
        - One-line Pitch
        - Detailed Description
        - Target Audience
        - Monetization Strategy
        - Why it works now (Trend alignment)
        """
        return await self.generate_response(prompt)
