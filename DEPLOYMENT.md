# Deployment Guide

This project is prepared for free Streamlit-style deployment on Hugging Face Spaces.

## Option A — Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Option B — Deploy to Hugging Face Spaces

1. Create a new Hugging Face Space.
2. Select **Streamlit** as the Space SDK.
3. Upload/push this repository to the Space.
4. Keep these files in the repository root:
   - `README.md`
   - `requirements.txt`
   - `app.py`
   - `models/keras_job_scam_model.weights.h5`
   - `models/vectorizer_vocabulary.txt`
   - `models/model_config.json`
   - `models/threshold_config.json`
   - `src/`
   - `app/`
5. The Space should read the README metadata and run `app.py`.

## GitHub Push Checklist

```bash
git init
git add .
git commit -m "Initial AI job scam detector project"
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```

The dataset CSV and virtual environment are ignored by `.gitignore`.


## Deployment Notes

Do not upload the raw dataset, virtual environment, notebook checkpoints, or baseline pickle model. The Streamlit app only needs the Keras weights, vocabulary, model config, and threshold config.
