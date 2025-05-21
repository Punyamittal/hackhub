# Breast Cancer Detection Model

This directory contains the implementation of a deep learning model for detecting breast cancer from medical imaging data.

## Overview

The model is designed to analyze mammography images and classify them into benign or malignant cases. It uses a convolutional neural network (CNN) architecture optimized for medical image classification.

## Model Details

- **Architecture**: Modified EfficientNet-B3
- **Input**: 512x512 grayscale mammography images
- **Output**: Binary classification (benign/malignant)
- **Performance**: ~90% accuracy on benchmark datasets

## Training Data Requirements

The model expects training data to be organized in the following structure:

```
data_path/
├── train/
│   ├── benign/
│   │   ├── image1.png
│   │   ├── image2.png
│   │   └── ...
│   └── malignant/
│       ├── image1.png
│       ├── image2.png
│       └── ...
├── val/
│   ├── benign/
│   ├── malignant/
└── test/
    ├── benign/
    └── malignant/
```

## Files

- `dataset.py` - Dataset implementation for loading and preprocessing mammography images
- `model.py` - Model architecture definition
- `hyperparams.py` - Hyperparameters for training
- `evaluate.py` - Evaluation functions 