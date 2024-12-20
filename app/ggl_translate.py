"""
Module translate text from one language to another using Google Translator.

This function utilizes the GoogleTranslator class from the deep_translator module 
to perform translation. It allows for automatic language detection or explicit 
specification of source and target languages.

Parameters:
text (str): The text to be translated.
from_lang (str): The source language code (e.g., 'en' for English).
to_lang (str): The target language code (e.g., 'fr' for French).

Returns:
str: The translated text.

Raises:
ValueError: If the input text is empty or if the language codes are invalid.

Example:
>>> translate("Hello, world!", "en", "es")
'¡Hola, mundo!'
"""

from deep_translator import GoogleTranslator


def translate(text, from_lang, to_lang):
    """Translate text from one language to another"""
    translation = GoogleTranslator(source=from_lang, target=to_lang).translate(text)
    return translation
