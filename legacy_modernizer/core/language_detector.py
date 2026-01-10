# core/language_detector.py

def detect_language(filename: str, code: str) -> str:
    """
    Simple language detection
    """
    if filename:
        ext_map = {
            '.py': 'python',
            '.java': 'java',
            '.js': 'javascript',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp'
        }
        
        for ext, lang in ext_map.items():
            if filename.endswith(ext):
                return lang
    
    # Heuristic fallback
    if 'def ' in code or 'import ' in code:
        return 'python'
    if 'class ' in code and '{' in code and ';' in code:
        return 'java'
    if 'function' in code or 'const ' in code:
        return 'javascript'
    
    return 'python'  # safe default