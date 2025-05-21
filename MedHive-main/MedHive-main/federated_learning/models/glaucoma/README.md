# Glaucoma Detection Model

This directory contains the implementation of a deep learning model for detecting glaucoma from retinal fundus images.

## Overview

The model is designed to analyze retinal fundus images and identify glaucomatous changes, including optic disc and cup changes, which are indicative of glaucoma. Early detection of glaucoma can significantly reduce the risk of permanent vision loss.

## Model Details

- **Architecture**: U-Net++ with DenseNet-121 encoder
- **Input**: 512x512 RGB fundus images
- **Output**: Binary classification (healthy/glaucoma) and segmentation of optic disc and cup
- **Performance**: ~95% sensitivity and ~92% specificity on benchmark datasets

## Training Data Requirements

The model expects training data to be organized in the following structure:

```
data_path/
├── train/
│   ├── images/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── ...
│   ├── masks/
│   │   ├── image1_mask.png
│   │   ├── image2_mask.png
│   │   └── ...
│   └── labels.csv
├── val/
│   ├── images/
│   ├── masks/
│   └── labels.csv
└── test/
    ├── images/
    ├── masks/
    └── labels.csv
```

The labels.csv file should contain the following format:
```
image_name,diagnosis
image1.jpg,0
image2.jpg,1
...
```
Where 0 represents healthy and 1 represents glaucoma.

## Files

- `dataset.py` - Dataset implementation for loading and preprocessing retinal images
- `model.py` - Model architecture definition
- `hyperparams.py` - Hyperparameters for training
- `evaluate.py` - Evaluation functions 