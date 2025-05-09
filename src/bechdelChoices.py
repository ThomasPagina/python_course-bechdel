import os
import glob
import csv
import re
from generateText import generate_text
from typing import List

class StatementSet:
    """
    Encapsulates a set of three ordered statements for classification and scoring.
    """
    def __init__(self, name: str, prompt_intro: str, statements: List[str]):
        self.name = name
        self.prompt_intro = prompt_intro
        # Ordered best→worst for Bechdel alignment
        self.statements = statements

    def process(self, conversation: str) -> float:
        """
        Generate the model response, parse it, and return a score between -1 and 1.
        """
        # Build prompt with options a), b), c)
        options = "\n".join(
            f"{chr(97 + i)}) {text}" for i, text in enumerate(self.statements)
        )
        prompt = (
            f"{self.prompt_intro}\n"
            f"Conversation:\n{conversation}\n"
            f"{options}\n"
            "Answer with a, b, or c."
        )
        response = generate_text(prompt).strip().lower()
        print(f"Response:\n{response}\n")
        choice = response[:1]
        idx = ord(choice) - 97
        # Map index 0→1.0, 1→0.0, 2→-1.0
        if idx == 0:
            return 1.0
        elif idx == 1:
            return 0.0
        elif idx == 2:
            return -1.0
        else:
            # Unknown response
            return 0.0

class SimpleBechdelPipeline:
    def __init__(self,
                 data_folder: str,
                 output_file: str,
                 statement_sets: List[StatementSet]):
        self.data_folder = data_folder
        # pattern: data/conversations/<scriptname><number>_<style>.txt
        self.input_pattern = os.path.join(data_folder, '*.txt')
        self.output_file = output_file
        self.statement_sets = statement_sets

    def run(self):
        files = sorted(glob.glob(self.input_pattern))
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Script', 'Number', 'Style', 'Test', 'Score']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for filepath in files:
                # extract metadata from filename
                base = os.path.splitext(os.path.basename(filepath))[0]
                # split script number and style by underscore
                if '_' in base:
                    name_part, style = base.split('_', 1)
                else:
                    name_part, style = base, ''
                # split trailing digits for number
                m = re.match(r"([a-zA-Z]+)(\d+)$", name_part)
                if m:
                    script, number = m.group(1), m.group(2)
                else:
                    script, number = name_part, ''

                # read conversation
                with open(filepath, encoding='utf-8') as f:
                    conv = f.read().strip()

                # process each test
                for stmt_set in self.statement_sets:
                    score = stmt_set.process(conv)
                    writer.writerow({
                        'Script': script,
                        'Number': number,
                        'Style': style,
                        'Test': stmt_set.name,
                        'Score': score
                    })
        print(f"Done! Ratings saved to {self.output_file}")

if __name__ == '__main__':
    # Define the four Bechdel-oriented statement sets
    subject_set = StatementSet(
        name='Subject',
        prompt_intro='Which of the following three statements is more applicable to this conversation regarding its primary subject?',
        statements=[
            'The primary subject of the conversation is something else than a man.',
            'The primary subject of the conversation is a man and in equal measure something else.',
            'The primary subject of the conversation is a specific man or men.'
        ]
    )
    women_set = StatementSet(
        name='Women',
        prompt_intro='Which of the following three statements best describes who is speaking?',
        statements=[
            'Both women are talking (Both have at least one line).',
            'Only one woman is talking (Only one has at least one line).',
            'No woman is talking (Neither has a line).'
        ]
    )
    topic_set = StatementSet(
        name='Topic',
        prompt_intro='Which of the following three statements describes the topic between the two women?',
        statements=[
            'The conversation between the two women does not deal with a man.',
            'The conversation between the two women includes at least one topic other than a man.',
            'The conversation between the two women includes no other topic than a man.'
        ]
    )
    conceal_set = StatementSet(
        name='Concealment',
        prompt_intro='Which of the following three statements best describes how the conversation refers to a man?',
        statements=[
            'The conversation is only talking in a concealed way about a man.',
            'The conversation sometimes directly refers to a man and sometimes is concealed.',
            'The conversation is openly and unconcealed about a man.'
        ]
    )

    # Initialize and run the pipeline
    pipeline = SimpleBechdelPipeline(
        data_folder='data/conversations',
        output_file='ratings_scored.csv',
        statement_sets=[subject_set, women_set, topic_set, conceal_set]
    )
    pipeline.run()
