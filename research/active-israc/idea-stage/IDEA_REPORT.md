+# Robotics Idea Discovery Report

**鏂瑰悜**锛氬弽棣堝紡 VLA 脳 WAM 鐨勮法鍔ㄤ綔璇樊杩佺Щ涓庡彲瀹¤鍙嶄緥  
**鏃ユ湡**锛?026-08-31  
**Pipeline**锛歳esearch-lit 鈫?robotics framing 鈫?novelty-check 鈫?matched-pilot  
**褰撳墠鍐冲畾**锛欼SRAC 鍗曚竴鍊欓€夛紝瀹為獙闂ㄥ墠鏆備笉瀹ｇО novelty > 7

## Robotics Problem Frame

- **Embodiment**锛歀IBERO Franka 鍗曡噦鎿嶄綔涓虹涓€骞冲彴锛汻oboTwin 涓虹浜屽钩鍙板€欓€夛紱涓嶈嚜涓诲惎鍔ㄧ湡瀹炴満鍣ㄤ汉銆?- **浠诲姟鏃?*锛氳法浠诲姟璇█鏉′欢鎿嶄綔锛涗粠鍐荤粨 StarVLA 鐨勮嚜鐒舵垚鍔熻建杩规彁鍙栫浉閭?factual/candidate action chunks銆?- **瑙傛祴/鍔ㄤ綔鎺ュ彛**锛歮ain RGB銆亀rist RGB銆乨epth銆乸roprio锛汼tarVLA 8脳7 continuous action chunks銆?- **瀛︿範璁剧疆**锛氬弽棣堝紡 action-conditioned WAM 鐨勬墽琛岄獙璇併€佸€欓€夎瘎浠锋垨 correction audit锛涚紪璇戝櫒鏈韩涓嶈缁?WAM銆?- **鍙敤璧勪骇**锛?脳A100-40GB銆丼tarVLA checkpoint銆丩IBERO rollback銆佺紦瀛樻垚鍔熻建杩癸紱杩滅浠呭彲鍐欎釜浜虹洰褰曘€?- **瀹夊叏绾︽潫**锛氭棤瑙﹁锛涘綋鍓嶅彧鍋?simulation锛涗笉杩涜鐪熷疄鏈哄櫒浜鸿繍鍔ㄣ€?- **璐＄尞绫诲瀷**锛歮ethodological diagnostic/compiler锛岃€屼笉鏄柊鐨?video generator 鎴?action head銆?
## 鍞竴淇濈暀 Idea锛欼SRAC

**鍏ㄧО**锛欼nfluence-Separated Residual-Alias Compiler  
**涓枃**锛氬奖鍝嶅垎绂荤殑娈嬪樊鍒悕鍙嶄簨瀹炵紪璇戝櫒

### 鏍稿績闂

鍙嶉寮?WAM 鍙兘鎶婁竴涓凡鎵ц factual action 鏆撮湶鐨?prediction residual锛岀敤鏉ヤ慨姝ｆ垨鎺掑簭鍙︿竴涓皻鏈墽琛岀殑 candidate action銆傝嫢鍚屼竴 factual feedback interface 鍦ㄤ袱涓悎娉曠墿鐞嗕笘鐣屼腑瀹屽叏鐩稿悓锛岃€?candidate 鐨勭湡瀹炴晥鏋滀笉鍚岋紝鍒欏崟涓€ residual 鏈韩涓嶈冻浠ュ喅瀹氬€欓€夊姩浣滅殑姝ｇ‘淇鏂瑰悜銆?
### 鏍稿績鏈哄埗

1. 浠庡喕缁?VLA 鐨勮嚜鐒舵垚鍔熻建杩瑰彇寰?factual chunk銆佹湭鏉?policy-supported candidate suffix 鍜屽彲鎭㈠杈圭晫锛?2. 寤虹珛 simulator-native contact/activation trace锛?3. 绛涘嚭瀵?factual 鍔ㄦ€佽浆褰曞奖鍝嶄负闆躲€佷絾浼氳 candidate 婵€娲荤殑鐗╃悊鍙傛暟鍧楋紱
4. 鍦ㄩ娉ㄥ唽鐗╃悊鑼冨洿鍐呯敓鎴?`theta+` / `theta-`锛?5. 杈撳嚭涓ゅ眰鍒嗙璇佹嵁锛?   - **model-free compiler certificate**锛歠actual RGB/depth/proprio/鍔ㄦ€?simulator state 鐩哥瓑锛宑andidate 鍙傛暟婵€娲讳笌棣栨鐗╃悊鍒嗘瀵归綈锛?   - **post-hoc WAM audit**锛歱air 鍐荤粨骞跺搱甯屽悗锛屾墠鍔犺浇鐩爣 WAM 娴?residual transport銆乺anking inversion 鍜?correction harm銆?
杩欓噷鐨勨€渟tate equality鈥濆彧鎸?rollout 鐨勫畬鏁村姩鎬佺姸鎬侊紝涓嶅寘鍚湰鏉ュ氨鏁呮剰涓嶅悓鐨勯潤鎬佺墿鐞嗗弬鏁伴厤缃紱鍙傛暟閰嶇疆鍗曠嫭鍝堝笇銆?
### 涓€鍙ヨ瘽 novelty delta

> 涓嶅悓浜庣幇鏈?VLA metamorphic testing 瀵规垚鍔?rollout 鏂藉姞棰勫畾涔夊満鏅彉鎹㈠悗妫€鏌ユ暣娈佃涓哄簲鍚屾垨搴斿彉锛孖SRAC 鍦ㄤ笉璇诲彇鐩爣 WAM score 鐨勬潯浠朵笅锛岃嚜鍔ㄦ悳绱㈠ factual action 鍏ㄥ姩鎬佽浆褰曢浂褰卞搷銆佸嵈浠呰鏈潵 policy-supported candidate 婵€娲荤殑鍚堟硶鐗╃悊鍙傛暟瀵癸紝骞惰緭鍑?equality鈥揳ctivation鈥揻irst-divergence 璇佷功锛屼互褰㈡垚鍙嶉娈嬪樊璺ㄥ姩浣滀笉鍙瘑鍒€х殑鍙璁?embodied witness銆?
### Benchmark 涓庢渶灏?pilot

- **绗竴骞冲彴**锛歀IBERO Goal锛屽喕缁?StarVLA 鎴愬姛杞ㄨ抗锛?- **鐜版湁 feasibility evidence**锛? 涓嚜鍔ㄧ瓫閫夎竟鐣屼腑 6 涓€氳繃锛屼骇鐢?24 涓?certified pairs锛涘彟淇濈暀 2 涓け璐ヨ竟鐣岋紱
- **褰撳墠杩愯**锛歝andidate-contact 涓?random-scene 鍚?3 selector seeds銆? 涓竟鐣屻€佺浉鍚岀墿鐞嗗€间笌姣忓潡 8 娆?rollout锛?- **鍚庣画寮?baseline**锛歡rid銆丆MA-ES銆丟hosh-style BO銆丅EACON-style BO+CMA锛?- **鎸囨爣**锛歝ertified pairs / 1k simulator rollouts銆乧alls/pair銆乸assing-block rate銆佸け璐ュ師鍥犮€乸aired bootstrap CI锛?- **姝ｄ俊鍙?*锛欼SRAC 鐩稿鏈€寮?matched-call baseline 鐨?yield ratio 鈮?锛屽苟璺ㄤ袱涓墿鐞嗘満鍒舵棌涓庣浜?simulator 閲嶇幇锛?- **kill**锛氭渶浣?matched-call baseline 绛夋晥/鏇村ソ锛屾垨 pair 渚濊禆浠诲姟鑴氭湰銆乤ction-indexed 寮€鍏炽€佸闃堝€笺€佷綆鏀寔鍔ㄤ綔銆乼arget-WAM leakage銆?
## Novelty Gate

鍚屽鏃忕嫭绔嬩笂涓嬫枃 reviewer 鐨勭粨璁猴細

- **matched-call 涔嬪墠**锛?.6/10锛屽尯闂?6.1鈥?.2锛涗笉寰楀绉?>7锛?- **绋冲仴 matched-call 浼樺娍鍚?*锛?.4/10锛屽尯闂?7.0鈥?.9锛?- **鏈€鍗遍櫓杩戦偦**锛歁etamorphic Testing of Vision鈥揕anguage Action鈥揈nabled Robots锛?- **绮剧‘琚祴鎺ュ彛杩戦偦**锛欶eedback World Model锛?- **涓€鑸悊璁鸿繎閭?*锛欼mperfect World Models are Exploitable锛?- **鎼滅储 baseline 杩戦偦**锛歝ontroller BO falsification銆丅EACON銆乧onstraint-supported metamorphic testing銆?
鍥犳 ISRAC 涓嶆槸宸茬粡纭畾鐨勬柊鏂规硶锛岃€屾槸涓€涓鍦ㄩ€氳繃瀹為獙浜夊彇 >7 鏂伴鎬х殑鍊欓€夈€?
## WAM Role

- **Compiler representation**锛歱rivileged simulator-native physics/contact trace锛屼粎鐢ㄤ簬绂荤嚎鐢熸垚璇佷功锛屼笉鏄儴缃茶緭鍏ワ紱
- **琚祴 WAM**锛氫紭鍏?latent/action-conditioned feedback interface锛屽悗缁彲鎵╁埌 pixel/video WAM锛?- **Control use**锛歎3 candidate evaluation / runtime correction audit锛?- **Policy**锛氬喕缁?StarVLA锛涗笉鎶?policy finetuning 褰撶涓€闂紱
- **绂佹娣锋穯**锛歝ompiler yield 涓?WAM harm 鏄袱涓嫭绔?claim锛涘墠鑰呴€氳繃鍚庢墠鍏佽鍚姩鍚庤€呫€?
## 宸叉窐姹版垨闄嶇骇璺嚎

- **generic WAM prediction-error correction**锛氳 Feedback World Model銆丷eDRAW銆丆heckVLA 绛夊己閲嶅彔锛?- **candidate-specific residual transport head**锛氬瓨鍦?candidate-only bypass锛屾棤娉曡瘑鍒?residual 鐨?load-bearing 浣滅敤锛?- **鏅€?WAM reranking**锛氳 tau0-WM銆丏REAMSTEER銆乄orldEval 绛夊崰鎹紱
- **浠呭仛 paired VLA metamorphic testing**锛氫笉瓒充互瓒呰繃宸叉湁 VLA metamorphic testing锛?- **Depth/PointMap auxiliary prediction**锛氬彲浠ヤ綔涓轰互鍚?WAM representation ablation锛屼笉鏄綋鍓嶆牳蹇?novelty銆?
## Evidence Package

- 蹇呴』鎶ュ憡鎵€鏈夊け璐ヤ笌鏈瓫閫夎竟鐣岋紝涓嶅彧灞曠ず閫氳繃鏍锋湰锛?- pair 蹇呴』鍦ㄤ换浣曠洰鏍?WAM 鍔犺浇鍓嶅喕缁撱€佸搱甯岋紱
- 鍚屽弬鏁?repeat noise 鐣屽繀椤婚鍏堝浐瀹氾紱
- 鍋?action-indexed/scripted switch 蹇呴』 100% 琚瘉涔︽嫆缁濓紱
- 蹇呴』鏈?matched simulator-call baseline 鍜岃嚦灏?3 compiler seeds锛?- 鑻ヤ富寮?WAM 璇婃柇浠峰€硷紝鑷冲皯涓や釜 held-out feedback methods 鐨?harm 蹇呴』楂樹簬 severity-matched 鏅€氭壈鍔紱
- 鐪熷疄鏈哄櫒浜轰笉鏄綋鍓?gate锛屽悗缁彧鑳藉湪鍗曠嫭瀹夊叏鍗忚鍜屾搷浣滃憳鎵瑰噯涓嬭繘琛屻€?
## 褰撳墠涓嬩竴姝?
1. 瀹屾垚姝ｅ湪杩愯鐨?8-boundary 脳 2-baseline 脳 3-seed pilot锛?2. 鏍规嵁 raw JSON 璁＄畻 yield ratio 涓?CI锛?3. 鑻ユ湭杩?2脳 闂紝鍔犲叆寮?BO/CMA baseline 鍚庨噸鏂板垽瀹氾紝涓嶈兘鐩存帴璁粌澶?WAM锛?4. 鑻ラ棬閫氳繃锛屽啀浣跨敤绌洪棽 A100 鍚姩 frozen feedback-WAM harm pilot銆?