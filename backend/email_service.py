import os
import aiosmtplib
from email.message import EmailMessage
from imap_tools import MailBox, AND
import logging
import pandas as pd
from typing import List, Optional
from .ai_agent import AIAgent

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
        self.port = int(os.getenv("EMAIL_PORT", 587))
        self.user = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.ai = AIAgent()

    async def send_bulk_emails(self, recipients: List[str], subject: str, body_template: str):
        """
        Sends emails to a list of recipients.
        """
        if not self.user or not self.password:
            logger.error("Email credentials not set.")
            return {"status": "error", "message": "Email credentials missing"}

        sent_count = 0
        failed_count = 0

        try:
            # Connect to SMTP server
            # Note: For Gmail, app passwords are required if 2FA is on.
            smtp = aiosmtplib.SMTP(hostname=self.host, port=self.port, start_tls=True)
            await smtp.connect()
            await smtp.login(self.user, self.password)

            for recipient in recipients:
                try:
                    message = EmailMessage()
                    message["From"] = self.user
                    message["To"] = recipient
                    message["Subject"] = subject
                    message.set_content(body_template)

                    await smtp.send_message(message)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send to {recipient}: {e}")
                    failed_count += 1

            await smtp.quit()
            return {"status": "success", "sent": sent_count, "failed": failed_count}

        except Exception as e:
            logger.error(f"SMTP Connection failed: {e}")
            return {"status": "error", "message": str(e)}

    async def analyze_inbox_for_feedback(self, subject_keyword: str):
        """
        Connects to IMAP, finds emails with the matching subject, and summarizes responses.
        """
        if not self.user or not self.password:
            return "Email credentials missing. Cannot check inbox."

        import asyncio

        imap_host = "imap.gmail.com" if "gmail" in self.host else self.host.replace("smtp", "imap")

        def _blocking_imap_check():
            try:
                # Standard synchronous IMAP tool (simpler for this context than aioimaplib)
                feedback_texts = []

                with MailBox(imap_host).login(self.user, self.password) as mailbox:
                    # fetch emails with specific subject keyword
                    for msg in mailbox.fetch(AND(subject=subject_keyword)):
                        # Simple heuristic: ignore auto-replies or very short msgs if needed
                        feedback_texts.append(f"From {msg.from_}: {msg.text[:200]}...") # limit text
                return feedback_texts
            except Exception as e:
                logger.error(f"IMAP check failed: {e}")
                return None

        # Run blocking IMAP in a thread
        feedback_texts = await asyncio.to_thread(_blocking_imap_check)

        if feedback_texts is None:
             return "Error checking email (check logs)."

        if not feedback_texts:
            return "No email responses found matching the criteria."

        # Use AI to summarize the sentiment
        summary_prompt = f"Analyze these email responses regarding the business idea '{subject_keyword}':\n" + "\n".join(feedback_texts)
        summary = await self.ai.generate_response(summary_prompt)

        return summary

    async def generate_email_list(self, niche: str) -> List[str]:
        """
        Uses AI + Search to find potential contacts.
        Note: This is a best-effort simulation as scraping emails is hard/blocked.
        """
        # 1. Search for "contact [niche] business"
        # 2. Extract anything looking like an email (regex)
        # For prototype, we might mock this or return a warning.
        return []
