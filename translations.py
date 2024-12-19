from deep_translator import GoogleTranslator
import re

with open('messages.pot', 'r', encoding='utf-8') as file:
    pot_content = file.read()

# Find all msgid entries using regex
msgid_pattern = re.compile(r'msgid "(.*?)"')
msgids = msgid_pattern.findall(pot_content)

# Translate each msgid entry to Spanish
translations = {}
for msgid in msgids:
    translation = GoogleTranslator(source='en', target='es').translate(msgid)
    translations[msgid] = translation

# Write the translated content to a new .po file
with open('app/translations/es/LC_MESSAGES/messages.po', 'w', encoding='utf-8') as po_file:
    po_file.write('''# Translations for PROJECT
# Generated by script

msgid ""
msgstr ""
"Project-Id-Version: PROJECT VERSION\\n"
"Report-Msgid-Bugs-To: EMAIL@ADDRESS\\n"
"POT-Creation-Date: 2024-12-19 16:52+0200\\n"
"PO-Revision-Date: 2024-12-19 19:35+0200\\n"
"Last-Translator: YOUR_NAME <YOUR_EMAIL>\\n"
"Language-Team: Spanish <es@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Generated-By: Babel 2.16.0\\n"
"Language: es\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"
''')

    # Add translated msgid and msgstr pairs
    for msgid in msgids:
        msgstr = translations.get(msgid, '')
        po_file.write(f'\n#: Generated\n')
        po_file.write(f'msgid "{msgid}"\n')
        po_file.write(f'msgstr "{msgstr}"\n')

print("Translation complete!")

