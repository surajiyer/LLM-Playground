import logging
import os

import dotenv
from openai import OpenAI
from langchain_community.llms import AzureOpenAI

dotenv.load_dotenv()


logger = logging.getLogger(__name__)


def get_llm(model_name: str, *a, **kws):
    if model_name == "gpt-4":
        llm = get_gpt_4(*a, **kws)
    elif model_name == "gpt-3":
        llm = get_gpt_35_turbo(*a, **kws)
    else:
        raise ValueError(f"Invalid model: {model_name}")

    return llm


def get_gpt_4(*a, **kws):
    logger.info("Loading LLM 'gpt-4'")
    return AzureOpenAI(
        model_name="gpt-4",
        # engine="gpt-4-us",
        temperature=kws.get("temperature", 0.7),
        max_tokens=kws.get("max_tokens", 256),
        top_p=kws.get("top_p", 1),
        verbose=False,
    )


def get_gpt_35_turbo(*a, **kws):
    # Different approach than gpt-4, as for gpt-3 we get an error:
    # "The completion operation does not work with the specified model, gpt-35-turbo."
    logger.info("Loading LLM 'gpt-3.5-turbo'")
    client = OpenAI()

    # this allows running the returned llm with llm("your prompt")
    return (
        lambda prompt: client.chat.completions.create(
            model="gpt-3.5-turbo",
            # engine="gpt-35-turbo-us",
            messages=kws.get("messages", [{"role": "user", "content": prompt}]),
            temperature=kws.get("temperature", 0.7),
            max_tokens=kws.get("max_tokens", 256),
            top_p=kws.get("top_p", 1),
        )
        .choices[0]
        .message.content
    )
