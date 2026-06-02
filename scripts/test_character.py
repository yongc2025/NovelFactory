import asyncio
import json
import os
import sys
from pathlib import Path

# 增加项目根目录到路径
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from novel_factory.engine.character import design_characters
from novel_factory.db.project_store import ProjectStore

async def main():
    project_id = "20260601_172217_9a0afb"
    store = ProjectStore()
    
    # 读取现状
    world = store.get_world(project_id)
    project = store.get_project(project_id)
    
    # 构造参数
    params = project or {}
    
    print(f"Testing character generation for: {project_id}...")
    try:
        characters = await design_characters(project_id, world, params)
        print(f"Successfully generated {len(characters)} characters.")
        
        # 保存结果
        store.save_characters(project_id, characters)
        print("Successfully saved characters.json")
    except Exception as e:
        print(f"Error during character generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
