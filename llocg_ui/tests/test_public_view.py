# -*- coding: utf-8 -*-
from __future__ import annotations

import unittest

from llocg_ui.views import make_view_state


class PublicViewStateTests(unittest.TestCase):
    def _state(self, **overrides):
        state = {
            "phase": "MAIN",
            "turn": 1,
            "hand": ["PL!HAND-bp1-001", "PL!HAND-bp1-002"],
            "deck": ["PL!DECK-bp1-001", "PL!DECK-bp1-002", "PL!DECK-bp1-003"],
            "green_room": ["PL!GREEN-bp1-001"],
            "set_zone": ["PL!SET-bp1-001", "PL!SET-bp1-002"],
            "resolve_zone": ["PL!RESOLVE-bp1-001"],
            "success_zone": ["PL!SUCCESS-bp1-001"],
            "stage": {
                "L": {"cardnumber": "PL!STAGE-bp1-001"},
                "C": None,
                "R": {"cardnumber": "PL!STAGE-bp1-002"},
            },
            "stage_detail": {},
            "set_zone_score_rows": [
                {"cardnumber": "PL!SET-bp1-001", "score": 10},
                {"cardnumber": "PL!SET-bp1-002", "score": 20},
            ],
            "pending": [
                {
                    "kind": "choose_from_topk",
                    "text": "PL!HAND-bp1-001 を含む候補から選ぶ",
                    "candidates": ["PL!DECK-bp1-001", "PL!DECK-bp1-002"],
                }
            ],
            "public_reveal_events": [],
            "public_hand_revealed_cards": [],
            "cn2name": {
                "PL!HAND-bp1-001": "Hidden hand",
                "PL!DECK-bp1-001": "Hidden deck",
                "PL!GREEN-bp1-001": "Public green",
                "PL!SET-bp1-001": "Face-down live",
                "PL!STAGE-bp1-001": "Public stage",
                "PL!RESOLVE-bp1-001": "Public resolve",
                "PL!SUCCESS-bp1-001": "Public success",
            },
            "cn2label": {},
            "cn2type": {},
            "cn2is_live": {},
            "cn2yell_hearts": {},
            "cn2yell_draw_icons": {},
            "cn2yell_score_icons": {},
            "cn2group": {},
            "cn2unit": {},
            "cn2cost": {},
            "cn2score": {},
            "debug": True,
            "root": "/private/path",
        }
        state.update(overrides)
        return state

    def test_public_view_redacts_private_zones_but_preserves_public_board(self):
        public = make_view_state(self._state(), "public")

        self.assertEqual(public["hand_count"], 2)
        self.assertEqual(public["deck_count"], 3)
        self.assertEqual(public["hand"], [])
        self.assertEqual(public["deck"], [])
        self.assertEqual(public["green_room"], ["PL!GREEN-bp1-001"])
        self.assertEqual(public["resolve_zone"], ["PL!RESOLVE-bp1-001"])
        self.assertEqual(public["success_zone"], ["PL!SUCCESS-bp1-001"])
        self.assertEqual(public["stage"]["L"]["cardnumber"], "PL!STAGE-bp1-001")
        self.assertEqual(public["set_zone"], ["__BACK__", "__BACK__"])
        self.assertEqual(public["set_zone_score_rows"], [None, None])
        self.assertNotIn("PL!HAND-bp1-001", public["cn2name"])
        self.assertNotIn("PL!DECK-bp1-001", public["cn2name"])
        self.assertNotIn("PL!SET-bp1-001", public["cn2name"])
        self.assertIn("PL!GREEN-bp1-001", public["cn2name"])
        self.assertIn("PL!STAGE-bp1-001", public["cn2name"])
        self.assertFalse(public["debug"])
        self.assertNotIn("root", public)

    def test_live_set_becomes_public_at_performance_timing(self):
        public = make_view_state(self._state(phase="LIVE_PERF"), "public")

        self.assertEqual(public["set_zone"], ["PL!SET-bp1-001", "PL!SET-bp1-002"])
        self.assertEqual(public["set_zone_score_rows"][0]["cardnumber"], "PL!SET-bp1-001")
        self.assertIn("PL!SET-bp1-001", public["cn2name"])

    def test_live_confirm_after_prompt_is_public_but_before_prompt_is_back(self):
        face_down = make_view_state(
            self._state(phase="LIVE_CONFIRM", live_start_prompted=False),
            "public",
        )
        face_up = make_view_state(
            self._state(phase="LIVE_CONFIRM", live_start_prompted=True),
            "public",
        )

        self.assertEqual(face_down["set_zone"], ["__BACK__", "__BACK__"])
        self.assertEqual(face_down["set_zone_score_rows"], [None, None])
        self.assertEqual(face_up["set_zone"], ["PL!SET-bp1-001", "PL!SET-bp1-002"])
        self.assertEqual(face_up["set_zone_score_rows"][1]["cardnumber"], "PL!SET-bp1-002")

    def test_pending_private_card_numbers_are_replaced_with_back_markers(self):
        public = make_view_state(self._state(), "public")
        pending = public["pending"][0]

        self.assertEqual(pending["candidates"], ["__BACK__", "__BACK__"])
        self.assertIn("非公開カード", pending["text"])
        self.assertNotIn("PL!DECK-bp1-001", str(pending))

    def test_pending_private_values_and_dict_keys_are_replaced_with_back_markers(self):
        public = make_view_state(
            self._state(
                pending=[
                    {
                        "kind": "discard_from_hand",
                        "source": "PL!HAND-bp1-001",
                        "choices_by_card": {
                            "PL!HAND-bp1-001": {"label": "PL!HAND-bp1-001"},
                            "PL!HAND-bp1-002": {"label": "PL!HAND-bp1-002"},
                        },
                        "options": ["PL!HAND-bp1-001", "PL!HAND-bp1-002"],
                    }
                ],
            ),
            "public",
        )
        pending = public["pending"][0]

        self.assertEqual(pending["source"], "__BACK__")
        self.assertEqual(pending["options"], ["__BACK__", "__BACK__"])
        self.assertEqual(set(pending["choices_by_card"].keys()), {"__BACK__"})
        self.assertNotIn("PL!HAND-bp1-001", str(pending))
        self.assertNotIn("PL!HAND-bp1-002", str(pending))

    def test_public_reveal_ack_cards_are_not_replaced_with_back_markers(self):
        public = make_view_state(
            self._state(
                pending=[
                    {
                        "kind": "show_revealed_cards_ack",
                        "display_cards": ["PL!DECK-bp1-001", "PL!DECK-bp1-002"],
                        "candidates": ["PL!DECK-bp1-001"],
                        "text": "PL!DECK-bp1-001 と PL!DECK-bp1-002 を公開",
                    }
                ],
                cn2name={
                    "PL!DECK-bp1-001": "Revealed deck one",
                    "PL!DECK-bp1-002": "Revealed deck two",
                },
            ),
            "public",
        )
        pending = public["pending"][0]

        self.assertEqual(pending["display_cards"], ["PL!DECK-bp1-001", "PL!DECK-bp1-002"])
        self.assertEqual(pending["candidates"], ["PL!DECK-bp1-001"])
        self.assertIn("PL!DECK-bp1-001", pending["text"])
        self.assertIn("PL!DECK-bp1-001", public["cn2name"])
        self.assertIn("PL!DECK-bp1-002", public["cn2name"])

    def test_public_reveal_events_and_refresh_notices_preserve_only_listed_cards(self):
        public = make_view_state(
            self._state(
                public_reveal_events=[
                    {
                        "kind": "public_reveal_event",
                        "display_cards": ["PL!DECK-bp1-001"],
                        "text": "公開イベント",
                    }
                ],
                refresh_notices=[
                    {
                        "returned_live_cards": [
                            {"cardnumber": "PL!DECK-bp1-002"},
                        ],
                    }
                ],
                cn2name={
                    "PL!DECK-bp1-001": "Revealed event card",
                    "PL!DECK-bp1-002": "Refresh notice card",
                    "PL!DECK-bp1-003": "Hidden deck card",
                },
            ),
            "public",
        )

        self.assertEqual(public["public_reveal_events"][0]["display_cards"], ["PL!DECK-bp1-001"])
        self.assertIn("PL!DECK-bp1-001", public["cn2name"])
        self.assertIn("PL!DECK-bp1-002", public["cn2name"])
        self.assertNotIn("PL!DECK-bp1-003", public["cn2name"])

    def test_revealed_hand_cards_remain_public_until_the_legal_window_closes(self):
        public = make_view_state(
            self._state(
                public_hand_revealed_cards=["PL!HAND-bp1-001"],
                cn2name={
                    "PL!HAND-bp1-001": "Revealed hand",
                    "PL!HAND-bp1-002": "Hidden hand",
                },
            ),
            "public",
        )

        self.assertEqual(public["hand"], [])
        self.assertEqual(public["hand_count"], 2)
        self.assertEqual(public["public_hand_revealed_cards"], ["PL!HAND-bp1-001"])
        self.assertIn("PL!HAND-bp1-001", public["cn2name"])
        self.assertNotIn("PL!HAND-bp1-002", public["cn2name"])

    def test_ui_bundle_has_no_css_secret_mask_and_uses_back_marker_routes(self):
        from llocg_ui.server import HTML

        self.assertNotIn("publicMaskCard", HTML)
        self.assertIn("renderTopCard(zels.deck, '__BACK__'", HTML)
        self.assertIn("renderMaskedHand(zels.hand", HTML)
        self.assertIn("const cn = (ri >= 0 && ri < revealedShow.length) ? revealedShow[ri] : '__BACK__';", HTML)
        self.assertIn("const isBack = (cn === '__BACK__');", HTML)


if __name__ == "__main__":
    unittest.main()
