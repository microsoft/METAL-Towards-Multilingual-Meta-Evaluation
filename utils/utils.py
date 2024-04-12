import os
import sys
import json
import pandas as pd
from queue import Queue
from random import shuffle
from .constants import str_to_int
from pydantic import BaseModel, Field
from threading import Thread, Event
from argparse import ArgumentParser


class Output(BaseModel):
    score: int = Field(
        name="score",
        description="The score for the metric. The score should be reached by considering the description of the metric and carefully evaluating the justification in light of the passages provided and the scale given.",
    )
    justification: str = Field(
        name="justification",
        description="The justification of the metric's score **in under 500 words**. Explain exactly what each passage does and provide the step by step reasoning to reach a conclusion.",
    )
    metric_description: str = Field(
        name="metric_description",
        description="A sentence explaining the metric including exactly how it is measured **in under 100 words**. **Always** provide your own explanation of high and low score settings.",
    )


class DeamonWriter:
    def __init__(self, filename, mode="a"):
        self.filename = filename
        self.mode = mode
        self._queue = Queue()  # queue to store datapoints for processing
        self._flag = Event()  # add an event to close the thread upon completion
        self._thread = Thread(target=self.write, daemon=True)
        self._thread.start()  # start the thread right away

    def put(self, obj):
        self._queue.put(obj)

    def _write(self, obj, f):
        try:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
            f.flush()
        except Exception as e:
            print(f"\n | > Deamon Writer - Error writing to file: {e}. Skipping ...")

    def write(self):
        with open(self.filename, self.mode, encoding="utf-8") as f:
            while True:
                # this is a busy wait
                # not so efficient, but it works
                obj = self._queue.get()
                self._write(obj, f)
                self._queue.task_done()

    def graceful_terminate(self):
        while not self._queue.empty():
            obj = self._queue.get()
            with open(self.filename, "a", encoding="utf-8") as f:
                self._write(obj, f)
            self._queue.task_done()

        self._flag.set()
        self._queue.join()


def read_data(infname, outfname):
    df = pd.read_excel(infname).replace(to_replace=str_to_int)
    df = _get_missing_instances(df, outfname)
    return df


def get_arg_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "-i", "--infname", type=str, default=None, required=True, help="Input file name"
    )
    parser.add_argument(
        "-o",
        "--outfname",
        type=str,
        default=None,
        required=True,
        help="Output file name",
    )
    parser.add_argument(
        "--temperature", type=float, default=0.0, help="Temperature for sampling"
    )
    parser.add_argument(
        "--max_output_tokens", type=int, default=1200, help="Max tokens to generate"
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        required=True,
        choices=["gpt-35-turbo", "gpt-4-32k", "text-bison"],
        help="The model to use for generation",
    )
    parser.add_argument(
        "--prompt_style",
        type=str,
        default="detailed",
        choices=["simple", "detailed"],
        help="The style of prompting to use for the model [EVALUATION ONLY]",
    )
    parser.add_argument(
        "--prompt_file",
        type=str,
        default=None,
        help="File containing the guidance prompt [GENERATION ONLY]",
    )
    parser.add_argument(
        "-l", "--language", type=str, default=None, help="Language of Language code"
    )
    return parser


def _load_predictions(fname):
    with open(fname, "r", encoding="utf-8") as f:
        ids = [json.loads(line.strip())["id"] for line in f]
    return set(ids)


def _get_missing_instances(df, outfname):
    if os.path.exists(outfname):
        n_samples_evaluated = _load_predictions(outfname)
        n_samples = set(df.index.tolist())

        if n_samples_evaluated == n_samples:
            sys.exit(1)
        else:
            remaining_counts = list(n_samples - n_samples_evaluated)
            df = df.loc[remaining_counts]

    return df


def _get_metric(metric, prompt_style="simple"):
    with open(
        os.path.join("metrics", prompt_style, f"{metric}.json"),
        "r",
        encoding="utf-8",
    ) as f:
        metrics = json.load(f)
    return metrics


def get_metrics(metrics, prompt_style="simple", permute=False):
    metrics = [_get_metric(metric, prompt_style) for metric in metrics]

    if permute:
        shuffle(metrics)

    return json.dumps(metrics, indent=4, ensure_ascii=False)


def majority_element(nums):
    candidate, count = None, 0

    for num in nums:
        if not count:
            candidate = num
        count += 1 if num == candidate else -1

    return candidate if nums.count(candidate) > len(nums) // 2 else 1
