
import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from wai_cli.wizards.init_wizard import InitWizard

class TestInitWizard(unittest.TestCase):
    @patch('wai_cli.wizards.init_wizard.safe_input')
    @patch('wai_cli.wizards.init_wizard.HubManager')
    def test_wizard_flow(self, mock_hub_cls, mock_input):
        # Setup Mocks
        mock_hub = mock_hub_cls.return_value
        mock_hub.get_insights.return_value = ["Always use TDD", "Avoid circular deps"]
        
        # Mock User Inputs: 
        # 1. Tags -> "python, cli"
        # 2. Description -> "A CLI tool"
        mock_input.side_effect = ["python, cli", "A CLI tool"]
        
        # Test Run
        wizard = InitWizard(hub_path=Path("/tmp/hub"))
        answers = wizard.run_interview()
        
        # Assertions
        self.assertEqual(answers['tags'], ['python', 'cli'])
        self.assertEqual(answers['description'], "A CLI tool")
        
        # Verify Hub Query
        mock_hub.get_insights.assert_called()
        
        # Verify Generated Content
        content = wizard.generate_seed_content()
        self.assertIn("Always use TDD", content)
        self.assertIn("A CLI tool", content)
        print("\nGenerated Content:\n" + content)

if __name__ == '__main__':
    unittest.main()
