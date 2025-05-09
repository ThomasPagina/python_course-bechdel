#!/usr/bin/env python3

import glob
import csv
import re

from pipeline9 import Pipeline, PipelineStep
from generateText import generate_text


class LoadConversationsStep(PipelineStep):
    def __init__(self, pattern: str):
        self.pattern = pattern

    def process(self, context: dict) -> dict:
        context['filenames'] = glob.glob(self.pattern)
        return context


class ClassifyStep(PipelineStep):
    def __init__(self, task_name: str, criterion: str, labels: list[str]):
        self.task_name = task_name
        self.criterion = criterion
        self.labels = labels

    def process(self, context: dict) -> dict:
        results = context.setdefault('results', [])
        for fname in context['filenames']:
            with open(fname, encoding='utf-8') as f:
                conversation = f.read().strip()

            prompt = (
                f"Rate the following conversation against this statement: {self.criterion}\n"
                f"Conversation:\n{conversation}\n"
                f"First give a short explanation of your rating, then choose exactly one of the following options:" +
                "".join(f"\n- {lab}" for lab in self.labels)
            )

            response = generate_text(prompt).strip()
            print(f"Response for {fname}:\n{response}\n")
            rating = next(
                (lab for lab in self.labels if lab.lower() in response.lower()),
                None
            )
            if rating is None:
                rating = "Neutral"

            results.append({
                'task': self.task_name,
                'criterion': self.criterion,
                'filename': fname,
                'rating': rating
            })
        return context


class ExtractScriptStyleStep(PipelineStep):
    def process(self, context: dict) -> dict:
        for row in context.get('results', []):
            fname = row['filename']
            base = fname.rsplit('/', 1)[-1]
            match = re.match(r'(.+?\d+)_(.+?)\.txt', base)
            if match:
                row['script'] = match.group(1)
                row['style'] = match.group(2)
            else:
                row['script'] = ''
                row['style'] = ''
        return context


class WriteCsvStep(PipelineStep):
    def __init__(self, out_file: str):
        self.out_file = out_file

    def process(self, context: dict) -> dict:
        with open(self.out_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Task', 'Criterion', 'Script', 'Style', 'Rating'])
            for row in context.get('results', []):
                script_name = row.get('script', '')
                style = row.get('style', '')
                writer.writerow([
                    row['task'],
                    row['criterion'],
                    script_name,
                    style,
                    row['rating']
                ])
        print(f"CSV geschrieben: {self.out_file}")
        return context


if __name__ == "__main__":
    tasks = [
        (
            "NonManTopic",
            "The conversation between two women includes at least one topic other than a man."
        ),
        (
            "ManTopic",
            "The conversation includes a man as a topic."
        ),
        (
            "WomenDialogue",
            "Both women characters talk to each other."
        ),
        (
            "ManFocused",
            "The primary subject of the conversation is a specific man or men."
        ),
        (
            "NotManFocused",
            "The primary subject of the conversation is something else than a man."
        ),
        (
            "IndirectMan",
            "The conversation indirectly refers to a man and that topic is dominant."
        ),
        (
            "SuperficialMan",
            "The conversation only superficially mentions a man."
        )	
    ]

    labels = [
        "Fully matches",
        "Largely matches",
        "Neutral",
        "Largely not matches",
        "Does not match"
    ]

    steps: list[PipelineStep] = []
    steps.append(LoadConversationsStep("data/conversations/*.txt"))
    for name, criterion in tasks[3:5]:
        steps.append(ClassifyStep(name, criterion, labels))
    steps.append(ExtractScriptStyleStep())
    steps.append(WriteCsvStep("ratings.csv"))

    pipeline = Pipeline(steps)
    pipeline.process({})
