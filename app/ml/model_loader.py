import joblib
from pathlib import Path
import logging

LOG = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).parent / "iot_rf_model_balanced_with_medians_normalized.pkl"

_bundle = None

def load_bundle():
    global _bundle
    if _bundle is not None:
        return _bundle
    if not MODEL_PATH.exists():
        LOG.error("Model bundle not found at %s", MODEL_PATH)
        raise FileNotFoundError(MODEL_PATH)
    _bundle = joblib.load(MODEL_PATH)
    # basic sanity
    for k in ("model", "scaler", "features", "medians"):
        if k not in _bundle:
            raise KeyError(f"Bundle missing key: {k}")
    LOG.info("ML model loaded from %s", MODEL_PATH)
    return _bundle

def get_model_objects():
    b = load_bundle()
    return b["model"], b["scaler"], b["features"], b["medians"]