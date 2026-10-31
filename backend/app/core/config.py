import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


# Reliably locate and load backend/.env and root .env regardless of working directory
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(BACKEND_DIR.parent / ".env")
load_dotenv()


import re


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _clean_str(val: str | None, default: str = "") -> str:
    if not val:
        return default
    cleaned = val.strip().strip("'\"")
    return cleaned if cleaned else default


def _normalize_notion_id(value: str | None) -> str:
    if not value:
        return ""
    match = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}|[0-9a-fA-F]{32})", value)
    if match:
        raw = match.group(1).replace("-", "")
        return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
    return value.strip()


class Settings(BaseModel):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "ResolveAI")
    VERSION: str = "1.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Gemma API (supports Gemini / Gemma endpoints)
    GEMMA_API_KEY: str = os.getenv("GEMMA_API_KEY", "")
    USE_MOCK_GEMMA_IF_NO_KEY: bool = _env_bool("USE_MOCK_GEMMA_IF_NO_KEY", True)

    # n8n Webhook Target
    N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "")
    SIMULATE_N8N_IF_OFFLINE: bool = _env_bool("SIMULATE_N8N_IF_OFFLINE", True)

    # Hybrid text / visual duplicate thresholds. They are intentionally
    # configuration rather than magic constants so campus teams can tune them.
    SEMANTIC_SIMILARITY_THRESHOLD: float = float(os.getenv("SEMANTIC_SIMILARITY_THRESHOLD", "0.50"))
    HYBRID_DUPLICATE_THRESHOLD: float = float(os.getenv("HYBRID_DUPLICATE_THRESHOLD", "0.58"))
    VISUAL_DUPLICATE_THRESHOLD: float = float(os.getenv("VISUAL_DUPLICATE_THRESHOLD", "0.88"))

    # Upload protection and OpenCV normalisation.
    MAX_IMAGES_PER_CASE: int = int(os.getenv("MAX_IMAGES_PER_CASE", "4"))
    MAX_IMAGE_BYTES: int = int(os.getenv("MAX_IMAGE_BYTES", str(8 * 1024 * 1024)))
    MAX_IMAGE_PIXELS: int = int(os.getenv("MAX_IMAGE_PIXELS", str(24_000_000)))
    MAX_IMAGE_DIMENSION: int = int(os.getenv("MAX_IMAGE_DIMENSION", "1920"))
    MIN_IMAGE_DIMENSION: int = int(os.getenv("MIN_IMAGE_DIMENSION", "48"))
    BLUR_VARIANCE_THRESHOLD: float = float(os.getenv("BLUR_VARIANCE_THRESHOLD", "18"))
    SUBMISSION_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("SUBMISSION_RATE_LIMIT_PER_MINUTE", "20"))

    # Cloudinary credentials are supplied only by the deployment environment.
    CLOUDINARY_CLOUD_NAME: str = Field(default_factory=lambda: _clean_str(os.getenv("CLOUDINARY_CLOUD_NAME")))
    CLOUDINARY_API_KEY: str = Field(default_factory=lambda: _clean_str(os.getenv("CLOUDINARY_API_KEY")))
    CLOUDINARY_API_SECRET: str = Field(default_factory=lambda: _clean_str(os.getenv("CLOUDINARY_API_SECRET")))
    CLOUDINARY_URL: str = Field(default_factory=lambda: _clean_str(os.getenv("CLOUDINARY_URL"), ""))
    CLOUDINARY_FOLDER_PREFIX: str = Field(default_factory=lambda: _clean_str(os.getenv("CLOUDINARY_FOLDER_PREFIX"), "resolveai-evidence"))

    # Notion documentation sync: accepts both NOTION_API_KEYS and NOTION_API_KEY
    NOTION_API_KEYS: str = Field(default_factory=lambda: _clean_str(os.getenv("NOTION_API_KEYS") or os.getenv("NOTION_API_KEY"), ""))
    NOTION_API_KEY: str = Field(default_factory=lambda: _clean_str(os.getenv("NOTION_API_KEYS") or os.getenv("NOTION_API_KEY"), ""))
    NOTION_PARENT_PAGE_ID: str = Field(default_factory=lambda: _normalize_notion_id(_clean_str(os.getenv("NOTION_PARENT_PAGE_ID"), "")))
    NOTION_DATABASE_ID: str = Field(default_factory=lambda: _normalize_notion_id(os.getenv("NOTION_DATABASE_ID", "")))
    NOTION_DOCUMENTATION_PAGE_ID: str = Field(default_factory=lambda: _normalize_notion_id(os.getenv("NOTION_DOCUMENTATION_PAGE_ID", "")))

    # Set this in deployments to require a server-side admin credential for
    # state mutations and documentation synchronisation. In the hackathon demo
    # it is intentionally empty to preserve the existing no-login workflow.
    ADMIN_API_TOKEN: str = os.getenv("ADMIN_API_TOKEN", "")

    # Role-based demo credentials (configurable via environment variables)
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin_resolve")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "MapleFox47")
    TESTER_USERNAME: str = os.getenv("TESTER_USERNAME", "tester_resolve")
    TESTER_PASSWORD: str = os.getenv("TESTER_PASSWORD", "OrbitPanda82")

    # Session authentication secret & cookie configuration
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "resolveai-demo-secret-key-2026")
    COOKIE_SECURE: bool = _env_bool("COOKIE_SECURE", os.getenv("ENVIRONMENT", "development") == "production")


# Normalize dashboard-added quotes before the SDK reads its environment at import.
if "CLOUDINARY_URL" in os.environ:
    os.environ["CLOUDINARY_URL"] = _clean_str(os.environ["CLOUDINARY_URL"])

settings = Settings()
