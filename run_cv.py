import pickle
import numpy as np
from src.config import Paths
from src.evaluation.cross_validation import cross_validate_autoencoder, print_cv_summary

paths = Paths.auto()

with open(paths.outputs_dir / "prepared.pkl", "rb") as f:
    prep = pickle.load(f)

# Run 5-fold CV on autoencoder
results = cross_validate_autoencoder(
    X=prep.X_train,
    input_dim=prep.input_dim,
    hidden_dim=256,
    latent_dim=64,
    n_folds=5,
    epochs=15,  # fewer epochs to keep it fast
    device="cpu"
)

print_cv_summary(results, model_name="Autoencoder")