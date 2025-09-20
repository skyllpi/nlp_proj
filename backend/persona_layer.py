# In backend/persona_layer.py

import random

def apply_persona(answer: str, persona: str):
    """
    Wraps the retrieved answer in a persona-based template.
    """
    personas = {
        "formal": [
            "According to the document, the relevant information is as follows: '{answer}'",
            "The provided text states: '{answer}'",
            "Based on the extracted content, we can ascertain that: '{answer}'"
        ],
        "friendly": [
            "Hey! I found this in the document for you: '{answer}' Hope it helps!",
            "I looked through the PDF and here's what I think you're looking for: '{answer}'",
            "Got it! Here's the relevant snippet: '{answer}'"
        ],
        "skeptical": [
            "Well, the document *claims* that: '{answer}', but you might want to verify that.",
            "If you trust the source, it says: '{answer}'",
            "The text suggests the following, for what it's worth: '{answer}'"
        ]
    }
    
    persona_key = persona.lower()
    if persona_key not in personas:
        return answer # Return the raw answer if persona is not found
        
    # Pick a random template from the list for variety.
    template = random.choice(personas[persona_key])
    return template.format(answer=answer)