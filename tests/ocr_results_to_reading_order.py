from evaluator import *
from dataclasses import dataclass
from typing import List
import random

DESCRIPTION = "Test if the model can generate Python code to sort OCR results into natural reading order."

TAGS = ["code", "python", "ocr", "astahlman"]


@dataclass
class Word:
    x1: float
    y1: float
    x2: float
    y2: float
    text: str


words = """
The quick brown fox jumps over the lazy dog.
Pack my box with five dozen liquor jugs.
How vexingly quick daft zebras jump!
"""
words = words.split()
assert len(words) == 23


def generate_test_data() -> List[Word]:

    # Initialize starting coordinates for the first word
    x, y = 0.1, 0.1
    test_data = []
    for i, word in enumerate(words):
        # Start a new line after every 9 words
        if i % 9 == 0 and i != 0:
            x = 0.1  # Reset x to the left margin
            y += 0.1  # Move to the next line

        # Calculate word dimensions
        width = len(word) * 0.02  # Width based on word length
        height = 0.05  # Fixed height for all words

        # Create a Word object with slight vertical variation
        vertical_variation = random.uniform(-0.005, 0.005)
        test_data.append(
            Word(
                x,
                y + vertical_variation,
                x + width,
                y + height + vertical_variation,
                word,
            )
        )

        # Move x coordinate for the next word
        x += width + 0.01  # Add word width plus a small gap

    random.shuffle(test_data)
    return test_data


class_def = """
@dataclass
class Word:
    x1: float
    y1: float
    x2: float
    y2: float
    text: str
"""

question = f"""
Create a Python function called `sort_ocr_results` that takes a list of Word objects (defined below) and sorts them into natural reading order (top-to-bottom, left-to-right). The function should handle minor variations in y-coordinates for words on the same line.

{class_def}

Your function should take a List[Word] as input and return a List[Word] sorted in reading order.
"""


test_case = """
from dataclasses import dataclass
import typing

{class_def}
words = {words}

def evaluate_sorting(sorted_words: typing.List[Word]) -> bool:
    return [word.text for word in sorted_words] == words

test_data = {test_data}
sorted_result = sort_ocr_results(test_data)
assert evaluate_sorting(sorted_result), "Sorting is incorrect"
print("Sorting is correct")
""".format(
    class_def=class_def,
    words=words,
    test_data=generate_test_data(),
)

TestOCRSorting = (
    question
    >> LLMRun()
    >> ExtractCode()
    >> PythonRun(test_case)
    >> SubstringEvaluator("Sorting is correct")
)

if __name__ == "__main__":
    print(run_test(TestOCRSorting))
