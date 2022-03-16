from datetime import datetime


def PossibleAnswers(input_text):
    message = str(input_text).lower()

    if message in ("Hola", "hola"):
        return "Hola, como puedo ayudarte?"

    if message in ("Krone Bot", "como estas?", "1", "2"):
        return "Soy Krone Bot"

    return "No te entiendo"