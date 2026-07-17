from __future__ import annotations

import random
import sys
import types
import unittest
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
    server_stub.HTML = "<html><head></head><body><script>function clearSel(){ selHand = []; updateTop(); render(); }\n  if(IS_PUBLIC_VIEW){\n    setInterval(()=>{ refreshStateFromServer({force:false}); }, 250);\n    window.addEventListener('storage', (ev)=>{</script></body></html>"
    views_stub.make_view_state = lambda state, mode: state
    db_stub._get_card = lambda db, cn: db.get(cn) if isinstance(db, dict) else None
    sys.modules["llocg_ui"] = pkg
    sys.modules["llocg_ui.server"] = server_stub
    sys.modules["llocg_ui.views"] = views_stub
    sys.modules["llocg_ui.db"] = db_stub

from llocg_dual_v2.core import DualMatchEngine, Phase
from llocg_dual_v2.server import LegacyUIAdapter, PlayerViewRuntime, _scoped_single_html

BUILD_TAG = "llocg_dual_v2_judgment_yell_ack_client_close_20260717s"


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

    def test_tie_both_win_but_two_live_player_does_not_move(self):
        a = self.make_adapter()
        self.enter_judgment(a, p1_indices=(0, 1), p2_indices=(0,))
        self.set_live_scores(a, 0, [1, 1])
        p2_cards = self.set_live_scores(a, 1, [2])
        self.advance_to_final_score(a)
        self.calculate_and_confirm_result(a)
        self.assertEqual(a.engine.state.live_winners, [0, 1])
        self.assertEqual(a.runtime("p1").app.gs.success_zone, [])
        self.assertEqual(a.runtime("p2").app.gs.success_zone, [p2_cards[0]])
        a.action("NEXT", {})
        self.assertEqual(a.engine.state.first_player_id, 1)

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

    def test_simultaneous_third_success_is_draw(self):
        a = self.make_adapter()
        self.enter_judgment(a)
        self.set_live_scores(a, 0, [2])
        self.set_live_scores(a, 1, [2])
        a.runtime("p1").app.gs.success_zone = ["A-010", "A-011"]
        a.runtime("p2").app.gs.success_zone = ["B-010", "B-011"]
        a._sync_all_views_to_core()
        self.advance_to_final_score(a)
        self.calculate_and_confirm_result(a); a.action("NEXT", {})
        self.assertEqual(a.engine.state.phase, Phase.GAME_OVER)
        self.assertEqual(a.engine.state.game_result, "DRAW")
        self.assertIsNone(a.engine.state.winner_player_id)

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


if __name__ == "__main__":
    unittest.main()
