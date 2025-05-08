from typing import Callable

def to_lower(s: str) -> str:
    """Wandelt den String in Kleinbuchstaben um."""
    return s.lower()

def to_capitalize(s: str) -> str:
    """Macht den ersten Buchstaben groß, den Rest klein."""
    return s.capitalize()

def reverse_string(s: str) -> str:
    """Kehrt den String um."""
    return s[::-1]

def remove_last_char(s: str) -> str:
    """Entfernt den letzten Buchstaben (falls vorhanden)."""
    return s[:-1] if s else s

def swap_first_last(s: str) -> str:
    """Vertauscht ersten und letzten Buchstaben."""
    if len(s) < 2:
        return s
    return s[-1] + s[1:-1] + s[0]

def double_last_char(s: str) -> str:
    """Verdoppelt den letzten Buchstaben."""
    if not s:
        return s
    return s + s[-1]

def last_becomes_first(s: str) -> str:
    """Setzt den letzten Buchstaben an den Anfang."""
    if len(s) < 2:
        return s
    return s[-1] + s[:-1]

def double(s: str) -> str:
    """Verdoppelt den String."""
    return s * 2

def make_appender(letter: str) -> Callable[[str], str]:
    """Gibt eine Funktion zurück, die den Buchstaben `letter` an das Ende eines Strings anfügt."""
    def appender(s: str) -> str:
        return s + letter
    return appender


def pipeline_independent(s: str, funcs: list) -> str:
    """
    Wendet jede Funktion jeweils auf den Ursprungs-String an
    und gibt das Ergebnis aus.
    """
    for f in funcs:
        result = f(s)
        print(result)
    return result


def pipeline_chained(s: str, funcs: list) -> str:
    """
    Wendet jede Funktion auf das Ergebnis der vorherigen Anwendung an
    und gibt das Zwischenergebnis aus.
    """
    current = s
    for f in funcs:
        current = f(current)
        print(current)
    return current

if __name__ == "__main__":
    # Ausgangswort
    word = "sunflower" # try lippstick
    target = "Flowerpower!" 

    # Beispiel: Appender-Funktion erstellen
    append_exclamation = make_appender('!')
    print("Beispiel append '!':", append_exclamation(word))

  

    # Liste der Methoden (gleich für beide Pipelines)
    methods = [
        to_lower,
        reverse_string,
        remove_last_char,
        remove_last_char,
        remove_last_char,
        double,
        remove_last_char,
        remove_last_char,
        make_appender('p'),
        reverse_string,
        to_capitalize,
        append_exclamation

    ]

    print("=== Pipeline: unabhängig ===")
    pipeline_independent(word, methods)

    print("\n=== Pipeline: verkettet ===")
    result_chained = pipeline_chained(word, methods)
    assert result_chained == target, f"Erwartet: '{target}', aber erhalten: '{result_chained}'"
    print("Endergebnis:", result_chained)
