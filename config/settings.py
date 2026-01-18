"""Configuration settings for the code analyzer."""

from typing import Optional
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings."""
    
    # LLM Configuration (OpenRouter)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")
    
    # Vector Store Configuration
    VECTOR_STORE_TYPE: str = os.getenv("VECTOR_STORE_TYPE", "faiss")  # "faiss" or "chroma"
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    VECTOR_DB_PATH: Path = Path(os.getenv("VECTOR_DB_PATH", "./vector_db"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Code Analysis Configuration
    MAX_FILE_SIZE_MB: float = float(os.getenv("MAX_FILE_SIZE_MB", "10.0"))
    EXCLUDE_PATTERNS: list = [
        "**/__pycache__/**",
        "**/.git/**",
        "**/node_modules/**",
        "**/.venv/**",
        "**/venv/**",
        "**/env/**",
        "**/.pytest_cache/**",
        "**/.mypy_cache/**",
        "**/dist/**",
        "**/build/**",
        "**/*.pyc",
        "**/*.pyo",
        "**/.DS_Store",
    ]
    
    # Agent Configuration
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "20"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))  # Low for more deterministic
    
    # Risk Scoring Weights
    RISK_WEIGHTS: dict = {
        "complexity": 0.3,
        "dependencies": 0.25,
        "dependents": 0.25,
        "size": 0.1,
        "test_coverage": 0.1,  # Placeholder
    }
    
    @classmethod
    def get_vector_db_path(cls) -> Path:
        """Get the vector database path, creating it if needed."""
        cls.VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
        return cls.VECTOR_DB_PATH


# Global settings instance
settings = Settings()
