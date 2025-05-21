# Symptom Analysis Model

This directory contains the implementation of a natural language processing (NLP) model for analyzing patient-reported symptoms and predicting potential medical conditions.

## Overview

The model is designed to process textual descriptions of symptoms and predict possible medical conditions or diseases. It can be used for preliminary triage, assisting healthcare professionals in diagnosis, or providing self-assessment tools for patients.

## Model Details

- **Architecture**: BERT-based model with medical domain adaptation
- **Input**: Text descriptions of symptoms (max 512 tokens)
- **Output**: Probabilities for 50+ common medical conditions
- **Performance**: ~85% top-3 accuracy on benchmark datasets

## Training Data Requirements

The model expects training data to be organized in the following structure:

```
data_path/
├── train.jsonl
├── val.jsonl
└── test.jsonl
```

Each JSONL file should contain records in the following format:
```json
{
  "symptoms": "Patient reports persistent dry cough for 3 weeks, fatigue, mild fever in evenings, and shortness of breath when walking up stairs.",
  "condition": "pneumonia",
  "demographics": {
    "age": 45,
    "sex": "M"
  },
  "additional_info": {
    "smoking_history": true,
    "recent_travel": false
  }
}
```

The `condition` field is required for training, while `demographics` and `additional_info` are optional.

## Files

- `dataset.py` - Dataset implementation for loading and preprocessing symptom text
- `model.py` - Model architecture definition
- `hyperparams.py` - Hyperparameters for training
- `evaluate.py` - Evaluation functions

## Ethical Considerations

This model is intended as a decision support tool and not as a replacement for professional medical diagnosis. Always consult healthcare professionals for proper medical advice.

## References

- Rajkomar A, Dean J, Kohane I. Machine Learning in Medicine. N Engl J Med. 2019
- Rajpurkar P, Chen E, Banerjee O, Topol EJ. AI in health and medicine. Nat Med. 2022 