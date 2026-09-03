from __future__ import annotations
import random
import unittest
from llocg_dual_v2.core import DualMatchEngine, Phase

BUILD_TAG = "llocg_dual_v2_random_first_cpu_match_20260828a"


def deck(prefix: str):
    return [f"{prefix}-{i:03d}" for i in range(60)]


class RuleCoreTests(unittest.TestCase):
    def test_first_player_id_can_start_with_player_two(self):
        e = DualMatchEngine(deck('A'), deck('B'), 'A', 'B', seed=3, first_player_id=1)
        self.assertEqual(e.state.first_player_id, 1)
        self.assertEqual(e.active_player_id(), 1)
        e.mulligan(1, [])
        self.assertEqual(e.state.phase, Phase.MULLIGAN_SECOND)
        self.assertEqual(e.active_player_id(), 0)

    def test_mulligan_then_automatic_first_normal_setup(self):
        e = DualMatchEngine(deck('A'), deck('B'), 'A', 'B', seed=3)
        e.mulligan(0, [0, 2])
        self.assertEqual(len(e.state.players[0].hand), 6)
        self.assertEqual(e.state.phase, Phase.MULLIGAN_SECOND)

        e.mulligan(1, [])
        # ACTIVE / ENERGY / DRAW are mandatory, no-choice steps and must stop at MAIN.
        self.assertEqual(e.state.phase, Phase.MAIN_FIRST)
        self.assertEqual(len(e.state.players[0].hand), 7)
        self.assertEqual(len(e.state.players[1].hand), 6)
        self.assertEqual(e.state.players[0].energy_active, 4)
        self.assertEqual(e.state.players[1].energy_active, 3)

    def test_main_end_autoruns_second_players_mandatory_steps(self):
        e = DualMatchEngine(deck('A'), deck('B'), 'A', 'B', seed=7)
        e.mulligan(0, [])
        e.mulligan(1, [])
        self.assertEqual(e.state.phase, Phase.MAIN_FIRST)
        e.advance()
        self.assertEqual(e.state.phase, Phase.MAIN_SECOND)
        self.assertEqual(len(e.state.players[1].hand), 7)
        self.assertEqual(e.state.players[1].energy_active, 4)

    def test_action_level_undo_includes_automatic_steps(self):
        e = DualMatchEngine(deck('A'), deck('B'), 'A', 'B', seed=9)
        e.mulligan(0, [])
        before_second = e.to_dict()
        e.mulligan(1, [])
        self.assertEqual(e.state.phase, Phase.MAIN_FIRST)
        self.assertTrue(e.undo())
        self.assertEqual(e.to_dict()['phase'], before_second['phase'])
        self.assertEqual(e.state.players[0].energy_active, 0)
        self.assertEqual(e.state.players[1].energy_active, 0)
        self.assertEqual(len(e.state.players[0].hand), 6)
        self.assertEqual(len(e.state.players[1].hand), 6)

    def test_100_random_mulligans(self):
        r = random.Random(11)
        for seed in range(100):
            e = DualMatchEngine(deck('A'), deck('B'), 'A', 'B', seed=seed)
            for pid in (0, 1):
                picks = [i for i in range(6) if r.random() < .45]
                e.mulligan(pid, picks)
            self.assertEqual(e.state.phase, Phase.MAIN_FIRST)
            for p in e.state.players:
                self.assertEqual(p.energy_active + p.energy_wait + p.energy_deck_remaining, 12)
                self.assertEqual(len(p.hand) + len(p.main_deck), 60)

    def test_live_set_phase_cannot_advance_before_legacy_commit(self):
        e = DualMatchEngine(deck('A'), deck('B'), 'A', 'B', seed=13)
        e.mulligan(0, [])
        e.mulligan(1, [])
        e.advance()
        e.advance()
        self.assertEqual(e.state.phase, Phase.LIVE_SET_FIRST)
        with self.assertRaises(ValueError):
            e.advance()
        e.state.players[e.active_player_id()].live_set_committed = True
        e.advance()
        self.assertEqual(e.state.phase, Phase.LIVE_SET_SECOND)

    def test_performance_completion_requires_explicit_bridge_commit(self):
        e = DualMatchEngine(deck('A'), deck('B'), 'A', 'B', seed=15)
        e.mulligan(0, [])
        e.mulligan(1, [])
        e.advance()
        e.advance()
        e.state.players[e.active_player_id()].live_set_committed = True
        e.advance()
        e.state.players[e.active_player_id()].live_set_committed = True
        e.advance()
        self.assertEqual(e.state.phase, Phase.PERFORMANCE_FIRST)
        with self.assertRaises(ValueError):
            e.advance()
        self.assertEqual(e.state.phase, Phase.PERFORMANCE_FIRST)
        e.complete_performance(e.active_player_id())
        self.assertEqual(e.state.phase, Phase.PERFORMANCE_SECOND)
        e.complete_performance(e.active_player_id())
        self.assertEqual(e.state.phase, Phase.LIVE_JUDGMENT)


if __name__ == '__main__':
    unittest.main()
