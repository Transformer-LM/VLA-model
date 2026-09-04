# WAM Route Cards

## GeoRetract primary card

- representation: sparse object PointMap + object-relative metric geometry
- inputs: prior typed relation belief, object addresses, current/next PointMaps, executed action chunk
- outputs: relation transition and uncertainty (established/preserved/invalidated/unobservable)
- control use: progress verification, local belief retraction, reobserve/recover gate
- policy relation: frozen VLA
- WM update: offline train, inference frozen
- primary evidence: decision error and closed-loop recovery, not geometry reconstruction
- fallback interpretation: direct geometry verifier if action-conditioned dynamics is unnecessary

