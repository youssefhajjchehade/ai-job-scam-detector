"""Utilities for loading the trained Keras job scam detector."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE_DIR / "models"


def _require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing required model artifact: {path}. "
            "Make sure the models/ directory was committed or restored."
        )


def load_thresholds() -> dict[str, Any]:
    """Load calibrated risk thresholds."""
    threshold_path = MODELS_DIR / "threshold_config.json"
    _require_file(threshold_path)

    with open(threshold_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_job_scam_model():
    """Rebuild the model architecture and load trained weights.

    TensorFlow is imported lazily so the Streamlit page can render faster.
    The first prediction will load the model, then Streamlit caches it.
    """
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

    import tensorflow as tf  # noqa: WPS433 - intentionally lazy import
    from tensorflow import keras  # noqa: WPS433

    layers = keras.layers

    config_path = MODELS_DIR / "model_config.json"
    vocab_path = MODELS_DIR / "vectorizer_vocabulary.txt"
    weights_path = MODELS_DIR / "keras_job_scam_model.weights.h5"

    for path in (config_path, vocab_path, weights_path):
        _require_file(path)

    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)

    with open(vocab_path, "r", encoding="utf-8") as file:
        vocabulary = [line.rstrip("\r\n") for line in file]

    vectorizer = layers.TextVectorization(
        max_tokens=config["max_tokens"],
        output_mode="int",
        output_sequence_length=config["sequence_length"],
        standardize="lower_and_strip_punctuation",
        vocabulary=vocabulary,
    )

    inputs = keras.Input(shape=(), dtype=tf.string, name="job_post_text")
    x = vectorizer(inputs)
    x = layers.Embedding(
        input_dim=config["max_tokens"],
        output_dim=config["embedding_dim"],
        mask_zero=True,
        name="token_embedding",
    )(x)
    x = layers.Bidirectional(layers.LSTM(config["lstm_units"]), name="bilstm")(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(64, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(1, activation="sigmoid", name="scam_probability")(x)

    model = keras.Model(inputs, outputs, name="job_scam_detector")

    # Build the model before loading weights.
    model(tf.convert_to_tensor(["test job post"], dtype=tf.string))
    model.load_weights(weights_path)

    return model
