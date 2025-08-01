import os
from dotenv import load_dotenv
from huggingface_hub import login
import torch
from transformers import AutoProcessor, Gemma3ForConditionalGeneration

load_dotenv()
hf_token = os.getenv("HUGGING_FACE")
if not hf_token:
    raise ValueError("Please set HUGGING_FACE in your environment")

_MODEL_ID = "google/gemma-3-4b-it"
_processor = AutoProcessor.from_pretrained(_MODEL_ID)
_model = Gemma3ForConditionalGeneration.from_pretrained(
    _MODEL_ID,
    device_map="auto",
    torch_dtype=torch.bfloat16
).eval()

def generate_text_with_messages(
    messages: list[dict],
    max_new_tokens: int = 1000,
    do_sample: bool = True,
    temperature: float = 0.8
) -> str:
    formatted = []
    for msg in messages:
        content = msg["content"]
        blocks = (
            content
            if isinstance(content, list)
            else [{"type": "text", "text": content}]
        )
        formatted.append({"role": msg["role"], "content": blocks})

    inputs = _processor.apply_chat_template(
        formatted,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        padding="longest",
        pad_to_multiple_of=8,
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
