import pytest
import os
from src.local_scanner import LocalScanner

# Test Data
SAFE_PYTHON = """
def add(a, b):
    return a + b
print(add(1, 2))
"""

MALICIOUS_PYTHON = """
import os
os.system("rm -rf /")
"""

MALICIOUS_JS = """
var x = "alert('xss')";
eval(x);
"""

MALICIOUS_JAVA = """
public class Hack {
    public static void main(String[] args) {
        Runtime.getRuntime().exec("cmd.exe /c format c:");
    }
}
"""

def test_local_scanner_python_safe(tmp_path):
    f = tmp_path / "safe.py"
    f.write_text(SAFE_PYTHON, encoding="utf-8")
    scanner = LocalScanner()
    findings = scanner.scan_file(str(f))
    assert len(findings) == 0

def test_local_scanner_python_malicious(tmp_path):
    f = tmp_path / "malicious.py"
    f.write_text(MALICIOUS_PYTHON, encoding="utf-8")
    scanner = LocalScanner()
    findings = scanner.scan_file(str(f))
    assert len(findings) > 0
    assert "os.system" in findings[0]['issue']

def test_local_scanner_js_malicious(tmp_path):
    f = tmp_path / "malicious.js"
    f.write_text(MALICIOUS_JS, encoding="utf-8")
    scanner = LocalScanner()
    findings = scanner.scan_file(str(f))
    assert len(findings) > 0
    assert "eval" in findings[0]['issue']

def test_local_scanner_java_malicious(tmp_path):
    f = tmp_path / "Malicious.java"
    f.write_text(MALICIOUS_JAVA, encoding="utf-8")
    scanner = LocalScanner()
    findings = scanner.scan_file(str(f))
    assert len(findings) > 0
    assert "Runtime.exec" in findings[0]['issue']
