import re
import os

class LocalScanner:
    PATTERNS = {
        'python': [
            (r'os\.system\(', "Possible shell command execution (os.system)"),
            (r'subprocess\.', "Possible subprocess execution"),
            (r'eval\(', "Dangerous code evaluation (eval)"),
            (r'exec\(', "Dangerous code execution (exec)"),
            (r'shutil\.rmtree\(', "Directory deletion detected"),
            (r'__import__\([\'"]os[\'"]\)', "Dynamic import of os module"),
        ],
        'javascript': [
            (r'eval\(', "Dangerous code evaluation (eval)"),
            (r'require\([\'"]child_process[\'"]\)', "Process spawning detected (child_process)"),
            (r'exec\(', "Possible command execution (exec)"),
            (r'spawn\(', "Possible command execution (spawn)"),
            (r'document\.write\(', "Possible XSS vector"),
        ],
        'java': [
            (r'Runtime\.getRuntime\(\)\.exec\(', "Command execution detected (Runtime.exec)"),
            (r'ProcessBuilder\(', "Process spawning detected (ProcessBuilder)"),
            (r'System\.exit\(', "Forced system exit"),
        ]
    }

    EXTENSION_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.java': 'java'
    }

    def scan_file(self, filepath):
        """
        Scans a file for malicious patterns.
        Returns a list of dicts: {'line': int, 'content': str, 'issue': str}
        """
        _, ext = os.path.splitext(filepath)
        language = self.EXTENSION_MAP.get(ext.lower())

        if not language:
            return []  # Unsupported language or file type

        findings = []
        patterns = self.PATTERNS.get(language, [])

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    for pattern, message in patterns:
                        if re.search(pattern, line):
                            findings.append({
                                'line': line_num,
                                'content': line.strip(),
                                'issue': message
                            })
        except Exception as e:
            print(f"Error scanning file {filepath}: {e}")

        return findings
