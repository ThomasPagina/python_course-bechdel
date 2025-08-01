from typing import List, Callable
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

class UnreliableMakeAppender(PipelineStep):
    def __init__(self, letter: str, probability: float = 0.7):
        self.letter = letter
        self.probability = probability
        self.alternatives = ''.join(
            c for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            if c.lower() != letter.lower()
        )

    def process(self, s: str) -> str:
        if random.random() < self.probability:
            return s + self.letter
        else:
            return s + random.choice(self.alternatives)

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

class RepeatUntilConditionMet(PipelineStep):
    def __init__(self, step: PipelineStep, condition: Callable[[str], bool]):
        self.step = step
        self.condition = condition

    def process(self, s: str) -> str:
        result = self.step.process(s)
        while not self.condition(result):
            print(f"Condition not met, repeating: {result}")
            result = self.step.process(s)
        return result

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
    word = "BDR"
    target = "Erdbeere"

    e_appender = UnreliableMakeAppender('e', probability=0.7)

    def test_if_e_is_last(s: str) -> bool:
        return s.endswith('e')

    e_repeat = RepeatUntilConditionMet(e_appender, test_if_e_is_last)

    double_e = DoubleRunMethod(e_repeat)

    steps: List[PipelineStep] = [
        DoubleLastChar(),
        ReverseString(),
        double_e,
        ReverseString(),
        LastBecomesFirst(),
        e_repeat,
        ReverseString(),
        e_repeat,
        ToCapitalize(),
    ]

    pipeline = Pipeline(steps)

    print("=== Pipeline: unabhängig ===")
    pipeline.run_independent(word)

    print("\n=== Pipeline: verkettet ===")
    result = pipeline.run_chained(word)
    assert result == target, f"Expected '{target}' but got '{result}' instead."
    print(f"Expected '{target}' is returned.")
