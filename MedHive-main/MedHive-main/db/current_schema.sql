-- 1. Create an enum for your roles
CREATE TYPE user_role AS ENUM (
  'admin',
  'data_provider',
  'contributor',
  'user'
);
-- User Profiles table
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role user_role NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    full_name TEXT,
    phone TEXT,
    organization TEXT
);

-- ML Models table
CREATE TABLE ml_models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL, -- e.g., 'ecg', 'pneumonia', 'breast_cancer', etc.
    version VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, archived
    model_path TEXT, -- path to the model file or URL
    huggingface_id VARCHAR(255), -- ID for model on Hugging Face
    accuracy FLOAT,
    f1_score FLOAT,
    precision_score FLOAT,
    recall_score FLOAT,
    created_by UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Datasets table
CREATE TABLE datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    data_provider_id UUID REFERENCES auth.users(id) ON DELETE CASCADE, -- Reference to the data provider
    size_bytes BIGINT,
    num_samples INTEGER,
    data_type VARCHAR(50), -- e.g., 'image', 'time_series', 'tabular'
    metadata JSONB, -- Additional metadata about the dataset
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Federated Learning Rounds
CREATE TABLE fl_rounds (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES ml_models(id),
    round_number INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, failed
    aggregated_model_path TEXT, -- path to the aggregated model
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Federated Learning Participants
CREATE TABLE fl_participants (
    id SERIAL PRIMARY KEY,
    round_id INTEGER REFERENCES fl_rounds(id),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'invited', -- invited, accepted, declined, completed
    local_model_path TEXT, -- path to the locally trained model
    training_metrics JSONB, -- metrics from local training
    training_start TIMESTAMP WITH TIME ZONE,
    training_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Model Performance History
CREATE TABLE model_performance (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES ml_models(id),
    round_id INTEGER REFERENCES fl_rounds(id),
    accuracy FLOAT,
    f1_score FLOAT,
    precision_score FLOAT,
    recall_score FLOAT,
    loss FLOAT,
    test_dataset_id INTEGER REFERENCES datasets(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chat History
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_user BOOLEAN NOT NULL, -- true if message is from user, false if from assistant
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
