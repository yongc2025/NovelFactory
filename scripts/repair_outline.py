import json
from pathlib import Path

def repair_outline(project_id):
    data_dir = Path(f"data/{project_id}")
    outline_path = data_dir / "outline.json"
    char_path = data_dir / "characters.json"
    
    if not outline_path.exists():
        print(f"Outline not found for {project_id}")
        return

    with open(outline_path, 'r', encoding='utf-8') as f:
        outline = json.load(f)
        
    char_names = []
    if char_path.exists():
        with open(char_path, 'r', encoding='utf-8') as f:
            chars = json.load(f)
            if isinstance(chars, dict):
                chars = chars.get("characters", [])
            char_names = [c.get("name") for c in chars if c.get("name")]

    print(f"Found characters: {char_names}")

    for ch in outline.get("chapters", []):
        # 1. 修复出场角色
        if not ch.get("characters_present"):
            present = []
            text = (ch.get("summary", "") + ch.get("core_event", "") + ch.get("action", ""))
            for name in char_names:
                if name in text:
                    present.append(name)
            ch["characters_present"] = present
            print(f"Chapter {ch.get('chapter_num')}: Found characters {present}")

        # 2. 修复情绪定位
        if not ch.get("emotion_position"):
            conflict = ch.get("conflict_level", 1)
            if conflict >= 3:
                ch["emotion_position"] = "激烈/高燃"
            elif conflict == 2:
                ch["emotion_position"] = "悬疑/紧迫"
            else:
                ch["emotion_position"] = "压抑/期待"

        # 3. 字段归一化 (core_event)
        if not ch.get("core_event") and ch.get("summary"):
            ch["core_event"] = ch.get("summary")

    with open(outline_path, 'w', encoding='utf-8') as f:
        json.dump(outline, f, ensure_ascii=False, indent=2)
    print(f"Successfully repaired outline for {project_id}")

if __name__ == "__main__":
    repair_outline("20260601_172217_9a0afb")
