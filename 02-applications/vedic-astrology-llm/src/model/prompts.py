import json
from typing import Literal

from pydantic import BaseModel


Difficulty = Literal["easy", "medium", "hard"]


class AstroQuestionResponse(BaseModel):
    thought: str
    answer: str
    difficulty: Difficulty

    @classmethod
    def get_prompt(cls) -> str:
        response_schema_dict = cls.model_json_schema()
        response_schema_json = json.dumps(response_schema_dict, indent=2)
        prompt = f"""
        I will ask you questions, and you will respond.
        Your response should be in the following format:
        ```json
        {response_schema_json}
        ```
        """
        return prompt
