from deep_translator import GoogleTranslator
import random, string


def rand_string(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def translate(text, lang1, lang2):
    translator = GoogleTranslator(source=lang1, target=lang2)
    translated_text = translator.translate(text)
    return translated_text