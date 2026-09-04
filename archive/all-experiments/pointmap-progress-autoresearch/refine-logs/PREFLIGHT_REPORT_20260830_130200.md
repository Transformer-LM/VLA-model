# Preflight Report

**Status:** PASS WITH NOVELTY WARNING

## Verified

- SSH uses Windows OpenSSH, user `liu_meng`, BatchMode and IdentitiesOnly.
- All new remote directories are inside `<PERSONAL_RESEARCH_ROOT_ALIAS>`.
- Existing personal OSMesa LIBERO runtime produces two-view RGB, metric depth, instance segmentation, object/proprio state, and exact simulator snapshot restore.
- Five selected LIBERO `inside/on` tasks can be programmatically placed into valid completed states using their BDDL predicates.
- One-task collection produced six accepted controlled events; three-task training smoke completed on physical GPU 2.
- All four A100s were idle at the two recorded preflight checks; this is not a reservation and must be rechecked at every launch.
- No remote download, root/sudo/su, profile edit, system CUDA change, shared/team write, paid compute, or real robot was used.

## Warning

Fresh novelty review scored the broad idea 4.0/10 (high overlap). POT-VLA already covers persistent 3D records, visibility/uncertainty, typed predicates, re-observation, and recovery; EV-WM/CheckVLA cover action-conditioned verification. Therefore E0 cannot be described as new WAM evidence. The only claim-bearing delta is conditional value of realized kinematics for historical non-active relation belief under a frozen aliasing population.

## Remaining before full launch

- fresh-agent code review;
- implement deterministic dataset audit and result aggregator;
- resync reviewed code;
- recheck selected GPU immediately before each job.
