import torch
import sys
p = torch.load(sys.argv[1], map_location="cpu")
print(type(p).__name__)
print(list(p.keys()) if isinstance(p, dict) else None)
if isinstance(p, dict) and "state_dict" in p:
    print(list(p["state_dict"].keys())[:20])
