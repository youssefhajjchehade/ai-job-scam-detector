from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.model_loader import load_job_scam_model, load_thresholds
from src.predict import predict_job_risk


app = FastAPI(
    title="AI Job Scam Detector API",
    description="NLP scam detection API using a trained Keras BiLSTM model.",
    version="1.0.0",
)

model = load_job_scam_model()
thresholds = load_thresholds()

LOW_THRESHOLD = thresholds.get("default_threshold", 0.5)
HIGH_THRESHOLD = thresholds.get("high_risk_threshold", 0.9345)


class JobPostRequest(BaseModel):
    job_text: str = Field(
        min_length=20,
        description="The full job post text to analyze.",
    )


@app.get("/")
def root():
    return {
        "message": "AI Job Scam Detector API is running",
        "model": "Keras BiLSTM",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "model_loaded": model is not None,
    }


@app.post("/predict")
def predict(request: JobPostRequest):
    result = predict_job_risk(
        job_text=request.job_text,
        model=model,
        low_threshold=LOW_THRESHOLD,
        high_threshold=HIGH_THRESHOLD,
    )

    return result