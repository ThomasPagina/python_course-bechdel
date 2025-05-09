from typing import List
from abc import ABC, abstractmethod
import random

class PipelineStep(ABC):
    @abstractmethod
    def process(self, s: str) -> str:
        pass

class ToLower(PipelineStep):
    def process(self, s: str) -> str:
        return s.lower()

class ToCapitalize(PipelineStep):
    def process(self, s: str) -> str:
        return s.capitalize()

class ReverseString(PipelineStep):
    def process(self, s: str) -> str:
        return s[::-1]

class RemoveLastChar(PipelineStep):
    def process(self, s: str) -> str:
        return s[:-1] if s else s

class SwapFirstLast(PipelineStep):
    def process(self, s: str) -> str:
        if len(s) < 2:
            return s
        return s[-1] + s[1:-1] + s[0]

class DoubleLastChar(PipelineStep):
    def process(self, s: str) -> str:
        if not s:
            return s
        return s + s[-1]

class LastBecomesFirst(PipelineStep):
    def process(self, s: str) -> str:
        if len(s) < 2:
            return s
        return s[-1] + s[:-1]

class MakeAppender(PipelineStep):
    def __init__(self, letter: str):
        self.letter = letter

    def process(self, s: str) -> str:
        return s + self.letter

class Pipeline:
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
            print(current)
        return current

    def train_chain(self, source: str, target: str) -> List[PipelineStep]:
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

    reverser = ReverseString()

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

    print("\n=== Pipeline: trainiert ===")
    pipeline.train_chain("rdb", "Erdbeere")
    pipeline.run_chained(word)
