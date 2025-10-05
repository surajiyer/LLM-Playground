# import os

from dotenv import load_dotenv
from gradio_client import Client
from PIL import Image


if load_dotenv():
    print("Loaded environment variables from .env file")

# HF_TOKEN = os.environ.get("HF_TOKEN")
# client = Client.duplicate("prithivMLmods/FLUX-LoRA-DLC", hf_token=HF_TOKEN)
client = Client("prithivMLmods/FLUX-LoRA-DLC")
# client.view_api()

result = client.predict(
    custom_lora="alvdansen/flux-koda",
    api_name="/add_custom_lora"
)
print("Loaded custom LoRa:", result[0]["visible"])

result = client.predict(
    prompt="A young woman with tousled hair and minimal makeup, wearing a oversized flannel shirt, looking directly at the camera with a slight smile. The background is slightly out of focus, suggesting a cozy bedroom, kodachrome, flmft style",
    image_input=None,
    image_strength=0.75,
    cfg_scale=3.5,
    steps=28,
    randomize_seed=True,
    seed=3067318270,
    width=1024,
    height=1024,
    lora_scale=1024,
    api_name="/run_lora"
)
image_path = result[0]["image"]
image = Image.open(image_path)
image.show()

result = client.predict(api_name="/remove_custom_lora")
print("Loaded custom LoRa:", result[0]["visible"])
