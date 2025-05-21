-- HachathonHub Database Schema

-- User Roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default roles
INSERT INTO roles (name, description) VALUES 
    ('admin', 'System administrators with full access'),
    ('data_provider', 'Hospitals and research centers that provide data'),
    ('contributor', 'Users who contribute computing resources for training'),
    ('user', 'Regular users who consume AI insights');

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    organization VARCHAR(255),
    role_id INTEGER REFERENCES roles(id),
    active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
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
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Datasets table
CREATE TABLE datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    data_provider_id UUID REFERENCES users(id), -- Reference to the data provider
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
    user_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'invited', -- invited, accepted, declined, completed
    local_model_path TEXT, -- path to the locally trained model
    training_metrics JSONB, -- metrics from local training
    training_start TIMESTAMP WITH TIME ZONE,
    training_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chat History
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    message TEXT NOT NULL,
    is_user BOOLEAN NOT NULL, -- true if message is from user, false if from assistant
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
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

-- Vector Store for RAG
CREATE TABLE vector_embeddings (
    id SERIAL PRIMARY KEY,
    content_id VARCHAR(255) NOT NULL, -- reference to the content this embedding represents
    content_type VARCHAR(50) NOT NULL, -- e.g., 'medical_document', 'research_paper', 'clinical_guideline'
    embedding VECTOR(1536), -- vector embedding of the content
    content TEXT, -- the actual content for retrieval
    metadata JSONB, -- additional metadata about the content
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_models_type ON ml_models(type);
CREATE INDEX idx_models_status ON ml_models(status);
CREATE INDEX idx_datasets_provider ON datasets(data_provider_id);
CREATE INDEX idx_fl_rounds_model ON fl_rounds(model_id);
CREATE INDEX idx_fl_participants_round ON fl_participants(round_id);
CREATE INDEX idx_fl_participants_user ON fl_participants(user_id);
CREATE INDEX idx_chat_history_user ON chat_history(user_id);
CREATE INDEX idx_model_performance_model ON model_performance(model_id);
CREATE INDEX idx_vector_embeddings_content ON vector_embeddings(content_id, content_type); 