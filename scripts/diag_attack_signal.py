"""Quick diagnostic: attack-context signal strength per family."""
import pickle
import numpy as np
from src.evaluation.evaluate_pipeline import _max_attack_context_signal
from src.config import Paths

paths = Paths.auto()
p = pickle.load(open(paths.outputs_dir / "prepared.pkl", "rb"))
wts = p.windows_test
yt = p.y_test
names = p.feature_channel_names
ind = yt == 2
fam = np.array([w.attack_family for w in wts])

for famname in ["industroyer", "arp-spoof"]:
    m = ind & (fam == famname)
    sigs = [_max_attack_context_signal(wts[i], names) for i in range(len(wts)) if m[i]]
    z = sum(1 for s in sigs if s <= 0)
    print(famname, "n_windows", len(sigs), "zero_signal", z, "max_sig", max(sigs) if sigs else None)
