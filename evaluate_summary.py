import os
import json
import warnings
from tqdm import tqdm
from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain_community.chat_models import AzureChatOpenAI, ChatVertexAI

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from utils.constants import (
    code_to_name,
    metric_aliases,
    HUMAN_MESSAGE,
    SYSTEM_MESSAGE,
)

from utils.utils import Output, DeamonWriter, read_data, get_arg_parser, get_metrics

load_dotenv()
warnings.filterwarnings("ignore")

## IMPORTANT: Reproducibility is not exactly guaranteed due to the nature of the API


# Optional: Add a backoff decorator to retry the function if it fails
def _gen_reponse(llm, prompt):
    response = llm(prompt.to_messages())
    return response.content.strip("```json").strip("```")


def main(args):
    if args.model.startswith("gpt"):
        llm = AzureChatOpenAI(
            openai_api_version=os.environ["OPENAI_API_VERSION"],
            openai_api_key=os.environ["OPENAI_API_KEY"],
            openai_api_base=os.environ["OPENAI_API_BASE"],
            temperature=args.temperature,
            max_tokens=args.max_output_tokens,
            deployment_name=args.model,
        )
    else:
        llm = ChatVertexAI(
            model_name=args.model,
            temperature=args.temperature,
            max_output_tokens=args.max_output_tokens,
        )

    parser = PydanticOutputParser(pydantic_object=Output)
    OUTPUT_FORMAT_INSTRUCTIONS = parser.get_format_instructions()

    chat_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE),
            HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE),
        ]
    )

    print(f" | > Reading {args.infname} and writing to {args.outfname}")
    df = read_data(args.infname, args.outfname)

    mode = "w" if not os.path.exists(args.outfname) else "a"
    writer = DeamonWriter(args.outfname, mode=mode)

    for index, row in tqdm(df.iterrows(), total=len(df)):
        row = row.to_dict()
        skip_current_evaluation = False
        curr_output = {"id": index, "lang": args.language, "XLSumm_ID": row["Id"]}

        for metric_name_ in tqdm(metric_aliases.values()):
            if skip_current_evaluation:
                break

            chat_prompt_with_values = chat_prompt.format_prompt(
                passage=row["Sentence"].strip(),
                summary=row["Summary"].strip(),
                language=code_to_name[args.language],
                format_instructions=OUTPUT_FORMAT_INSTRUCTIONS,
                metric_description=get_metrics([metric_name_], args.prompt_style),
            )

            try:
                response = _gen_reponse(llm, chat_prompt_with_values)
                # some hacks might be required to handle the response
                # and convert it to a valid JSON, especially for VertexAI
                curr_output[metric_name_] = json.loads(response)
            except Exception as e:
                print(f"\n | Skipping {index} due to {e}")
                skip_current_evaluation = True

        if not skip_current_evaluation:
            writer.put(curr_output)

    writer.graceful_terminate()


if __name__ == "__main__":
    parser = get_arg_parser()
    args = parser.parse_args()
    main(args)
