import argparse, json, pathlib, numpy as np
from state_repair_e0 import _predict

ap=argparse.ArgumentParser(); ap.add_argument('--inputs', required=True); ap.add_argument('--meta', required=True); ap.add_argument('--out', required=True); ap.add_argument('--port', type=int, default=10097); args=ap.parse_args()
from deployment.model_server.tools.websocket_policy_client import WebsocketClientPolicy
d=np.load(args.inputs, allow_pickle=False); m=json.loads(pathlib.Path(args.meta).read_text())
c=WebsocketClientPolicy(host='127.0.0.1', port=args.port); rows=[]
for item in m['records']:
    k=item['key']; arr=[_predict(c,d[f'{k}_primary'],d[f'{k}_wrist'],item['instruction']) for _ in range(3)]
    rows.append({**item, 'pair_l2':[float(np.linalg.norm(arr[i]-arr[0])) for i in (1,2)]})
c.close(); pathlib.Path(args.out).write_text(json.dumps({'schema':'policy-repeat-v1','records':rows},indent=2))
