import time
from huggingface_hub import hf_hub_download
from mflux import ConfigControlnet, Flux1, Config, Flux1Controlnet
from mflux.config.model_config import ModelConfig


class ImageGenerator:
    def __init__(self, repo_id, lora_file_name, model_alias="schnell", quantize=8):
        self.repo_id = repo_id
        self.lora_file_name = lora_file_name
        self.model_alias = model_alias
        self.quantize = quantize
        self.flux = None
        self.controlnet = None

    def download_lora_file(self):
        return hf_hub_download(repo_id=self.repo_id, filename=self.lora_file_name)

    def load_model(self, lora_file_path):
        self.flux = Flux1(
            model_config=ModelConfig.from_alias(self.model_alias),
            quantize=self.quantize,
            lora_paths=[lora_file_path],
            lora_scales=[0.95],
        )
        self.controlnet = Flux1Controlnet(
            model_config=ModelConfig.from_alias(self.model_alias),
            quantize=self.quantize,
            lora_paths=[lora_file_path],
            lora_scales=[0.95],
        )

    def generate_image(self, num_inference_steps, width, height, seed, prompt, output_path, controlnet_image_path=None):
        if self.flux is None:
            raise ValueError("Model is not loaded. Call load_model() first.")

        if controlnet_image_path is not None:
            config = ConfigControlnet(
                num_inference_steps=num_inference_steps,
                width=width,
                height=height,
                guidance=3.5,
                controlnet_strength=0.75,
            )

            t0 = time.time()
            image = self.controlnet.generate_image(
                seed=seed,
                prompt=prompt,
                output=output_path,
                controlnet_image_path=controlnet_image_path,
                config=config,
            )
        else:
            config = Config(
                num_inference_steps=num_inference_steps,
                width=width,
                height=height,
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
    repo_id = "prithivMLmods/Castor-Character-Polygon-Flux-LoRA"
    lora_file_name = "Castor-Character-Polygon-LoRA.safetensors"
    output_path = "data/image.png"

    generator = ImageGenerator(repo_id, lora_file_name, model_alias="dev")
    lora_file_path = generator.download_lora_file()
    generator.load_model(lora_file_path)
    generator.generate_image(
        num_inference_steps=28,
        width=1024,
        height=1024,
        seed=3973736786,
        prompt="Create a 3D polygon character portrait of a young athletic Indian man in his early 20s. He has short, curly black hair, dark brown eyes, and a bearded face. His muscular build is visible through a sleeveless workout shirt, and his skin is glowing with sweat, hinting at recent physical activity. His expression is focused and intense. The lighting is dynamic, highlighting the contours of his muscles and the texture of his skin. The background is a garden setting, slightly out of focus",
        controlnet_image_path="image.webp",
        output_path=output_path
    )
