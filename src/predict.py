"""Prediction utilities for the job scam detector."""

from __future__ import annotations

from src.risk_rules import detect_warning_signs


def predict_job_risk(
    job_text: str,
    model,
    low_threshold: float = 0.5,
    high_threshold: float = 0.9345,
) -> dict:
    """Predict risk level and warning signs for a job posting."""
    import tensorflow as tf  # Lazy import keeps Streamlit startup lighter.

    clean_text = job_text.strip()
    job_tensor = tf.convert_to_tensor([clean_text], dtype=tf.string)
    scam_probability = float(model.predict(job_tensor, verbose=0)[0][0])

    if scam_probability >= high_threshold:
        risk_level = "High Risk"
        prediction = "Likely Scam"
    elif scam_probability >= low_threshold:
        risk_level = "Medium Risk"
        prediction = "Suspicious"
    else:
        risk_level = "Low Risk"
        prediction = "Likely Legitimate"

    warning_signs = detect_warning_signs(clean_text)

    return {
        "prediction": prediction,
        "risk_level": risk_level,
        "scam_probability": round(scam_probability, 4),
        "warning_signs": warning_signs,
    }
