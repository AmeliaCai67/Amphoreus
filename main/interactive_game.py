"""
interactive_game.py - 玩家扮演交互模式状态机

提供有状态的游戏会话，让玩家可以扮演一位黄金裔，
在关键决策点（逐火、交火种等）介入，其余角色由 AI 控制。
"""

import json
import uuid
import random
import time
from typing import Optional

import agent
import stage
from prompt_manager import get_prompt_manager


# 内存中的会话存储
_sessions: dict[str, "GameSession"] = {}


def get_session(session_id: str) -> "GameSession":
    if session_id not in _sessions:
        raise ValueError(f"未找到游戏会话: {session_id}")
    return _sessions[session_id]


def create_session(max_rounds: int = 1) -> str:
    """创建新游戏会话"""
    session = GameSession(max_rounds=max_rounds)
    _sessions[session.session_id] = session
    return session.session_id


def delete_session(session_id: str):
    """删除游戏会话"""
    if session_id in _sessions:
        del _sessions[session.session_id]


class GameSession:
    """一局交互式游戏的状态"""

    def __init__(self, max_rounds: int = 1):
        self.session_id = str(uuid.uuid4())
        self.max_rounds = max(1, max_rounds)
        self.round = 0
        self.stage = "created"
        self.player_char_id: Optional[str] = None

        # 跨回合保留的盗火行者
        self.black_heirs = agent.init_black_heir()

        # 每回合重新初始化的黄金裔
        self.heirs: dict = {}

        self.oracle: str = ""
        self.fire_chasers_dict: dict = {}
        self.robbed_characters: list = []
        self.black_heir_word: str = ""

        # 事件流与日志
        self.events: list = []

        # 可用角色（排除缇宝）
        pm = get_prompt_manager()
        all_ids = pm.get_all_character_ids()
        self.available_characters = [cid for cid in all_ids if cid != "HapLotes405" and cid != "Black_NeiKo"]

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    def _add_event(self, event_type: str, **kwargs):
        """添加事件到事件流（对 list/dict 做快照，避免后续修改影响已记录事件）"""
        event = {"type": event_type}
        for key, value in kwargs.items():
            if isinstance(value, list):
                event[key] = value.copy()
            elif isinstance(value, dict):
                event[key] = value.copy()
            else:
                event[key] = value
        self.events.append(event)
        return event

    def _get_player_heir(self):
        """获取玩家扮演的角色 Agent"""
        if not self.player_char_id or self.player_char_id not in self.heirs:
            raise ValueError("玩家尚未选择角色")
        return self.heirs[self.player_char_id]

    def _format_decision_memory(self, decision: str, reason: str) -> str:
        """把玩家决策和理由格式化为 agent 记忆中的 JSON 字符串"""
        return json.dumps({"decision": decision, "reason": reason}, ensure_ascii=False)

    def _decode_player_decision(self, decision_input) -> str:
        """把玩家的输入归一化为 '1' 或 '0'"""
        if isinstance(decision_input, bool):
            return "1" if decision_input else "0"
        if isinstance(decision_input, int):
            return "1" if decision_input == 1 else "0"
        s = str(decision_input).strip().lower()
        if s in ("1", "true", "yes", "是", "逐火", "交出火种", "同意"):
            return "1"
        return "0"

    def _record_player_fire_decision(self, player_decision: str, reason: Optional[str], is_re_decision: bool = False) -> str:
        """记录玩家逐火决策到记忆与事件流，返回最终使用的理由"""
        player_heir = self._get_player_heir()
        pm = get_prompt_manager()
        char_names = pm.get_character_names()

        if reason is None or reason.strip() == "":
            # 由 AI 生成理由，但决策强制使用玩家的选择
            question = pm.get_scene_prompt(
                "fire_decision",
                name=player_heir.name,
                path=player_heir.path,
                drive=player_heir.drive,
                profile=player_heir.profile,
                memory=player_heir.memory,
                oracle=self.oracle,
            )
            player_heir.make_decision(question=question)
            ai_reason = extract_reason_from_message(player_heir.memory[-1])
            reason = ai_reason if ai_reason else "我做出了自己的选择。"
            # 覆盖决策为玩家选择
            memory_entry = self._format_decision_memory(player_decision, reason)
            player_heir.memory[-1] = memory_entry
        else:
            memory_entry = self._format_decision_memory(player_decision, reason)
            player_heir.memory.append(memory_entry)

        event_type = "fire_redecision" if is_re_decision else "fire_decision"
        self._add_event(
            event_type,
            char_id=self.player_char_id,
            char_name=char_names.get(self.player_char_id, self.player_char_id),
            decision=player_decision,
            decision_text="逐火" if player_decision == "1" else "不逐火",
            reason=reason,
            is_player=True,
        )
        return reason

    def _get_tribbie_nickname(self, char_id: str) -> str:
        """缇宝对各位黄金裔的昵称映射"""
        nicknames = {
            "OreXis945": "小飞儿",
            "KaLos618": "阿雅",
            "NeiKos496": "小白",
            "PoleMos600": "小敌",
            "EleOs252": "小风堇",
            "SkeMma720": "小夏",
            "HubRis504": "凯撒大人",
            "EpieiKeia216": "小小蝶",
        }
        if char_id in nicknames:
            return nicknames[char_id]
        pm = get_prompt_manager()
        char_names = pm.get_character_names()
        return f"{char_names.get(char_id, char_id)}大人"

    def _get_persuader_nickname(self, persuader_id: str, target_char_id: str) -> str:
        """根据劝说者身份决定称呼

        缇宝用亲昵的「小X」系列；阿格莱雅与众人同辈，通常直呼原名，
        仅对特定角色使用尊称或真名。
        """
        pm = get_prompt_manager()
        char_names = pm.get_character_names()

        if persuader_id == "KaLos618":
            # 阿格莱雅：同辈相称，不用小X
            aglaea_nicknames = {
                "OreXis945": "赛法利娅",
                "SkeMma720": "老师",
                "HubRis504": "凯撒大人",
            }
            return aglaea_nicknames.get(
                target_char_id, char_names.get(target_char_id, target_char_id)
            )

        return self._get_tribbie_nickname(target_char_id)

    def _ensure_tribbie_fire_memory(self):
        """缇宝作为神谕发布者，确保她的记忆中存在逐火决策，以便参与后续交火种决策"""
        if "HapLotes405" not in self.heirs:
            return
        tribbie = self.heirs["HapLotes405"]
        if tribbie.memory:
            last = tribbie.memory[-1]
            if isinstance(last, str) and last.strip().startswith("{"):
                try:
                    data = json.loads(last)
                    if "decision" in data:
                        return
                except Exception:
                    pass
        memory_entry = self._format_decision_memory(
            "1", "我是神谕的传递者，自然响应逐火之路。"
        )
        tribbie.memory.append(memory_entry)

    def _summarize_fire_result(self):
        """汇总所有角色的逐火结果"""
        self.fire_chasers_dict = {}
        for char_id, heir in self.heirs.items():
            if char_id == "HapLotes405":
                # 缇宝是神谕发布者，天然逐火
                self.fire_chasers_dict[char_id] = "逐火"
                continue
            if char_id == self.player_char_id:
                # 玩家决策已记录在最后一条记忆中
                decision = stage.decode_decision_from_memory(char_id, heir.memory[-1])
                self.fire_chasers_dict[char_id] = "逐火" if decision == "1" else "不逐火"
                continue
            decision = stage.decode_decision_from_memory(char_id, heir.memory[-1])
            self.fire_chasers_dict[char_id] = "逐火" if decision == "1" else "不逐火"

        self._add_event(
            "fire_result",
            result=self.fire_chasers_dict,
            fire_chasers=[cid for cid, status in self.fire_chasers_dict.items() if status == "逐火"],
        )

    def _state_response(self) -> dict:
        """生成统一的状态响应"""
        pm = get_prompt_manager()
        choices = None

        if self.stage == "choose_character":
            choices = {
                "can_decide": True,
                "decision_type": "choose_character",
                "available_characters": [
                    {"id": cid, "name": pm.get_character_names().get(cid, cid)}
                    for cid in self.available_characters
                ],
            }
        elif self.stage == "fire_decision":
            choices = {
                "can_decide": True,
                "decision_type": "fire_decision",
                "target_char": self.player_char_id,
                "target_name": pm.get_character_names().get(self.player_char_id, self.player_char_id),
            }
        elif self.stage == "handover_decision":
            choices = {
                "can_decide": True,
                "decision_type": "handover_decision",
                "target_char": self.player_char_id,
                "target_name": pm.get_character_names().get(self.player_char_id, self.player_char_id),
            }
        elif self.stage == "fire_persuasion":
            choices = {
                "can_decide": True,
                "decision_type": "fire_persuasion_decision",
                "target_char": self.player_char_id,
                "target_name": pm.get_character_names().get(self.player_char_id, self.player_char_id),
                "message": "缇宝和阿格莱雅劝说了你。你是否改变主意，决定逐火？",
            }
        elif self.stage == "handover_persuasion":
            choices = {
                "can_decide": True,
                "decision_type": "handover_persuasion_decision",
                "target_char": self.player_char_id,
                "target_name": pm.get_character_names().get(self.player_char_id, self.player_char_id),
                "message": "盗火行者劝说了你。你是否改变主意，交出火种？",
            }
        elif self.stage == "round_end":
            choices = {
                "can_decide": True,
                "decision_type": "continue",
            }

        return {
            "session_id": self.session_id,
            "stage": self.stage,
            "round": self.round,
            "max_rounds": self.max_rounds,
            "player_char_id": self.player_char_id,
            "events": self.events,
            "choices": choices,
            "fire_chasers_dict": self.fire_chasers_dict,
            "robbed_characters": self.robbed_characters,
        }

    # ------------------------------------------------------------------
    # 主要流程方法
    # ------------------------------------------------------------------

    def start(self) -> dict:
        """开始游戏：返回开场文案、神谕和可选角色"""
        if self.stage != "created":
            raise ValueError(f"游戏已经启动，当前阶段: {self.stage}")

        self.round = 1
        self.heirs = agent.init_chrysos_heir()

        pm = get_prompt_manager()

        # 开场文案
        intro = pm.get_scene_prompt("intro")
        self._add_event("intro", message=intro)

        # 缇宝发布神谕
        oracle_question = pm.get_scene_prompt("oracle")
        self.oracle = self.heirs["HapLotes405"].answer(oracle_question)
        self._add_event(
            "oracle",
            char_id="HapLotes405",
            char_name=pm.get_character_names().get("HapLotes405", "缇宝"),
            message=self.oracle,
        )

        self.stage = "choose_character"
        return self._state_response()

    def choose_character(self, char_id: str) -> dict:
        """玩家选择扮演的角色"""
        if self.stage != "choose_character":
            raise ValueError(f"当前不是选择角色阶段: {self.stage}")
        if char_id not in self.available_characters:
            raise ValueError(f"不能选择该角色: {char_id}")

        self.player_char_id = char_id
        pm = get_prompt_manager()
        char_names = pm.get_character_names()

        self._add_event(
            "character_chosen",
            char_id=char_id,
            char_name=char_names.get(char_id, char_id),
            message=f"你选择了扮演 {char_names.get(char_id, char_id)}",
        )

        # 生成给玩家的逐火决策问题
        player_heir = self.heirs[char_id]
        question = pm.get_scene_prompt(
            "player_fire_decision",
            name=player_heir.name,
            path=player_heir.path,
            drive=player_heir.drive,
            profile=player_heir.profile,
            memory=player_heir.memory,
            oracle=self.oracle,
        )
        self._add_event(
            "fire_question",
            char_id=char_id,
            char_name=char_names.get(char_id, char_id),
            message=question,
        )

        self.stage = "fire_decision"
        return self._state_response()

    def submit_fire_decision(self, decision, reason: Optional[str] = None) -> dict:
        """玩家提交逐火决策（支持初次决策与劝说后的二次决策）"""
        if self.stage == "fire_decision":
            return self._submit_first_fire_decision(decision, reason)
        elif self.stage == "fire_persuasion":
            return self._submit_persuasion_fire_decision(decision, reason)
        else:
            raise ValueError(f"当前不是逐火决策阶段: {self.stage}")

    def _submit_first_fire_decision(self, decision, reason: Optional[str] = None) -> dict:
        """玩家第一次提交逐火决策"""
        player_decision = self._decode_player_decision(decision)
        self._record_player_fire_decision(player_decision, reason)

        # AI 控制其他角色做逐火决策
        self._run_ai_fire_decisions()

        # 汇总逐火结果，并确保缇宝记忆中有逐火决策
        self._summarize_fire_result()
        self._ensure_tribbie_fire_memory()

        # 玩家逐火则进入交火种决策；否则缇宝和阿格莱雅各劝一轮
        if self.fire_chasers_dict.get(self.player_char_id) == "逐火":
            self._enter_handover_stage()
        else:
            self._run_player_fire_persuasion()
            self.stage = "fire_persuasion"

        return self._state_response()

    def _submit_persuasion_fire_decision(self, decision, reason: Optional[str] = None) -> dict:
        """缇宝和阿格莱雅劝说后，玩家再次提交逐火决策"""
        player_decision = self._decode_player_decision(decision)
        self._record_player_fire_decision(player_decision, reason, is_re_decision=True)

        pm = get_prompt_manager()
        char_names = pm.get_character_names()
        player_name = char_names.get(self.player_char_id, self.player_char_id)

        if player_decision == "1":
            self.fire_chasers_dict[self.player_char_id] = "逐火"
            self._add_event(
                "fire_result_update",
                char_id=self.player_char_id,
                char_name=player_name,
                decision="1",
                decision_text="逐火",
                message="在缇宝和阿格莱雅的劝说后，你决定逐火。",
            )
            self._enter_handover_stage()
        else:
            self.fire_chasers_dict[self.player_char_id] = "不逐火"
            self._add_event(
                "fire_result_update",
                char_id=self.player_char_id,
                char_name=player_name,
                decision="0",
                decision_text="不逐火",
                message="即便经过劝说，你仍然拒绝逐火。",
            )
            self._end_round_for_non_player()

        return self._state_response()

    def _enter_handover_stage(self):
        """玩家逐火，进入交火种决策阶段"""
        player_heir = self._get_player_heir()
        pm = get_prompt_manager()
        char_names = pm.get_character_names()

        # 盗火行者先劝诫
        self._run_black_heir_persuade()
        handover_question = pm.get_scene_prompt(
            "player_handover_decision",
            name=player_heir.name,
            path=player_heir.path,
            drive=player_heir.drive,
            profile=player_heir.profile,
            memory=player_heir.memory,
            black_heir_word=self.black_heir_word,
        )
        self._add_event(
            "handover_question",
            char_id=self.player_char_id,
            char_name=char_names.get(self.player_char_id, self.player_char_id),
            message=handover_question,
        )
        self.stage = "handover_decision"

    def _end_round_for_non_player(self):
        """玩家最终不逐火，AI 自动完成本回合剩余流程"""
        self._run_black_heir_persuade()
        self._run_ai_handover_decisions()
        self._run_handover_persuasion_round()
        self.stage = "round_end"

    def submit_handover_decision(self, decision, reason: Optional[str] = None, max_persuasion_attempts: int = 3) -> dict:
        """玩家提交交火种决策

        Args:
            max_persuasion_attempts: 盗火行者劝说顽固者的最大轮数，默认 3
        """
        if self.stage != "handover_decision":
            raise ValueError(f"当前不是交火种决策阶段: {self.stage}")

        player_decision = self._decode_player_decision(decision)
        player_heir = self._get_player_heir()
        pm = get_prompt_manager()
        char_names = pm.get_character_names()

        # 处理玩家决策理由
        if reason is None or reason.strip() == "":
            question = pm.get_scene_prompt(
                "handover_decision",
                name=player_heir.name,
                path=player_heir.path,
                drive=player_heir.drive,
                profile=player_heir.profile,
                memory=player_heir.memory,
                black_heir_word=self.black_heir_word,
            )
            player_heir.make_decision(question=question)
            ai_reason = extract_reason_from_message(player_heir.memory[-1])
            reason = ai_reason if ai_reason else "我做出了自己的选择。"
            memory_entry = self._format_decision_memory(player_decision, reason)
            player_heir.memory[-1] = memory_entry
        else:
            memory_entry = self._format_decision_memory(player_decision, reason)
            player_heir.memory.append(memory_entry)

        self._add_event(
            "handover_decision",
            char_id=self.player_char_id,
            char_name=char_names.get(self.player_char_id, self.player_char_id),
            decision=player_decision,
            decision_text="交出火种" if player_decision == "1" else "拒绝交出",
            reason=reason,
            is_player=True,
        )

        self.fire_chasers_dict[self.player_char_id] += (
            "_交出火种" if player_decision == "1" else "_不交出火种"
        )

        # AI 控制其他逐火者做交火种决策
        self._run_ai_handover_decisions()

        # 盗火行者劝说，AI 重新决策；若玩家被劝说则进入 handover_persuasion
        self._run_handover_persuasion_round(max_attempts=max_persuasion_attempts)

        return self._state_response()

    def submit_handover_redecision(self, decision, reason: Optional[str] = None) -> dict:
        """盗火行者劝说后，玩家再次提交交火种决策"""
        if self.stage != "handover_persuasion":
            raise ValueError(f"当前不是交火种二次决策阶段: {self.stage}")

        player_decision = self._decode_player_decision(decision)
        player_heir = self._get_player_heir()
        pm = get_prompt_manager()
        char_names = pm.get_character_names()

        # 处理玩家二次决策理由
        if reason is None or reason.strip() == "":
            question = pm.get_scene_prompt(
                "handover_decision",
                name=player_heir.name,
                path=player_heir.path,
                drive=player_heir.drive,
                profile=player_heir.profile,
                memory=player_heir.memory,
                black_heir_word=self.black_heir_word,
            )
            player_heir.make_decision(question=question)
            ai_reason = extract_reason_from_message(player_heir.memory[-1])
            reason = ai_reason if ai_reason else "我做出了自己的选择。"
            memory_entry = self._format_decision_memory(player_decision, reason)
            player_heir.memory[-1] = memory_entry
        else:
            memory_entry = self._format_decision_memory(player_decision, reason)
            player_heir.memory.append(memory_entry)

        self._add_event(
            "handover_redecision",
            char_id=self.player_char_id,
            char_name=char_names.get(self.player_char_id, self.player_char_id),
            decision=player_decision,
            decision_text="改变主意，交出火种" if player_decision == "1" else "仍然拒绝",
            reason=reason,
            is_player=True,
        )

        if player_decision == "1":
            self.fire_chasers_dict[self.player_char_id] = "逐火_交出火种"

        # 结算强夺与记忆
        self._run_robbery_and_collect()
        self.stage = "round_end"
        return self._state_response()

    def continue_game(self) -> dict:
        """继续下一回合或结束游戏"""
        if self.stage != "round_end":
            raise ValueError(f"当前不是回合结束阶段: {self.stage}")

        if self.round >= self.max_rounds:
            self.stage = "complete"
            self._add_event(
                "complete",
                message=f"永劫回归测试完成！共执行 {self.max_rounds} 轮迭代",
            )
            return self._state_response()

        # 进入下一轮
        self.round += 1
        self.heirs = agent.init_chrysos_heir()
        self.fire_chasers_dict = {}
        self.robbed_characters = []
        self.black_heir_word = ""

        pm = get_prompt_manager()
        char_names = pm.get_character_names()

        # 新神谕
        oracle_question = pm.get_scene_prompt("oracle")
        self.oracle = self.heirs["HapLotes405"].answer(oracle_question)
        self._add_event(
            "round_start",
            round_num=self.round,
            message=f">>> [第 {self.round} 轮永劫回归开始]",
        )
        self._add_event(
            "oracle",
            char_id="HapLotes405",
            char_name=char_names.get("HapLotes405", "缇宝"),
            message=self.oracle,
        )

        # 生成给玩家的逐火决策问题
        player_heir = self.heirs[self.player_char_id]
        question = pm.get_scene_prompt(
            "player_fire_decision",
            name=player_heir.name,
            path=player_heir.path,
            drive=player_heir.drive,
            profile=player_heir.profile,
            memory=player_heir.memory,
            oracle=self.oracle,
        )
        self._add_event(
            "fire_question",
            char_id=self.player_char_id,
            char_name=char_names.get(self.player_char_id, self.player_char_id),
            message=question,
        )

        self.stage = "fire_decision"
        return self._state_response()

    # ------------------------------------------------------------------
    # AI 控制逻辑
    # ------------------------------------------------------------------

    def _run_ai_fire_decisions(self):
        """AI 控制非玩家角色做逐火决策"""
        pm = get_prompt_manager()
        char_names = pm.get_character_names()

        for char_id, heir in self.heirs.items():
            if char_id == self.player_char_id or char_id == "HapLotes405":
                continue

            question = pm.get_scene_prompt(
                "fire_decision",
                name=heir.name,
                path=heir.path,
                drive=heir.drive,
                profile=heir.profile,
                memory=heir.memory,
                oracle=self.oracle,
            )
            res = heir.make_decision(question=question)
            decision = stage.decode_decision_from_memory(char_id, heir.memory[-1])
            self._add_event(
                "fire_decision",
                char_id=char_id,
                char_name=char_names.get(char_id, char_id),
                decision=decision,
                decision_text="逐火" if decision == "1" else "不逐火",
                reason=extract_reason_from_message(res),
                is_player=False,
            )

    def _run_black_heir_persuade(self):
        """盗火行者劝诫"""
        pm = get_prompt_manager()
        char_names = pm.get_character_names()

        for char_id, heir in self.black_heirs.items():
            question = pm.get_scene_prompt("black_heir_persuade")
            self.black_heir_word = heir.answer(question=question)
            self._add_event(
                "persuasion",
                char_id=char_id,
                char_name=char_names.get(char_id, char_id),
                message=self.black_heir_word,
            )

    def _run_player_fire_persuasion(self):
        """玩家不逐火时，缇宝和阿格莱雅各劝一轮"""
        pm = get_prompt_manager()
        char_names = pm.get_character_names()
        player_heir = self._get_player_heir()
        player_reason = extract_reason_from_message(player_heir.memory[-1])
        if not player_reason:
            player_reason = "我还没有准备好。"

        persuaders = ["HapLotes405", "KaLos618"]
        for persuader_id in persuaders:
            if persuader_id not in self.heirs:
                continue
            # 玩家扮演阿格莱雅时，避免阿格莱雅自己劝自己
            if persuader_id == self.player_char_id:
                continue
            persuader = self.heirs[persuader_id]
            nickname = self._get_persuader_nickname(persuader_id, self.player_char_id)
            question = pm.get_scene_prompt(
                "fire_persuade_player",
                name=persuader.name,
                path=persuader.path,
                drive=persuader.drive,
                profile=persuader.profile,
                target_name=player_heir.name,
                player_reason=player_reason,
                nickname=nickname,
            )
            res = persuader.answer(question=question)
            self._add_event(
                "fire_persuasion",
                persuader_id=persuader_id,
                persuader_name=char_names.get(persuader_id, persuader_id),
                target_id=self.player_char_id,
                target_name=char_names.get(self.player_char_id, self.player_char_id),
                message=res,
            )

        # 再次向玩家提问
        question = pm.get_scene_prompt(
            "player_fire_decision",
            name=player_heir.name,
            path=player_heir.path,
            drive=player_heir.drive,
            profile=player_heir.profile,
            memory=player_heir.memory,
            oracle=self.oracle,
        )
        self._add_event(
            "fire_question",
            char_id=self.player_char_id,
            char_name=char_names.get(self.player_char_id, self.player_char_id),
            message=question,
            is_re_decision=True,
        )

    def _run_ai_handover_decisions(self):
        """AI 控制非玩家逐火者做交火种决策"""
        # 缇宝若因劝说环节产生了新的记忆，需确保最后一条是逐火决策，才能正确解析交火种决策
        self._ensure_tribbie_fire_memory()

        pm = get_prompt_manager()
        char_names = pm.get_character_names()

        for char_id, heir in self.heirs.items():
            if char_id == self.player_char_id:
                continue
            if self.fire_chasers_dict.get(char_id) != "逐火":
                continue

            question = pm.get_scene_prompt(
                "handover_decision",
                name=heir.name,
                path=heir.path,
                drive=heir.drive,
                profile=heir.profile,
                memory=heir.memory,
                black_heir_word=self.black_heir_word,
            )
            res = heir.make_decision(question=question)
            decision = stage.decode_decision_from_memory(char_id, heir.memory[-1])
            self.fire_chasers_dict[char_id] += (
                "_交出火种" if decision == "1" else "_不交出火种"
            )
            self._add_event(
                "handover_decision",
                char_id=char_id,
                char_name=char_names.get(char_id, char_id),
                decision=decision,
                decision_text="交出火种" if decision == "1" else "拒绝交出",
                reason=extract_reason_from_message(res),
                is_player=False,
            )

    def _run_robbery_and_collect(self):
        """强夺剩余顽固者的火种并收集记忆"""
        pm = get_prompt_manager()
        char_names = pm.get_character_names()

        self.robbed_characters = []
        for char_id, status in self.fire_chasers_dict.items():
            if status == "逐火_不交出火种":
                self.fire_chasers_dict[char_id] = "逐火_火种被强夺"
                self.robbed_characters.append(char_id)
                self._add_event(
                    "robbery",
                    char_id=char_id,
                    char_name=char_names.get(char_id, char_id),
                )

        self._add_event(
            "round_end",
            round_num=self.round,
            final_result=self.fire_chasers_dict,
            robbed_characters=self.robbed_characters,
        )
        self._collect_memories()

    def _run_handover_persuasion_round(self, max_attempts: int = 1):
        """盗火行者劝说顽固者，并让 AI 顽固者重新决策。

        若玩家在被劝说的目标中，则进入 handover_persuasion 阶段等待玩家二次决策；
        否则直接强夺并结束回合。
        """
        pm = get_prompt_manager()
        char_names = pm.get_character_names()

        player_targeted = False

        for attempt in range(max_attempts):
            stubborn = [
                cid for cid, status in self.fire_chasers_dict.items()
                if status == "逐火_不交出火种"
            ]
            if not stubborn:
                break

            self._add_event(
                "persuasion_attempt",
                attempt=attempt + 1,
                targets=stubborn,
            )

            # 盗火行者劝说顽固者；玩家优先
            for black_heir_id, black_heir in self.black_heirs.items():
                if not stubborn:
                    break

                if self.player_char_id in stubborn:
                    target = self.player_char_id
                    player_targeted = True
                else:
                    target = random.choice(stubborn)

                stubborn.remove(target)
                question = pm.get_scene_prompt(
                    "persuade_target",
                    target_name=target,
                    attempt=attempt + 1,
                )
                res = black_heir.answer(question=question)
                self._add_event(
                    "persuasion_detail",
                    persuader_id=black_heir_id,
                    persuader_name=char_names.get(black_heir_id, black_heir_id),
                    target_id=target,
                    target_name=char_names.get(target, target),
                    message=res,
                )

            # AI 顽固者重新决策并记录回复
            for char_id in list(stubborn):
                if char_id == self.player_char_id:
                    continue
                heir = self.heirs[char_id]
                question = pm.get_scene_prompt(
                    "reconsider",
                    name=heir.name,
                    path=heir.path,
                    drive=heir.drive,
                    profile=heir.profile,
                    memory=heir.memory,
                    attempt=attempt + 1,
                )
                res = heir.make_decision(question=question)
                decision = stage.decode_decision_from_memory(char_id, heir.memory[-1])
                self._add_event(
                    "handover_redecision",
                    char_id=char_id,
                    char_name=char_names.get(char_id, char_id),
                    decision=decision,
                    decision_text="改变主意，交出火种" if decision == "1" else "仍然拒绝",
                    message=res,
                )
                if decision == "1":
                    self.fire_chasers_dict[char_id] = "逐火_交出火种"

        if player_targeted and self.fire_chasers_dict.get(self.player_char_id) == "逐火_不交出火种":
            # 玩家需要二次决策
            player_heir = self._get_player_heir()
            question = pm.get_scene_prompt(
                "player_handover_decision",
                name=player_heir.name,
                path=player_heir.path,
                drive=player_heir.drive,
                profile=player_heir.profile,
                memory=player_heir.memory,
                black_heir_word=self.black_heir_word,
            )
            self._add_event(
                "handover_question",
                char_id=self.player_char_id,
                char_name=char_names.get(self.player_char_id, self.player_char_id),
                message=question,
                is_re_decision=True,
            )
            self.stage = "handover_persuasion"
        else:
            # 无需玩家二次决策，直接结算
            self._run_robbery_and_collect()
            self.stage = "round_end"

    def _collect_memories(self):
        """盗火行者收集火种记忆"""
        for black_heir in self.black_heirs.values():
            for char_id, status in self.fire_chasers_dict.items():
                if status in ["逐火_交出火种", "逐火_火种被强夺"]:
                    for memory in self.heirs[char_id].memory:
                        black_heir.memory.append(memory)
                elif status == "不逐火":
                    if self.heirs[char_id].memory:
                        black_heir.memory.append(self.heirs[char_id].memory[0])

            if self.robbed_characters:
                black_heir.memory.append(
                    f"被强夺火种的角色：{self.robbed_characters}，这些角色因被强夺火种受伤甚至死亡"
                )


def extract_reason_from_message(message: str) -> str:
    """从消息中提取 reason 字段，兼容 JSON 和 markdown code block"""
    if not message or not isinstance(message, str):
        return ""
    message = message.strip()

    # 去除 markdown 代码块标记
    if message.startswith("```"):
        lines = message.splitlines()
        if len(lines) > 2:
            message = "\n".join(lines[1:-1]).strip()
        else:
            message = message.replace("```", "").strip()

    if 'reason' in message:
        try:
            import re
            pattern = r"['\"]reason['\"]\s*:\s*['\"](.+?)['\"](?:,|\})"
            match = re.search(pattern, message, re.DOTALL)
            if match:
                return match.group(1).strip()
            data = json.loads(message)
            if isinstance(data, dict) and 'reason' in data:
                return str(data['reason']).strip()
        except Exception:
            pass
    return ""


# ===================================================================
# 命令行演示：直接运行 python main/interactive_game.py 即可体验
# ===================================================================

if __name__ == "__main__":
    print(">>> 欢迎使用 Amphoreus 交互式逐火之旅（命令行演示）")
    print(">>> 创建游戏会话...")

    session_id = create_session(max_rounds=1)
    session = get_session(session_id)

    # 开始游戏
    state = session.start()
    pm = get_prompt_manager()
    char_names = pm.get_character_names()

    # 打印开场
    for event in state["events"]:
        if event["type"] == "intro":
            print("\n===== 开场 =====")
            print(event["message"])
        elif event["type"] == "oracle":
            print(f"\n===== [{event['char_name']}] 发布神谕 =====")
            print(event["message"])

    # 选择角色
    print("\n===== 可选角色 =====")
    for i, ch in enumerate(state["choices"]["available_characters"], 1):
        print(f"{i}. {ch['name']} ({ch['id']})")

    while True:
        choice = input("\n请选择要扮演的角色（输入序号）: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(state["choices"]["available_characters"]):
            char_id = state["choices"]["available_characters"][int(choice) - 1]["id"]
            break
        print("无效输入，请重新选择。")

    state = session.choose_character(char_id)
    print(f"\n>>> 你选择了扮演：{char_names.get(char_id, char_id)}")

    # 逐火决策
    fire_question = [e for e in state["events"] if e["type"] == "fire_question"][0]["message"]
    print(f"\n===== 逐火决策 =====\n{fire_question}")

    while True:
        decision = input("你的选择（1=逐火，0=不逐火）: ").strip()
        if decision in ("0", "1"):
            break
        print("无效输入，请输入 0 或 1。")

    reason = input("你的理由（直接回车由AI生成）: ").strip() or None

    print("\n>>> 正在提交决策，请稍候...")
    state = session.submit_fire_decision(decision, reason)

    print("\n===== 逐火结果 =====")
    for cid, status in state["fire_chasers_dict"].items():
        print(f"  {char_names.get(cid, cid)}: {status}")

    # 玩家不逐火时，缇宝和阿格莱雅会劝说一轮
    while state["stage"] == "fire_persuasion":
        print("\n===== 缇宝与阿格莱雅的劝说 =====")
        for event in state["events"]:
            if event["type"] == "fire_persuasion":
                print(f"\n[{event['persuader_name']}] 对你说：")
                print(event["message"])

        re_questions = [e for e in state["events"] if e["type"] == "fire_question" and e.get("is_re_decision")]
        if re_questions:
            print(f"\n===== 再次决定 =====\n{re_questions[-1]['message']}")

        while True:
            decision = input("你的选择（1=逐火，0=不逐火）: ").strip()
            if decision in ("0", "1"):
                break
            print("无效输入，请输入 0 或 1。")

        reason = input("你的理由（直接回车由AI生成）: ").strip() or None

        print("\n>>> 正在提交决策，请稍候...")
        state = session.submit_fire_decision(decision, reason)

        print("\n===== 逐火结果 =====")
        for cid, status in state["fire_chasers_dict"].items():
            print(f"  {char_names.get(cid, cid)}: {status}")

    # 如果玩家逐火，继续交火种决策
    if state["stage"] == "handover_decision":
        handover_question = [e for e in state["events"] if e["type"] == "handover_question"][0]["message"]
        print(f"\n===== 交火种决策 =====\n{handover_question}")

        while True:
            decision = input("你的选择（1=交出火种，0=拒绝交出）: ").strip()
            if decision in ("0", "1"):
                break
            print("无效输入，请输入 0 或 1。")

        reason = input("你的理由（直接回车由AI生成）: ").strip() or None

        print("\n>>> 正在提交决策，请稍候...")
        # 命令行演示：盗火行者先劝玩家一次，再决定是否强夺
        state = session.submit_handover_decision(decision, reason, max_persuasion_attempts=1)

    # 玩家拒绝交出火种后，盗火行者劝说并等待玩家二次决策
    while state["stage"] == "handover_persuasion":
        print("\n===== 盗火行者的劝说 =====")
        for event in state["events"]:
            if event["type"] == "persuasion_attempt":
                print(f"\n第 {event['attempt']} 次劝说目标: {', '.join(char_names.get(cid, cid) for cid in event['targets'])}")
            elif event["type"] == "persuasion_detail":
                print(f"\n[{event['persuader_name']}] 劝说 [{event['target_name']}]:")
                print(event["message"])
            elif event["type"] == "handover_redecision" and not event.get("is_player"):
                print(f"\n[{event['char_name']}] 回应: {event['decision_text']}")
                print(f"  理由: {extract_reason_from_message(event['message'])}")

        re_handover_questions = [e for e in state["events"] if e["type"] == "handover_question" and e.get("is_re_decision")]
        if re_handover_questions:
            print(f"\n===== 再次决定 =====\n{re_handover_questions[-1]['message']}")

        while True:
            decision = input("你的选择（1=交出火种，0=仍然拒绝）: ").strip()
            if decision in ("0", "1"):
                break
            print("无效输入，请输入 0 或 1。")

        reason = input("你的理由（直接回车由AI生成）: ").strip() or None

        print("\n>>> 正在提交决策，请稍候...")
        state = session.submit_handover_redecision(decision, reason)

    # 最终结果
    print("\n===== 本轮最终结果 =====")
    for cid, status in state["fire_chasers_dict"].items():
        print(f"  {char_names.get(cid, cid)}: {status}")

    if state["robbed_characters"]:
        print(f"\n被强夺火种的角色: {', '.join(char_names.get(cid, cid) for cid in state['robbed_characters'])}")

    print("\n>>> 游戏结束")
