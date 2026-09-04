from __future__ import annotations

import unittest

import numpy as np

from certify_policy_boundary_alias import (
    all_nonrobot_groups,
    choose_groups,
    groups_from_pairs,
)


class DummyModel:
    def __init__(self) -> None:
        self.ngeom = 6
        self.geom_bodyid = np.asarray([0, 1, 1, 2, 3, 3], dtype=np.int64)
        self.names = {
            0: "world",
            1: "panda_hand",
            2: "cup_main",
            3: "tray_main",
        }

    def body_id2name(self, body_id: int) -> str:
        return self.names[body_id]


class BlockSelectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = DummyModel()

    def test_contact_groups_exclude_robot(self) -> None:
        groups = groups_from_pairs(self.model, {(1, 3), (2, 4), (4, 5)})
        self.assertEqual(groups, {"cup_main": {3}, "tray_main": {4, 5}})

    def test_allowed_geometries_implement_influence_screen(self) -> None:
        groups = groups_from_pairs(
            self.model,
            {(1, 3), (3, 4), (4, 5)},
            allowed_geoms={3, 5},
        )
        self.assertEqual(groups, {"cup_main": {3}, "tray_main": {5}})

    def test_random_scene_pool_and_matched_count_are_deterministic(self) -> None:
        groups = all_nonrobot_groups(self.model)
        self.assertEqual(
            groups,
            {"world": {0}, "cup_main": {3}, "tray_main": {4, 5}},
        )
        first = choose_groups(groups, count=2, seed=17)
        second = choose_groups(groups, count=2, seed=17)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 2)


if __name__ == "__main__":
    unittest.main()
