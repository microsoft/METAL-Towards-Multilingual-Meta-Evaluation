code_to_name = {
    "AR": "arabic",
    "EN": "english",
    "ZH": "chinese_simplified",
    "FR": "french",
    "HI": "hindi",
    "BN": "bengali",
    "JA": "japanese",
    "RU": "russian",
    "SW": "swahili",
    "TR": "turkish",
}

metric_aliases = {
    "Linguistic Acceptability": "linguistic_acceptability",
    "Output Content Quality": "output_content_quality",
    "Task Quality": "task_quality",
    "Hallucinations": "hallucinations",
    "Problematic Content": "problematic_content",
}

str_to_int = {"Good": 2, "Medium": 1, "Bad": 0, "Absent": 0, "Present": 1}

name_to_code = {v: k for k, v in code_to_name.items()}

SYSTEM_MESSAGE = """
# Role
You are a helpful assistant.

## Task
Summarize: Given a passage and a brief summary of that passage which attempts to capture the essence of it, your task is to evaluate the summary with respect to the given passage and listed set of metrics. For each metric listed, you must always return a score and a justification of the score. Note that, both the passage and its summary are given in {language}.

### Outputs
- The description 
    - A description of the metric, how it works, what it measures and how to utilize it.

- The score: 
    - Scores are integer values in accoradance to the metric description provided.

- The justification:
    - Justification provide the evidence and step by step reasoning on how the score is reached. Justifications must always be given in English, be factual and reference the evidence used in each passage to support claims. Claims **must always** be referenced with evidence. For referencing use passage name <dot> the line number.

- The Output format:
    - Your output **must** always follow the below format and instructions.
    - {format_instructions}
"""

HUMAN_MESSAGE = """
PASSAGE = '{passage}'
SUMMARY = '{summary}'
LANGUAGE = '{language}'

Now, evaluate the above summary in the context of the above given passage with regard to the following metrics.

### Metrics
You are given below the metrics, with their descriptions and scoring schema in a JSON format.

```json
{metric_description}
```
"""