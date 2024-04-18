import asyncio
import json
import sys

import schema as drawing
from dotenv import dotenv_values

from typechat import Success, Failure, TypeChatJsonTranslator, TypeChatValidator, PromptSection, create_language_model, process_requests


async def main(file_path: str | None):
    env_vals = dotenv_values()
    model = create_language_model(env_vals)
    validator = TypeChatValidator(drawing.Drawing)
    translator = TypeChatJsonTranslator(model, validator, drawing.Drawing)
    # print(translator._schema_str)

    history: list[tuple[str, str]] = []

    async def request_handler(request: str):
        result: Success[drawing.Drawing] | Failure = await translator.translate(request, chat_history=history)
        if isinstance(result, Failure):
            print(result.message)
        else:
            value = result.value
            output = json.dumps(value, indent=2)
            print(output)
            if any(item["type"] == "Unknown" for item in value["items"]):
                print("I did not understand the following")
                for item in value["items"]:
                    if item["type"] == "Unknown":
                        print(item["text"])
            else:
                history.append((request, output))

    await process_requests("~> ", file_path, request_handler)


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) == 2 else None
    asyncio.run(main(file_path))
