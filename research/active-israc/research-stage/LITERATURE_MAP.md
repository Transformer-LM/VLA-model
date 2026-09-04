# ISRAC 鏂囩尞璇佹嵁鍥撅紙2026-08-31锛?
## 妫€绱㈤棶棰樹笌杈圭晫

ISRAC 涓嶆槸鏂扮殑 residual correction 绠楁硶銆傚畠瑕佹楠岀殑鏄細褰撳弽棣堝紡 WAM 鎶婂凡鎵ц鍔ㄤ綔鐨勯娴嬫畫宸縼绉诲埌鍙︿竴涓皻鏈墽琛岀殑鍊欓€夊姩浣滄椂锛屽崟涓€ factual feedback interface 鏄惁瓒充互鍐冲畾鍊欓€夊姩浣滀笅鐨勬纭慨姝ｆ柟鍚戙€傛嫙淇濈暀鐨勬柊棰栨€у彧闄愪簬锛?
> 浠庡喕缁?VLA 鐨勮嚜鐒舵垚鍔熻建杩瑰嚭鍙戯紝鑷姩瀵绘壘瀵?factual action 鐨勫畬鏁村彲瑙傛祴鍙嶉瀹屽叏鐩稿悓銆佷絾瀵?future candidate 鐨勭墿鐞嗘晥鏋滀笉鍚岀殑 simulator-native twin worlds锛屽苟杈撳嚭閫愬抚涓€鑷存€с€佸奖鍝嶆縺娲诲拰棣栨鍒嗘鐨勬満鍣ㄨ瘉涔︺€?
涓嶄富寮犱互涓嬪唴瀹规槸鏂扮殑锛氫笘鐣屾ā鍨嬩細鍑洪敊銆佹ā鍨嬪彲琚?planner 鍒╃敤銆佸弽浜嬪疄鍒嗘敮銆乵etamorphic testing銆侀殢鏈?simulator fuzzing銆乼wo-point non-identifiability lower bound銆佸湪绾?residual correction 鎴栧€欓€夊姩浣滈噸鎺掑簭銆?
妫€绱㈣鐩?2018--2026锛岃繎鏈熼噸鐐逛负 2023--2026銆傝瘉鎹潵婧愬寘鎷細椤圭洰鏈湴 48 绡?PDF 涓笌鏈棶棰樻渶鐩稿叧鐨勫師鏂囬椤?鎽樿/鏂规硶娈碉紱2026-08-31 鐨?OpenAlex銆丆rossref 鍜?Semantic Scholar 鏌ヨ锛涢」鐩悓鏃ヤ繚瀛樼殑鏌ユ柊蹇収銆俛rXiv API 鍦ㄦ湰杞洜 TLS EOF 澶辫触锛孲emantic Scholar 閮ㄥ垎鏌ヨ鍑虹幇 HTTP 429锛屽洜姝も€滄湭鍙戠幇绮剧‘鍚屾瀯宸ヤ綔鈥濆彧鑳芥槸鏉′欢鎬х粨璁猴紝涓嶈兘鍐欐垚缁濆涓嶅瓨鍦ㄣ€?
## 鐩存帴杩戦偦锛氬弽棣堛€侀獙璇併€佷慨澶嶄笌 exploitation

| 宸ヤ綔 | 瀹冪湡姝ｈВ鍐崇殑闂 | 涓?ISRAC 鐨勯噸鍙?| ISRAC 蹇呴』瀹堜綇鐨勫樊寮?| 璇佹嵁 |
|---|---|---|---|---|
| [Feedback World Model](https://arxiv.org/abs/2605.15705) (2026, preprint) | 鎶婄湡瀹炶娴嬩笌浼犳挱鐘舵€佺殑 latent residual 浣滀负鍦ㄧ嚎鍙嶉锛屼慨姝ｅ綋鍓?world-model state/velocity锛屽苟寮曞鍔ㄤ綔鐢熸垚 | **鏈€楂樻満鍒跺▉鑳?*锛歠actual residual 琚敤浜庡悗缁姩浣滃喅绛栵紱generic residual correction 宸茶鍗犳嵁 | ISRAC 涓嶆彁鍑哄彟涓€涓?correction head锛涘畠鐢熸垚 action-separated counterexamples锛屾鏌ュ悓涓€ residual 瀵逛笉鍚?candidate 鐨勮縼绉绘槸鍚﹀彲璇嗗埆 | 椤圭洰鍚屾棩鍘熸枃鏈哄埗鏍搁獙锛歋ec. 4.2--4.3 / Eqs. 8--16 |
| [ReDRAW](https://arxiv.org/abs/2504.02252) (2025, preprint) | 鐢ㄥ皯閲忕洰鏍囧煙鏁版嵁璁粌 `delta(z,a)` 淇鍐荤粨 source latent dynamics锛屽啀鍦ㄤ慨姝ｅ悗鐨?imagined dynamics 涓紭鍖?actor--critic | residual dynamics adaptation 宸叉湁锛涘姩浣滄潯浠?residual 涔熶笉鏄柊鐐?| ISRAC 鐨勫璞℃槸娴嬭瘯/璇佷吉鏍锋湰缂栬瘧鍣紝涓嶅涔?`delta`锛屼笖蹇呴』鍦ㄧ紪璇戞椂鐪嬩笉鍒拌娴?WAM score | 椤圭洰鍚屾棩鍘熸枃鏈哄埗鏍搁獙 |
| [When to Trust Imagination](https://arxiv.org/abs/2605.06222) (Wang et al., 2026, preprint) | 鐢?FFDC 姣旇緝棰勬祴鏈潵銆佺湡瀹炶瀵熴€佸姩浣滃拰璇█锛屽喅瀹氱户缁墽琛岃繕鏄彁鍓?replanning | 浣跨敤 prediction--reality discrepancy 瑙﹀彂鍙嶉鎺у埗 | 瀹冧笉妫€楠屸€滅浉鍚?factual discrepancy 瀵瑰彟涓€涓€欓€夊姩浣滄槸鍚︽剰鍛崇潃鐩稿悓淇鈥濓紱ISRAC 涔熶笉鎶?replan 鏈韩褰撳垱鏂?| 鏈湴 PDF 鍘熸枃 |
| [CheckVLA](https://arxiv.org/abs/2607.26789) (Liu et al., 2026, preprint) | 鍐荤粨 action-conditioned WM 鍋氬湪绾块闄╂娴嬨€乧onformal 瑙﹀彂銆乤ction suffix rewrite 鍜?re-anchor | execution-time verification/correction 宸茶鐩存帴鍗犳嵁 | ISRAC 鍙彲澹扮О鐢熸垚 matched residual-alias stress tests锛屽苟娴?unnecessary/wrong interventions锛涗笉鑳藉０绉伴涓?WAM 绾犻敊 VLA | 鏈湴 PDF 鍘熸枃 |
| [DREAM-Chunk](https://arxiv.org/abs/2606.18589) (Chen et al., 2026, preprint) | 閲囨牱澶氫釜 action chunks锛岀敤 latent futures 涓庣湡瀹?rollout 瀵归綈锛岃繍琛屾椂鍒囨崲 chunk | 鍊欓€夊姩浣?+ latent WM + 鐪熷疄鍙嶉鎺ュ彛宸叉湁 | ISRAC 涓嶆彁鍑?chunk switching锛涙鏌?feedback 鏄惁閿欒鍦拌法 candidate 娉涘寲 | 鏈湴 PDF 鍘熸枃 |
| [tau0-WM](https://arxiv.org/abs/2606.01027) (Zhou et al., 2026, preprint) | 鑱斿悎 video-action model銆乤ction-conditioned simulator銆乸rogress scorer锛岀敤 re-denoising 閫夋嫨/rectify candidates | WAM rollout 鎺掑簭涓?rectification 宸茶鍗犳嵁 | ISRAC 鐨?novelty 涓嶅緱鍐欐垚 candidate reranking锛涘畠鏄?WAM-blind counterexample compiler | 鏈湴 PDF 鍘熸枃 |
| [World Action Verifier](https://arxiv.org/abs/2604.01985) (Liu et al., 2026, preprint) | 鐢?state plausibility 涓?action reachability 鐨?forward--inverse asymmetry 鑷獙璇佸拰鑷敼杩?WM | 鈥滀慨姝?WAM 棰勬祴閿欒鈥濆拰 under-explored actions 宸茶鍗犳嵁 | ISRAC 涓嶄慨澶嶆ā鍨嬶紱鍏惰瘉涔﹁姹傜湡瀹?simulator action effect divergence锛岃€岄潪 cycle consistency | 鏈湴 PDF 鍘熸枃 |
| [Imperfect World Models are Exploitable](https://arxiv.org/abs/2605.15960) (Bhamidipaty et al., 2026, preprint) | 褰㈠紡鍖?model-induced policy preference reversal锛屽苟璇佹槑澶?policy set 涓?exploitation 鍩烘湰涓嶅彲閬垮厤 | 鐩存帴鍗犳嵁 ranking inversion / exploitation 鐨勪竴鑸悊璁?| ISRAC 鍙兘璐＄尞鑷姩浜х敓 embodied銆乵atched銆佸彲澶嶇幇鐨?witness锛涗笉鑳芥妸 preference reversal 褰撶悊璁烘柊棰栨€?| 鏈湴 PDF 鍘熸枃 |
| [RENEW](https://arxiv.org/abs/2607.14180) (Bhamidipaty et al., 2026, workshop preprint) | 鐢?human preferences 鐩存帴淇 imagined dynamics 涓彲鍒╃敤鐨勯敊璇紝骞剁敤 epistemic uncertainty 閫?query | 鑷姩瀵绘壘/淇 exploitable region 鐩搁偦 | RENEW 鐨勭洰鏍囪 world-model uncertainty/preferences锛汭SRAC 缂栬瘧杩囩▼绂佹璇诲彇鐩爣 WAM锛屽苟楠岃瘉 held-out feedback methods | 鏈湴 PDF 鍘熸枃 |
| [Uncertainty-aware Latent Safety Filters](https://arxiv.org/abs/2505.00779) (Seo et al., CoRL 2025) | ensemble epistemic uncertainty + conformal OOD threshold + latent reachability filter | 鈥滃涓嶅彲淇?imagination 鍋氬畨鍏ㄨ繃婊も€濆凡琚崰鎹?| ISRAC 涓嶆彁鍑?uncertainty gate锛涘叾 paired worlds涓撻棬妫€楠屽悓涓€鍙娴嬪弽棣堜笅鐨?action-dependent ambiguity | 鏈湴 PDF 鍘熸枃 |
| [Planning and Execution using Inaccurate Models with Provable Guarantees](https://www.roboticsproceedings.org/rss16/p001.html) (Vemula et al., RSS 2020) / [CMAX++](https://doi.org/10.1609/aaai.v35i7.16765) (AAAI 2021) | 鍦ㄧ嚎鍙戠幇 model discrepancies 鍚庣粫寮€涓嶅噯纭?transition锛涘悗鑰呰法閲嶅浠诲姟鍒╃敤缁忛獙 | 鍘嗗彶 discrepancy 鐨勮法鏃堕棿浣跨敤涓?inaccurate-model control 宸叉垚鐔?| ISRAC 蹇呴』瀹炶瘉 residual 鐨勯敊璇法鍔ㄤ綔杩愯緭锛岃€屼笉鏄硾绉扳€滃巻鍙茶宸笉鑳芥硾鍖栤€?| 鏈湴 PDF 鍘熸枃 |

## 鐩存帴杩戦偦锛氭祴璇曘€佸弽渚嬬敓鎴愪笌鐗╃悊 paired worlds

| 宸ヤ綔鏃?| 宸叉湁鑳藉姏 | 瀵?ISRAC 鐨勫▉鑳?| 灏氭湭鍦ㄦ湰杞瘉鎹腑鍙戠幇鐨勭粍鍚?|
|---|---|---|---|
| [Metamorphic Testing: Testing the Untestable](https://doi.org/10.1109/MS.2018.2875968) (Segura et al., IEEE Software 2018) 鍙?adaptive / feedback-directed MT | 閫氳繃 source/follow-up inputs 涓?metamorphic relations 鍦ㄦ棤瀹屾暣 oracle 鏃跺彂鐜伴敊璇紱宸叉湁鑷姩/鑷€傚簲 MR 鎼滅储 | 鈥滄垚瀵逛笘鐣?+ 鍏崇郴璇佷功鈥濇湰韬笉鏄柊娴嬭瘯鑼冨紡 | 閽堝鍙嶉寮?WAM 鐨?**factual-interface equality + candidate-only physical influence activation + first-divergence certificate** |
| [Metamorphic Testing of Vision--Language Action--Enabled Robots](https://arxiv.org/abs/2602.22579) (2026, preprint) | 鍥哄畾 seed锛屽浠诲姟/鐜鍋?controlled transformations锛屾鏌ユ垚鍔熺巼鍜岃建杩瑰簲淇濇寔鎴栧簲鍙樺寲 | VLA paired testing 宸插嚑涔庣洿鎺ュ崰鎹紱鑻ュ叾琛ュ厖鏉愭枡宸叉湁 snapshot restore銆乶ative physics parameter blocks 鍜岃法 action equality锛孖SRAC 鏂伴鎬т細鏄捐憲涓嬮檷 | 褰撳墠宸叉牳楠屾潗鏂欐樉绀哄畠姣旇緝 transformation 涓嬬殑 VLA behavior锛屼笉淇濇寔涓€涓?action 鐨勫畬鏁村弽棣堟帴鍙ｅ悗鍐嶈鍙︿竴涓?candidate 鍒嗘 |
| [Verifying Controllers Against Adversarial Examples with Bayesian Optimization](https://doi.org/10.1109/ICRA.2018.8460635) (Ghosh et al., ICRA 2018) | 鐢?Bayesian optimization 瀵绘壘鎺у埗鍣ㄥ弽渚?| 鑷姩鍙嶄緥鎼滅储銆乻imulator falsification 涓嶆柊 | WAM-blind influence-zero screening 鏄惁鑳藉湪鍖归厤 calls 涓嬩紭浜?BO/CMA/grid 蹇呴』瀹為獙锛岃€屼笉鑳介潬瀹氫箟鍙栬儨 |
| [BEACON](https://doi.org/10.1109/ACCESS.2024.3436515) (Yancosek & Baheri, IEEE Access 2024) | Bayesian evolutionary counterexample generation for control systems | evolutionary counterexample generation 鏄己 baseline | ISRAC 蹇呴』鐢ㄧ浉鍚?simulator calls 姣旇緝 yield/calls-per-pair |
| [Counterexample-Guided Synthesis of Perception Models and Control](https://doi.org/10.23919/ACC50511.2021.9482896) (Ghosh et al., ACC 2021) | 鍙嶄緥椹卞姩鍦拌仈鍚?perception/control synthesis | 鍙嶄緥鍙敤浜庢敼杩涙劅鐭ュ拰鎺у埗骞朵笉鏂?| ISRAC 褰撳墠鍙厑璁?diagnostic compiler claim锛涘悗缁嫢璁粌妯″瀷闇€涓?CEGIS 鍖哄垎 |
| [Using Constraint Solvers to Support Metamorphic Testing](https://doi.org/10.1109/MET.2019.00013) (de Castro-Cabrera et al., MET 2019) | 鐢ㄧ害鏉熸眰瑙ｇ敓鎴?鏀寔 metamorphic tests | 鈥渃ompiler + constraint鈥濇帾杈炰笉鑳借嚜鍔ㄦ瀯鎴愭柊棰栨€?| 鐗╃悊 influence graph銆乫actual zero-effect 涓?candidate activation 蹇呴』鏄笉鍙 random/solver baseline 鏇夸唬鐨勬牳蹇?|
| [Automated Inference of Expressive Metamorphic Relations](https://doi.org/10.1109/ICST69053.2026.00016) (Nolasco, ICST 2026) | 鑷姩鎺ㄦ柇 metamorphic relations | 鑷姩鍏崇郴鍙戠幇鍓婂急鈥滆嚜鍔ㄧ敓鎴愭祴璇曞叧绯烩€濈殑骞夸箟 claim | ISRAC 搴斿喕缁?relation schema锛屽彧鑷姩瀹氫綅鐗╃悊鍙傛暟鍧楀拰杈圭晫锛涗笉瑕佸０绉伴涓嚜鍔?MR inference |

## 鏀寔鎬т絾涓嶆瀯鎴愭柊棰栨€х殑璇佹嵁

| 宸ヤ綔 | 鏀寔鐨勪簨瀹?| 涓嶈兘鎹澹扮О浠€涔?|
|---|---|---|
| [WorldEval](https://arxiv.org/abs/2505.19017) (Li et al., 2025, preprint) | learned world simulator 鍙敤浜?policy/checkpoint 鎺掑簭锛屼絾 action following 鏄叧閿毦鐐?| 涓嶈兘鎺ㄥ嚭 learned ranking 瀵?counterfactual candidates 鍙潬 |
| [Foundational World Models Accurately Detect Bimanual Manipulator Failures](https://arxiv.org/abs/2603.06987) (Ward et al., 2026, preprint) | latent WM uncertainty 鍙敤浜?failure monitoring | failure detection 涓嶇瓑浜?error attribution 鎴栬法鍔ㄤ綔 residual identifiability |
| [Foresight](https://arxiv.org/abs/2606.23085) (Zhang et al., 2026, preprint) | action-conditioned WM latents + conformal calibration 鍙仛闀挎椂 failure detection | 涓嶈兘璇佹槑 residual 鍙縼绉诲埌鍙︿竴涓€欓€夊姩浣?|
| [Efficient Imitation Learning with Conservative World Models](https://proceedings.mlr.press/v242/kolev24a.html) (Kolev et al., L4DC 2024) | model bias 涓庨澶?distribution shift 闇€瑕佷繚瀹堢洰鏍?| 涓嶈兘鎶婁繚瀹?uncertainty penalty 褰?ISRAC 鏂规硶璐＄尞 |

## 璇佹嵁缁煎悎涓庢潯浠舵€?novelty verdict

1. **鏅€氱殑 WAM 绾犻敊宸茬粡琚仛浜嗐€?* FWM銆丷eDRAW銆丆heckVLA銆丏REAM-Chunk銆乼au0-WM 鍜?WAV 鍒嗗埆瑕嗙洊浜?residual feedback銆乷ffline dynamics adaptation銆乺untime verification/suffix repair銆乧hunk switching銆乸re-execution rectification 涓?self-verification銆傚洜姝?ISRAC 涓嶈兘鍐嶄互鈥滀慨姝?WAM 閿欒鈥濅负涓昏础鐚€?2. **model exploitation 涓?ranking inversion 涔熶笉鏄┖鐧姐€?* 2026 鐨勭悊璁哄拰瀹炶瘉宸ヤ綔宸茬粡鏄庣‘璁ㄨ optimizer 鍒╃敤涓嶅畬缇庢ā鍨嬨€侷SRAC 鐨勪环鍊煎彧鑳芥槸鏋勯€犵洰鍓嶆柟娉曢毦浠ラ€冮伩鐨勩€佺墿鐞嗕笂閰嶅涓斿彲瀹¤鐨?embodied witnesses銆?3. **paired testing / counterexample generation 鏄垚鐔熼鍩熴€?* Metamorphic testing銆丅ayesian/evolutionary falsification銆乧onstraint-supported testing 閮芥槸寮哄厛渚嬨€侷SRAC 鏄惁瓒呰繃鈥滀负 VLA/WAM 鍐欎簡涓€涓柊鐨?metamorphic relation鈥濓紝瀹屽叏鍙栧喅浜?influence separation 鍦ㄥ悓绛?simulator-call 棰勭畻涓嬭兘鍚︽樉钁楁彁楂樹弗鏍煎悎鏍?pair 鐨勪骇鐜囷紝骞惰兘鍚︽毚闇叉湭鍙備笌缂栬瘧鐨勫涓弽棣堟柟娉曠殑 correction harm銆?4. **鏈疆娌℃湁鎵惧埌绮剧‘鍖呭惈鍏ㄩ儴鍥涢」鐨勫凡楠岃瘉宸ヤ綔锛?* (a) 鍐荤粨鑷劧 VLA 杞ㄨ抗锛?b) factual 瀹屾暣鍙嶉鎺ュ彛閫愬抚鐩哥瓑锛?c) future candidate 鎵嶆縺娲荤殑 simulator-native physical parameter锛?d) 鏈哄櫒鍙獙鐨?activation/first-divergence 璇佷功銆備絾鏁版嵁搴撹闂彈闄愶紝涓や釜 2026 骞磋鎻愬悕鐨勭悊璁鸿繎閭绘湭鑾峰緱鍙牳楠屽叏鏂囷紝鍥犳杩欎笉鏄€滅‘瀹氭病浜哄仛杩団€濈殑缁撹銆?
褰撳墠涓ユ牸鍒ゆ柇锛?*鏉′欢鎬у彲鍋氾紝provisional novelty 7.1/10锛堝悎鐞嗗尯闂?6.4--7.7锛?*銆傚彧鏈夊綋涓嬮潰涓変釜闂ㄥ悓鏃堕€氳繃锛屾墠鑳界淮鎸佸ぇ浜?7 鐨勪富寮狅細

- matched-call ISRAC yield 鑷冲皯涓烘渶寮?random/grid/CMA/BO baseline 鐨?2 鍊嶏紱
- 鑷冲皯涓や釜 simulator-native mechanism family銆佸涓换鍔°€佹棤浠诲姟涓撶敤浠ｇ爜锛?- 鑷冲皯涓や釜鏈弬涓庣紪璇戠殑 feedback-WAM 鎺ュ彛鍦?alias set 涓婂憟鐜版樉钁楅珮浜庢櫘閫?perturbation set 鐨?correction harm / ranking inversion銆?
鑻?matched baseline 绛夋晥锛孖SRAC 搴旈檷绾т负 **WAM/VLA metamorphic benchmark engineering锛堢害 6.3--6.7锛?*锛涜嫢 feedback methods 涓嶅彈杩欎簺 pairs 褰卞搷锛屽垯淇濈暀 simulator diagnostic artifact锛屾斁寮?WAM correction-harm 涓诲紶銆?
## 涓嬩竴璇佹嵁闂?
鍏堣繍琛屽尮閰嶉绠楃殑 compiler baselines銆傛闂ㄥ彧浣跨敤缂撳瓨鐨勫喕缁?StarVLA 鎴愬姛杞ㄨ抗鍜?MuJoCo rollback锛屼笉璁粌 5B WAM銆傞€氳繃鍚庢墠鍚姩 GPU WAM 鎺ㄧ悊/鏈€灏忔帴鍙ｅ鐜帮紱鏈€氳繃鍒欏仠姝㈠綋鍓?Idea锛岄伩鍏嶇敤绠楀姏鎺╃洊鏂规硶璐＄尞涓嶈冻銆?