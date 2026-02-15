import json
from datetime import datetime
from pathlib import Path

lugs_path = Path("WAI-Spoke/reference/auto/lugs.jsonl")
ids_to_close = {
    "a1b2c3d4e5f6a7b8", # Intro Banner
    "b2c3d4e5f6a7b8c9", # SCF Remove
    "c3d4e5f6a7b8c9d0", # WAI Point Only
    "d4e5f6a7b8c9d0e1", # Hide Raw JSON
    "e5f6a7b8c9d0e1f2", # Render Markdown
    "f6a7b8c9d0e1f2a3"  # Fix Menu Indentation
}

lines = []
if lugs_path.exists():
    with open(lugs_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            try:
                lug = json.loads(line)
                if lug.get('i') in ids_to_close:
                    lug['s'] = 'closed'
                    lug['ua'] = datetime.utcnow().isoformat()
                    lug['cla'] = datetime.utcnow().isoformat()
                    lug['su'] = "Completed during Visual & Branding Polish session."
                    print(f"Closing Lug: {lug['t']}")
                lines.append(lug)
            except Exception as e:
                print(f"Error parsing line: {e}")

    with open(lugs_path, 'w', encoding='utf-8') as f:
        for lug in lines:
            f.write(json.dumps(lug) + "\n")
    print("Lugs updated.")
else:
    print("lugs.jsonl not found.")
