from functools import lru_cache

import torch
from PIL import Image

MODEL_NAME = "openai/clip-vit-base-patch32"

ARTIST_PROMPTS = {
    "dali": "a surrealist painting by Salvador Dali with melting clocks and dreamlike landscapes",
    "magritte": "a surrealist painting by Rene Magritte with bowler hats and mysterious objects",
    "ernst": "a surrealist painting by Max Ernst with bizarre creatures and dark forests",
    "miro": "a colorful surrealist painting by Joan Miro with biomorphic shapes and symbols",
    "other": "a realistic photograph, a landscape photo, a portrait photo, or a classical realistic painting",
}


@lru_cache(maxsize=1)
def _load_model():
    """Load CLIP once, on the first classification request."""
    from transformers import CLIPModel, CLIPProcessor

    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    model = CLIPModel.from_pretrained(MODEL_NAME).to(device)
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    model.eval()
    return model, processor, device


def classify_image(image_input):
    """Return probability percentages for four artist styles and the other class."""
    if isinstance(image_input, str):
        image = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, Image.Image):
        image = image_input.convert("RGB")
    else:
        raise TypeError(f"Expected str or PIL.Image, got {type(image_input)}")

    model, processor, device = _load_model()
    labels = list(ARTIST_PROMPTS)
    texts = [ARTIST_PROMPTS[label] for label in labels]
    inputs = processor(text=texts, images=image, return_tensors="pt", padding=True)
    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.inference_mode():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits_per_image.squeeze(), dim=0)

    return {
        label: round(float(probability.item()) * 100, 1)
        for label, probability in zip(labels, probabilities)
    }
