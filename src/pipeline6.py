from typing import List
from abc import ABC, abstractmethod
import random

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
    """Verwaltet eine Folge von PipelineSteps, führt sie aus und ermöglicht Training der Reihenfolge."""
    def __init__(self, steps: List[PipelineStep]):
        # Ursprüngliche Schrittfolge sichern
        self.original_steps = steps.copy()
        self.steps = steps.copy()

    def run_independent(self, s: str) -> str:
        """
        Wendet jeden Schritt auf den Ursprungs-String an
        und gibt die Ergebnisse aus.
        """
        result = None
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

    def train_chain(self, source: str, target: str) -> List[PipelineStep]:
        """
        Trainiert die Reihenfolge der Pipeline, indem zufällige Permutationen
        der Ursprungs-Schritte solange ausprobiert werden, bis aus `source`
        das `target` resultiert. Setzt anschließend `self.steps` auf die gefundene
        Reihenfolge und gibt diese zurück.
        """
        attempts = 0
        while True:
            attempts += 1
            permuted = self.original_steps.copy()
            random.shuffle(permuted)
            result = source
            for step in permuted:
                result = step.process(result)
            if result == target:
                self.steps = permuted
                print(f"Gefundene Schrittfolge nach {attempts} Versuchen")
                return permuted
            print(f"Training: Im {attempts} Versuch lautet das Ergebnis: {result}.")

if __name__ == "__main__":
    word = "BDR"

    # Beispiel: Appender-Schritt erstellen und nutzen
    appender = MakeAppender('!')
    print("Beispiel append '!':", appender.process(word))

    reverser = ReverseString()

    # Liste der PipelineSteps (gleich für beide Pipelines)
    steps: List[PipelineStep] = [
          DoubleLastChar(),
          LastBecomesFirst(),
          MakeAppender('e'),
          MakeAppender('e'),
          MakeAppender('e'),
          MakeAppender('e'),
          ReverseString(),
          ReverseString(),
          ReverseString(),
          ToCapitalize()
    ]

    pipeline = Pipeline(steps)

    print("\n=== Pipeline: verkettet ===")
    pipeline.run_chained(word)

    # Beispiel für train_chain
    print("\n=== Pipeline: trainiert ===")
    # z.B. trainiert Pipeline-Schritte, um aus 'rdb' 'Erdbeere' zu erzeugen
    pipeline.train_chain("rdb", "Erdbeere")
    pipeline.run_chained(word)
