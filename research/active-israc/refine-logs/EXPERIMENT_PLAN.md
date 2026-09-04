# 瀹為獙璁″垝锛欼nfluence-Separated Residual-Alias Compiler锛圛SRAC锛?
**闂**锛氬弽棣堝紡 WAM 鏍规嵁涓€涓凡鎵ц鍔ㄤ綔鏆撮湶鐨勯娴嬭宸紝鍘讳慨姝ｅ彟涓€涓皻鏈墽琛岀殑鍊欓€夊姩浣滐紱浣嗗崟涓?factual residual 鍙兘鏃犳硶璇嗗埆璺ㄥ姩浣滅殑璇樊鍝嶅簲锛屽鑷粹€滀慨姝ｂ€濆弽鑰岄鍊掔湡瀹炲姩浣滄帓搴忋€?
**鏂规硶涓诲紶**锛欼SRAC 鑷姩鎼滅储涓や釜鍚堟硶鐗╃悊涓栫晫锛屼娇宸叉墽琛屽姩浣滅殑瀹屾暣鍙嶉鎺ュ彛瀹屽叏鐩稿悓锛屼絾涓€涓敱鍐荤粨绛栫暐鎻愬嚭鐨勬湭鎵ц鍊欓€夊姩浣滃湪涓や釜涓栫晫涓骇鐢熺浉鍙嶇殑鐗╃悊鏁堟灉鎴?residual/ranking锛涙瘡涓牱鏈檮甯︽満鍣ㄥ彲楠岀殑鐗╃悊涓庡悓涓€鎬ц瘉涔︺€?
**鏃ユ湡**锛?026-08-31

## Claim Map

| Claim | 涓轰粈涔堥噸瑕?| 鏈€浣庡彲淇¤瘉鎹?| 鍏宠仈瀹為獙鍧?|
|---|---|---|---|
| C1锛堜富锛塈SRAC 鑳借嚜鍔ㄣ€佽法浠诲姟鍦扮紪璇戦潪 action-indexed銆佺墿鐞嗚嚜鐒剁殑 feedback-interface-preserving residual-alias twins | 杩欐槸鐩稿 Capability Separation銆丣oint MDPs 鍜屾櫘閫?metamorphic testing 鐨勫敮涓€鍙畧鏂伴鐐?| 涓や釜妯℃嫙鍣ㄣ€佽嚦灏戜袱涓墿鐞嗘満鍒舵棌锛涚浉瀵?random/grid/CMA-ES 鍦ㄥ悓绛?simulator calls 涓嬫樉钁楁彁楂樺悎鏍?pair 浜х巼锛涙墍鏈?pair 閫氳繃閫愬抚鍚屼竴鎬т笌棣栨鐗╃悊鍒嗘璇佷功 | B0銆丅1銆丅3 |
| C2锛堣緟锛夎繖浜?twins 鑳芥毚闇茬幇鏈夊弽棣?WAM 淇鍣ㄧ殑 correction harm锛岃€屼笖涓嶆槸閽堝鏌愪竴鏂规硶杩囨嫙鍚?| 璇佹槑缂栬瘧鍣ㄧ敓鎴愮殑鏄湁鎺у埗鎰忎箟鐨勫弽渚嬶紝鑰岄潪婕備寒浣嗘棤鍏崇殑 simulator artifact | pair 缂栬瘧杩囩▼涓嶈鍙栫洰鏍?WAM ranking锛涘湪鏈弬涓庣紪璇戠殑 FWM/FBFM/ReDRAW 绫绘柟娉曚笂锛宖alse transport銆乺anking inversion 鍜?regret 鏄捐憲楂樹簬鏅€氭壈鍔ㄩ泦 | B2銆丅4 |

**蹇呴』鎺掗櫎鐨勫弽瑙ｉ噴**锛氱粨鏋滄潵鑷墜宸?`if action==a1`銆乻cripted failure銆佹覆鏌撻潪纭畾鎬с€佷綆鏀寔鍔ㄤ綔銆佺洿鎺ユ妸鐩爣 WAM ranking 鏀捐繘鎼滅储鐩爣銆佹垨鍗曚竴浠诲姟鐨勫弬鏁扮宸с€?
## 璁烘枃璇佹嵁涓荤嚎

- 涓绘枃蹇呴』璇佹槑锛氳嚜鍔?compiler 鐨勫悎娉?alias 浜х巼锛涜瘉涔︾‘瀹炴垚绔嬶紱杩欎簺鏍锋湰瀵瑰弽棣?WAM 鏈夌嫭鐗圭殑 correction-harm 璇婃柇浠峰€笺€?- 闄勫綍鏀寔锛氭洿澶氫换鍔°€佸弬鏁拌寖鍥淬€佽瘉涔﹀彲瑙嗗寲銆佺湡瀹炴満鍣ㄤ汉鍙縼绉绘€ф帰绱€?- 鏄庣‘涓嶄富寮狅細two-point lower bound 鏈韩鏂伴锛汭SRAC 鑳戒慨澶?WAM锛沘lias twin 瑕嗙洊鎵€鏈夌湡瀹炲垎甯冨閿欒锛涙ā鎷熻瘉涔︾瓑浠蜂簬鐪熷疄瀹夊叏淇濊瘉銆?- 鏆傛椂鍒犲幓锛氫粠澶磋缁冩柊 WAM銆佸ぇ瑙勬ā RGB 鐢熸垚璐ㄩ噺姣旇緝銆佽Е瑙夈€侀暱鏈?RL post-training銆?
## 瀹為獙鍧?
### B0锛氱‘瀹氭€с€佹帴鍙ｅ悓涓€鎬т笌璇佷功鍗曞厓娴嬭瘯

- **Claim tested**锛氳瘉涔︽祴鍒扮殑鍚屼竴鎬т笌鍒嗘涓嶆槸澶嶈窇鍣０鎴栨棩蹇楀亣璞°€?- **Why**锛氳嫢 factual transcript 涓嶆槸鍚屼竴涓緭鍏ワ紝鏁翠釜涓嶅彲璇嗗埆鎬ц璇佸け鏁堛€?- **Dataset / task**锛歀IBERO/robosuite-MuJoCo 1 涓?pick-place 鎴?contact-rich task锛汻oboTwin/SAPIEN 1 涓搴斾换鍔★紱姣忎换鍔?20 涓彲鎭㈠ snapshot銆?- **Compared systems**锛氱浉鍚屽弬鏁伴噸澶嶅洖鏀撅紱鍗曚釜鍚堟硶鐗╃悊鍙傛暟寰壈锛沘ction-indexed fake switch锛堜粎浣滃簲琚嫆缁濈殑闃虫€ф帶鍒讹級銆?- **Metrics**锛歴imulator state hash锛涢€愬抚 RGB/depth 鏈€澶у樊涓?LPIPS锛沺roprio 鏈€澶у樊锛沠actual WAM residual 宸紱棣栨鐘舵€佸垎姝у抚锛涙帴瑙︿簨浠跺抚锛涜瘉涔︽嫆缁濆師鍥犮€?- **Setup**锛氬厛涓嶇敤鐩爣 WAM 璁粌锛涘浐瀹氶殢鏈虹瀛愩€佹覆鏌撳櫒銆佹帶鍒堕鐜囦笌 checkpoint 鎭㈠椤哄簭銆傚櫔澹伴槇鍊肩敱 30 娆″悓鍙傛暟澶嶈窇鐨勬渶澶у€肩‘瀹氾紝涓嶄汉涓烘寚瀹氬闃堝€笺€?- **Success criterion**锛氬悓鍙傛暟澶嶈窇 100% 閫氳繃锛沘ction-indexed/scripted 鎺у埗 100% 琚嫆缁濓紱鍚堟牸 twin 鐨?factual RGB/depth/proprio/residual 宸笉瓒呰繃鍚勮嚜澶嶈窇鍣０涓婄晫銆?- **Failure interpretation**锛歝heckpoint 鎭㈠鎴栨覆鏌撻潪纭畾锛屾棤娉曞舰鎴愬彲淇?benchmark锛岀珛鍗冲仠姝€?- **Table / figure**锛氫富鏂?Table 1锛堣瘉涔﹀畾涔変笌鍣０涓婄晫锛夛紱Figure 2锛堝悓涓€ factual銆佸垎鍙?candidate锛夈€?- **Priority**锛歁UST-RUN銆?
### B1锛氳嚜鍔?alias compiler 鐨勪骇鐜囦笌鏁堢巼

- **Claim tested**锛歩nfluence separation 鏄紪璇戝櫒鐨勫疄璐ㄨ础鐚紝涓嶆槸鏅€?fuzzing銆?- **Why**锛氫弗鏍艰瘎瀹¤涓鸿繖鍐冲畾 novelty 鏄?7.3 杩樻槸閫€鍖栧埌绾?6.4銆?- **Compiler**锛?  1. 浠庡喕缁撶瓥鐣?top-K chunk 涓€?factual `a0` 鍜?alternative `a1`锛?  2. 寤虹珛瀵硅薄鈥旇〃闈⑩€斿叧鑺傜墿鐞嗗弬鏁板潡涓?contact/event activation trace锛?  3. 鐢ㄦ湁闄愬樊鍒嗘垨 simulator 渚濊禆鍥剧瓫鍑哄 `a0` 瀹屾暣 transcript 褰卞搷浣庝簬鍣０銆佷絾浼氳 `a1` 婵€娲荤殑鍙傛暟鍧楋紱
  4. 鍦ㄧ墿鐞嗗悎娉曡寖鍥村唴姹傝В `theta+ / theta-`锛屽彧鏈€澶у寲 `a1` 鐨勭湡瀹炰换鍔℃晥鏋滃垎绂伙紝骞剁‖绾︽潫 `a0` transcript 鍚屼竴锛?  5. post-hoc 妫€鏌?residual sign/ranking inversion锛涚洰鏍?WAM ranking 涓嶅緱杩涘叆浼樺寲鐩爣銆?- **Baselines**锛氶殢鏈?domain randomization + rejection锛涚瓑棰勭畻缃戞牸/CMA-ES constrained fuzzing锛涘幓鎺?influence-zero 绛涢€夌殑 ISRAC銆?- **Metrics**锛氭瘡 1,000 simulator rollouts 鐨勫悎鏍?pair 鏁帮紱鍚堟硶 pair 鎴愬姛鐜囷紱calls/pair锛泈all time锛涜法 snapshot/task/鏈哄埗瑕嗙洊锛涢娆″垎姝т笌 contact activation 鍚屽抚姣斾緥锛涗汉宸ヨ皟鍙傛鏁帮紙蹇呴』涓?0锛夈€?- **Setup**锛氫袱涓ā鎷熷櫒鍚?1 涓换鍔★紝20 snapshots锛宼op-8 chunks锛涜嚦灏戞懇鎿?鎺ヨЕ闈笌璐熻浇/閬尅鐘舵€佷袱涓満鍒舵棌锛? 涓?compiler seeds銆?- **Success criterion锛?8h E0 gate锛?*锛氭瘡涓钩鍙拌嚦灏戜袱涓満鍒舵棌銆佹瘡鏃忚嚜鍔ㄥ緱鍒?鈮? 瀵瑰悎鏍?twins锛汭SRAC 鐨勫悎娉?pair 浜х巼鑷冲皯涓烘渶浣冲悓棰勭畻 baseline 鐨?2 鍊嶏紱鈮?0% pair 鐨勯娆″垎姝т笌璁板綍鐨勭湡瀹炵墿鐞嗘縺娲诲悓甯э紱鏃犻€愬疄渚嬫墜璋冦€?- **Failure interpretation**锛氫换涓€骞冲彴鏃犲悎鏍?pair銆佸彧鑳界敤 action-indexed/scripted 淇敼銆佹垨鍘绘帀鐩爣 WAM ranking 鍚?pair 娑堝け锛宬ill 鏈?Idea銆?- **Table / figure**锛氫富鏂?Table 2锛堜骇鐜?鏁堢巼锛夛紱Figure 3锛堝弬鏁板奖鍝嶅浘涓庣害鏉熸眰瑙ｏ級銆?- **Priority**锛歁UST-RUN銆?
### B2锛氬弽棣?WAM correction-harm 璇勬祴

- **Claim tested**锛歛lias twins 鏆撮湶鐨勬槸鐜版湁鍙嶉淇鍣ㄧ殑鐪熷疄璺ㄥ姩浣滈敊璇縼绉汇€?- **Why**锛氭妸 compiler 浠?simulator fuzzing 鎻愬崌涓?WAM/VLA 鐮旂┒宸ュ叿銆?- **Compared systems**锛氭棤淇 WAM锛汧WM锛汧BFM锛汻eDRAW-style point residual锛涜嫢浠ｇ爜涓嶅彲寰楋紝鍏堝疄鐜拌鏂囨帴鍙ｇ瓑浠风殑鏈€灏忓鐜板苟鏄庣‘鏍囨敞銆?- **Metrics**锛歠alse-transfer rate锛沜orrected-vs-uncorrected top-1 rollback regret锛沺airwise ranking accuracy锛沜orrection-harm rate锛堝師鏈纭€佷慨姝ｅ悗閿欒锛夛紱task success锛沠uture feature error浠呬綔娆℃寚鏍囥€?- **Setup**锛歝ompiler 涓嶈闂换浣曞緟璇勬柟娉曠殑 score/ranking锛涘悓涓€ candidate bundle銆佸悓涓€ rollback ground truth锛涢厤瀵?bootstrap 95% CI锛? seeds銆?- **Success criterion**锛氳嚦灏戜袱绉嶆湭鍙備笌缂栬瘧鐨勫弽棣堟柟娉曞湪 alias set 涓?correction-harm 鏄捐憲楂樹簬鏅€氱墿鐞嗘壈鍔ㄩ泦锛屼笖 uncorrected WAM 涓嶅憟鐜板悓绛夊箙搴︾殑浜轰负閫€鍖栥€?- **Failure interpretation**锛氳嫢鍙涓€涓閽堝鐨勬柟娉曟湁鏁堬紝鍒欐槸鏂规硶鐗瑰畾 adversarial test锛屼笉瓒虫敮鎾?C2銆?- **Table / figure**锛氫富鏂?Table 3锛堝弽棣堟柟娉?harm锛夛紱Figure 4锛堝悓 residual銆佺浉鍙嶆纭慨姝ｆ柟鍚戯級銆?- **Priority**锛歁UST-RUN锛岄』鍦?B1 閫氳繃鍚庡惎鍔?GPU銆?
### B3锛氭柊棰栨€ч殧绂讳笌鍙嶄綔寮婃帶鍒?
- **Claim tested**锛氭敹鐩婃潵鑷?influence-separated physical activation锛岃€岄潪鏇村ぇ鐨勬悳绱㈤绠楁垨瀹芥澗璇佷功銆?- **Controls**锛氬幓鎺?influence-zero锛涚敤鐩爣 WAM ranking 鍙備笌浼樺寲锛堝簲鎶ュ憡涓鸿繃鎷熷悎涓婄晫鑰岄潪鏂规硶锛夛紱鍏佽 action-indexed switch锛堝簲琚瘉涔︽嫆缁濓級锛沘ppearance-only nuisance锛涗綆鏀寔 candidate锛涙斁瀹?transcript 闃堝€硷紱鍙繚鐣欏崟 simulator銆?- **Metrics**锛氬悎娉?pair 浜х巼銆佽法鏂规硶 transfer銆佽瘉涔﹁繚瑙勭巼銆乧orrection-harm銆?- **Success criterion**锛氬畬鏁?ISRAC 鍦ㄧ浉鍚?calls 涓嬩紭浜?random/CMA-ES锛況anking-aware overfit 鐗堟湰鍦?held-out WAM 涓婃槑鏄句笅闄嶏紱瀹芥澗闃堝€煎彧鎻愰珮浼?pair 鑰屼笉鎻愰珮 certified pair銆?- **Failure interpretation**锛氳嫢鏅€?CMA-ES + rejection 绛夋晥锛宑ompiler 娌℃湁鏂规硶璐＄尞銆?- **Table / figure**锛氫富鏂?Table 4锛堝垹闄ゅ疄楠岋級锛涘叾浣欐斁闄勫綍銆?- **Priority**锛歁UST-RUN銆?
### B4锛氳法浠诲姟/璺ㄥ紩鎿庝笌鐪熷疄鏈哄櫒浜哄彲杩佺Щ鎬?
- **Claim tested**锛歝ompiler 涓嶆槸鍗曚换鍔″伐绋嬭剼鏈€?- **Setup**锛氭墿鑷虫瘡寮曟搸 鈮? 涓换鍔°€佲墺3 涓満鍒舵棌锛涚湡瀹炴満鍣ㄤ汉浠呭仛灏戦噺瀹夊叏銆侀鍏堢晫瀹氬弬鏁扮殑 replay 楠岃瘉锛屼笉瀹ｇО瀹夊叏淇濊瘉銆?- **Metrics**锛氭柊浠诲姟 zero-manual-edit yield锛涜瘉涔﹂€氳繃鐜囷紱鏈弬涓庣紪璇?WAM 鐨?harm transfer锛涚湡瀹?妯℃嫙 effect direction 涓€鑷寸巼銆?- **Success criterion**锛氬悓涓€ compiler schema 鍦ㄤ袱涓紩鎿庝笌澶氭暟鏂颁换鍔′腑鏃犻渶浠诲姟涓撶敤浠ｇ爜鍗冲彲浜у嚭 pair銆?- **Failure interpretation**锛氶渶姣忎换鍔￠噸鍐欏弬鏁拌涔夊垯闄嶄负 benchmark engineering銆?- **Table / figure**锛氶檮褰曚富琛紱鐪熷疄鏈哄櫒浜?qualitative figure銆?- **Priority**锛歂ICE-TO-HAVE锛孍0 涓嶅仛銆?
## Run Order and Milestones

| Milestone | Goal | Runs | Decision Gate | Cost | 椋庨櫓 |
|---|---|---|---|---|---|
| M0 | 鎭㈠ simulator checkpoint銆佺‘瀹氬璺戝櫔澹般€侀獙璇佽瘉涔?| R001鈥揜004 | 涓ゅ钩鍙?deterministic replay 閫氳繃锛沠ake switch 琚嫆缁?| CPU 4鈥?h锛屾棤 GPU | 娓叉煋/鐗╃悊闈炵‘瀹氭€?|
| M1 | 48h compiler E0 | R005鈥揜012 | 姣忓钩鍙颁袱鏈哄埗鏃忓悇 鈮? 瀵癸紱浜х巼 鈮?脳鏈€浣?baseline | CPU 24鈥?8h锛涘繀瑕佹椂灏戦噺鍗曞崱绛栫暐閲囨牱 | 闈炲厜婊戞帴瑙︿紭鍖栥€佸弬鏁拌涔変笉缁熶竴 |
| M2 | 鍐荤粨 蟺0.5/WAM 鍩虹嚎涓?feedback 鏂规硶 | R013鈥揜018 | 鏃犱慨姝?baseline 涓庤嚦灏戜袱绉嶅弽棣堟柟娉曞彲澶嶇幇 | GPU 0鈥?4h锛屾寜浠ｇ爜鍙緱鎬?| 璁烘枃浠ｇ爜/鏉冮噸涓嶅彲寰椼€佹湇鍔″櫒鏃犲缃?|
| M3 | 鏍稿績 correction-harm 璇勬祴 | R019鈥揜030 | 鈮?绉?held-out 鏂规硶鍑虹幇鍙噸澶?harm锛涙櫘閫氭壈鍔ㄨ礋瀵圭収涓嶇瓑鏁?| 4脳A100 绾?24鈥?2 GPUh | WAM 鎺ㄧ悊鎴愭湰銆佸€欓€?bundle 鏂瑰樊 |
| M4 | 鍒犻櫎瀹為獙涓庢墿灞?| R031+ | C1/C2 鍧囪鏀寔鍚庢墠缁х画 | 瑙嗙粨鏋滃喅瀹?| scope creep |

## Compute and Data Budget

- **E0**锛氫互 simulator CPU 涓轰富锛涘厛鐢ㄧ紦瀛?鍥哄畾 candidate chunks锛岄伩鍏嶅湪 premise 鏈€氳繃鍓嶆秷鑰?GPU銆?- **閫氳繃 E0 鍚?*锛氬喕缁?蟺0.5 涓?WAM锛屽彧鍋氬€欓€夐噰鏍枫€乺ollout 鍜屽弽棣堝熀绾挎帹鐞嗭紱鍥涘紶 A100 鍙苟琛屾寜 snapshot 鎴栨柟娉曞垏鍒嗐€?- **GPU 瑙勫垯**锛氬惎鍔ㄥ墠閫愬崱纭鏄惧瓨 <500 MiB銆佸埄鐢ㄧ巼 鈮?%銆佹棤 compute process锛涢粯璁?GPU 2/3锛屽彧鏈夊洓鍗″叏閮ㄧ┖闂叉椂浣跨敤 0鈥?锛涗笉鎶㈠崰銆佷笉鍏卞崱銆?- **鏁版嵁**锛氬叏閮ㄤ綅浜?`<PERSONAL_RESEARCH_ROOT>`锛涗笉寰楀啓鍏ュ洟闃?鍏变韩鐩綍銆?- **澶栫綉**锛氭湇鍔″櫒鏃犲缃戯紱浠ｇ爜銆佹潈閲嶄笌渚濊禆蹇呴』浠庢湰鍦板凡鏈夊畨瑁呮垨缁忔湰鏈哄畨鍏ㄤ紶杈撱€?- **鏈€澶х摱棰?*锛氳法 MuJoCo/SAPIEN 鐨勭墿鐞嗗弬鏁板潡鎶借薄涓?deterministic certificate锛岃€屼笉鏄?GPU 绠楀姏銆?
## 椋庨櫓涓庣紦瑙?
- **椋庨櫓锛歝ompiler 鍋风湅鐩爣 WAM ranking銆?* 缂撹В锛歳anking 姘镐笉杩涘叆浼樺寲鐩爣锛涘彧鍦ㄥ喕缁?pair 鍚?post-hoc 璇勪及锛屽苟鍋?held-out WAM transfer銆?- **椋庨櫓锛氭墍璋?twin 鏉ヨ嚜 renderer noise銆?* 缂撹В锛氶槇鍊肩粦瀹氬悓鍙傛暟澶嶈窇鏈€澶у櫔澹帮紱淇濆瓨閫愬抚 hash 涓庨娆″垎姝ц瘉涔︺€?- **椋庨櫓锛氱墿鐞嗗弬鏁版槸闅愯棌鑴氭湰寮€鍏炽€?* 缂撹В锛氬彧鍏佽鍏峰 simulator 鍘熺敓鐗╃悊璇箟鐨勫弬鏁板潡锛涙嫆缁?action-indexed 鏉′欢閫昏緫銆?- **椋庨櫓锛歵op-K 鍔ㄤ綔涓嶇湡姝ｅ彲鎵ц銆?* 缂撹В锛氬€欓€夊繀椤绘潵鑷喕缁撶瓥鐣ヤ笖閫氳繃 IK/workspace/control-limit 妫€鏌ワ紱鎶ュ憡 eligibility coverage銆?- **椋庨櫓锛氶殢鏈?fuzzing 宸茶冻澶熴€?* 缂撹В锛歮atched simulator-call 棰勭畻姣旇緝锛沜ompiler 鐨勬柊棰栨€т互鍚堟硶 pair yield 涓庤法鏂规硶 transfer 涓哄噯銆?- **椋庨櫓锛氱幇鏈夊弽棣堟柟娉曢毦浠ュ畬鏁村鐜般€?* 缂撹В锛氬厛瀹屾垚涓庢柟娉曟棤鍏崇殑 C1锛汢2 浣跨敤瀹樻柟瀹炵幇浼樺厛锛屾帴鍙ｇ瓑浠峰鐜板繀椤诲崟鍒楄€屼笉鍐掑厖瀹樻柟缁撴灉銆?
## Final Checklist

- [x] 涓诲紶涓嶈秴杩囦袱涓?- [x] novelty 鐢?compiler 浜х巼涓庡垹闄ゅ疄楠岀洿鎺ラ殧绂?- [x] 鏍囧噯 lower bound 涓嶈浣滃垱鏂?- [x] E0 鏈夌‖鍋滄鏉′欢
- [x] GPU 浠呭湪 compiler premise 閫氳繃鍚庝娇鐢?- [x] 涓嶄娇鐢ㄨЕ瑙?- [x] 鎵€鏈夎繙绔暟鎹檺瀹氬湪涓汉鐩綍
- [ ] 涓ゅ钩鍙?deterministic replay 宸查€氳繃
- [ ] 鑷姩 compiler E0 宸查€氳繃
- [ ] correction-harm 鍦?held-out 鏂规硶涓婃垚绔?