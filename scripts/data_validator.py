import re

def validate_user_prompt(user_input: str) -> dict:
    """Pipeline de validation DATA/CYBER pour le chatbot financier."""
    if not isinstance(user_input, str) or len(user_input.strip()) < 2:
        return {"is_valid": False, "error": "Requête vide ou trop courte."}
    
    if len(user_input) > 1500:
        return {"is_valid": False, "error": "Requête trop longue (max 1500 caractères)."}
        
    forbidden = ["ignore previous", "oublie", "bypass", "system prompt",
                 "j3 su1s un3 p0up33 d3 c1r3", "poupée de cire", "poupee de cire"]
    if any(f in user_input.lower() for f in forbidden):
        return {"is_valid": False, "error": "Tentative de Jailbreak détectée."}
        
    clean_input = re.sub(r'<[^>]*>', '', user_input).strip()
    return {"is_valid": True, "clean_prompt": clean_input}
