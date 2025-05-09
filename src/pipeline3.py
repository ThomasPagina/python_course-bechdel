from typing import Callable

def to_lower(s: str) -> str:
    return s.lower()

def to_capitalize(s: str) -> str:
    return s.capitalize()

def reverse_string(s: str) -> str:
    return s[::-1]

def remove_last_char(s: str) -> str:
    return s[:-1] if s else s

def swap_first_last(s: str) -> str:
    if len(s) < 2:
        return s
    return s[-1] + s[1:-1] + s[0]

def double_last_char(s: str) -> str:
    if not s:
        return s
    return s + s[-1]

def last_becomes_first(s: str) -> str:
    if len(s) < 2:
        return s
    return s[-1] + s[:-1]

def double(s: str) -> str:
    return s * 2

def make_appender(letter: str) -> Callable[[str], str]:
    def appender(s: str) -> str:
        return s + letter
    return appender

def pipeline_independent(s: str, funcs: list) -> str:
    for f in funcs:
        result = f(s)
        print(result)
    return result

def pipeline_chained(s: str, funcs: list) -> str:
    current = s
    for f in funcs:
        current = f(current)
        print(current)
    return current

if __name__ == "__main__":
    word = "BDR"
    target = "Erdbeere"

    append_exclamation = make_appender('!')
    print("Beispiel append '!':", append_exclamation(word))

    e_new = make_appender('e')

    methods = [
        double_last_char,
        reverse_string,
        e_new,
        e_new,
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
