from typing import List
from abc import ABC, abstractmethod
import itertools

class PipelineStep(ABC):
    """Abstrakte Basisklasse für Pipeline-Schritte."""
    @abstractmethod
    def process(self, s: str) -> str:
        pass

    def __repr__(self) -> str:      
        return self.__class__.__name__
    


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
    def __repr__(self) -> str:
        return f"MakeAppender({self.letter})"
    
class DoubleRunMethod(PipelineStep):
    def __init__(self, step: PipelineStep):
        self.step = step

    def process(self, s: str) -> str:
        funcname = self.step.__class__.__name__
        print(f"Running {funcname} on '{s}'")
        result = self.step.process(s)
        print(f"first run: {result}")
        result = self.step.process(result)
        print(f"second run: {result}")
        return result

class Pipeline:
    """Verwaltet eine Folge von PipelineSteps, führt sie aus und ermöglicht Training der Reihenfolge."""
    def __init__(self, steps: List[PipelineStep]):
        self.original_steps = steps.copy()
        self.steps = steps.copy()

    def run_independent(self, s: str) -> str:
        result = None
        for step in self.steps:
            result = step.process(s)
            print(result)
        return result

    def run_chained(self, s: str) -> str:
        current = s
        for step in self.steps:
            current = step.process(current)
            #print(current)
        return current


    def train_chain(self, source: str, target: str) -> List[PipelineStep]:
        """
        Trainiert die Reihenfolge der Pipeline, indem zufällige Permutationen
        der Ursprungs-Schritte solange ausprobiert werden, bis aus `source`
        das `target` resultiert. Bereits getestete Permutationen (nach Signatur)
        werden übersprungen.
        """
        def signature(step: PipelineStep) -> str:
            if isinstance(step, MakeAppender):
                return f"MakeAppender({step.letter})"
            return step.__class__.__name__

        attempts = 0
        for permutation in itertools.permutations(self.original_steps):
            attempts += 1
            self.steps = list(permutation)
            result = self.run_chained(source)
            if result == target:
                print(f"Found valid permutation after {attempts} attempts: {self.steps}")
                return self.steps
            else:
                print(f"Attempt {attempts}: {result}")

if __name__ == "__main__":
    word = "BDR"
    target = "Erdbeere"

    # Einzigartige Instanzen wiederverwenden
    e_appender = MakeAppender('e')
    reverser = ReverseString()
    

    # Liste der PipelineSteps mit mehrfacher Referenz
    steps: List[PipelineStep] = [
        DoubleLastChar(),
       	LastBecomesFirst(),
        e_appender, e_appender, e_appender, e_appender,
        reverser, reverser, reverser,
        ToCapitalize()
    ]

    pipeline = Pipeline(steps)
    print("\n=== Innerhalb verkettet ===")
    pipeline.run_chained(word)

    print("\n=== Pipeline trainiert ===")
    pipeline.train_chain(word, target)
    pipeline.run_chained(word)
