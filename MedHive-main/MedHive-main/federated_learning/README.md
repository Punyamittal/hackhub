# HachathonHub Federated Learning System

This directory contains the implementation of HachathonHub's federated learning system, which enables collaborative training of healthcare AI models while preserving data privacy.

## Overview

Federated learning is a machine learning approach that trains an algorithm across multiple decentralized devices or servers holding local data samples, without exchanging them. This enables multiple healthcare institutions to collaboratively train models without sharing sensitive patient data.

## Components

### Client

The client component runs on data providers' systems and handles:
- Local model training on private data
- Secure communication with the federated learning server
- Model encryption and decryption

Files:
- `client/client.py` - Main client implementation
- `client/encryption.py` - Encryption utilities for secure model transmission
- `client/local_training.py` - Local model training logic

### Server

The server component coordinates the federated learning process:
- Manages federated learning rounds
- Selects clients for participation
- Aggregates client models
- Evaluates global model performance

Files:
- `server/server.py` - Main server implementation
- `server/aggregator.py` - Model aggregation algorithms
- `server/security.py` - Security management and authentication

### Models

The `models` directory contains implementations for different healthcare AI models:
- Breast Cancer Detection
- ECG Analysis
- Glaucoma Detection
- Pneumonia Detection
- Symptom Analysis

Each model follows a standard structure for compatibility with the federated learning framework.

## Usage

### Server Setup

```bash
# Generate security keys
python -m federated_learning.server.security --generate-keys

# Start the federated learning server
python -m federated_learning.server.server --host 0.0.0.0 --port 5000
```

### Client Setup

```bash
# Start a federated learning client
python -m federated_learning.client.client \
  --client_id "hospital_1" \
  --server_url "https://fl-server.HachathonHub.com" \
  --data_path "/path/to/local/data" \
  --model_type "pneumonia"
```

## Security

The system implements several security measures:
- End-to-end encryption of model parameters
- Authentication and authorization
- Secure key management
- Differential privacy (optional)

## Adding New Models

To add a new model type, follow the structure in the models directory:
1. Create a new directory with the model name
2. Implement standard files: dataset.py, model.py, hyperparams.py, evaluate.py
3. Add documentation

## Requirements

- Python 3.8+
- PyTorch 1.8+
- cryptography
- requests
- jwt
- numpy

## License

This project is licensed under the MIT License - see the LICENSE file for details. 