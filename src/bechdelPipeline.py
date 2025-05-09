#!/usr/bin/env python3
"""
Objektorientierte Version von SimpleBechdel3.py.
Verwendet eine separate generateText.py für die Textgenerierung.
"""
import glob
import csv
import re

from pipeline9 import Pipeline, PipelineStep
from generateText import generate_text


class LoadConversationsStep(PipelineStep):
    """
    Lädt alle Konversationsdateien anhand eines Glob-Patterns.
    """
    def __init__(self, pattern: str):
        self.pattern = pattern

    def process(self, context: dict) -> dict:
        context['filenames'] = glob.glob(self.pattern)
        return context


class ClassifyStep(PipelineStep):
    """
    Führt für jede Datei eine Klassifikation anhand eines Kriteriums durch.
    """
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
            # log response
            print(f"Response for {fname}:\n{response}\n")
            # Normalisiere die Antwort
            # Suche nach einem Label in der Antwort, unabhängig von Position
            rating = next(
                (lab for lab in self.labels if lab.lower() in response.lower()),
                None
            )
            # Fallback auf "Neutral", falls kein Label erkannt wurde
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
    """
    Extrahiert Skript-Namen und Stil aus dem Dateinamen.
    Script-Namen können Unterstriche enthalten, enden aber immer auf eine Ziffer gefolgt von einem Unterstrich.
    Erwartetes Format: AnyNameWithDigits_Style.txt
    """
    def process(self, context: dict) -> dict:
        for row in context.get('results', []):
            fname = row['filename']
            base = fname.rsplit('/', 1)[-1]
            # Split am Unterstrich, der auf eine Ziffer folgt
            match = re.match(r'(.+?\d+)_(.+?)\.txt', base)
            if match:
                row['script'] = match.group(1)
                row['style'] = match.group(2)
            else:
                row['script'] = ''
                row['style'] = ''
        return context


class WriteCsvStep(PipelineStep):
    """
    Schreibt die Ergebnisse in eine CSV-Datei.
    """
    def __init__(self, out_file: str):
        self.out_file = out_file

    def process(self, context: dict) -> dict:
        with open(self.out_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Task', 'Criterion', 'Script', 'Style', 'Rating'])
            for row in context.get('results', []):
                # Nur den reinen Skript-Namen (ohne Pfad)
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
    # Definiere die Bechdel-Test-Tasks
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

    # Baue die Pipeline
    steps: list[PipelineStep] = []
    steps.append(LoadConversationsStep("data/conversations/*.txt"))
    for name, criterion in tasks[3:5]:
        steps.append(ClassifyStep(name, criterion, labels))
    steps.append(ExtractScriptStyleStep())
    steps.append(WriteCsvStep("ratings.csv"))

    pipeline = Pipeline(steps)
    pipeline.process({})
