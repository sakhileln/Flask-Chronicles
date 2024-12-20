"""
This module checks if the translation service is configured with a valid subscription key. 
It sends a POST request to the Microsoft Translator API with the provided text and language 
parameters. If successful, it returns the translated text; otherwise, it returns an error message.

Parameters:
text (str): The text to be translated.
source_language (str): The language code of the source text (e.g., 'en' for English).
dest_language (str): The language code of the target translation (e.g., 'fr' for French).

Returns:
str: The translated text or an error message if the service is not configured or fails.

Raises:
KeyError: If the translation service configuration is missing or invalid.

Example:
>>> translate("Hello, world!", "en", "es")
'¡Hola, mundo!'
"""

import requests
from flask_babel import _
from app import app


def translate(text, source_language, dest_language):
    """Translarte text from one language to another"""
    if "MS_TRANSLATOR_KEY" not in app.config or not app.config["MS_TRANSLATOR_KEY"]:
        return _("Error: the translation service is not configured.")
    auth = {
        "Ocp-Apim-Subscription-Key": app.config["MS_TRANSLATOR_KEY"],
        "Ocp-Apim-Subscription-Region": "westus",
    }
    r = requests.post(
        "https://api.cognitive.microsofttranslator.com"
        "/translate?api-version=3.0&from={}&to={}".format(
            source_language, dest_language
        ),
        headers=auth,
        json=[{"Text": text}],
    )
    if r.status_code != 200:
        return _("Error: the translation service failed.")
    return r.json()[0]["translations"][0]["text"]
