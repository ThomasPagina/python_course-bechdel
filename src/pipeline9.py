from typing import List
from abc import ABC, abstractmethod
import random
from graphviz import Digraph

class PipelineStep(ABC):
    """Abstrakte Basisklasse für Pipeline-Schritte."""
    @abstractmethod
    def process(self, s: str) -> str:
        pass
    def __repr__(self) -> str:
        """Gibt den Klassennamen zurück."""
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
        """Gibt den Klassennamen zurück."""
        return f"MakeAppender({self.letter})"

class Pipeline(PipelineStep):
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

    def visualize(self, filename: str = None, format: str = 'png') -> Digraph:
        """
        Erstellt eine Graphviz-Darstellung der Pipeline.
        Jede Pipeline (auch verschachtelt) wird als Kasten dargestellt.
        Wenn `filename` angegeben, wird das Ergebnis in eine Datei gerendert.
        """
        graph = Digraph(format=format)
        graph.attr('node', shape='box')

        def _add_steps(subg: Digraph, steps: List[PipelineStep], parent: str):
            with subg.subgraph(name=f'cluster_{parent}') as c:
                c.attr(label=parent)
                c.attr('node', shape='box')
                prev = None
                for idx, st in enumerate(steps):
                    node_id = f"{parent}_{idx}"
                    if isinstance(st, Pipeline):
                        # Verschachtelte Pipeline
                        _add_steps(c, st.steps, node_id)
                    else:
                        c.node(node_id, str(st))
                    if prev:
                        c.edge(prev, node_id)
                    prev = node_id

        _add_steps(graph, self.steps, 'Pipeline')

        if filename:
            graph.render(filename, cleanup=True)
        return graph

    def process(self, s: str) -> str:
        """Wendet die Pipeline auf den String an."""
        return self.run_chained(s)
    def __repr__(self) -> str:
        """Gibt die Schrittfolge als String zurück."""
        return " -> ".join([step.__class__.__name__ for step in self.steps])

if __name__ == "__main__":
    word = "BDR"
    target="Erdbeere"

 

    reverser = ReverseString()
    e_appender = MakeAppender('e')
    steps_Double_e = [
       e_appender, e_appender
    ]
    pipeline_Double_e = Pipeline(steps_Double_e)

   

    # Liste der PipelineSteps (gleich für beide Pipelines)
    steps: List[PipelineStep] = [
          DoubleLastChar(),
          LastBecomesFirst(),
          e_appender, e_appender,
          pipeline_Double_e,
          reverser, reverser, reverser,
          ToCapitalize()
    ]

    pipeline = Pipeline(steps)

    print("\n=== Pipeline: verkettet ===")
    pipeline.run_chained(word)

    # Beispiel für train_chain
    print("\n=== Pipeline: trainiert ===")
    # z.B. trainiert Pipeline-Schritte, um aus 'rdb' 'Erdbeere' zu erzeugen
    pipeline.train_chain(word,target)
    pipeline.run_chained(word)
    pipeline.visualize("pipeline", format='png').view()
    #show the pipeline graph

