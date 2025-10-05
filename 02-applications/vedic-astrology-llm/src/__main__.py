import logging
from pathlib import Path
import sys

sys.path.insert(0, Path(__file__).parent.parent.parent.as_posix())

from common.llm import get_llm, ValidationError
from src.model.prompts import AstroQuestionResponse

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    llm = get_llm("gpt-3")
    input_ = input("Question?")

    raw_response = llm(AstroQuestionResponse.get_prompt() + f"\nQuestion: {input_}")

    # Note: When you are using pydantic<2.0, use parse_raw instead of model_validate_json
    try:
        validated_response = AstroQuestionResponse.model_validate_json(raw_response)
    except ValidationError as e:
        logger.error("Unable to validate LLM response.")
        # Add your own error handling here
        raise e

    logger.info(validated_response)
    logger.info(type(validated_response))
