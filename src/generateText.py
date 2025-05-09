# text_generation.py
import os
from dotenv import load_dotenv
from huggingface_hub import login
import torch
from transformers import AutoProcessor, Gemma3ForConditionalGeneration

load_dotenv()
hf_token = os.getenv("HUGGING_FACE")
if not hf_token:
    raise ValueError("Please set HUGGING_FACE in your environment")

login(token=hf_token)

_MODEL_ID = "google/gemma-3-4b-it"
_processor = AutoProcessor.from_pretrained(_MODEL_ID)
_model = Gemma3ForConditionalGeneration.from_pretrained(
    _MODEL_ID,
    device_map="auto",
    torch_dtype=torch.bfloat16
).eval()

def generate_text(
    prompt: str,
    max_new_tokens: int = 1000,
    do_sample: bool = True,
    temperature: float = 0.8
) -> str:
    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    inputs = _processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt"
    ).to(_model.device, dtype=torch.bfloat16)

    input_len = inputs["input_ids"].shape[-1]
    with torch.inference_mode():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=temperature
        )
    return _processor.decode(outputs[0][input_len:], skip_special_tokens=True).strip()

# main 
if __name__ == "__main__":
    # Example usage
    prompt = "How does surveillance capitalismn work? Answer in pirate speak."
    response = generate_text(prompt)
    print(response)
