# METAL: Towards Multilingual Meta-Evaluation

**Official Repository for ["METAL: Towards Multilingual Meta-Evaluation"](https://aclanthology.org/2024.findings-naacl.148/) (Presented at NAACL 2024)**

## Abstract
With the rising human-like precision of Large Language Models (LLMs) in numerous tasks, their utilization in a variety of real-world applications is becoming more prevalent. Several studies have shown that LLMs excel on many standard NLP benchmarks. However, it is challenging to evaluate LLMs due to test dataset contamination and the limitations of traditional metrics. Since human evaluations are difficult to collect, there is a growing interest in the community to use LLMs themselves as reference-free evaluators for subjective metrics. However, past work has shown that LLM-based evaluators can exhibit bias and have poor alignment with human judgments. In this study, we propose a framework for an end-to-end assessment of LLMs as evaluators in multilingual scenarios. We create a carefully curated dataset, covering 10 languages containing native speaker judgments for the task of summarization. This dataset is created specifically to evaluate LLM-based evaluators, which we refer to as meta-evaluation (METAL). We compare the performance of LLM-based evaluators created using GPT-3.5-Turbo, GPT-4, and PaLM2. Our results indicate that LLM-based evaluators based on GPT-4 perform the best across languages, while GPT-3.5-Turbo performs poorly. Additionally, we perform an analysis of the reasoning provided by LLM-based evaluators and find that it often does not match the reasoning provided by human judges.

## Setup
Follow the given commands to create a virtual environment for this project and install necessary packages. 

- Clone this repository in it and run the following commands to install the dependencies

```bash 
# create a virtual environment (preferably, use Python 3.10+)
conda create -n metal python=3.10
conda activate metal

# install dependencies
pip install pandas python-dotenv langchain langchain-community guidance
```
- Create a `.env` file and and add all the API keys/secrets to it, so that they can can loaded using the `dotenv` library

## Directory Structure
```bash
.
├── README.md
├── evaluate_summary.py
├── generate_summary.py
├── generation_prompts
│   ├── bad_prompt.md
│   └── good_prompt.md
├── data
│   └── METAL_dataset.json
├── metrics
│   ├── detailed
│   │   ├── hallucinations.json
│   │   ├── linguistic_acceptability.json
│   │   ├── output_content_quality.json
│   │   ├── problematic_content.json
│   │   └── task_quality.json
│   └── simple
│       ├── hallucinations.json
│       ├── linguistic_acceptability.json
│       ├── output_content_quality.json
│       ├── problematic_content.json
│       └── task_quality.json
└── utils
    ├── __init__.py
    ├── constants.py
    └── utils.py
```

## Dataset
- The dataset is available in the `data/` directory. Please refer to our [paper](https://aclanthology.org/2024.findings-naacl.148/) for the dataset curation methodology, metrics, prompts and annotator instructions.  

- The dataset consists of 100 summaries each, for 10 languages: English (En), French (Fr), Chinese Simplified (Zh), Hindi (Hi), Arabic (Ar), Bengali (Bn), Russian (Ru), Turkish (Tr), Japanese (Ja), and Swahili (Sw). The main text for each summary in our dataset was chosen from XL-Sum [(Hasan et al., 2021)](https://huggingface.co/datasets/csebuetnlp/xlsum). 

- Each instance in our dataset is either a _good_ or a _bad_ summary of the given passage, generated by GPT-4, and each summary is rated across 5 metrics (Linguistic Acceptability, Task Quality, Output Content Quality, Hallucinations, and Problematic Content) by 3 Human Annotators, and 3 LLMs (GPT-4, GPT-3.5-Turbo, and PaLM2). The first three metrics are rated on a trinary scale of 0-2 while the latter two are binary on a scale of 0-1.

- The annotators occasionaly provide a comment/justification for their scores. The LLMs are prompted to always provide a justification for their score. Note that, since we employ single-calls (the model is prompted once for each metric independently), we have the justification by the LLMs for each metric in the instance, whereas the human annotator only give one single combined comment for all the metrics in the instance. 

- We explore two prompting strategies in the work. The LLM evaluator scores with both strategies are available in our dataset. 
    - **Simple Instruction:** A rudimentary description of the metric and scoring schema is provided.
    - **Detailed Instruction:** An informative and thorough description of the metric and a case-by-case breakdown of the scoring schema is provided.

- Each instance of our dataset is a dictionary object organised in the following fashion. The key to the dictionary object is a SHA256 checksum hash of following string: `Summ/{lang_code}/{xl_sum_id}/{index}`, where `lang_code`, `xl_sum_id` and `index` are variables as per the instance.
```json
{
    "<checksum>": {
        "XLSum_ID": <XLSum ID>,
        "Index": <Index>,
        "Type": <Type of Summary (Good or Bad)>,
        "Language": <Language>,
        "Generated_Summary": <GPT-4 generated summary>,
        "Human_Scores": {
            "linguistic_acceptability": {
                "A1": <Score by Annotator-1>,
                "A2": <Score by Annotator-2>,
                "A3": <Score by Annotator-3>
            },
            .
            .
            .
            "problematic_content": {
                "A1": <Score by Annotator-1>,
                "A2": <Score by Annotator-2>,
                "A3": <Score by Annotator-3>
            }
        },
        "Human_Comments": {
            "A1": <Optional Comment by Annotator-1>,
            "A2": <Optional Comment by Annotator-2>,
            "A3": <Optional Comment by Annotator-3>
        },
        "LLM_Scores_Simple": {
            "linguistic_acceptability": {
                "comments": {
                    "gpt-35-turbo": <Comment/Justification by GPT-3.5 for its score>,
                    "gpt-4": <Comment/Justification by GPT-4 for its score>,
                    "PaLM2": <Comment/Justification by PaLM2 for its score>
                },
                "scores": {
                    "gpt-35-turbo": <Score by GPT-3.5>,
                    "gpt-4": <Score by GPT-4>,
                    "PaLM2": <Score by PaLM2>
                }
            },
            .
            .
            .
            "problematic_content": {
                "comments": {
                    "gpt-35-turbo": <Comment/Justification by GPT-3.5 for its score>,
                    "gpt-4": <Comment/Justification by GPT-4 for its score>,
                    "PaLM2": <Comment/Justification by PaLM2 for its score>
                },
                "scores": {
                    "gpt-35-turbo": <Score by GPT-3.5>,
                    "gpt-4": <Score by GPT-4>,
                    "PaLM2": <Score by PaLM2>
                }
            }
        },
        "LLM_Scores_Detailed": {
            "linguistic_acceptability": {
                "comments": {
                    "gpt-35-turbo": <Comment/Justification by GPT-3.5 for its score>,
                    "gpt-4": <Comment/Justification by GPT-4 for its score>,
                    "PaLM2": <Comment/Justification by PaLM2 for its score>
                },
                "scores": {
                    "gpt-35-turbo": <Score by GPT-3.5>,
                    "gpt-4": <Score by GPT-4>,
                    "PaLM2": <Score by PaLM2>
                }
            },
            .
            .
            .
            "problematic_content": {
                "comments": {
                    "gpt-35-turbo": <Comment/Justification by GPT-3.5 for its score>,
                    "gpt-4": <Comment/Justification by GPT-4 for its score>,
                    "PaLM2": <Comment/Justification by PaLM2 for its score>
                },
                "scores": {
                    "gpt-35-turbo": <Score by GPT-3.5>,
                    "gpt-4": <Score by GPT-4>,
                    "PaLM2": <Score by PaLM2>
                }
            }
        },
    },
```

## Important Notice
- The passages for this dataset have been collected from the test set of XL-Sum, and may have been consumed by some LLMs.  
- <span style="color:red"> **Since the METAL dataset we release (with all the scores and comments) is also a test set, we sincerely request not to use these instances to train/fine-tune any models**.

## Citation
In you use this dataset, or code-base, please cite our works,
```bibtex
@inproceedings{hada-etal-2024-metal,
    title = "{METAL}: Towards Multilingual Meta-Evaluation",
    author = "Hada, Rishav  and
      Gumma, Varun  and
      Ahmed, Mohamed  and
      Bali, Kalika  and
      Sitaram, Sunayana",
    editor = "Duh, Kevin  and
      Gomez, Helena  and
      Bethard, Steven",
    booktitle = "Findings of the Association for Computational Linguistics: NAACL 2024",
    month = jun,
    year = "2024",
    address = "Mexico City, Mexico",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.findings-naacl.148",
    pages = "2280--2298",
    abstract = "With the rising human-like precision of Large Language Models (LLMs) in numerous tasks, their utilization in a variety of real-world applications is becoming more prevalent. Several studies have shown that LLMs excel on many standard NLP benchmarks. However, it is challenging to evaluate LLMs due to test dataset contamination and the limitations of traditional metrics. Since human evaluations are difficult to collect, there is a growing interest in the community to use LLMs themselves as reference-free evaluators for subjective metrics. However, past work has shown that LLM-based evaluators can exhibit bias and have poor alignment with human judgments. In this study, we propose a framework for an end-to-end assessment of LLMs as evaluators in multilingual scenarios. We create a carefully curated dataset, covering 10 languages containing native speaker judgments for the task of summarization. This dataset is created specifically to evaluate LLM-based evaluators, which we refer to as meta-evaluation (METAL). We compare the performance of LLM-based evaluators created using GPT-3.5-Turbo, GPT-4, and PaLM2. Our results indicate that LLM-based evaluators based on GPT-4 perform the best across languages, while GPT-3.5-Turbo performs poorly. Additionally, we perform an analysis of the reasoning provided by LLM-based evaluators and find that it often does not match the reasoning provided by human judges.",
}
```
```bibtex
@inproceedings{hada-etal-2024-large,
    title = "Are Large Language Model-based Evaluators the Solution to Scaling Up Multilingual Evaluation?",
    author = "Hada, Rishav  and
      Gumma, Varun  and
      Wynter, Adrian  and
      Diddee, Harshita  and
      Ahmed, Mohamed  and
      Choudhury, Monojit  and
      Bali, Kalika  and
      Sitaram, Sunayana",
    editor = "Graham, Yvette  and
      Purver, Matthew",
    booktitle = "Findings of the Association for Computational Linguistics: EACL 2024",
    month = mar,
    year = "2024",
    address = "St. Julian{'}s, Malta",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.findings-eacl.71",
    pages = "1051--1070",
    abstract = "Large Language Models (LLMs) excel in various Natural Language Processing (NLP) tasks, yet their evaluation, particularly in languages beyond the top 20, remains inadequate due to existing benchmarks and metrics limitations. Employing LLMs as evaluators to rank or score other models{'} outputs emerges as a viable solution, addressing the constraints tied to human annotators and established benchmarks. In this study, we explore the potential of LLM-based evaluators in enhancing multilingual evaluation by calibrating them against 20K human judgments across three text-generation tasks, five metrics, and eight languages. Our analysis reveals a bias in LLM-based evaluators towards higher scores, underscoring the necessity of calibration with native speaker judgments, especially in low-resource and non-Latin script languages, to ensure accurate evaluation of LLM performance across diverse languages.",
}
```

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.


## Privacy

You can read more about Microsoft's privacy statement [here](https://go.microsoft.com/fwlink/?LinkId=521839).
