"""Deterministic physical toy used only to test ISRAC certificate logic.

This is an engineering unit test, never evidence for a paper claim.  The two
worlds differ only in a surface friction parameter.  A factual motion avoids
the surface, whereas a policy-supported candidate contacts it.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib

from .certificate import FrameTrace, PhysicalParameter, RolloutTrace


def make_world(world_id: str, friction: float, *, action_conditioned: bool = False) -> PhysicalParameter:
    return PhysicalParameter(
        block_id="table_contact_pair",
        family="object_surface_friction",
        engine_field="geom_friction[object,table]",
        value=friction,
        lower=0.05,
        upper=1.50,
        physical_units="dimensionless_coulomb_coefficient",
        action_conditioned=action_conditioned,
    )


def rollout(parameter: PhysicalParameter, action_id: str, action_rank: int) -> RolloutTrace:
    position = 0.0
    velocity = 0.0
    frames: list[FrameTrace] = []
    for step in range(7):
        contacting = action_id == "candidate_contact" and step >= 3
        if action_id == "factual_free":
            velocity = 0.10
        elif contacting:
            velocity = 0.44 - 0.28 * parameter.value
        else:
            velocity = 0.12
        position += velocity
        effect = position - 0.72
        physical_effect_probe = (effect,) if action_id == "candidate_contact" else (0.0,)
        frames.append(
            FrameTrace(
                state=(position, velocity),
                proprio=(position,),
                rgb_sha256=hashlib.sha256(f"rgb:{position:.17g}".encode()).hexdigest(),
                depth_sha256=hashlib.sha256(f"depth:{position:.17g}".encode()).hexdigest(),
                physical_effect_probe=physical_effect_probe,
                task_effect=(effect,),
                active_parameter_blocks=(parameter.block_id,) if contacting else (),
            )
        )
    return RolloutTrace(
        world_id="world_low" if parameter.value < 0.5 else "world_high",
        action_id=action_id,
        action_rank=action_rank,
        frames=tuple(frames),
        parameters=(parameter,),
    )


def action_indexed_copy(trace: RolloutTrace) -> RolloutTrace:
    return replace(trace, parameters=tuple(replace(p, action_conditioned=True) for p in trace.parameters))
