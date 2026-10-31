"""Backend-mediated Cloudinary evidence uploads with atomic batch cleanup."""
from __future__ import annotations

import asyncio
import io
import logging
import uuid
from datetime import datetime, timezone
from typing import Iterable, List
from urllib.parse import unquote, urlsplit

from app.core.config import settings
from app.models.schemas import ProblemImage
from app.services.image_processing_service import PreparedImage

logger = logging.getLogger(__name__)


class CloudinaryStorageError(RuntimeError):
    pass


class CloudinaryStorageService:
    @staticmethod
    def _clean(value: str | None) -> str:
        return (value or "").strip().strip("'\"").strip()

    @classmethod
    def _credentials(cls) -> dict[str, str]:
        url = cls._clean(settings.CLOUDINARY_URL)
        if url:
            try:
                parsed = urlsplit(url)
                if parsed.scheme != "cloudinary" or not all((parsed.hostname, parsed.username, parsed.password)):
                    raise ValueError()
                return {"cloud_name": parsed.hostname, "api_key": unquote(parsed.username),
                        "api_secret": unquote(parsed.password)}
            except ValueError:
                raise CloudinaryStorageError(
                    "Invalid CLOUDINARY_URL. Set cloudinary://API_KEY:API_SECRET@CLOUD_NAME in Render, "
                    "or remove it and set the three CLOUDINARY credential variables."
                ) from None
        credentials = {"cloud_name": cls._clean(settings.CLOUDINARY_CLOUD_NAME),
                       "api_key": cls._clean(settings.CLOUDINARY_API_KEY),
                       "api_secret": cls._clean(settings.CLOUDINARY_API_SECRET)}
        missing = [f"CLOUDINARY_{key.upper()}" for key, value in credentials.items() if not value]
        if missing:
            raise CloudinaryStorageError("Image storage is not configured. Set " + ", ".join(missing) + " in Render.")
        return credentials

    @classmethod
    def is_configured(cls) -> bool:
        try:
            cls._credentials()
            return True
        except CloudinaryStorageError:
            return False

    @classmethod
    def get_configuration_status(cls) -> dict[str, object]:
        has_url = bool(cls._clean(settings.CLOUDINARY_URL))
        fields = {"cloud_name": bool(cls._clean(settings.CLOUDINARY_CLOUD_NAME)) or has_url,
                  "api_key": bool(cls._clean(settings.CLOUDINARY_API_KEY)) or has_url,
                  "api_secret": bool(cls._clean(settings.CLOUDINARY_API_SECRET)) or has_url}
        return {"configured": cls.is_configured(),
                **{f"has_{key}": value for key, value in fields.items()},
                "missing_credentials": [f"CLOUDINARY_{key.upper()}" for key, value in fields.items() if not value]}

    @staticmethod
    def _failure_message(exc: Exception) -> str:
        # Never expose provider exception text: it can contain credentials/signatures.
        message = str(exc).lower()
        if any(term in message for term in ("401", "403", "api_key", "api key", "signature", "unauthorized", "cloud name")):
            return "Cloudinary rejected the storage credentials. Update CLOUDINARY_URL or the three Cloudinary variables in Render."
        return "Image storage is temporarily unavailable. Your report was not submitted; please retry with your photos."

    @classmethod
    def verify_connection(cls) -> dict[str, object]:
        try:
            credentials = cls._credentials()
            import cloudinary.api
            result = cloudinary.api.ping(**credentials, secure=True, timeout=20)
            return {"connected": True, "status": result.get("status", "ok")}
        except CloudinaryStorageError as exc:
            return {"connected": False, "reason": str(exc)}
        except Exception as exc:
            return {"connected": False, "error": cls._failure_message(exc)}

    @classmethod
    async def upload_images(cls, case_id: str, images: Iterable[PreparedImage]) -> List[ProblemImage]:
        images = list(images)
        if not images:
            return []
        return await asyncio.to_thread(cls._upload_images_sync, case_id, images)

    @classmethod
    def _upload_images_sync(cls, case_id: str, images: List[PreparedImage]) -> List[ProblemImage]:
        credentials = cls._credentials()
        uploaded_ids: list[str] = []
        assets: List[ProblemImage] = []
        try:
            import cloudinary.uploader
            import cloudinary.utils
            for image in images:
                image_id = uuid.uuid4().hex
                prefix = cls._clean(settings.CLOUDINARY_FOLDER_PREFIX) or "resolveai-evidence"
                result = cloudinary.uploader.upload(
                    io.BytesIO(image.content), public_id=f"{prefix}/{case_id}/{image_id}",
                    resource_type="image", overwrite=False, unique_filename=False, use_filename=False,
                    context={"case_id": case_id, "source": "resolveai"},
                    **credentials, secure=True, timeout=30,
                )
                uploaded_ids.append(result["public_id"])
                if not result.get("secure_url", "").startswith("https://"):
                    raise ValueError("Image provider did not return an HTTPS URL")
                thumbnail, _ = cloudinary.utils.cloudinary_url(
                    result["public_id"], cloud_name=credentials["cloud_name"], secure=True,
                    version=result.get("version"),
                    transformation=[{"width": 480, "height": 320, "crop": "fill", "quality": "auto", "fetch_format": "auto"}],
                )
                assets.append(ProblemImage(
                    id=image_id, public_id=result["public_id"], secure_url=result["secure_url"],
                    thumbnail_url=thumbnail, original_filename=image.original_filename,
                    content_type=image.content_type, byte_size=len(image.content), width=image.width,
                    height=image.height, perceptual_hash=image.perceptual_hash,
                    blur_variance=image.blur_variance, quality_warning=image.quality_warning,
                    uploaded_at=datetime.now(timezone.utc).isoformat(), visual_analysis=image.visual_analysis,
                ))
            return assets
        except Exception as exc:
            for public_id in uploaded_ids:
                try:
                    cloudinary.uploader.destroy(public_id, resource_type="image", invalidate=True, **credentials, timeout=20)
                except Exception:
                    logger.error("Evidence rollback failed; orphaned asset requires cleanup: %s", public_id)
            logger.warning("Evidence upload failed (%s)", type(exc).__name__)
            raise CloudinaryStorageError(cls._failure_message(exc)) from None

    @classmethod
    async def delete_images(cls, images: Iterable[ProblemImage]) -> None:
        await asyncio.to_thread(cls._delete_images_sync, list(images))

    @classmethod
    def _delete_images_sync(cls, images: List[ProblemImage]) -> None:
        # Existing inline records have no remote asset to delete.
        remote = [image for image in images if not image.secure_url.startswith("data:")]
        if not remote:
            return
        credentials = cls._credentials()
        try:
            import cloudinary.uploader
            for image in remote:
                result = cloudinary.uploader.destroy(image.public_id, resource_type="image", invalidate=True,
                                                     **credentials, timeout=20)
                if result.get("result") not in {"ok", "not found"}:
                    raise ValueError("Provider did not confirm deletion")
        except Exception:
            raise CloudinaryStorageError("Image storage could not confirm deletion. Evidence was retained; please retry.") from None
