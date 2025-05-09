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

def pipeline_independent(s: str, funcs: list) -> None:
    for f in funcs:
        result = f(s)
        print(result)
     

def pipeline_chained(s: str, funcs: list) -> None:
    current = s
    for f in funcs:
        current = f(current)
        print(current)

if __name__ == "__main__":
 
    word = "Sunflower"

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

