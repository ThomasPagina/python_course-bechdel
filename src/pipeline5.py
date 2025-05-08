from typing import List
from abc import ABC, abstractmethod

class PipelineStep(ABC):
    """Abstrakte Basisklasse für Pipeline-Schritte."""
    @abstractmethod
    def process(self, s: str) -> str:
        pass

class ToLower(PipelineStep):
    def process(self, s: str) -> str:
        """Wandelt den String in Kleinbuchstaben um."""
        return s.lower()

class ToCapitalize(PipelineStep):
    def process(self, s: str) -> str:
        """Macht den ersten Buchstaben groß, den Rest klein."""
        return s.capitalize()

class ReverseString(PipelineStep):
    def process(self, s: str) -> str:
        """Kehrt den String um."""
        return s[::-1]

class RemoveLastChar(PipelineStep):
    def process(self, s: str) -> str:
        """Entfernt den letzten Buchstaben (falls vorhanden)."""
        return s[:-1] if s else s

class SwapFirstLast(PipelineStep):
    def process(self, s: str) -> str:
        """Vertauscht ersten und letzten Buchstaben."""
        if len(s) < 2:
            return s
        return s[-1] + s[1:-1] + s[0]

class DoubleLastChar(PipelineStep):
    def process(self, s: str) -> str:
        """Verdoppelt den letzten Buchstaben."""
        if not s:
            return s
        return s + s[-1]

class LastBecomesFirst(PipelineStep):
    def process(self, s: str) -> str:
        """Setzt den letzten Buchstaben an den Anfang."""
        if len(s) < 2:
            return s
        return s[-1] + s[:-1]

class MakeAppender(PipelineStep):
    def __init__(self, letter: str):
        self.letter = letter

    def process(self, s: str) -> str:
        """Hängt den Buchstaben `letter` ans Ende des Strings an."""
        return s + self.letter

class Pipeline:
    """Verwaltet eine Folge von PipelineSteps und führt sie aus."""
    def __init__(self, steps: List[PipelineStep]):
        self.steps = steps

    def run_independent(self, s: str) -> str:
        """
        Wendet jeden Schritt auf den Ursprungs-String an
        und gibt die Ergebnisse aus.
        """
        for step in self.steps:
            result = step.process(s)
            print(result)
        return result


    def run_chained(self, s: str) -> str:
        """
        Wendet jeden Schritt auf das Ergebnis des vorherigen Schritts an
        und gibt die Zwischenergebnisse aus.
        """
        current = s
        for step in self.steps:
            current = step.process(current)
            print(current)
        return current

if __name__ == "__main__":
    word = "sunflower"

    # Beispiel: Appender-Schritt erstellen und nutzen
    appender = MakeAppender('!')
    print("Beispiel append '!':", appender.process(word))

    reverser = ReverseString()

    # Liste der PipelineSteps (gleich für beide Pipelines)
    steps: List[PipelineStep] = [
        ToLower(),
        reverser,
        DoubleLastChar(),
        LastBecomesFirst(),
        reverser,
        ToCapitalize(),
        appender,
    ]

    pipeline = Pipeline(steps)

    print("=== Pipeline: unabhängig ===")
    pipeline.run_independent(word)

    print("\n=== Pipeline: verkettet ===")
    pipeline.run_chained(word)
