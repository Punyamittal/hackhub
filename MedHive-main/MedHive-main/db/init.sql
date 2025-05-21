-- Create a separate database for MLflow
CREATE DATABASE mlflow;

-- Connect to the HachathonHub database
\c HachathonHub

-- Enable the vector extension for FAISS-like functionality
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the tables as defined in our schema
-- Include the schema.sql file content here
\i /docker-entrypoint-initdb.d/schema.sql 