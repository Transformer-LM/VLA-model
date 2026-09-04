# PGR-Audit v2.1 implementation overlay

This directory is the locally auditable source used to populate the isolated
personal StarVLA workspace. It is bound to freeze-manifest SHA256
`21267bf7a0b34d1f101398963011697ea451a6a4a5869dd97317319bd637ea6f`.

The package starts with the fail-closed foundation: canonical hashing,
personal-root containment, deterministic role seeding, rank-32 identity adapter,
sealed artifact handling, and the one-retry ledger. Scientific model/data paths
are added only after their protocol mapping and tests are reviewed.

`pgr_audit.launcher` exposes only one internally constructed V2-007 command. It
re-verifies the reviewed overlay, raw review/test receipts, environment lock,
clean upstream Git blobs, Qwen tree, checkpoint, exact key set, and sanitized
host config before taking a GPU snapshot. During the job it maintains a private
hardware-UUID reservation, checks PID/PGID ownership and foreign occupancy on
every heartbeat, enforces a fixed timeout, and releases the lock only after a
post-exit snapshot proves the selected UUID empty. A successful attempt must
produce one exact hash-sealed file set. `pgr_audit.engineering_canary` uses only
synthetic images and an instruction; it cannot read scientific targets or
outcomes.

Live robot connectivity and motion are not implemented or authorized.
