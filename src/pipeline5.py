from typing import List
from abc import ABC, abstractmethod

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
        self.steps = steps

    def run_independent(self, s: str) -> str:
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

if __name__ == "__main__":
    word = "sunflower"

    appender = MakeAppender('!')
    print("Beispiel append '!':", appender.process(word))

    reverser = ReverseString()

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
