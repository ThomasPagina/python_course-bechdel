from typing import List
from abc import ABC, abstractmethod
import random

class PipelineStep(ABC):
    @abstractmethod
    def process(self, s: str) -> str:
        pass
    def __repr__(self) -> str:
        return self.__class__.__name__

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

    def __repr__(self) -> str:
        return f"MakeAppender({self.letter})"

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
        def signature(step: PipelineStep) -> str:
            if isinstance(step, MakeAppender):
                return f"MakeAppender({step.letter})"
            return step.__class__.__name__

        attempts = 0
        tested = set()
        while True:
            permuted = self.original_steps.copy()
            random.shuffle(permuted)
            key = tuple(signature(step) for step in permuted)
            if key in tested:
                continue
            tested.add(key)
            attempts += 1
            result = source
            for step in permuted:
                result = step.process(result)
            if result == target:
                self.steps = permuted
                print(f"Gefundene Schrittfolge nach {attempts} Versuchen: {key}")
                return permuted
            print(f"Training: Versuch {attempts}, Ergebnis: {result}\n{key}")

if __name__ == "__main__":
    word = "BDR"
    target = "Erdbeere"

    e_appender = MakeAppender('e')
    reverser = ReverseString()

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
