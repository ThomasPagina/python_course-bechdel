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

def pipeline_independent(s: str, funcs: list) -> None:
    """
    Wendet jede Funktion jeweils auf den Ursprungs-String an
    und gibt das Ergebnis aus.
    """
    for f in funcs:
        result = f(s)
        print(result)

def pipeline_chained(s: str, funcs: list) -> None:
    """
    Wendet jede Funktion auf das Ergebnis der vorherigen Anwendung an
    und gibt das Zwischenergebnis aus.
    """
    current = s
    for f in funcs:
        current = f(current)
        print(current)

if __name__ == "__main__":
    # Ausgangswort
    word = "sunflower"
   

    # Liste der Methoden (gleich für beide Pipelines)
    methods = [
        to_lower,
        reverse_string,
        double_last_char,
        last_becomes_first,
        reverse_string,
        to_capitalize
    ]

    print("=== Pipeline: unabhängig ===")
    pipeline_independent(word, methods)

    print("\n=== Pipeline: verkettet ===")
    pipeline_chained(word, methods)

