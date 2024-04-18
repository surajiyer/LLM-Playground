from functions import download_transcript
from functions import summarize_transcript
from modal import Image
from modal import Secret
from modal import Stub
from modal import web_endpoint

image = Image.debian_slim().pip_install(
    "langchain_community==0.0.32",
    "openai==1.17.0",
    "pydantic==2.6.4",
    "python-dotenv==0.21.1",
    "youtube-transcript-api==0.6.2",
)
stub = Stub()


@stub.function(
    image=image,
    secrets=[Secret.from_name("my-openai-secret")],
)
@web_endpoint()
def summarise(link: str):
    transcript = download_transcript(link)
    summary = summarize_transcript(link, transcript)
    return summary
