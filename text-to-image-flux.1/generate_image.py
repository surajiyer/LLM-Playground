import time
from huggingface_hub import hf_hub_download
from mflux import Flux1, Config
from mflux.config.model_config import ModelConfig


class ImageGenerator:
    def __init__(self, repo_id, lora_file_name, model_alias="schnell", quantize=8):
        self.repo_id = repo_id
        self.lora_file_name = lora_file_name
        self.model_alias = model_alias
        self.quantize = quantize
        self.flux = None

    def download_lora_file(self):
        return hf_hub_download(repo_id=self.repo_id, filename=self.lora_file_name)

    def load_model(self, lora_file_path):
        self.flux = Flux1(
            model_config=ModelConfig.from_alias(self.model_alias),
            quantize=self.quantize,
            lora_paths=[lora_file_path],
            lora_scales=[1.0],
        )

    def generate_image(self, seed, prompt, num_inference_steps, height, width, output_path):
        if self.flux is None:
            raise ValueError("Model is not loaded. Call load_model() first.")

        config = Config(
            num_inference_steps=num_inference_steps,
            height=height,
            width=width,
        )

        t0 = time.time()
        image = self.flux.generate_image(
            seed=seed,
            prompt=prompt,
            config=config
        )
        print(f"Generation time: {time.time() - t0:.2f}s")

        image.save(path=output_path)


if __name__ == "__main__":
    repo_id = "aleksa-codes/flux-ghibsky-illustration"
    lora_file_name = "lora.safetensors"
    output_path = "data/image.png"

    generator = ImageGenerator(repo_id, lora_file_name)
    lora_file_path = generator.download_lora_file()
    generator.load_model(lora_file_path)
    generator.generate_image(
        seed=43,
        prompt="GHIBSKY style, the most beautiful place in the universe",
        num_inference_steps=3,
        height=1024,
        width=1024,
        output_path=output_path
    )
