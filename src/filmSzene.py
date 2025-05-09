import os

from generateText import generate_text

def load_scripts(script_dir: str = "./data/scripts") -> dict:
    scripts = {}
    for filename in sorted(os.listdir(script_dir)):
        if filename.endswith(".txt"):
            name = os.path.splitext(filename)[0]
            path = os.path.join(script_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                scripts[name] = f.read().strip()
    return scripts

def save_script(content: str, script_name: str, style: str, output_dir: str = "./data/output-2"):
    safe_style = style.lower().replace(" ", "_").replace(",", "")
    safe_name = script_name.lower().replace(" ", "_")
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{safe_name}_{safe_style}.txt"
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved {path}")

if __name__ == "__main__":
    styles = [
        "1970s arthouse cinema",
        "Italian neorealism",
        "1940s Screw ball comedy",
        "Danish Dogme 95",
        "Film noir",
        "Shakespearean",
        "Anime"
    ]

    scene_brief_map = {
        "1970s arthouse cinema": "In a sun-dappled living room.",
        "Italian neorealism": (
            "In a humble Roman courtyard at dusk, two women, both washerwomen worn thin by hardship, "
            "sit among faded stone walls and scattered laundry."
        ),
        "1940s Screw ball comedy": ("In a sun-dappled living room. There is a table with a vase of flowers and two glasses of martini."),
        "Danish Dogme 95": (
            "In a stark, minimalist apartment, two friends engage in a heated discussion about life choices."
        ),
        "Film noir": (
            "On a rain-slicked back alley at midnight, two women trade terse threats. The air is thick with tension, "
            "and the distant sound of sirens echoes."
        ),
        "Shakespearean": (
            "In a grand castle hall, two noblewomen engage in a witty exchange, their words laced with double meanings and hidden agendas."
        ),
        "Anime": (
            "In a vibrant, bustling city street, two friends, one with bright pink hair and the other with blue, engage in a lively conversation."
        ),
    }

    scripts = load_scripts()

    for script_name, full_desc in scripts.items():
        for style in styles:
            brief_desc = scene_brief_map[style]
            prompt = (
                f"Generate a dialogue scene in the style of {style} based on the following scene description:\n"
                f"{brief_desc}\n{full_desc}\n\n"
                f"Stick to the scene description and the style, don't add additional personalities or plot.\n"
                "Dialogue:"
            )
            output = generate_text(prompt)
            save_script(output, script_name=script_name, style=style)
