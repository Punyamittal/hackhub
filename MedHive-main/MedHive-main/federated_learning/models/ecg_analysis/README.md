# ECG Analysis Model

This directory contains the implementation of a deep learning model for analyzing ECG (electrocardiogram) data to detect cardiac abnormalities.

## Overview

The model is designed to analyze ECG signals and classify them into normal or abnormal patterns, with sub-classification of various cardiac conditions such as arrhythmias, myocardial infarction, and other heart abnormalities.

## Model Details

- **Architecture**: 1D ResNet with attention mechanism
- **Input**: ECG signal with 12 leads, sampled at 500Hz for 10 seconds
- **Output**: Multi-class classification (normal and 5 abnormality types)
- **Performance**: ~93% accuracy on benchmark datasets

## Training Data Requirements

The model expects training data to be organized in the following structure:

```
data_path/
├── train/
│   ├── normal/
│   │   ├── ecg1.npy
│   │   ├── ecg2.npy
│   │   └── ...
│   ├── arrhythmia/
│   ├── mi/
│   ├── hypertrophy/
│   ├── conduction_defect/
│   └── abnormal/
├── val/
│   ├── normal/
│   ├── ...
└── test/
    ├── normal/
    └── ...
```

Each .npy file should contain a numpy array of shape (12, 5000) representing 12 leads sampled at 500Hz for 10 seconds.

## Files

- `dataset.py` - Dataset implementation for loading and preprocessing ECG signals
- `model.py` - Model architecture definition
- `hyperparams.py` - Hyperparameters for training
- `evaluate.py` - Evaluation functions 