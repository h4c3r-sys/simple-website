import google.generativeai as genai
import json
import os

# In a real scenario, use environment variables.
# For this specific task, I will use the key provided by the user in the prompt,
# but I will structure it to check env var first.
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAItEW2xVnRYDAIoQJZ8UUa2lpfDp3qdHg")

genai.configure(api_key=API_KEY)

def analyze_trend(trend_data):
    """
    Uses Gemini to analyze a trend snippet and extract product info and hype score.
    """
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    You are a dropshipping and viral product expert. Analyze the following search result snippet for a potential viral tech product.

    Title: {trend_data.get('title')}
    Snippet: {trend_data.get('snippet')}

    Your task is to return a valid JSON object (no markdown formatting) with the following fields:
    1. "product_name": The specific name of the product (e.g., "Transparent Wireless Earbuds").
    2. "hype_score": An integer from 0 to 100 representing buying intent and virality based on the text.
    3. "reason": A short sentence explaining why it is viral.

    If no specific product is found, return "product_name": null.
    """

    try:
        response = model.generate_content(prompt)
        text_response = response.text.strip()

        # Clean up markdown code blocks if Gemini includes them
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]

        return json.loads(text_response)
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return {
            "product_name": "Unknown Product",
            "hype_score": 0,
            "reason": "AI analysis failed."
        }
