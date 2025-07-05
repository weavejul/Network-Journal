"""
Shared configuration settings for the Network Journal application.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Database Configuration
    NEO4J_URI: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    NEO4J_USER: str = Field(default="neo4j", env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(default="password", env="NEO4J_PASSWORD")
    NEO4J_DATABASE: str = Field(default="neo4j", env="NEO4J_DATABASE")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_PREFIX: str = Field(default="/api/v1", env="API_PREFIX")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # CORS Configuration
    CORS_ORIGINS: list = Field(default=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://127.0.0.1:5176", "http://127.0.0.1:5177", "http://127.0.0.1:5178"], env="CORS_ORIGINS")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    # AI Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    TAVILY_API_KEY: Optional[str] = Field(default=None, env="TAVILY_API_KEY")
    
    # LLM Configuration
    DEFAULT_LLM_PROVIDER: str = Field(default="openai", env="DEFAULT_LLM_PROVIDER")
    DEFAULT_MODEL: str = Field(default="gpt-4o-mini", env="DEFAULT_MODEL")
    MAX_TOKENS: int = Field(default=4000, env="MAX_TOKENS")
    TEMPERATURE: float = Field(default=0.1, env="TEMPERATURE")
    
    # Agent Configuration
    AGENT_RUN_INTERVAL_HOURS: int = Field(default=168, env="AGENT_RUN_INTERVAL_HOURS")  # 1 week
    AGENT_BATCH_SIZE: int = Field(default=10, env="AGENT_BATCH_SIZE")
    AGENT_MAX_SEARCH_RESULTS: int = Field(default=5, env="AGENT_MAX_SEARCH_RESULTS")
    
    # Security Configuration
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_FILE_TYPES: list = Field(default=[".jpg", ".jpeg", ".png", ".pdf"])
    
    # Pagination Configuration
    DEFAULT_PAGE_SIZE: int = Field(default=20, env="DEFAULT_PAGE_SIZE")
    MAX_PAGE_SIZE: int = Field(default=100, env="MAX_PAGE_SIZE")
    
    # Cache Configuration
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    CACHE_TTL_SECONDS: int = Field(default=3600, env="CACHE_TTL_SECONDS")  # 1 hour
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def is_development() -> bool:
    """Check if running in development mode."""
    return settings.DEBUG


def is_production() -> bool:
    """Check if running in production mode."""
    return not settings.DEBUG


def get_database_url() -> str:
    """Get the database connection URL."""
    return f"{settings.NEO4J_URI}"


def get_ai_provider_config() -> dict:
    """Get AI provider configuration."""
    config = {
        "provider": settings.DEFAULT_LLM_PROVIDER,
        "model": settings.DEFAULT_MODEL,
        "max_tokens": settings.MAX_TOKENS,
        "temperature": settings.TEMPERATURE,
    }
    
    if settings.DEFAULT_LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        config["api_key"] = settings.OPENAI_API_KEY
    elif settings.DEFAULT_LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
        config["api_key"] = settings.ANTHROPIC_API_KEY
    
    return config 