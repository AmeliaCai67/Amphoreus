"""
PromptManager - 统一管理 Amphoreus 所有提示词与角色配置

用法:
    from prompt_manager import PromptManager

    pm = PromptManager()
    system = pm.get_system_prompt("EpieiKeia216", memory=[...])
    question = pm.get_scene_prompt("fire_decision", oracle="...")
"""

import yaml
from pathlib import Path


class PromptManager:
    """
    提示词管理器：从 prompts/ 目录加载角色配置、基础提示词、场景提示词，
    并提供格式化后的提示词获取接口。
    """

    def __init__(self, prompts_dir=None):
        """
        初始化 PromptManager

        Args:
            prompts_dir: prompts 目录路径，默认使用项目根目录下的 prompts/
        """
        if prompts_dir is None:
            # main/prompt_manager.py -> .. -> project_root/prompts
            self.base_dir = Path(__file__).resolve().parent.parent / "prompts"
        else:
            self.base_dir = Path(prompts_dir)

        self.characters = {}
        self.scenes = {}
        self.base = {}

        self._load_base_prompts()
        self._load_scene_prompts()
        self._load_characters()

    # ------------------------------------------------------------------
    # 加载逻辑
    # ------------------------------------------------------------------

    def _load_base_prompts(self):
        """加载 prompts/base/*.md"""
        base_dir = self.base_dir / "base"
        if not base_dir.exists():
            raise FileNotFoundError(f"基础提示词目录不存在: {base_dir}")

        for file_path in sorted(base_dir.glob("*.md")):
            self.base[file_path.stem] = file_path.read_text(encoding="utf-8").strip()

    def _load_scene_prompts(self):
        """加载 prompts/scenes/*.md"""
        scenes_dir = self.base_dir / "scenes"
        if not scenes_dir.exists():
            raise FileNotFoundError(f"场景提示词目录不存在: {scenes_dir}")

        for file_path in sorted(scenes_dir.glob("*.md")):
            self.scenes[file_path.stem] = file_path.read_text(encoding="utf-8").strip()

    def _load_characters(self):
        """加载 prompts/characters/*.yaml 以及 prompts/characters/black_heir/*.yaml"""
        chars_dir = self.base_dir / "characters"
        if not chars_dir.exists():
            raise FileNotFoundError(f"角色配置目录不存在: {chars_dir}")

        for file_path in sorted(chars_dir.glob("*.yaml")):
            char_id = file_path.stem
            self.characters[char_id] = yaml.safe_load(file_path.read_text(encoding="utf-8"))

        black_heir_dir = chars_dir / "black_heir"
        if black_heir_dir.exists():
            for file_path in sorted(black_heir_dir.glob("*.yaml")):
                char_id = file_path.stem
                self.characters[char_id] = yaml.safe_load(file_path.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def get_character(self, char_id: str) -> dict:
        """获取角色原始配置 dict"""
        if char_id not in self.characters:
            raise ValueError(f"未找到角色配置: {char_id}")
        return self.characters[char_id]

    def get_character_names(self) -> dict:
        """返回 {char_id: name} 映射表"""
        return {
            char_id: config.get("name", char_id)
            for char_id, config in self.characters.items()
        }

    def get_all_character_ids(self) -> list:
        """返回所有角色 ID 列表"""
        return list(self.characters.keys())

    def get_system_prompt(self, char_id: str, memory=None) -> str:
        """
        获取某角色的系统提示词（已渲染模板变量）

        Args:
            char_id: 角色 ID
            memory: 当前记忆列表，如果不传则使用角色配置文件中的初始 memory
        """
        char = self.get_character(char_id)

        # 盗火行者使用专门的基础提示词模板
        if char_id == "Black_NeiKo":
            template = self.base.get("black_heir_system") or self.base.get("system")
        else:
            # 角色可单独覆盖基础系统提示词
            template = char.get("system_override") or self.base.get("system")

        if not template:
            raise ValueError(f"未找到系统提示词模板 (role={char_id})")

        if memory is None:
            memory = char.get("memory", [])

        return template.format(
            id=char_id,
            name=char.get("name", ""),
            path=char.get("path", ""),
            drive=char.get("drive", ""),
            profile=char.get("profile", ""),
            memory=memory,
        )

    def get_scene_prompt(self, scene_name: str, **kwargs) -> str:
        """
        获取并渲染某个场景的提示词/问题

        Args:
            scene_name: 场景名，对应 prompts/scenes/{scene_name}.md
            **kwargs: 模板变量
        """
        template = self.scenes.get(scene_name)
        if not template:
            raise ValueError(f"未找到场景提示词: {scene_name}")
        return template.format(**kwargs)

    def get_decision_format(self) -> str:
        """获取决策输出格式要求"""
        return self.base.get("decision_format", "")

    def get_decode_fallback_prompt(self, text: str) -> str:
        """获取决策解析失败时的兜底 AI 提示词"""
        template = self.base.get("decode_fallback")
        if not template:
            raise ValueError("未找到 decode_fallback 提示词模板")
        return template.format(text=text)


# 全局单例，方便各模块直接导入使用
_prompt_manager = None


def get_prompt_manager(prompts_dir=None) -> PromptManager:
    """获取 PromptManager 单例"""
    global _prompt_manager
    if _prompt_manager is None or prompts_dir is not None:
        _prompt_manager = PromptManager(prompts_dir)
    return _prompt_manager
