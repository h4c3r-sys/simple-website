from .ai_agent import AIAgent
from .sources.web_search import WebSearcher
from .sources.social_mock import SocialMediaScanner
from .email_service import EmailService
import logging

logger = logging.getLogger(__name__)

class AnalysisManager:
    def __init__(self):
        self.ai = AIAgent()
        self.web_search = WebSearcher()
        self.social = SocialMediaScanner()
        self.email = EmailService()

    async def run_market_check(self, idea: str, use_email_data: bool = False):
        """
        Orchestrates the market validation process.
        """
        # 1. Gather Data concurrently (in a real app, use asyncio.gather)
        logger.info(f"Starting market check for: {idea}")

        # Web Search
        search_results = await self.web_search.search_general(idea)

        # Social Search (Reddit, etc)
        social_results = await self.social.scan_sentiment(idea)

        # Email Data (if applicable)
        email_summary = "No email data requested."
        if use_email_data:
            # In a real scenario, this might analyze previously stored responses
            # or trigger a check of the inbox now.
            email_summary = await self.email.analyze_inbox_for_feedback(idea)

        # 2. AI Synthesis
        logger.info("Synthesizing data with AI...")
        report = await self.ai.analyze_market_data(
            idea=idea,
            search_data=str(search_results),
            social_data=str(social_results),
            email_data=email_summary
        )

        return {
            "report": report,
            "sources": {
                "web": search_results,
                "social": social_results,
                "email": email_summary
            }
        }

    async def generate_new_idea(self, niche: str):
        """
        Orchestrates the idea generation process.
        """
        logger.info(f"Generating idea for niche: {niche}")

        # Gather trends
        trends = await self.web_search.search_trends(niche)
        discourse = await self.social.scan_sentiment(niche)

        # AI Generation
        idea_proposal = await self.ai.generate_business_idea(
            niche=niche,
            search_data=str(trends),
            social_data=str(discourse)
        )

        return {
            "proposal": idea_proposal,
            "based_on": {
                "trends": trends,
                "discourse": discourse
            }
        }
