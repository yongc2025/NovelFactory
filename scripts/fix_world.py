import json
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到 sys.path
root = Path(__file__).resolve().parent.parent
sys.path.append(str(root / "src"))

from dotenv import load_dotenv
load_dotenv(root / ".env")

from novel_factory.engine.worldbuilder import build_world

async def main():
    project_id = "20260601_172217_9a0afb"
    
    # 1. 加载 Topic
    topic_path = root / "data" / project_id / "topic.json"
    with open(topic_path, "r", encoding="utf-8") as f:
        topics = json.load(f)
        proposal = topics[0]
        
    # 2. 加载 Project Params
    project_path = root / "data" / project_id / "project.json"
    with open(project_path, "r", encoding="utf-8") as f:
        project = json.load(f)
        params = project
        
    # 3. 重新生成
    print(f"Regenerating world for: {proposal.get('title')}...")
    try:
        world = await build_world(project_id, proposal, params)
        
        # 4. 保存
        output_path = root / "data" / project_id / "world.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(world, f, indent=2, ensure_ascii=False)
            
        print("Successfully regenerated and saved world.json")
    except Exception as e:
        print(f"Regeneration failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
