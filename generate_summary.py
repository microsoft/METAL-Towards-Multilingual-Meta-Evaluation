import os
import json
import guidance
import warnings
from tqdm import tqdm
from dotenv import load_dotenv
from utils.utils import DeamonWriter, get_arg_parser, read_data

load_dotenv()
warnings.filterwarnings("ignore")

## IMPORTANT: The following uses Guidance (v0.0.64).
# If possible, please try to modify the code to work with the latest version of Guidance.
# Reproducibility is not exactly guaranteed due to the nature of the API


# Optional: Add a backoff decorator to retry the function if it fails
def _gen_reponse(program, sent, language):
    executed_program = program(passage=sent, language=language)
    return executed_program["evaluation"].strip("```json").strip("```")


def main(args):
    with open(args.prompt_file, "r", encoding="utf-8") as f:
        GUIDANCE_INSTRUCTION = f.read().strip()

    llm = guidance.llms.OpenAI(
        model=args.model,
        max_retries=25,
        deployment_id=args.model,
        api_key=os.environ["OPENAI_API_KEY"],
        api_type=os.environ["OPENAI_API_TYPE"],
        api_base=os.environ["OPENAI_API_BASE"],
        api_version=os.environ["OPENAI_API_VERSION"],
    )

    df = read_data(args.infname, args.outfname)
    mode = "w" if not os.path.exists(args.outfname) else "a"
    writer = DeamonWriter(args.outfname, mode=mode)

    program = guidance(GUIDANCE_INSTRUCTION, llm=llm)

    for _, row in tqdm(df.iterrows(), total=len(df)):
        row = row.to_dict()
        sent = row["text"].strip()

        try:
            response = _gen_reponse(program, sent, args.language)
            output = json.loads(response)
            # some hacks might be required to handle the response
            # and convert it to a valid JSON
            prediction = {
                "id": row["id"],
                "sentence": sent.strip(),
                "summary": output["summary"].strip(),
                "original_summary": row["summary"].strip(),
                "justification": output["justification"].strip(),
            }
        except Exception as e:
            print(f" | > Skipping {row['id']} due to {e}")
            continue

        writer.put(prediction)

    writer.graceful_terminate()


if __name__ == "__main__":
    args = get_arg_parser().parse_args()
    main(args)
