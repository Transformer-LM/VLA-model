"""Repeatable, non-writing LIBERO environment witness for the compute ledger."""

from __future__ import annotations

from pathlib import Path


def main() -> None:
    root = Path("<PERSONAL_RESEARCH_ROOT>").resolve(strict=True)
    bddl = (
        root
        / "workspace/third_party/LIBERO/libero/libero/bddl_files/libero_90"
        / "LIVING_ROOM_SCENE1_pick_up_the_alphabet_soup_and_put_it_in_the_basket.bddl"
    ).resolve(strict=True)
    if not bddl.is_relative_to(root):
        raise RuntimeError("BDDL path escaped the personal root")
    from libero.libero.envs import OffScreenRenderEnv

    env = OffScreenRenderEnv(
        bddl_file_name=str(bddl),
        camera_heights=32,
        camera_widths=32,
        camera_depths=True,
    )
    try:
        obs = env.reset()
        state = env.sim.get_state().flatten()
        rgb = obs["agentview_image"]
        depth = obs["agentview_depth"]
        print(
            "WITNESS_LIBERO",
            f"state={state.shape}",
            f"rgb={rgb.shape}/{rgb.dtype}",
            f"depth={depth.shape}/{depth.dtype}",
        )
    finally:
        env.close()


if __name__ == "__main__":
    main()
