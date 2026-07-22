from __future__ import annotations

import json
import random
import sys
import tempfile
import types
import unittest
from pathlib import Path
from dataclasses import dataclass
from types import SimpleNamespace

try:
    import llocg_ui.server  # type: ignore  # noqa: F401
except ModuleNotFoundError:
    pkg = types.ModuleType("llocg_ui")
    server_stub = types.ModuleType("llocg_ui.server")
    views_stub = types.ModuleType("llocg_ui.views")
    db_stub = types.ModuleType("llocg_ui.db")
    server_stub.App = object
    server_stub.HTML = "<html><head></head><body><script>function clearSel(){ selHand = []; updateTop(); render(); }\n  const cardInfoUrl='/cardinfo?cn='+cn;\n  if(IS_PUBLIC_VIEW){\n    setInterval(()=>{ refreshStateFromServer({force:false}); }, 250);\n    window.addEventListener('storage', (ev)=>{</script></body></html>"
    views_stub.make_view_state = lambda state, mode: state
    db_stub._get_card = lambda db, cn: db.get(cn) if isinstance(db, dict) else None
    sys.modules["llocg_ui"] = pkg
    sys.modules["llocg_ui.server"] = server_stub
    sys.modules["llocg_ui.views"] = views_stub
    sys.modules["llocg_ui.db"] = db_stub

from llocg_dual_v2.core import DualMatchEngine, Phase
import llocg_dual_v2.server as dual_server
from llocg_dual_v2.server import (
    LegacyUIAdapter,
    PlayerViewRuntime,
    _find_runtime_card_image,
    _first_existing_file,
    _runtime_image_candidates,
    _scoped_single_html,
    _transparent_png_bytes,
)

BUILD_TAG = "llocg_dual_v2_opponent_hand_position_bridge_tests_20260721a"


def deck(prefix: str):
    return [f"{prefix}-{i:03d}" for i in range(60)]


@dataclass
class FakeSlot:
    cardnumber: str
    active: bool = True
    energy_under: int = 0


class FakeApp:
    def __init__(self, deck_code: str, seed: int):
        self.root = SimpleNamespace()
        self.outdir = SimpleNamespace()
        self.cards_db = {
            f"{deck_code}-{i:03d}": {
                "cardnumber": f"{deck_code}-{i:03d}",
                "score": 1,
                "blade_heart_score_n": 0,
                "effect_text_raw": "",
            }
            for i in range(60)
        }
        self.img = SimpleNamespace()
        self.rng = random.Random(seed)
        self.deck_code = deck_code
        self.ui_code = deck_code
        self.finish_performance_with_pending = False
        self.generate_success_effect_pending = False
        self._success_effect_generated = False
        self.success_effect_applied = False
        self.attempt_succeeds = True
        self.defer_failed_live_cleanup = False
        self.show_attempt_summary_notice = False
        self.reopen_yell_if_live_start_reset = False
        self.state_only_yell_popup = False
        self.filter_all_set_cards_at_live_confirm = False
        self.live_resolve_calls = 0
        self.gs = SimpleNamespace(
            deck=[], hand=[], energy_active=0, energy_wait=0, energy_total=12,
            stage={"L": None, "C": None, "R": None},
            green_room=[], set_zone=[], success_zone=[], resolve_zone=[],
            pending=[], log=[], turn=1, phase="MULLIGAN", turn_order="first",
            next_turn_order="", live_start_prompted=False,
            opponent_wait_count=0, opponent_success_count=0,
            opponent_excess_heart_count=0, last_excess_heart_count=0,
            yell_reveal_notice=False, attempt_summary_notice=False,
            yell_reveal_acknowledged_this_live=False,
            yell_revealed_cards=[], last_attempt_result="",
        )

    def state_json(self):
        return {
            "turn": self.gs.turn,
            "phase": self.gs.phase,
            "deck": list(self.gs.deck),
            "hand": list(self.gs.hand),
            "energy_active": self.gs.energy_active,
            "energy_wait": self.gs.energy_wait,
            "stage": {
                k: ({"cardnumber": v.cardnumber, "active": v.active} if v else None)
                for k, v in self.gs.stage.items()
            },
            "set_zone": list(self.gs.set_zone),
            "success_zone": list(self.gs.success_zone),
            "resolve_zone": list(self.gs.resolve_zone),
            "green_room": list(self.gs.green_room),
            "pending": list(self.gs.pending),
            "yell_reveal_notice": bool(self.gs.yell_reveal_notice),
            "yell_reveal_acknowledged_this_live": bool(self.gs.yell_reveal_acknowledged_this_live),
            "yell_revealed_cards": list(self.gs.yell_revealed_cards),
            "attempt_summary_notice": bool(self.gs.attempt_summary_notice),
            "last_attempt_result": str(self.gs.last_attempt_result),
            "state_yell_popup_open": bool(self.state_only_yell_popup),
            "log": list(self.gs.log),
        }

    def cmd(self, name, payload):
        if name == "play":
            idx = int(payload.get("hand_idx", -1))
            pos = str(payload.get("pos", ""))
            if idx < 0 or idx >= len(self.gs.hand):
                raise ValueError("bad hand index")
            if pos not in self.gs.stage:
                raise ValueError("bad position")
            cn = self.gs.hand.pop(idx)
            self.gs.stage[pos] = FakeSlot(cn)
            self.gs.energy_active -= 1
            self.gs.log.append(f"played {cn} to {pos}")
        elif name == "resolve_pending":
            if self.gs.pending:
                self.gs.pending.pop(0)
        elif name == "ack_yell_reveal":
            self.gs.log.append("[ACK] yell reveal fallback acknowledged")
            self.gs.yell_reveal_notice = False
            self.gs.yell_reveal_acknowledged_this_live = True
            self.state_only_yell_popup = False
            if self.gs.phase == "LIVE_PERF":
                self.gs.phase = "LIVE_ATTEMPT"
        elif name == "next":
            if self.gs.pending:
                item = self.gs.pending.pop(0)
                if isinstance(item, dict) and item.get("kind") == "live_success_effect":
                    self.success_effect_applied = True
            elif self.gs.yell_reveal_notice:
                self.gs.yell_reveal_notice = False
                self.gs.phase = "LIVE_ATTEMPT"
            elif self.gs.attempt_summary_notice:
                self.gs.attempt_summary_notice = False
                self.gs.phase = "LIVE_RESOLVE"
            elif self.gs.phase == "LIVE_SET":
                raw = payload.get("indices", []) if isinstance(payload, dict) else []
                indices = sorted({int(i) for i in raw})
                if any(i < 0 or i >= len(self.gs.hand) for i in indices):
                    raise ValueError("bad live-set hand index")
                chosen = [self.gs.hand[i] for i in indices]
                for i in reversed(indices):
                    self.gs.hand.pop(i)
                self.gs.set_zone.extend(chosen)
                draw_n = len(chosen)
                self.gs.hand.extend(self.gs.deck[:draw_n])
                del self.gs.deck[:draw_n]
                self.gs.phase = "LIVE_CONFIRM"
            elif self.gs.phase == "LIVE_CONFIRM":
                if self.filter_all_set_cards_at_live_confirm:
                    moved = list(self.gs.set_zone)
                    self.gs.green_room.extend(moved)
                    self.gs.set_zone = []
                    self.gs.phase = "LIVE_RESOLVE"
                    self.gs.log.append(f"[INFO] confirm: no LIVE after filtering; moved={len(moved)}")
                    return
                self.gs.live_start_prompted = True
                self.gs.phase = "LIVE_PERF"
            elif self.gs.phase == "LIVE_PERF":
                self.gs.log.append("[YELL] fake reveal")
                if self.gs.deck:
                    self.gs.resolve_zone.append(self.gs.deck.pop(0))
                self.gs.yell_reveal_notice = True
            elif self.gs.phase == "LIVE_ATTEMPT":
                if self.attempt_succeeds:
                    self.gs.last_attempt_result = "SUCCESS"
                else:
                    self.gs.last_attempt_result = "FAILURE"
                    if not self.defer_failed_live_cleanup:
                        self.gs.green_room.extend(self.gs.set_zone)
                        self.gs.set_zone = []
                if self.show_attempt_summary_notice:
                    self.gs.attempt_summary_notice = True
                else:
                    self.gs.phase = "LIVE_RESOLVE"
                    if self.attempt_succeeds and self.gs.set_zone:
                        self.gs.pending = [{
                            "kind": "success_zone_choice",
                            "message": "成功したライブを成功ライブカード置き場に置くか選択",
                        }]
                    if self.finish_performance_with_pending:
                        self.gs.pending.append({"kind": "performance_tail"})
            elif self.gs.phase == "LIVE_RESOLVE":
                self.live_resolve_calls += 1
                if self.reopen_yell_if_live_start_reset and not self.gs.live_start_prompted:
                    self.gs.yell_reveal_notice = True
                    self.gs.phase = "LIVE_PERF"
                elif self.generate_success_effect_pending and not self._success_effect_generated:
                    self._success_effect_generated = True
                    self.gs.pending = [{"kind": "live_success_effect", "message": "ライブ成功時：確認"}]
                else:
                    self.gs.phase = "MAIN"
        return self.state_json()


class LegacyAdapterTransactionTests(unittest.TestCase):
    def make_adapter(self):
        engine = DualMatchEngine(deck("A"), deck("B"), "A", "B", seed=4)
        p1 = PlayerViewRuntime("p1", 0, "P1", "#00f", FakeApp("A", 4))
        p2 = PlayerViewRuntime("p2", 1, "P2", "#f60", FakeApp("B", 5))
        return LegacyUIAdapter(engine, p1, p2)

    def enter_first_main(self, a: LegacyUIAdapter):
        a.action("NEXT", {"indices": []})
        a.action("NEXT", {"indices": []})
        self.assertEqual(a.engine.state.phase, Phase.MAIN_FIRST)

    def enter_first_live_set(self, a: LegacyUIAdapter):
        self.enter_first_main(a)
        a.action("NEXT", {})
        self.assertEqual(a.engine.state.phase, Phase.MAIN_SECOND)
        a.action("NEXT", {})
        self.assertEqual(a.engine.state.phase, Phase.LIVE_SET_FIRST)

    def enter_performance(self, a: LegacyUIAdapter, p1_indices=(0,), p2_indices=(0,)):
        self.enter_first_live_set(a)
        a.action("NEXT", {"indices": list(p1_indices)})
        a.action("NEXT", {"indices": list(p2_indices)})
        self.assertEqual(a.engine.state.phase, Phase.PERFORMANCE_FIRST)

    def finish_one_performance(self, a: LegacyUIAdapter, expected_phase: Phase):
        # LIVE_CONFIRM -> LIVE_PERF
        a.action("NEXT", {})
        # YELL creates a confirmation notice and stays in LIVE_PERF.
        a.action("NEXT", {})
        self.assertTrue(a._active_runtime().app.gs.yell_reveal_notice)
        # Central NEXT acknowledges the notice, not the central phase.
        out = a.action("NEXT", {})
        self.assertTrue(out.get("dialog_acknowledged"))
        self.assertFalse(a._active_runtime().app.gs.yell_reveal_notice)
        self.assertEqual(a._active_runtime().app.gs.phase, "LIVE_ATTEMPT")
        # Required-heart attempt reaches the dual 8.3/8.4 boundary.
        a.action("NEXT", {})
        self.assertEqual(a.engine.state.phase, expected_phase)

    def enter_judgment(self, a: LegacyUIAdapter, p1_indices=(0,), p2_indices=(0,)):
        self.enter_performance(a, p1_indices, p2_indices)
        self.finish_one_performance(a, Phase.PERFORMANCE_SECOND)
        self.finish_one_performance(a, Phase.LIVE_JUDGMENT)

    def advance_to_final_score(self, a: LegacyUIAdapter):
        a.action("NEXT", {})  # initial score
        a.action("NEXT", {})  # enter first success timing
        a.action("NEXT", {})  # finish first success timing
        a.action("NEXT", {})  # finish second success timing -> final score step
        self.assertEqual(a.engine.state.judgment_step, "FINAL_SCORE")

    def calculate_and_confirm_result(self, a: LegacyUIAdapter):
        a.action("NEXT", {})  # calculate final score and show RESULT_CONFIRM
        self.assertEqual(a.engine.state.judgment_step, "RESULT_CONFIRM")
        a.action("NEXT", {})  # confirm result, then move/prompt success card

    def set_live_scores(self, a: LegacyUIAdapter, player_id: int, scores):
        rt = a.runtime("p1" if player_id == 0 else "p2")
        cards = list(rt.app.gs.set_zone)
        self.assertEqual(len(cards), len(scores))
        for cn, score in zip(cards, scores):
            rt.app.cards_db[cn]["score"] = int(score)
        return cards


    def test_mulligans_remain_two_distinct_player_transactions(self):
        a = self.make_adapter()
        p1_before = list(a.engine.state.players[0].hand)
        p2_before = list(a.engine.state.players[1].hand)
        a.action("NEXT", {
            "indices": [0, 2],
            "expected_phase": "MULLIGAN_FIRST",
            "expected_active_player_key": "p1",
        })
        self.assertEqual(a.engine.state.phase, Phase.MULLIGAN_SECOND)
        self.assertTrue(a.engine.state.players[0].mulligan_done)
        self.assertFalse(a.engine.state.players[1].mulligan_done)
        self.assertNotEqual(a.engine.state.players[0].hand, p1_before)
        self.assertEqual(a.engine.state.players[1].hand, p2_before)

        a.action("NEXT", {
            "indices": [1],
            "expected_phase": "MULLIGAN_SECOND",
            "expected_active_player_key": "p2",
        })
        self.assertTrue(a.engine.state.players[1].mulligan_done)
        self.assertNotEqual(a.engine.state.players[1].hand, p2_before)
        self.assertEqual(a.engine.state.phase, Phase.MAIN_FIRST)

    def test_stale_mulligan_client_state_is_rejected(self):
        a = self.make_adapter()
        a.action("NEXT", {
            "indices": [],
            "expected_phase": "MULLIGAN_FIRST",
            "expected_active_player_key": "p1",
        })
        with self.assertRaisesRegex(ValueError, "画面のフェイズが更新前"):
            a.action("NEXT", {
                "indices": [],
                "expected_phase": "MULLIGAN_FIRST",
                "expected_active_player_key": "p1",
            })
        self.assertEqual(a.engine.state.phase, Phase.MULLIGAN_SECOND)
        self.assertFalse(a.engine.state.players[1].mulligan_done)

    def test_embedded_board_is_event_driven_and_preserves_transient_ui(self):
        html = _scoped_single_html("p1", upper=False, label="P1", color="#00f")
        self.assertNotIn("IS_PUBLIC_VIEW || document.body.classList.contains('dualPlayerView')", html)
        self.assertIn("llocg-dual-board-command", html)
        self.assertIn("keepSelection", html)
        self.assertIn("__dualPreserveLogScroll", html)
        self.assertNotIn("MutationObserver(schedulePin)", html)

    def test_player_play_is_committed_and_not_erased_by_poll(self):
        a = self.make_adapter(); self.enter_first_main(a)
        before_hand = list(a.runtime("p1").app.gs.hand)
        out = a.player_command("p1", "play", {"hand_idx": 0, "pos": "L"})
        self.assertTrue(out.get("dual_transaction_committed"))
        self.assertIsNotNone(a.runtime("p1").app.gs.stage["L"])
        a.state()
        self.assertEqual(len(a.runtime("p1").app.gs.hand), len(before_hand) - 1)

    def test_match_undo_restores_last_card_action(self):
        a = self.make_adapter(); self.enter_first_main(a)
        hand_before = list(a.runtime("p1").app.gs.hand)
        a.player_command("p1", "play", {"hand_idx": 0, "pos": "C"})
        a.action("UNDO", {})
        self.assertEqual(a.engine.state.phase, Phase.MAIN_FIRST)
        self.assertIsNone(a.runtime("p1").app.gs.stage["C"])
        self.assertEqual(a.runtime("p1").app.gs.hand, hand_before)

    def test_central_next_closes_confirmation_pending_before_phase(self):
        a = self.make_adapter(); self.enter_first_main(a)
        a.runtime("p1").app.gs.pending = [{"kind": "confirm", "message": "OK"}]
        out = a.action("NEXT", {})
        self.assertTrue(out.get("dialog_acknowledged"))
        self.assertEqual(a.engine.state.phase, Phase.MAIN_FIRST)
        self.assertFalse(a.runtime("p1").app.gs.pending)

    def test_central_next_resolves_single_auto_order_pending(self):
        a = self.make_adapter(); self.enter_first_main(a)
        a.runtime("p1").app.gs.pending = [{
            "kind": "auto_order",
            "text": "ライブ開始時効果が発生：解決するカードを選択",
            "options": ["A-001 ライブ開始時"],
            "queue": [{"label": "A-001 ライブ開始時", "source_cn": "A-001"}],
        }]
        out = a.action("NEXT", {})
        self.assertTrue(out.get("dialog_acknowledged"))
        self.assertEqual(a.engine.state.phase, Phase.MAIN_FIRST)
        self.assertFalse(a.runtime("p1").app.gs.pending)
        self.assertTrue(any("[NEXT AUTO_ORDER][P1]" in line for line in a.engine.state.log))

    def test_yell_confirmation_is_closed_by_central_next(self):
        a = self.make_adapter(); self.enter_performance(a)
        a.action("NEXT", {})
        a.action("NEXT", {})
        self.assertEqual(a.engine.state.phase, Phase.PERFORMANCE_FIRST)
        self.assertTrue(a.runtime("p1").app.gs.yell_reveal_notice)
        out = a.action("NEXT", {})
        self.assertTrue(out.get("dialog_acknowledged"))
        self.assertEqual(a.engine.state.phase, Phase.PERFORMANCE_FIRST)
        self.assertEqual(a.runtime("p1").app.gs.phase, "LIVE_ATTEMPT")

    def test_live_set_transaction_and_undo(self):
        a = self.make_adapter(); self.enter_first_live_set(a)
        rt = a.runtime("p1"); hand_before = list(rt.app.gs.hand); deck_before = list(rt.app.gs.deck)
        a.action("NEXT", {"indices": [0, 2]})
        self.assertEqual(a.engine.state.phase, Phase.LIVE_SET_SECOND)
        self.assertEqual(rt.app.gs.set_zone, [hand_before[0], hand_before[2]])
        self.assertEqual(len(rt.app.gs.deck), len(deck_before) - 2)
        a.action("UNDO", {})
        self.assertEqual(a.engine.state.phase, Phase.LIVE_SET_FIRST)
        self.assertEqual(rt.app.gs.set_zone, [])
        self.assertEqual(rt.app.gs.hand, hand_before)

    def test_zero_card_live_set_is_legal(self):
        a = self.make_adapter(); self.enter_first_live_set(a)
        a.action("NEXT", {"indices": []})
        self.assertEqual(a.engine.state.phase, Phase.LIVE_SET_SECOND)
        self.assertTrue(a.engine.state.players[0].live_set_committed)

    def test_one_player_success_placement_popup_is_removed_at_boundary(self):
        a = self.make_adapter(); self.enter_performance(a)
        self.finish_one_performance(a, Phase.PERFORMANCE_SECOND)
        p1 = a.runtime("p1").app
        self.assertEqual(p1.gs.success_zone, [])
        self.assertEqual(len(p1.gs.set_zone), 1)
        self.assertFalse(any(a._is_single_player_success_placement_pending(x) for x in p1.gs.pending))

    def test_performance_tail_pending_must_resolve_before_next_player(self):
        a = self.make_adapter(); self.enter_performance(a)
        a.runtime("p1").app.finish_performance_with_pending = True
        a.action("NEXT", {}); a.action("NEXT", {}); a.action("NEXT", {}); a.action("NEXT", {})
        self.assertEqual(a.engine.state.phase, Phase.PERFORMANCE_FIRST)
        self.assertTrue(a.runtime("p1").app.gs.pending)
        a.action("NEXT", {})
        self.assertFalse(a.runtime("p1").app.gs.pending)
        self.assertEqual(a.engine.state.phase, Phase.PERFORMANCE_SECOND)

    def test_non_live_set_card_completes_performance_without_attempt_result(self):
        a = self.make_adapter()
        self.enter_performance(a)
        p1 = a.runtime("p1").app
        p1.filter_all_set_cards_at_live_confirm = True
        set_before = list(p1.gs.set_zone)

        a.action("NEXT", {})

        self.assertEqual(a.engine.state.phase, Phase.PERFORMANCE_SECOND)
        self.assertEqual(p1.gs.set_zone, [])
        self.assertTrue(all(cn in p1.gs.green_room for cn in set_before))
        self.assertIs(p1._dual_live_attempt_succeeded, False)
        self.assertTrue(
            any("no_live_after_filter=1" in line for line in a.engine.state.log)
        )

    def test_higher_score_wins_moves_one_and_sets_next_first(self):
        a = self.make_adapter()
        self.enter_judgment(a)
        p1_cards = self.set_live_scores(a, 0, [3])
        self.set_live_scores(a, 1, [2])
        self.advance_to_final_score(a)
        self.calculate_and_confirm_result(a)
        self.assertEqual(a.engine.state.live_winners, [0])
        self.assertEqual(a.engine.state.judgment_step, "CLEANUP")
        self.assertEqual(a.runtime("p1").app.gs.success_zone, [p1_cards[0]])
        a.action("NEXT", {})
        self.assertEqual(a.engine.state.phase, Phase.TURN_END)
        self.assertEqual(a.engine.state.first_player_id, 0)
        self.assertEqual(a.runtime("p1").app.gs.set_zone, [])
        self.assertEqual(a.runtime("p2").app.gs.set_zone, [])

    def test_tie_both_win_success_zone_two_player_does_not_move(self):
        a = self.make_adapter()
        self.enter_judgment(a, p1_indices=(0, 1), p2_indices=(0,))
        self.set_live_scores(a, 0, [1, 1])
        self.set_live_scores(a, 1, [2])
        a.runtime("p1").app.gs.success_zone = ["A-010", "A-011"]
        a.runtime("p2").app.gs.success_zone = ["B-010", "B-011"]
        a._sync_all_views_to_core()
        self.advance_to_final_score(a)
        self.calculate_and_confirm_result(a)
        self.assertEqual(a.engine.state.live_winners, [0, 1])
        self.assertEqual(a.engine.state.success_move_queue, [])
        self.assertEqual(a.runtime("p1").app.gs.success_zone, ["A-010", "A-011"])
        self.assertEqual(a.runtime("p2").app.gs.success_zone, ["B-010", "B-011"])
        a.action("NEXT", {})
        self.assertEqual(a.engine.state.phase, Phase.TURN_END)
        self.assertEqual(a.engine.state.game_result, "")
        self.assertEqual(a.engine.state.first_player_id, 0)
        self.assertTrue(
            any("成功置き場2枚のため成功移動なし" in line for line in a.engine.state.log)
        )

    def test_tie_both_win_depends_on_success_zone_not_live_set_count(self):
        a = self.make_adapter()
        self.enter_judgment(a, p1_indices=(0, 1), p2_indices=(0,))
        p1_cards = self.set_live_scores(a, 0, [1, 1])
        p2_cards = self.set_live_scores(a, 1, [2])
        self.advance_to_final_score(a)
        self.calculate_and_confirm_result(a)
        prompt = a.engine.state.judgment_prompt
        self.assertEqual(a.engine.state.live_winners, [0, 1])
        self.assertEqual(prompt.get("kind"), "pick_success_live")
        self.assertEqual(prompt.get("player_id"), 0)
        selected = int(prompt["candidates"][1]["index"])
        a.action("NEXT", {"live_index": selected})
        self.assertEqual(a.runtime("p1").app.gs.success_zone, [p1_cards[selected]])
        self.assertEqual(a.runtime("p2").app.gs.success_zone, [p2_cards[0]])

    def test_multiple_live_winner_uses_dual_selection_prompt(self):
        a = self.make_adapter()
        self.enter_judgment(a, p1_indices=(0, 1), p2_indices=(0,))
        p1_cards = self.set_live_scores(a, 0, [3, 2])
        self.set_live_scores(a, 1, [1])
        self.advance_to_final_score(a)
        self.calculate_and_confirm_result(a)
        prompt = a.engine.state.judgment_prompt
        self.assertEqual(prompt.get("kind"), "pick_success_live")
        self.assertEqual(len(prompt.get("candidates", [])), 2)
        self.assertFalse(a.runtime("p1").app.gs.pending)
        selected = int(prompt["candidates"][1]["index"])
        selected_cn = p1_cards[selected]
        a.action("NEXT", {"live_index": selected})
        self.assertEqual(a.runtime("p1").app.gs.success_zone, [selected_cn])
        self.assertEqual(a.engine.state.judgment_step, "CLEANUP")

    def test_card_text_can_forbid_success_zone_move(self):
        a = self.make_adapter()
        self.enter_judgment(a)
        p1_cards = self.set_live_scores(a, 0, [3])
        self.set_live_scores(a, 1, [1])
        a.runtime("p1").app.cards_db[p1_cards[0]]["effect_text_raw"] = "このカードは成功ライブカード置き場に置くことができない。"
        self.advance_to_final_score(a)
        self.calculate_and_confirm_result(a)
        self.assertEqual(a.runtime("p1").app.gs.success_zone, [])
        self.assertEqual(a.engine.state.judgment_step, "CLEANUP")

    def test_canonical_db_text_can_forbid_success_zone_move(self):
        a = self.make_adapter()
        self.enter_judgment(a)
        rt = a.runtime("p1")
        rt.app.root = Path(".")
        rt.app.outdir = Path(".")
        rt.app.cards_db["PL!S-bp2-024"] = {
            "cardnumber": "PL!S-bp2-024",
            "cardname": "runtime placeholder",
            "score": 3,
            "effect_text_raw": "",
        }
        rt.app.gs.set_zone = ["PL!S-bp2-024"]
        rt.app.gs.resolve_zone = []
        rt.app.gs.last_attempt_result = "SUCCESS"
        a.engine.state.players[0].live_set = ["PL!S-bp2-024"]
        self.set_live_scores(a, 1, [1])
        a._detail_db_cache = None

        self.advance_to_final_score(a)
        self.calculate_and_confirm_result(a)

        self.assertTrue(a._success_move_blocked(rt, "PL!S-bp2-024"))
        self.assertEqual(rt.app.gs.success_zone, [])
        self.assertEqual(rt.app.gs.set_zone, ["PL!S-bp2-024"])
        self.assertEqual(a.engine.state.judgment_step, "CLEANUP")

    def test_cleanup_moves_remaining_live_and_yell_to_waiting_room(self):
        a = self.make_adapter()
        self.enter_judgment(a)
        self.set_live_scores(a, 0, [3])
        p2_cards = self.set_live_scores(a, 1, [1])
        p1_yell = list(a.runtime("p1").app.gs.resolve_zone)
        p2_yell = list(a.runtime("p2").app.gs.resolve_zone)
        self.advance_to_final_score(a); self.calculate_and_confirm_result(a); a.action("NEXT", {})
        self.assertTrue(all(cn in a.runtime("p1").app.gs.green_room for cn in p1_yell))
        self.assertTrue(all(cn in a.runtime("p2").app.gs.green_room for cn in p2_yell))
        self.assertIn(p2_cards[0], a.runtime("p2").app.gs.green_room)

    def test_judgment_undo_restores_score_move(self):
        a = self.make_adapter()
        self.enter_judgment(a)
        p1_cards = self.set_live_scores(a, 0, [3])
        self.set_live_scores(a, 1, [1])
        self.advance_to_final_score(a)
        self.calculate_and_confirm_result(a)
        self.assertEqual(a.runtime("p1").app.gs.success_zone, [p1_cards[0]])
        a.action("UNDO", {})
        self.assertEqual(a.engine.state.judgment_step, "RESULT_CONFIRM")
        self.assertEqual(a.runtime("p1").app.gs.success_zone, [])
        self.assertEqual(a.runtime("p1").app.gs.set_zone, p1_cards)


    def test_performance_never_executes_legacy_live_resolve_tail(self):
        a = self.make_adapter()
        self.enter_judgment(a)
        self.assertEqual(a.runtime("p1").app.live_resolve_calls, 0)
        self.assertEqual(a.runtime("p2").app.live_resolve_calls, 0)
        self.assertTrue(a.runtime("p1").app.gs.set_zone)
        self.assertTrue(a.runtime("p2").app.gs.set_zone)

    def test_legacy_success_store_prompt_is_blocked_not_acknowledged(self):
        a = self.make_adapter(); self.enter_performance(a)
        rt = a.runtime("p1")
        rt.app.gs.phase = "LIVE_RESOLVE"
        rt.app.gs.pending = [{"kind": "success_zone_choice", "message": "成功したライブを置くか"}]
        before_calls = rt.app.live_resolve_calls
        out = a.action("NEXT", {})
        self.assertTrue(out.get("legacy_success_boundary_blocked"))
        self.assertEqual(rt.app.live_resolve_calls, before_calls)
        self.assertFalse(rt.app.gs.pending)
        self.assertEqual(a.engine.state.phase, Phase.PERFORMANCE_SECOND)

    def test_result_is_visible_before_success_move(self):
        a = self.make_adapter(); self.enter_judgment(a)
        p1_cards = self.set_live_scores(a, 0, [3])
        self.set_live_scores(a, 1, [1])
        self.advance_to_final_score(a)
        a.action("NEXT", {})
        self.assertEqual(a.engine.state.judgment_step, "RESULT_CONFIRM")
        self.assertEqual(a.runtime("p1").app.gs.success_zone, [])
        self.assertIn("最終結果", a.state().get("judgment_message", ""))
        a.action("NEXT", {})
        self.assertEqual(a.runtime("p1").app.gs.success_zone, [p1_cards[0]])

    def test_direct_score_set_and_per_card_add_feed_dual_total(self):
        a = self.make_adapter()
        rt = a.runtime("p1")
        cn = "A-000"
        rt.app.gs.set_zone = [cn]
        rt.app.gs.last_attempt_result = "SUCCESS"
        rt.app._dual_live_attempt_succeeded = True
        rt.app.gs.last_attempt_score_set = {cn: 4}
        rt.app.gs.last_attempt_score_add = {cn: 2}
        score, source = a._calculate_live_score(rt)
        self.assertEqual(score, 6)
        self.assertIn("set=", source)
        self.assertIn("per_card_add=", source)

    def test_opponent_wait_notify_updates_real_opponent_stage_and_undo(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p2.cards_db["B-001"]["cost"] = 2
        p2.cards_db["B-002"]["cost"] = 9
        p2.gs.stage["C"] = FakeSlot("B-001", active=True)
        p2.gs.stage["R"] = FakeSlot("B-002", active=True)
        p1.gs.pending.append({
            "kind": "opponent_wait_notify",
            "source_cn": "A-SRC",
            "effect_text": "コスト4以下のメンバーを1人までウェイトにする",
            "options": ["0", "1"],
            "max_delta": 1,
        })
        out = a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "1"})
        self.assertTrue(out.get("dual_transaction_committed"))
        self.assertFalse(p2.gs.stage["C"].active)
        self.assertTrue(p2.gs.stage["R"].active)
        self.assertEqual(a.engine.state.players[1].stage["C"], "B-001")
        a.action("UNDO", {})
        self.assertTrue(p2.gs.stage["C"].active)
        self.assertTrue(p2.gs.stage["R"].active)

    def test_opponent_energy_ack_updates_real_opponent_energy_and_undo(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p2.gs.energy_active = 3
        p2.gs.energy_wait = 0
        p1.gs.pending.append({
            "kind": "message_ack",
            "label": "相手エネルギー確認",
            "text": "相手はエネルギーデッキからエネルギーカードを2枚ウェイト状態で置きます。",
            "options": ["ok"],
            "source_cn": "A-SRC",
        })
        out = a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "ok"})
        self.assertTrue(out.get("dual_transaction_committed"))
        self.assertEqual(p2.gs.energy_wait, 2)
        self.assertEqual(a.engine.state.players[1].energy_wait, 2)
        self.assertIn("[DUAL EFFECT][OPPONENT ENERGY WAIT]", "\n".join(p1.gs.log))
        a.action("UNDO", {})
        self.assertEqual(p2.gs.energy_wait, 0)
        self.assertEqual(a.engine.state.players[1].energy_wait, 0)

    def test_optional_opponent_draw_apply_updates_real_opponent_hand_and_undo(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p2.gs.deck = ["B-010", "B-011", "B-012"]
        p2.gs.hand = []
        p1.gs.pending.append({
            "kind": "confirm_effect",
            "text": "A-SRC[ライブ成功時] エネルギーカードを1枚ウェイト状態で置いてもよいです。置いた場合、相手はカードを2枚引きます。",
            "options": ["apply", "skip"],
            "after_effect_template": "",
            "ctx": {"source_cn": "A-SRC"},
            "source_cn": "A-SRC",
        })
        out = a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "apply"})
        self.assertTrue(out.get("dual_transaction_committed"))
        self.assertEqual(p2.gs.hand, ["B-010", "B-011"])
        self.assertEqual(p2.gs.deck, ["B-012"])
        self.assertEqual(a.engine.state.players[1].hand, ["B-010", "B-011"])
        self.assertIn("[DUAL EFFECT][OPPONENT DRAW]", "\n".join(p1.gs.log))
        a.action("UNDO", {})
        self.assertEqual(p2.gs.hand, [])
        self.assertEqual(p2.gs.deck, ["B-010", "B-011", "B-012"])

    def test_optional_opponent_draw_refreshes_when_opponent_deck_runs_empty(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p2.gs.deck = ["B-010"]
        p2.gs.green_room = ["B-020", "B-021", "B-022"]
        p2.gs.hand = []
        p1.gs.pending.append({
            "kind": "confirm_effect",
            "text": "A-SRC[ライブ成功時] 置いた場合、相手はカードを2枚引きます。",
            "options": ["apply", "skip"],
            "after_effect_template": "",
            "ctx": {"source_cn": "A-SRC"},
            "source_cn": "A-SRC",
        })
        out = a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "apply"})
        self.assertTrue(out.get("dual_transaction_committed"))
        self.assertEqual(len(p2.gs.hand), 2)
        self.assertEqual(p2.gs.hand[0], "B-010")
        self.assertTrue(getattr(p2.gs, "deck_refreshed_this_turn", False))
        self.assertEqual(p2.gs.green_room, [])
        self.assertEqual(len(p2.gs.deck), 2)
        self.assertIn("[REFRESH]", "\n".join(p2.gs.log))
        a.action("UNDO", {})
        self.assertEqual(p2.gs.hand, [])
        self.assertEqual(p2.gs.deck, ["B-010"])
        self.assertEqual(p2.gs.green_room, ["B-020", "B-021", "B-022"])

    def test_choose_opponent_green_live_bottom_updates_real_opponent_zones_and_undo(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p2.cards_db["B-010"]["card_type"] = "LIVE"
        p2.cards_db["B-011"]["card_type"] = "MEMBER"
        p2.cards_db["B-012"]["card_type"] = "LIVE"
        p2.gs.green_room = ["B-010", "B-011", "B-012"]
        p2.gs.deck = ["B-020"]
        p1.gs.pending.append({
            "kind": "choose_player_for_green_bottom",
            "text": "自分か相手を選ぶ。",
            "options": ["self", "opponent"],
            "want_kind": "LIVE",
            "remaining": 2,
            "allow_less": False,
            "source_cn": "A-SRC",
        })
        out = a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "opponent"})
        self.assertTrue(out.get("dual_transaction_committed"))
        self.assertEqual(p2.gs.green_room, ["B-011"])
        self.assertEqual(p2.gs.deck, ["B-020", "B-010", "B-012"])
        self.assertEqual(a.engine.state.players[1].waiting_room, ["B-011"])
        self.assertIn("[DUAL EFFECT][OPPONENT GREEN BOTTOM]", "\n".join(p1.gs.log))
        a.action("UNDO", {})
        self.assertEqual(p2.gs.green_room, ["B-010", "B-011", "B-012"])
        self.assertEqual(p2.gs.deck, ["B-020"])

    def test_manual_opponent_mass_member_bottom_updates_real_opponent_zones_and_undo(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p2.cards_db["B-010"]["card_type"] = "MEMBER"
        p2.cards_db["B-011"]["card_type"] = "LIVE"
        p2.cards_db["B-012"]["card_type"] = "MEMBER"
        p2.gs.green_room = ["B-010", "B-011", "B-012"]
        p2.gs.deck = []
        p1.gs.pending.append({
            "kind": "manual_opponent_mass_bottom_threshold",
            "text": "相手も自身の控え室にあるすべてのメンバーカードをシャッフルし、相手のデッキの下に置きます。",
            "options": ["threshold_met", "threshold_not_met"],
            "source_cn": "A-SRC",
        })
        out = a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "threshold_met"})
        self.assertTrue(out.get("dual_transaction_committed"))
        self.assertEqual(p2.gs.green_room, ["B-011"])
        self.assertCountEqual(p2.gs.deck, ["B-010", "B-012"])
        a.action("UNDO", {})
        self.assertEqual(p2.gs.green_room, ["B-010", "B-011", "B-012"])
        self.assertEqual(p2.gs.deck, [])

    def test_choose_opponent_top1_can_move_real_top_to_waiting_room_and_undo(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p2.gs.deck = ["B-010", "B-011"]
        p2.gs.green_room = []
        p1.gs.pending.append({
            "kind": "choose_player_for_deck_top_action",
            "text": "自分か相手を選ぶ。",
            "options": ["self", "opponent"],
            "action": "top1_optional_green",
            "k": 1,
            "source_cn": "A-SRC",
        })
        out = a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "opponent"})
        self.assertTrue(out.get("dual_transaction_committed"))
        self.assertEqual(p1.gs.pending[0]["kind"], "dual_opponent_top1_to_green_or_keep")
        self.assertEqual(p1.gs.pending[0]["display_cards"], ["B-010"])
        out = a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "green"})
        self.assertTrue(out.get("dual_transaction_committed"))
        self.assertEqual(p2.gs.deck, ["B-011"])
        self.assertEqual(p2.gs.green_room, ["B-010"])
        a.action("UNDO", {})
        self.assertEqual(p2.gs.deck, ["B-010", "B-011"])
        self.assertEqual(p2.gs.green_room, [])

    def test_choose_opponent_topk_reorders_real_top_and_moves_rest_to_waiting_room(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p2.gs.deck = ["B-010", "B-011", "B-012", "B-013"]
        p2.gs.green_room = []
        p1.gs.pending.append({
            "kind": "choose_player_for_deck_top_action",
            "text": "自分か相手を選ぶ。",
            "options": ["self", "opponent"],
            "action": "topk_reorder_keep_any",
            "k": 3,
            "source_cn": "A-SRC",
        })
        a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "opponent"})
        self.assertEqual(p1.gs.pending[0]["kind"], "dual_opponent_topk_reorder_keep_any")
        self.assertEqual(p1.gs.pending[0]["display_cards"], ["B-010", "B-011", "B-012"])
        a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "B-012,B-010"})
        self.assertEqual(p2.gs.deck, ["B-012", "B-010", "B-013"])
        self.assertEqual(p2.gs.green_room, ["B-011"])

    def test_opponent_optional_discard_creates_real_opponent_hand_choice_and_undo(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p2.gs.hand = ["B-010", "B-011"]
        p1.gs.pending.append({
            "kind": "opponent_optional_discard_hand_else_self_gain_icons",
            "text": "相手は手札を1枚控え室に置いてもよい。",
            "options": ["opponent_discard", "not_discard"],
            "source_cn": "A-SRC",
            "source_pos": "C",
            "discard_n": 1,
            "icons": "<(ブレード)>",
        })
        a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "opponent_discard"})
        self.assertEqual(p1.gs.pending[0]["kind"], "dual_opponent_discard_from_hand")
        out = a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "B-011"})
        self.assertTrue(out.get("dual_transaction_committed"))
        self.assertEqual(p2.gs.hand, ["B-010"])
        self.assertEqual(p2.gs.green_room, ["B-011"])
        a.action("UNDO", {})
        self.assertEqual(p2.gs.hand, ["B-010", "B-011"])
        self.assertEqual(p2.gs.green_room, [])

    def test_opponent_live_discard_choice_filters_live_cards(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p2.cards_db["B-010"]["card_type"] = "LIVE"
        p2.cards_db["B-011"]["card_type"] = "MEMBER"
        p2.gs.hand = ["B-010", "B-011"]
        p1.gs.pending.append({
            "kind": "confirm_effect",
            "text": "A-SRC[登場] 相手がライブカードを控え室に置かなかった場合、ライブ終了時までライブの合計スコアを+1します。置かなかったなら Apply、置いたなら Skip。",
            "options": ["apply", "skip"],
            "source_cn": "A-SRC",
        })
        a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "skip"})
        self.assertEqual(p1.gs.pending[0]["kind"], "dual_opponent_discard_from_hand")
        self.assertEqual(p1.gs.pending[0]["options"], ["B-010"])

    def test_opponent_random_reveal_uses_real_hand_and_draws_only_without_live(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p2.cards_db["B-010"]["card_type"] = "MEMBER"
        p2.gs.hand = ["B-010"]
        p1.gs.deck = ["A-020", "A-021"]
        p1.gs.hand = []
        p1.gs.pending.append({
            "kind": "confirm_effect",
            "text": "相手の手札を見ないで1枚公開し、その中にライブカードがない場合カードを1枚引きます。",
            "options": ["apply", "skip"],
            "source_cn": "A-SRC",
        })
        out = a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "apply"})
        self.assertTrue(out.get("dual_transaction_committed"))
        self.assertEqual(p1.gs.hand, ["A-020"])
        self.assertEqual(p1.gs.pending[0]["kind"], "show_revealed_cards_ack")
        self.assertEqual(p1.gs.pending[0]["display_cards"], ["B-010"])

    def test_favorite_answer_applies_opponent_draw_and_stage_blade(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p2.gs.deck = ["B-010"]
        p2.gs.hand = []
        p1.gs.pending.append({"kind": "favorite_icecream_answer", "source_cn": "A-SRC"})
        a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "あなた"})
        self.assertEqual(p2.gs.hand, ["B-010"])
        p1.gs.pending.append({"kind": "favorite_icecream_answer", "source_cn": "A-SRC"})
        p2.gs.stage["C"] = FakeSlot("B-011", active=True)
        a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "それ以外"})
        self.assertEqual(getattr(p2.gs.stage["C"], "temp_blade", 0), 1)

    def test_opponent_front_position_notice_creates_real_position_choice_and_undo(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p1.gs.stage["L"] = FakeSlot("A-SRC", active=True)
        p2.gs.stage["C"] = FakeSlot("B-010", active=True)
        p2.gs.stage["R"] = None
        p1.gs.pending.append({
            "kind": "effect_notice",
            "text": "相手ステージのメンバー1人をこのメンバーの正面にポジションチェンジします。",
            "options": ["ok"],
            "source_cn": "A-SRC",
        })
        a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "ok"})
        self.assertEqual(p1.gs.pending[0]["kind"], "dual_opponent_position_change")
        self.assertEqual(p1.gs.pending[0]["dest"], "R")
        a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "C"})
        self.assertIsNone(p2.gs.stage["C"])
        self.assertEqual(p2.gs.stage["R"].cardnumber, "B-010")
        a.action("UNDO", {})
        self.assertEqual(p2.gs.stage["C"].cardnumber, "B-010")
        self.assertIsNone(p2.gs.stage["R"])

    def test_both_center_position_notice_creates_opponent_center_choice(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p2.gs.stage["C"] = FakeSlot("B-010", active=True)
        p2.gs.stage["L"] = None
        p1.gs.pending.append({
            "kind": "choose_stage_member_to_position_change_source",
            "text": "自分のセンターにいるメンバーをポジションチェンジします。相手のセンターは手動で処理してください。",
            "options": ["C"],
            "source_cn": "A-SRC",
        })
        a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "C"})
        self.assertEqual(p1.gs.pending[0]["kind"], "dual_opponent_position_change")
        self.assertEqual(p1.gs.pending[0]["src_pos"], "C")
        a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "L"})
        self.assertEqual(p2.gs.stage["L"].cardnumber, "B-010")
        self.assertIsNone(p2.gs.stage["C"])

    def test_opponent_rotate_position_notice_updates_real_opponent_stage(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        p1 = a.runtime("p1").app
        p2 = a.runtime("p2").app
        p2.gs.stage["L"] = FakeSlot("B-L", active=True)
        p2.gs.stage["C"] = FakeSlot("B-C", active=True)
        p2.gs.stage["R"] = FakeSlot("B-R", active=True)
        p1.gs.pending.append({
            "kind": "effect_notice",
            "text": "自分のステージを C→L、L→R、R→C に移動しました。相手も同じ移動を手動で処理してください。",
            "options": ["ok"],
            "source_cn": "A-SRC",
        })
        a.player_command("p1", "resolve_pending", {"idx": 0, "choice": "ok"})
        self.assertEqual(p2.gs.stage["L"].cardnumber, "B-C")
        self.assertEqual(p2.gs.stage["R"].cardnumber, "B-L")
        self.assertEqual(p2.gs.stage["C"].cardnumber, "B-R")

    def test_legacy_success_placement_aliases_are_filtered(self):
        a = self.make_adapter()
        samples = [
            {"kind": "live_success_place"},
            {"kind": "success_live_place"},
            {"kind": "place_live", "message": "成功したライブを置きますか"},
        ]
        self.assertTrue(all(a._is_single_player_success_placement_pending(item) for item in samples))

    def test_tied_success_choices_follow_current_first_player_order(self):
        a = self.make_adapter()
        self.enter_judgment(a)
        self.set_live_scores(a, 0, [2])
        self.set_live_scores(a, 1, [2])
        a.engine.state.first_player_id = 1
        self.advance_to_final_score(a)
        self.calculate_and_confirm_result(a)
        self.assertEqual(a.engine.state.success_moved_player_ids, [1, 0])

    def test_draw_result_remains_as_simultaneous_three_success_safety(self):
        a = self.make_adapter()
        a.engine.state.players[0].success_zone = ["A-010", "A-011", "A-012"]
        a.engine.state.players[1].success_zone = ["B-010", "B-011", "B-012"]
        winner, result = a._game_result_after_success_moves()
        self.assertIsNone(winner)
        self.assertEqual(result, "DRAW")

    def test_third_success_winner_is_announced(self):
        a = self.make_adapter()
        self.enter_judgment(a)
        self.set_live_scores(a, 0, [3])
        self.set_live_scores(a, 1, [1])
        a.runtime("p1").app.gs.success_zone = ["A-010", "A-011"]
        a._sync_all_views_to_core()
        self.advance_to_final_score(a)
        self.calculate_and_confirm_result(a); a.action("NEXT", {})
        st = a.state()
        self.assertEqual(st["phase"], "GAME_OVER")
        self.assertEqual(st["winner_player_id"], 0)
        self.assertIn("プレイヤー1の勝利", st["game_over_message"])
        self.assertIn("対戦終了", st["phase_label"])

    def test_suspend_export_import_restores_branch_point(self):
        a = self.make_adapter()
        self.enter_first_main(a)
        saved_hand = list(a.runtime("p1").app.gs.hand)
        data = a.export_suspend_data("branch")
        self.assertEqual(data["format"], "llocg_dual_v2_suspend_state")
        self.assertEqual(data["label"], "branch")
        self.assertIn("snapshot_b64", data)
        a.player_command("p1", "play", {"hand_idx": 0, "pos": "C"})
        self.assertIsNotNone(a.runtime("p1").app.gs.stage["C"])
        restored = a.import_suspend_data(data)
        self.assertEqual(restored["phase"], "MAIN_FIRST")
        self.assertEqual(a.runtime("p1").app.gs.hand, saved_hand)
        self.assertIsNone(a.runtime("p1").app.gs.stage["C"])
        self.assertEqual(a.history, [])
        self.assertIn("[RESUME]", "\n".join(a.engine.state.log))
        a.player_command("p1", "play", {"hand_idx": 0, "pos": "L"})
        self.assertIsNotNone(a.runtime("p1").app.gs.stage["L"])

    def test_shell_html_has_suspend_resume_and_game_over_notice(self):
        html = dual_server._shell_html()
        self.assertIn("中断保存", html)
        self.assertIn("再開読込", html)
        self.assertIn("/suspend_state", html)
        self.assertIn("/resume_state", html)
        self.assertIn("gameOverNotice", html)
        self.assertIn("#divider{position:relative;display:grid", html)
        self.assertIn("grid-template-columns:minmax(150px,1fr) minmax(260px,1.35fr) minmax(390px,max-content)", html)
        self.assertIn("#phaseBanner{grid-column:2;grid-row:1", html)
        self.assertIn("#controls{grid-column:3;grid-row:1", html)
        self.assertIn("#requestStatus{grid-column:1;grid-row:1", html)
        self.assertNotIn("#controls{position:absolute", html)

    def test_scoped_html_reserves_label_width_from_topbar(self):
        html = _scoped_single_html("p1", upper=False, label="プレイヤー1（7QEC8）", color="#3355aa")
        self.assertIn("--dualLabelW:178px", html)
        self.assertIn("width:var(--dualLabelW)", html)
        self.assertIn("padding-left:calc(var(--dualLabelW) + 14px)", html)
        self.assertIn("text-overflow:ellipsis", html)

    def test_dual_image_helpers_find_back_energy_and_noimage_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            img_dir = root / "llocg_db_out_full" / "card_images"
            img_dir.mkdir(parents=True)
            back = img_dir / "back.png"
            energy = img_dir / "energy.png"
            noimage = img_dir / "NoImage.PNG"
            back.write_bytes(b"back")
            energy.write_bytes(b"energy")
            noimage.write_bytes(b"noimage")
            rt = SimpleNamespace(
                app=SimpleNamespace(
                    root=root,
                    outdir=root,
                    img=SimpleNamespace(find=lambda _cn: None),
                )
            )

            self.assertIn(back, _runtime_image_candidates(rt, "__BACK__"))
            self.assertIsNotNone(_first_existing_file(_runtime_image_candidates(rt, "__BACK__")))
            self.assertIn(energy, _runtime_image_candidates(rt, "__ENERGY__"))
            self.assertEqual(_first_existing_file(_runtime_image_candidates(rt, "__ENERGY__")), energy)
            self.assertEqual(_find_runtime_card_image(rt, "NO_SUCH_CARD_20260720").name, noimage.name)
            energy.unlink()
            self.assertIsNone(_first_existing_file(_runtime_image_candidates(rt, "__ENERGY__")))
            self.assertGreater(len(_transparent_png_bytes()), 0)

    def test_stale_failure_from_previous_turn_is_not_applied_at_live_start(self):
        a = self.make_adapter()
        p1 = a.runtime("p1").app
        p1.gs.last_attempt_result = "FAILURE"
        p1.gs.last_attempt_total_score = 99
        self.enter_performance(a)
        live_cards = list(p1.gs.set_zone)
        green_before = list(p1.gs.green_room)
        self.assertTrue(live_cards)

        a.action("NEXT", {})  # LIVE_CONFIRM -> LIVE_PERF

        self.assertEqual(p1.gs.set_zone, live_cards)
        self.assertEqual(p1.gs.green_room, green_before)
        self.assertEqual(p1.gs.last_attempt_result, "")
        self.assertIsNone(p1._dual_live_attempt_succeeded)
        self.assertIsNone(getattr(p1.gs, "last_attempt_total_score", None))

    def test_stale_failure_is_not_consumed_by_yell_confirmation(self):
        a = self.make_adapter()
        self.enter_performance(a)
        p1 = a.runtime("p1").app
        live_cards = list(p1.gs.set_zone)

        a.action("NEXT", {})  # LIVE_CONFIRM -> LIVE_PERF
        p1.gs.last_attempt_result = "FAILURE"  # stale/late mirror refresh
        a.action("NEXT", {})  # create YELL confirmation
        a.action("NEXT", {})  # close YELL confirmation -> LIVE_ATTEMPT

        self.assertEqual(p1.gs.phase, "LIVE_ATTEMPT")
        self.assertEqual(p1.gs.set_zone, live_cards)
        self.assertIsNone(p1._dual_live_attempt_succeeded)

        a.action("NEXT", {})  # real attempt overwrites result with SUCCESS
        self.assertIs(p1._dual_live_attempt_succeeded, True)
        self.assertEqual(p1.gs.set_zone, live_cards)

    def test_failed_live_is_kept_failed_and_scores_zero(self):
        a = self.make_adapter()
        self.enter_performance(a)
        p1 = a.runtime("p1").app
        failed_live = list(p1.gs.set_zone)
        p1.attempt_succeeds = False
        self.finish_one_performance(a, Phase.PERFORMANCE_SECOND)
        self.assertEqual(p1.gs.set_zone, [])
        self.assertTrue(all(cn in p1.gs.green_room for cn in failed_live))
        self.assertIs(p1._dual_live_attempt_succeeded, False)
        self.finish_one_performance(a, Phase.LIVE_JUDGMENT)
        self.set_live_scores(a, 1, [2])
        self.advance_to_final_score(a)
        a.action("NEXT", {})
        self.assertEqual(a.engine.state.live_scores[0], 0)
        self.assertEqual(a.engine.state.live_winners, [1])
        a.action("NEXT", {})
        self.assertEqual(p1.gs.success_zone, [])

    def test_attempt_summary_does_not_reopen_yell_and_success_effect_runs(self):
        a = self.make_adapter()
        self.enter_performance(a)
        p1 = a.runtime("p1").app
        p1.show_attempt_summary_notice = True
        p1.reopen_yell_if_live_start_reset = True
        p1.generate_success_effect_pending = True

        a.action("NEXT", {})  # LIVE_CONFIRM -> LIVE_PERF
        a.action("NEXT", {})  # YELL notice
        self.assertTrue(p1.gs.yell_reveal_notice)
        a.action("NEXT", {})  # acknowledge YELL
        self.assertFalse(p1.gs.yell_reveal_notice)
        a.action("NEXT", {})  # attempt -> heart/attempt summary notice
        self.assertTrue(p1.gs.attempt_summary_notice)
        a.action("NEXT", {})  # close summary -> dual boundary
        self.assertEqual(a.engine.state.phase, Phase.PERFORMANCE_SECOND)
        self.assertFalse(p1.gs.yell_reveal_notice)
        self.assertTrue(p1.gs.live_start_prompted)

        self.finish_one_performance(a, Phase.LIVE_JUDGMENT)
        a.action("NEXT", {})  # initial score
        a.action("NEXT", {})  # enter P1 success timing
        a.action("NEXT", {})  # generate P1 success-effect pending
        self.assertTrue(p1.gs.pending)
        self.assertFalse(p1.gs.yell_reveal_notice)
        a.action("NEXT", {})  # acknowledge/apply success effect
        self.assertTrue(p1.success_effect_applied)
        self.assertFalse(p1.gs.yell_reveal_notice)

    def test_explicit_failure_result_clears_live_even_if_legacy_tail_has_not(self):
        a = self.make_adapter()
        self.enter_performance(a)
        p1 = a.runtime("p1").app
        failed_live = list(p1.gs.set_zone)
        p1.attempt_succeeds = False
        p1.defer_failed_live_cleanup = True
        p1.show_attempt_summary_notice = True

        a.action("NEXT", {})  # LIVE_CONFIRM -> LIVE_PERF
        a.action("NEXT", {})  # YELL notice
        a.action("NEXT", {})  # acknowledge YELL -> LIVE_ATTEMPT
        a.action("NEXT", {})  # explicit FAILURE + attempt summary
        self.assertEqual(p1.gs.last_attempt_result, "FAILURE")
        self.assertEqual(p1.gs.set_zone, [])
        self.assertTrue(all(cn in p1.gs.green_room for cn in failed_live))
        self.assertIs(p1._dual_live_attempt_succeeded, False)
        score, source = a._calculate_live_score(a.runtime("p1"))
        self.assertEqual(score, 0)
        self.assertIn("attempt-failed", source)

    def test_acknowledged_yell_popup_is_hidden_for_non_active_player_during_judgment(self):
        a = self.make_adapter()
        self.enter_performance(a)
        p1 = a.runtime("p1").app
        a.action("NEXT", {})
        a.action("NEXT", {})
        self.assertTrue(p1.gs.yell_reveal_notice)
        a.action("NEXT", {})
        self.assertTrue(p1._dual_yell_notice_acknowledged)
        p1.gs.yell_popup_open = True
        p1.gs.pending = [{"kind": "yell_reveal_confirm", "message": "エール公開カード確認"}]
        p1.state_only_yell_popup = True
        a.engine.state.phase = Phase.LIVE_JUDGMENT
        a.engine.state.judgment_step = "SUCCESS_SECOND"
        a.engine.state.judgment_active_player_id = 1

        state = a.player_state("p1", "private")
        self.assertFalse(state.get("state_yell_popup_open"))
        self.assertFalse(state.get("yell_popup_open", False))
        self.assertFalse(any(a._is_yell_confirmation_pending(x) for x in state.get("pending", [])))
        self.assertFalse(getattr(p1.gs, "yell_popup_open", False))
        self.assertFalse(any(a._is_yell_confirmation_pending(x) for x in p1.gs.pending))

    def test_confirm_button_persists_yell_ack_and_returns_sanitized_state(self):
        a = self.make_adapter()
        self.enter_performance(a)
        p1 = a.runtime("p1").app
        a.action("NEXT", {})  # LIVE_CONFIRM -> LIVE_PERF
        a.action("NEXT", {})  # create YELL notice
        p1.gs.yell_revealed_cards = ["A-YELL-001"]
        self.assertTrue(p1.gs.yell_reveal_notice)

        out = a.player_command("p1", "ack_yell_reveal", {})
        self.assertTrue(out.get("dual_presentation_acknowledged"))
        self.assertFalse(out.get("yell_reveal_notice"))
        self.assertFalse(p1.gs.yell_reveal_notice)
        self.assertTrue(p1._dual_yell_notice_acknowledged)
        self.assertTrue(p1.gs.yell_reveal_acknowledged_this_live)
        self.assertEqual(p1.gs.yell_revealed_cards, ["A-YELL-001"])

        # A success-effect redraw must not resurrect the acknowledged popup.
        p1.gs.yell_reveal_notice = True
        p1.yell_popup_open = True
        p1.state_only_yell_popup = True
        state = a.player_state("p1", "private")
        self.assertFalse(state.get("yell_reveal_notice"))
        self.assertFalse(state.get("state_yell_popup_open"))
        self.assertEqual(state.get("yell_revealed_cards"), ["A-YELL-001"])

    def test_inactive_player_can_close_stale_yell_popup_during_other_success_timing(self):
        a = self.make_adapter()
        self.enter_performance(a)
        p1 = a.runtime("p1").app
        a.action("NEXT", {})
        a.action("NEXT", {})
        a.action("NEXT", {})  # central acknowledgement
        self.assertTrue(p1._dual_yell_notice_acknowledged)

        a.engine.state.phase = Phase.LIVE_JUDGMENT
        a.engine.state.judgment_active_player_id = 1
        p1.gs.yell_reveal_notice = True
        p1.yell_popup_open = True
        p1.state_only_yell_popup = True
        out = a.player_command("p1", "ack_yell_reveal", {})
        self.assertTrue(out.get("dual_presentation_acknowledged"))
        self.assertFalse(out.get("yell_reveal_notice"))
        self.assertFalse(out.get("state_yell_popup_open"))
        self.assertNotIn("dual_command_error", out)
        self.assertTrue(p1.gs.yell_reveal_acknowledged_this_live)

    def test_card_detail_uses_tokv1_raw_record_effect_text(self):
        a = self.make_adapter()
        rt = a.runtime("p1")
        cn = next(iter(rt.app.cards_db))
        rt.app.cards_db[cn] = {
            "cardnumber": cn,
            "cardname": "詳細テスト",
            "card_type_norm": "MEMBER",
            "group": "テストグループ",
            "cost": 3,
            "blade": 2,
            "effect_text_norm": "<登場> カードを1枚引く。",
        }
        payload = a.card_info_payload("p1", cn)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["name"], "詳細テスト")
        self.assertEqual(payload["type"], "MEMBER")
        self.assertEqual(payload["effect"], "<登場> カードを1枚引く。")
        self.assertEqual(payload["abilities"], ["<登場> カードを1枚引く。"])

    def test_card_detail_flattens_compiled_ability_list(self):
        a = self.make_adapter()
        rt = a.runtime("p1")
        cn = next(iter(rt.app.cards_db))
        rt.app.cards_db[cn] = {
            "cardnumber": cn,
            "cardname": "複数能力テスト",
            "abilities": [
                {"raw_text": "<常時> ブレードを得る。"},
                {"text": "<ライブ成功時> カードを1枚引く。"},
            ],
        }
        payload = a.card_info_payload("p1", cn)
        self.assertIn("<常時> ブレードを得る。", payload["effect"])
        self.assertIn("<ライブ成功時> カードを1枚引く。", payload["effect"])
        self.assertTrue(payload["abilities"])

    def test_player_state_persists_ack_marker_for_dom_derived_yell_dialog(self):
        a = self.make_adapter()
        p1 = a.runtime("p1").app
        a.engine.state.phase = Phase.LIVE_JUDGMENT
        a.engine.state.judgment_active_player_id = 0
        p1.gs.resolve_zone = ["A-YELL-001"]
        p1.gs.yell_reveal_notice = True
        a.player_command("p1", "ack_yell_reveal", {})

        # Even if the legacy renderer derives a dialog from LIVE_RESOLVE +
        # resolve_zone rather than a popup flag, every later state payload keeps
        # a client-side close marker for the same performance epoch.
        p1.gs.phase = "LIVE_RESOLVE"
        p1.gs.yell_reveal_notice = True
        state = a.player_state("p1", "private")
        self.assertTrue(state.get("dual_yell_notice_acknowledged"))
        self.assertTrue(state.get("dual_force_close_yell_notice"))
        self.assertFalse(state.get("yell_reveal_notice"))
        self.assertEqual(state.get("resolve_zone"), ["A-YELL-001"])

    def test_player_state_decorates_after_view_filter_and_scrubs_rebuilt_modal(self):
        a = self.make_adapter()
        p1 = a.runtime("p1").app
        a.engine.state.phase = Phase.LIVE_JUDGMENT
        a.engine.state.judgment_active_player_id = 0
        p1.gs.yell_reveal_notice = True
        p1.gs.resolve_zone = ["A-YELL-001"]
        a.player_command("p1", "ack_yell_reveal", {})

        original = dual_server.make_view_state
        def rebuilding_view(state, mode):
            # Reproduce a view adapter that drops unknown dual_* keys and
            # recreates a generic modal from legacy YELL data.
            out = {k: v for k, v in state.items() if not str(k).startswith("dual_")}
            out["modal"] = {
                "title": "エール内容確認",
                "message": "公開カードを確認してください",
                "open": True,
            }
            out["yell_reveal_notice"] = True
            return out
        dual_server.make_view_state = rebuilding_view
        try:
            state = a.player_state("p1", "private")
        finally:
            dual_server.make_view_state = original

        self.assertTrue(state.get("dual_yell_notice_acknowledged"))
        self.assertTrue(state.get("dual_force_close_yell_notice"))
        self.assertFalse(state.get("yell_reveal_notice"))
        self.assertEqual(state.get("modal"), {})
        self.assertIn("dual_card_effects", state)

    def test_card_detail_loads_canonical_tokv1_csv(self):
        a = self.make_adapter()
        rt = a.runtime("p1")
        cn = next(iter(rt.app.cards_db))
        rt.app.cards_db[cn] = {"cardnumber": cn, "cardname": "runtime only", "effect_text_raw": ""}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dbdir = root / "llocg_db_out_full"
            dbdir.mkdir(parents=True)
            (dbdir / "cards_min_tokv1.csv").write_text(
                "cardnumber,cardname,card_type_norm,effect_text_raw\n"
                f'{cn},canonical csv,MEMBER,"<登場> カードを2枚引く。"\n',
                encoding="utf-8",
            )
            rt.app.root = root
            a._detail_db_cache = None
            payload = a.card_info_payload("p1", cn)
            state = a.player_state("p1", "private")
        self.assertEqual(payload["name"], "canonical csv")
        self.assertEqual(payload["effect"], "<登場> カードを2枚引く。")
        self.assertEqual(state["dual_card_effects"][cn], "<登場> カードを2枚引く。")

    def test_card_detail_loads_canonical_tokv1_when_runtime_record_has_no_text(self):
        a = self.make_adapter()
        rt = a.runtime("p1")
        cn = next(iter(rt.app.cards_db))
        rt.app.cards_db[cn] = {"cardnumber": cn, "cardname": "runtime only", "effect_text_raw": ""}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dbdir = root / "llocg_db_out_full"
            dbdir.mkdir(parents=True)
            (dbdir / "cards_min_tokv1.json").write_text(json.dumps([{
                "cardnumber": cn,
                "cardname": "canonical",
                "card_type_norm": "MEMBER",
                "effect_text_raw": "<登場> カードを1枚引く。",
            }], ensure_ascii=False), encoding="utf-8")
            rt.app.root = root
            a._detail_db_cache = None
            payload = a.card_info_payload("p1", cn)
        self.assertEqual(payload["name"], "canonical")
        self.assertEqual(payload["effect"], "<登場> カードを1枚引く。")

    def test_card_text_formats_compiled_clauses(self):
        value = {
            "abilities": [{
                "ability_type": "自動",
                "trigger": "ライブ成功時",
                "clauses": [{"raw": "カードを2枚引き、手札を1枚控え室に置く。"}],
            }]
        }
        text = LegacyUIAdapter._card_text_value(value)
        self.assertIn("<自動><ライブ成功時>", text)
        self.assertIn("カードを2枚引き", text)

    def test_turn_end_next_starts_next_turn(self):
        a = self.make_adapter()
        self.enter_judgment(a)
        self.set_live_scores(a, 0, [3])
        self.set_live_scores(a, 1, [1])
        self.advance_to_final_score(a)
        self.calculate_and_confirm_result(a); a.action("NEXT", {})
        self.assertEqual(a.engine.state.phase, Phase.TURN_END)
        a.action("NEXT", {})
        self.assertEqual(a.engine.state.turn, 2)
        self.assertEqual(a.engine.state.phase, Phase.MAIN_FIRST)


class JudgmentYellAckRegressionTests(unittest.TestCase):
    @staticmethod
    def make_adapter():
        engine = DualMatchEngine(deck("A"), deck("B"), "A", "B", seed=4)
        p1 = PlayerViewRuntime("p1", 0, "P1", "#00f", FakeApp("A", 4))
        p2 = PlayerViewRuntime("p2", 1, "P2", "#f60", FakeApp("B", 5))
        return LegacyUIAdapter(engine, p1, p2)

    def test_active_judgment_yell_ack_bypasses_legacy_fallback_and_forces_client_close(self):
        a = self.make_adapter()
        p2 = a.runtime("p2").app
        a.engine.state.phase = Phase.LIVE_JUDGMENT
        a.engine.state.judgment_active_player_id = 1
        p2.gs.phase = "LIVE_RESOLVE"
        p2.gs.yell_reveal_notice = True
        p2.state_only_yell_popup = True
        out = a.player_command("p2", "ack_yell_reveal", {})

        self.assertNotIn("[ACK] yell reveal fallback acknowledged", p2.gs.log)
        self.assertTrue(out.get("dual_force_close_yell_notice"))
        self.assertTrue(out.get("dual_presentation_acknowledged"))
        self.assertFalse(out.get("yell_reveal_notice"))
        self.assertFalse(out.get("state_yell_popup_open"))
        self.assertTrue(p2._dual_yell_notice_acknowledged)

    def test_embedded_html_removes_legacy_poll_and_has_ack_response_bridge(self):
        html = _scoped_single_html("p2", upper=True, label="P2", color="#f60")
        self.assertNotIn("setInterval(()=>{ refreshStateFromServer({force:false}); }, 250);", html)
        self.assertIn("dual_force_close_yell_notice", html)
        self.assertIn("window.dualApplyCommandState", html)
        self.assertIn("commandName==='ack_yell_reveal'", html)
        self.assertIn("dual_yell_notice_acknowledged", html)
        self.assertIn("ack_yell_reveal", html)
        self.assertNotIn("dualRepairCardDetail", html)
        self.assertNotIn("MutationObserver(queue)", html)
        self.assertNotIn("dualCardEffectText", html)
        self.assertIn("/p2/cardinfo?cn=", html)
        self.assertNotIn("const cardInfoUrl='/cardinfo?cn=", html)
        # The previous DOM workaround could hide the entire board root and
        # leave the iframe black.  The new client repair never hides dialogs.
        self.assertNotIn("dualHideYellConfirmationDom", html)
        self.assertNotIn("data-dual-yell-hidden','1'", html)
        self.assertNotIn("style.setProperty('display','none'", html)


if __name__ == "__main__":
    unittest.main()
