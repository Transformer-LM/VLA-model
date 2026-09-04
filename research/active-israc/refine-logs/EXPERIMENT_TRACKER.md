# 瀹為獙璺熻釜琛細ISRAC

| Run ID | Milestone | Purpose | System / Variant | Split | Metrics | Priority | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| R001 | M0 | 娴?MuJoCo deterministic replay 鍣０ | same-parameter 脳30 | LIBERO 1 task / 20 snapshots | state/RGB/depth/proprio max drift | MUST | TODO | CPU only |
| R002 | M0 | 娴?SAPIEN deterministic replay 鍣０ | same-parameter 脳30 | RoboTwin 1 task / 20 snapshots | state/RGB/depth/proprio max drift | MUST | TODO | CPU only |
| R003 | M0 | 璇佷功鎷掔粷 action-indexed 鍋囧弽渚?| scripted fake switch | 涓ゅ钩鍙板悇 10 cases | rejection rate | MUST | TODO | 搴斾负 100% |
| R004 | M0 | 楠岃瘉棣栨鐗╃悊鍒嗘瀹氫綅 | single native parameter perturbation | 涓ゅ钩鍙板悇 10 cases | first divergence/contact alignment | MUST | TODO | 涓嶆秹鍙?WAM |
| R005 | M1 | ISRAC 鎽╂摝/鎺ヨЕ E0 | full compiler | LIBERO / 20 snapshots / top-8 | certified pairs, calls/pair | MUST | TODO | 绂佹鎵嬭皟 |
| R006 | M1 | ISRAC 璐熻浇/閬尅 E0 | full compiler | LIBERO / 20 snapshots / top-8 | certified pairs, calls/pair | MUST | TODO | 鍙傛暟蹇呴』鏈夌墿鐞嗚涔?|
| R007 | M1 | ISRAC 鎽╂摝/鎺ヨЕ E0 | full compiler | RoboTwin / 20 snapshots / top-8 | certified pairs, calls/pair | MUST | TODO | 绂佹鎵嬭皟 |
| R008 | M1 | ISRAC 璐熻浇/閬尅 E0 | full compiler | RoboTwin / 20 snapshots / top-8 | certified pairs, calls/pair | MUST | TODO | 鍙傛暟蹇呴』鏈夌墿鐞嗚涔?|
| R009 | M1 | random baseline | domain randomization + rejection | 涓?R005鈥揜008 鍚岄绠?| yield per 1k calls | MUST | TODO | matched calls |
| R010 | M1 | grid/CMA-ES baseline | constrained fuzzing | 涓?R005鈥揜008 鍚岄绠?| yield per 1k calls | MUST | TODO | 涓嶄娇鐢?influence graph |
| R011 | M1 | 鍒犻櫎 influence-zero | ISRAC w/o separation | 涓?R005鈥揜008 鍚岄绠?| yield, invalid rate | MUST | TODO | 鏍稿績 novelty ablation |
| R012 | M1 | 48h E0 gate 姹囨€?| frozen pair set | 涓ゅ钩鍙?| gate pass/fail | MUST | TODO | FAIL 鍒欏仠姝㈠叏閮?GPU |
| R013 | M2 | 鍐荤粨 蟺0.5 candidate bundle | 蟺0.5 top-K | certified snapshots | eligibility, diversity | MUST | TODO | GPU 2/3 浼樺厛 |
| R014 | M2 | 鏃犱慨姝?WAM | DreamZero-compatible WAM | normal + alias | ranking/regret | MUST | TODO | common candidate bundles |
| R015 | M2 | FWM baseline | official or clearly labeled replica | normal + alias | prediction error, ranking | MUST | TODO | 涓嶅啋鍏呭畼鏂?|
| R016 | M2 | FBFM baseline | official or clearly labeled replica | normal + alias | correction harm | MUST | TODO | 寮烘渶杩戦偦 |
| R017 | M2 | ReDRAW-style baseline | point residual dynamics | normal + alias | correction harm | MUST | TODO | 鏈哄埗鏃忓熀绾?|
| R018 | M2 | baseline reproducibility gate | all baselines | ordinary perturbations | expected direction checks | MUST | TODO | 澶辫触鍒欎慨澶嶏紝涓嶈繘鍏ヤ富缁撴灉 |
| R019 | M3 | 鏍稿績 alias 璇勬祴 seed 0 | all frozen methods | alias + controls | false-transfer, regret, harm | MUST | TODO | 鍙寜鏂规硶鍒?GPU |
| R020 | M3 | 鏍稿績 alias 璇勬祴 seed 1 | all frozen methods | alias + controls | false-transfer, regret, harm | MUST | TODO | 鍙寜鏂规硶鍒?GPU |
| R021 | M3 | 鏍稿績 alias 璇勬祴 seed 2 | all frozen methods | alias + controls | false-transfer, regret, harm | MUST | TODO | 鍙寜鏂规硶鍒?GPU |
| R022 | M3 | held-out WAM transfer | pair compiler blind to model | alias | harm transfer | MUST | TODO | 鎺掗櫎 target overfit |
| R023 | M3 | 鏅€氭壈鍔ㄨ礋瀵圭収 | matched severity | non-alias | harm delta | MUST | TODO | 鎺掗櫎涓€鑸?OOD |
| R024 | M3 | 缁熻姹囨€?| paired bootstrap | all | 95% CI, effect size | MUST | TODO | 涓嶅彧鎶ュ潎鍊?|
| R031 | M4 | 鎵╄嚦 4 tasks/engine | full compiler | held-out tasks | zero-edit yield | NICE | TODO | C1/C2 閫氳繃鍚?|
| R032 | M4 | 鐪熷疄鏈哄櫒浜哄皬鏍锋湰 | safe replay only | pre-defined cases | direction agreement | NICE | TODO | 涓嶅绉板畨鍏ㄤ繚璇?|
