#!/usr/bin/env python3
"""
Language Detector Tool
Simple language detection for TTS input
"""

def detect_language(text: str) -> str:
    """
    Very simple language detection (pt-br/en/es/fr/it).
    Returns a language code string.
    """
    text_lower = text.lower()
    pt_words = ['olá', 'bom', 'boa', 'tarde', 'noite', 'dia', 'porreiro', 'bora', 'lá', 'este', 'é', 'uma', 'para', 'com', 'que', 'não', 'sim', 'muito', 'bem', 'mal', 'grande', 'pequeno']
    if any(w in text_lower for w in pt_words):
        return 'pt-br'
    en_words = ['hello', 'good', 'morning', 'afternoon', 'evening', 'night', 'thank', 'please', 'yes', 'no']
    if any(w in text_lower for w in en_words):
        return 'en'
    es_words = ['hola', 'buenos', 'días', 'tardes', 'noches', 'gracias', 'favor', 'sí', 'no']
    if any(w in text_lower for w in es_words):
        return 'es'
    fr_words = ['bonjour', 'bonsoir', 'salut', 'merci', 'oui', 'non']
    if any(w in text_lower for w in fr_words):
        return 'fr'
    it_words = ['ciao', 'buongiorno', 'buonasera', 'grazie', 'prego', 'sì', 'no']
    if any(w in text_lower for w in it_words):
        return 'it'
    return 'pt-br'  # default 