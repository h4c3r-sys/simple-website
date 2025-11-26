import google.generativeai as genai
import json
import os

# In a real scenario, use environment variables.
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    # Fallback only for local testing if explicitly set in code,
    # but preferably rely on env vars for security.
    print("Warning: GEMINI_API_KEY not set in environment.")

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
