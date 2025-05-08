from typing import Callable
import random

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

def make_appender(letter: str, probability: float = 0.7) -> Callable[[str], str]:
    """
    Gibt eine Funktion zurück, die an das Ende eines Strings entweder
    mit Wahrscheinlichkeit `probability` den Buchstaben `letter` anfügt,
    ansonsten einen zufälligen anderen Buchstaben derselben Kategorie.

    :param letter:       der gewünschte Anfügebuchstabe
    :param probability:  Wahrscheinlichkeit, mit der `letter` tatsächlich angehängt wird
    :return:             eine Funktion, die einen String entgegennimmt und modifiziert zurückgibt
    """
    alternatives = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ".replace(letter.lower(), "")

    def appender(s: str) -> str:
        # Würfelwurf
        if random.random() < probability:
            return s + letter
        else:
            return s + random.choice(alternatives)

    return appender

def make_double_run_method(func: Callable[[str], str]) -> str:
    """
    Wendet die Funktion `func` auf den String `s` an und gibt das Ergebnis aus.
    """
    def wrapper(s: str) -> str:
        funcname = func.__name__
        print(f"Running {funcname} on '{s}'")
        result = func(s)
        print(f"first run: {result}")
        result = func(result)
        print(f"second run: {result}")
        return result
    return wrapper

def repeat_until_condition_met(func: Callable[[str], str], condition: Callable[[str], bool]) -> Callable[[str], str]:
    """
    Gibt eine Funktion zurück, die `func` so lange aufruft, bis die Bedingung `condition` erfüllt ist.
    """
    def wrapper(s: str) -> str:
        result = func(s)
        while not condition(result):
            print(f"Condition not met, repeating: {result}")
            result = func(s)
        return result
        
    return wrapper




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
    word = "BDR"
    target = "Erdbeere"

    # Beispiel: Appender-Funktion erstellen
    append_exclamation = make_appender('!')
    print("Beispiel append '!':", append_exclamation(word))

    #TODO: Turn into flowerpower

    e_new = make_appender('e')
    def test_if_e_is_last(s: str) -> bool:
        return s[-1] == 'e'
    e_new = repeat_until_condition_met(e_new, test_if_e_is_last)
    
    double_e = make_double_run_method(e_new)
   
   

    # Liste der Methoden (gleich für beide Pipelines)
    methods = [
        double_last_char,
        reverse_string,
        double_e,
        reverse_string,
        last_becomes_first,
        e_new,
        reverse_string,
        e_new,
        to_capitalize,

    ]

    print("=== Pipeline: unabhängig ===")
    pipeline_independent(word, methods)

    print("\n=== Pipeline: verkettet ===")
    result_chained = pipeline_chained(word, methods)
    assert result_chained == target, f"Expected '{target}' but got '{result_chained}' instead."
    print(f"Expected '{target}' is returned.")