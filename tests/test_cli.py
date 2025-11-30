import pytest
from unittest.mock import patch, MagicMock
from src.main import main
import os

@patch("src.main.AIScanner")
@patch("src.main.LocalScanner")
@patch("src.main.shutil.move")
def test_cli_quarantine_flow(mock_move, MockLocalScanner, MockAIScanner, tmp_path):
    # Setup malicious file
    malicious_file = tmp_path / "bad.py"
    malicious_file.write_text("import os\nos.system('hack')", encoding="utf-8")

    # Mock Local Scanner to return a finding
    mock_local_instance = MockLocalScanner.return_value
    mock_local_instance.scan_file.return_value = [{'line': 2, 'content': "os.system('hack')", 'issue': 'Bad'}]

    # Mock AI Scanner (doesn't matter if this passes if local fails, but let's say it fails too)
    mock_ai_instance = MockAIScanner.return_value
    mock_ai_instance.scan_code.return_value = {'is_safe': False, 'reason': 'AI says bad'}

    # Run main with arguments
    with patch("sys.argv", ["main.py", str(malicious_file)]):
        main()

    # Verify quarantine was called
    mock_move.assert_called_once()
    args, _ = mock_move.call_args
    assert args[0] == str(malicious_file)
    assert "infected" in args[1]

@patch("src.main.AIScanner")
@patch("src.main.LocalScanner")
@patch("src.main.shutil.move")
def test_cli_safe_flow(mock_move, MockLocalScanner, MockAIScanner, tmp_path):
    # Setup safe file
    safe_file = tmp_path / "good.py"
    safe_file.write_text("print('hello')", encoding="utf-8")

    # Mock Local Scanner to return no findings
    mock_local_instance = MockLocalScanner.return_value
    mock_local_instance.scan_file.return_value = []

    # Mock AI Scanner to return safe
    mock_ai_instance = MockAIScanner.return_value
    mock_ai_instance.scan_code.return_value = {'is_safe': True, 'reason': 'Looks good'}

    # Run main with arguments
    with patch("sys.argv", ["main.py", str(safe_file)]):
        main()

    # Verify quarantine was NOT called
    mock_move.assert_not_called()
