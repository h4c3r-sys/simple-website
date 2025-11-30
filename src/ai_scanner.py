import os
import google.generativeai as genai

class AIScanner:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found. AI scanning will be skipped.")
            self.model = None
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')

    def scan_code(self, code_content):
        """
        Sends code to Gemini for security analysis.
        Returns a dict: {'is_safe': bool, 'reason': str}
        """
        if not self.model:
            return {'is_safe': True, 'reason': "AI Scanner skipped (No API Key)"}

        prompt = f"""
        You are a highly skilled cybersecurity analyst. Analyze the following source code for malicious intent, security vulnerabilities, and safety to execute.

        CODE:
        ```
        {code_content}
        ```

        Task:
        1. Determine if this code is MALICIOUS (e.g., malware, spyware, destructive) or UNSAFE (e.g., severe vulnerabilities).
        2. Determine if this code is SAFE to run.

        Response Format (Strictly follow this):
        IS_SAFE: [TRUE or FALSE]
        REASON: [Detailed explanation of why it is safe or unsafe. Mention specific lines or patterns if found.]

        Analysis:
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text

            is_safe = "IS_SAFE: TRUE" in text
            reason = text.split("REASON:", 1)[1].strip() if "REASON:" in text else text

            return {
                'is_safe': is_safe,
                'reason': reason
            }
        except Exception as e:
            return {
                'is_safe': False,
                'reason': f"AI Analysis failed: {str(e)}"
            }
