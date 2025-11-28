import unittest
from backend.email_service import EmailService
from backend.manager import AnalysisManager
from backend.ai_agent import AIAgent
import asyncio
import os

class TestBackendStructure(unittest.TestCase):

    def test_email_service_init(self):
        # Ensure it initializes without error even with missing env vars (should just log warnings)
        service = EmailService()
        self.assertIsNotNone(service)

    def test_manager_init(self):
        manager = AnalysisManager()
        self.assertIsNotNone(manager)
        self.assertIsInstance(manager.ai, AIAgent)

    def test_ai_agent_init(self):
        # Mocking env var for the test if needed, or asserting it handles missing key gracefully
        agent = AIAgent()
        self.assertIsNotNone(agent)

if __name__ == '__main__':
    unittest.main()
