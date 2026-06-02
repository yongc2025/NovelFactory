import os
import re
from typing import Dict, Optional, Tuple
from jinja2 import Template

class SkillLoader:
    """
    SkillLoader 负责从 skills/*.md 文件中加载和解析提示词模板。
    它将 Markdown 文件解析为 System Prompt 和 User Prompt，并支持 Jinja2 渲染。
    """
    
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir

    def load_skill(self, skill_name: str) -> Tuple[str, str]:
        """
        加载指定技能的提示词模板。
        """
        skill_path = os.path.join(self.skills_dir, skill_name, "SKILL.md")
        if not os.path.exists(skill_path):
            raise FileNotFoundError(f"Skill file not found at {skill_path}")

        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()

        system_prompt = self._extract_section(content, "System Prompt")
        user_prompt = self._extract_section(content, "User Prompt")

        if not system_prompt and not user_prompt:
            raise ValueError(f"Skill {skill_name} does not contain 'System Prompt' or 'User Prompt' sections.")

        return system_prompt, user_prompt

    def render(self, skill_name: str, context: dict) -> Tuple[str, str]:
        """
        加载并渲染指定技能的提示词。
        """
        system_tmpl, user_tmpl = self.load_skill(skill_name)
        
        # 使用 Jinja2 渲染
        rendered_sys = Template(system_tmpl).render(**context)
        rendered_user = Template(user_tmpl).render(**context)
        
        return rendered_sys, rendered_user

    def _extract_section(self, content: str, section_name: str) -> str:
        """
        提取 Markdown 中指定标题下的内容。
        """
        # 0025: 修复匹配逻辑，防止在 ### 等更深层级标题处中断
        # 我们要匹配的是 ## Section Name，停止条件是下一个同级的 ## 标题或文件末尾
        pattern = rf"\n## {section_name}\s*\n(.*?)(?=\n##\s+|$)"
        # 兼容文件开头没有换行的情况
        if not content.startswith("\n"):
            content = "\n" + content
            
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

if __name__ == "__main__":
    # 简单的本地测试逻辑
    loader = SkillLoader(r"d:\workspace\NovelFactory\src\novel_factory\skills")
    try:
        sys_p, usr_p = loader.load_skill("writer")
        print(f"System Prompt Length: {len(sys_p)}")
        print(f"User Prompt Length: {len(usr_p)}")
    except Exception as e:
        print(f"Test failed: {e}")
