import importlib.util
import json
import logging
import os
import sys
from pathlib import Path

if importlib.util.find_spec("chromadb") is not None:
    import chromadb
else:
    chromadb = None
from pydantic import BaseModel, ValidationError
from youtube_transcript_api import YouTubeTranscriptApi

sys.path.insert(0, Path(__file__).parent.parent.as_posix())

from general_utils.llm import get_llm  # noqa: E402


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
if chromadb and os.environ.get("CHROMA_DB_PATH"):
    chroma_client = chromadb.PersistentClient(
        path=str(os.environ.get("CHROMA_DB_PATH")),
    )
    collection = chroma_client.get_or_create_collection(name="youtube_summarizer")
else:
    collection = None
PROMPT_TEMPLATE = (
    json.dumps(
        {
            "format": "json",
            "system": "Youtube Video Summarizer",
            "goal": "Summarize the transcript of a youtube video.",
            "instructions": [
                "Transcript (transcript) of the video is provided as input in parts.",
                "last_part is a boolean field that indicates if the last part is received.",
                "Only create a summary when last_part is True.",
                "Output must contain message and summary fields.",
                "When last part is received, create a summary in bullet points.",
                "Each point starts with an relevant emoji.",
                "Each point is in order as mentioned in the transcript.",
                "Each point contains a one line reference to the section of the transcript"
                " that the point is from. e.g., `* summary point. Reference: reference text"
                " from transcript`.",
                "Must be minimum 10 points. Add more points if needed and are not similar to" " previous points.",
                "Each point must be be salient and non-repetitive.",
                "Output must be json format.",
                "Output follows this input template.",
                "Output must remove and not include the transcript field.",
                "Output must contain the summary text in the summary field.",
            ],
            "last_part": "{}",
            "transcript": "{}",
            "message": "'waiting' if last_part is False, otherwise 'done'.",
            "summary": "Empty list [] if last_part is False else a list[str] summary of the video transcript.",
        }
    )
    .replace("{", "{{")
    .replace("}", "}}")
    .replace("{{}}", "{}")
)
MAX_RETRIES = 3


class GenericResponse(BaseModel):
    message: str

    @classmethod
    def validate_response(cls, raw_response: str, expected_msg: str) -> bool:
        try:
            response = cls.model_validate_json(raw_response)
            if response.message != expected_msg:
                raise ValidationError.from_exception_data(
                    f"Expected message: {expected_msg}, got: {response.message}",
                    [],
                )
            return True
        except ValidationError as e:
            logger.error(f"❌ Unable to validate LLM response: {e}")
        return False


class SummaryResponse(BaseModel):
    summary: list[str]

    @classmethod
    def validate_response(cls, raw_response: str) -> bool:
        try:
            cls.model_validate_json(raw_response)
            return True
        except ValidationError as e:
            logger.error(f"❌ Unable to validate LLM response: {e}")
        return False


def download_transcript(yt_vid_link: str) -> str:
    # handle shortened youtube links
    if "youtu.be" in yt_vid_link:
        yt_vid_link = yt_vid_link.split("?")[0]
        yt_vid_link = yt_vid_link.replace("youtu.be/", "youtube.com/watch?v=")

    # download the transcript of the video
    video_id = yt_vid_link.split("v=")[1]
    try:
        if collection:
            transcript_json = collection.get(ids=[video_id], where={"type": "transcript"})
            if video_id in transcript_json["ids"]:
                logger.info("✅ Got the transcript of the video from the database")
                return transcript_json["documents"][0]
        transcript_json = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=[
                "en",
                "en-US",
                "en-GB",
                "en-AU",
                "en-CA",
                "en-IN",
                "en-NZ",
                "en-ZA",
                "en-IE",
                "en-JM",
                "en-BZ",
                "en-TT",
            ],
        )
    except Exception as e:
        logger.error(f"❌ Downloading the transcript: {e}")
        raise e
    transcript = " ".join([item["text"] for item in transcript_json])
    if collection:
        try:
            collection.add(
                documents=[transcript], metadatas=[{"source": yt_vid_link, "type": "transcript"}], ids=[video_id]
            )
        except Exception as e:
            logger.error(f"❌ Adding transcript to database: {e}")
            raise e
    logger.info("✅ Got the transcript of the video")
    return transcript


def _split_string_into_substrings(s, num_words):
    words = s.split()
    return [" ".join(words[i : i + num_words]) for i in range(0, len(words), num_words)]


def summarize_transcript(yt_vid_link: str, transcript: str) -> str:
    # split the transcript into parts
    transcript_parts = _split_string_into_substrings(transcript, 2048)
    number_of_parts = len(transcript_parts)
    logger.info(f"Transcript split into {number_of_parts} parts")

    # summarize the transcript
    for i in range(MAX_RETRIES):
        # openai completion
        llm = get_llm("gpt-3", max_tokens=1024)
        retry = False

        try:
            for i, t in enumerate(transcript_parts):
                formatted_prompt = PROMPT_TEMPLATE.format(i + 1 == number_of_parts, t)
                response = llm(formatted_prompt)
                if i + 1 < number_of_parts and not GenericResponse.validate_response(response, "waiting"):
                    retry = True
                    break
            if retry or not SummaryResponse.validate_response(response):
                logger.warn("Retrying...")
                continue
            summary = SummaryResponse.parse_raw(response).summary
            break
        except Exception as e:
            logger.error(f"❌ Summarizing the transcript: {e}")
            raise e

    logger.info("✅ Generated the summary of the video")
    return summary


def save_summary_to_database(yt_vid_link: str, summary: str):
    video_id = yt_vid_link.split("v=")[1]
    try:
        collection.upsert(
            ids=[video_id + "_summary"],
            metadatas=[
                {
                    "source": yt_vid_link,
                    "type": "summary",
                    "prompt_template": PROMPT_TEMPLATE,
                }
            ],
            documents=[json.dumps({"summary": summary})],
        )
    except Exception as e:
        logger.error(f"❌ Adding summary to database: {e}")
        raise e


def get_summary_from_database(yt_vid_link: str) -> str:
    video_id = yt_vid_link.split("v=")[1]
    try:
        summary_json = collection.get(
            ids=[video_id + "_summary"],
            where={"type": "summary"},
        )
        if video_id + "_summary" in summary_json["ids"]:
            logger.info("✅ Got the summary of the video from the database")
            return summary_json["documents"][0]
    except Exception as e:
        logger.error(f"❌ Downloading the summary: {e}")
        raise e
