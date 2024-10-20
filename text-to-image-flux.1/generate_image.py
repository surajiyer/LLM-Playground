# https://github.com/filipstrand/mflux
import time

from mflux import Flux1, Config

# Load the model
flux = Flux1.from_alias(
    alias="schnell",  # "schnell" or "dev"
    quantize=8,       # 4 or 8
)

# Generate an image
t0 = time.time()
image = flux.generate_image(
    seed=2,
    prompt="Luxury food photograph",
    config=Config(
        num_inference_steps=2,  # "schnell" works well with 2-4 steps, "dev" works well with 20-25 steps
        height=1024,
        width=1024,
    )
)
print(f"Generation time: {time.time() - t0:.2f}s")

image.save(path="data/image.png")
