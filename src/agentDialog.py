import os
import re
import random
from dotenv import load_dotenv
from huggingface_hub import login
import torch
from transformers import AutoProcessor, Gemma3ForConditionalGeneration

DEFAULT_TEMP = 1.2
MODEL_ID = "google/gemma-3-4b-it"

load_dotenv()
hf_token = os.environ.get("HUGGING_FACE")
if not hf_token:
    raise ValueError("HUGGING_FACE environment variable is not set.")
login(token=hf_token)

processor = AutoProcessor.from_pretrained(MODEL_ID)
model = Gemma3ForConditionalGeneration.from_pretrained(
    MODEL_ID,
    device_map="auto"
).eval()

current_topic_info = {
    "initiator": None,
    "rounds": 0
}
end_signalers = set()
next_speaker_override = None

def generate_text(
    prompt: str,
    max_new_tokens: int = 100,
    do_sample: bool = True,
    temperature: float = DEFAULT_TEMP
) -> str:
    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt"
    ).to(model.device, dtype=torch.bfloat16)
    input_len = inputs["input_ids"].shape[-1]
    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=temperature
        )
    return processor.decode(outputs[0][input_len:], skip_special_tokens=True).strip()

def clean_generated_text(generated_text, prompt=""):
    if prompt and generated_text.startswith(prompt):
        generated_text = generated_text[len(prompt):]
    generated_text = re.sub(r'^[A-Za-z]+\s*:\s*', '', generated_text)
    generated_text = generated_text.replace('**', '')
    generated_text = re.sub(r'\*+', '', generated_text)
    generated_text = generated_text.strip()
    quote_match = re.search(r'```([^`]+)```', generated_text)
    if quote_match:
        return quote_match.group(1).strip()
    for pat in [r'"([^"]+)"', r'“([^”]+)”']:
        m = re.search(pat, generated_text)
        if m:
            return m.group(1).strip()
    return generated_text

def build_dialog_prompt(dialog_turns):
    return "\n".join(f"{turn['speaker']}: {turn['text']}" for turn in dialog_turns)

def decide_action(dialog_turns, agent):
    global current_topic_info, end_signalers, next_speaker_override
    if dialog_turns:
        last = dialog_turns[-1]
        txt = last['text'].lower()
        if any(w in txt for w in ["schluss", "ende", "abschließen", "beenden"]):
            end_signalers.add(last['speaker'])
    if next_speaker_override and agent.name == next_speaker_override:
        next_speaker_override = None
        return "reflect_end" if end_signalers and agent.name not in end_signalers else agent.special_fallback
    if next_speaker_override:
        return None
    for action, prob in agent.special_actions.items():
        if random.random() < prob:
            return action
    if end_signalers and agent.name not in end_signalers:
        return "reflect_end"
    if dialog_turns and dialog_turns[-1]['text'].strip().endswith('?'):
        return "confirm"
    if current_topic_info['initiator'] is None:
        return "change"
    if current_topic_info['rounds'] == 0:
        return "support" if agent.name != current_topic_info['initiator'] else random.choices(["support","confirm"],[0.7,0.3])[0]
    if current_topic_info['rounds'] >= 2:
        return random.choices(["change","support"],[0.6,0.4])[0]
    return random.choices(["change","support"],[0.4,0.6])[0]

class Agent:
    def __init__(
        self, name, topics, role_desc,
        special_actions=None,
        special_fallback="support"
    ):
        self.name = name
        self.topics = topics
        self.role_desc = role_desc
        self.current_topic_index = 0
        self.special_actions = special_actions or {}
        self.special_fallback = special_fallback

    def get_current_topic(self):
        return self.topics[self.current_topic_index] if self.current_topic_index < len(self.topics) else None

    def mark_topic_done(self):
        self.current_topic_index += 1

    def generate_response(self, prompt, max_new_tokens=100):
        raw = generate_text(prompt, max_new_tokens=max_new_tokens)
        return clean_generated_text(raw, prompt)

    def speak_greeting(self, scene):
        prompt = f"Scene: {scene}\n# role: {self.name}\n{self.role_desc}\n# task: Greet briefly.\nGreeting:"
        return self.generate_response(prompt, max_new_tokens=50)
    def speak_confirm(self, dialog_turns):
        prompt = f"# dialog:\n{build_dialog_prompt(dialog_turns)}\n# role: {self.name}\n{self.role_desc}\n# task: Answer clearly.\nResponse:"
        return self.generate_response(prompt)
    def speak_support(self, dialog_turns):
        prompt = f"# dialog:\n{build_dialog_prompt(dialog_turns)}\n# role: {self.name}\n{self.role_desc}\n# task: Provide a short supportive comment.\nResponse:"
        return self.generate_response(prompt)
    def speak_change(self, dialog_turns):
        global current_topic_info
        current_topic_info['initiator'] = self.name
        current_topic_info['rounds'] = 0
        self.mark_topic_done()
        new_topic = self.get_current_topic()
        prompt = f"# dialog:\n{build_dialog_prompt(dialog_turns)}\n# role: {self.name}\n{self.role_desc}\n"
        prompt += (f"# task: Introduce new topic: {new_topic}.\nResponse:" if new_topic else "# task: Provide a polite closing.\nResponse:")
        return self.generate_response(prompt, max_new_tokens=150)
    def speak_reflect_end(self, dialog_turns):
        prompt = f"# dialog:\n{build_dialog_prompt(dialog_turns)}\n# role: {self.name}\n{self.role_desc}\n# task: Reflect briefly if it's time to end; you may stay silent or offer a short thought.\nResponse:"
        return self.generate_response(prompt, max_new_tokens=50)
    def speak_summary(self, dialog_turns):
        prompt = (
            f"# dialog:\n{build_dialog_prompt(dialog_turns)}\n# role: {self.name}\n{self.role_desc}\n"
            "# task: Provide a concise summary and ask everyone to commit: 'So you are saying, that ...?'\nResponse:"
        )
        return self.generate_response(prompt, max_new_tokens=100)
    def speak_probe(self, dialog_turns):
        global next_speaker_override
        others = [a for a in all_agents if a.name != self.name]
        target = random.choice(others).name if others else None
        next_speaker_override = target
        prompt = (
            f"# dialog:\n{build_dialog_prompt(dialog_turns)}\n# role: {self.name}\n{self.role_desc}\n"
            f"# task: Ask a direct probing question to {target}. Response:"
        )
        return self.generate_response(prompt, max_new_tokens=100)

def run_dialog_simulation(agents, max_rounds=10):
    global all_agents, next_speaker_override
    all_agents = agents
    dialog_turns = []
    scene = generate_text(f"Generate a concise scene description for: {', '.join(a.name for a in agents)}", max_new_tokens=80)
    dialog_turns.append({"speaker":"Narrator","text":scene})
    print(f"Scene: {scene}\n")
    for a in agents:
        g = a.speak_greeting(scene)
        dialog_turns.append({"speaker":a.name,"text":g})
        print(f"{a.name}: {g}")
    for rnd in range(1, max_rounds+1):
        if not any(a.get_current_topic() for a in agents): break
        print(f"\n--- Round {rnd} ---")
        if next_speaker_override:
            speaker = next(a for a in agents if a.name==next_speaker_override)
            action = decide_action(dialog_turns, speaker)
            next_speaker_override = None
            line = getattr(speaker, f"speak_{action}")(dialog_turns) if action else ''
            dialog_turns.append({"speaker":speaker.name,"text":line})
            print(f"{speaker.name} ({action}): {line}")
            continue
        for a in agents:
            action = decide_action(dialog_turns, a)
            if not action: continue
            method = getattr(a, f"speak_{action}")
            line = method(dialog_turns)
            dialog_turns.append({"speaker":a.name,"text":line})
            print(f"{a.name} ({action}): {line}")
            if action in ("support","confirm") and current_topic_info['initiator']:
                current_topic_info['rounds'] += 1
    full = "\n".join(f"{t['speaker']}: {t['text']}" for t in dialog_turns)
    xml = "".join(f"<sp who=\"#{t['speaker']}\"><speaker>{t['speaker']}.</speaker><p>{t['text']}</p></sp>\n" for t in dialog_turns)
    print("\nFinal Dialogue:\n", full)
    return full, xml

if __name__ == "__main__":
    def save_dialog_history(prompt, xml, prefix="dialog"):
        with open(f"{prefix}_prompt.txt", "w") as f:
            f.write(prompt)
        with open(f"{prefix}_history.xml", "w") as f:
            f.write(xml)

    agent1 = Agent(
        name="Alice",
        topics=["technology", "artificial intelligence", "robotics"],
        role_desc="Alice ist technische Expertin mit einer Leidenschaft für Innovation.",
        special_actions={"summary": 0.1, "probe": 0.05}
    )
    agent2 = Agent(
        name="Bob",
        topics=["cooking", "travel", "photography"],
        role_desc="Bob ist neugieriger Entdecker mit Abenteuergeist.",
        special_actions={"summary": 0.05, "probe": 0.1}
    )
    agent3 = Agent(
        name="Eve",
        topics=["music", "literature", "cinema"],
        role_desc="Eve ist kreative Persönlichkeit mit Interesse an Kunst.",
        special_actions={"summary": 0.07, "probe": 0.08}
    )

    agents = [agent1, agent2, agent3]
    final_prompt, final_xml = run_dialog_simulation(agents, max_rounds=10)
    save_dialog_history(final_prompt, final_xml)
    print("\n--- Dialog history saved to files. ---")
