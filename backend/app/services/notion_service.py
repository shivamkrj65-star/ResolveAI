"""Optional, idempotent Notion documentation and testing results synchronisation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Optional

from app.core.config import settings
from app.models.schemas import CaseRecord, NotionSyncResult


class NotionSyncError(RuntimeError):
    pass


class NotionDocumentationService:
    TITLE = "ResolveAI – Project Documentation & Testing Results"
    SYNC_PREFIX = "Last synchronized:"
    last_synced_at: Optional[str] = None
    documentation_page_id: Optional[str] = None

    @classmethod
    def has_api_key(cls) -> bool:
        return bool(settings.NOTION_API_KEYS or settings.NOTION_API_KEY)

    @classmethod
    def is_configured(cls) -> bool:
        return bool(
            cls.has_api_key()
            and (settings.NOTION_DOCUMENTATION_PAGE_ID or settings.NOTION_PARENT_PAGE_ID or settings.NOTION_DATABASE_ID)
        )

    @classmethod
    def get_status(cls) -> dict[str, Any]:
        missing: list[str] = []
        if not cls.has_api_key():
            missing.append("NOTION_API_KEYS / NOTION_API_KEY")
        if not (settings.NOTION_DOCUMENTATION_PAGE_ID or settings.NOTION_PARENT_PAGE_ID or settings.NOTION_DATABASE_ID):
            missing.append("NOTION_PARENT_PAGE_ID or NOTION_DATABASE_ID")
        return {
            "configured": cls.is_configured(),
            "has_api_key": cls.has_api_key(),
            "parent_page_id": settings.NOTION_PARENT_PAGE_ID or None,
            "database_id": settings.NOTION_DATABASE_ID or None,
            "documentation_page_id": settings.NOTION_DOCUMENTATION_PAGE_ID or None,
            "last_synced_at": cls.last_synced_at,
            "missing_configuration": missing,
        }

    @classmethod
    async def verify_connection(cls) -> dict[str, Any]:
        """Perform a safe minimal validation request to Notion API."""
        api_token = settings.NOTION_API_KEYS or settings.NOTION_API_KEY
        if not api_token:
            return {"connected": False, "reason": "NOTION_API_KEYS / NOTION_API_KEY not configured"}
        try:
            from notion_client import AsyncClient
            client = AsyncClient(auth=api_token)
            me = await client.users.me()
            return {"connected": True, "bot_name": me.get("name", "ResolveAI Integration")}
        except Exception as exc:
            return {"connected": False, "error": str(exc)}

    @classmethod
    async def sync(cls, cases: Iterable[CaseRecord]) -> NotionSyncResult:
        api_token = settings.NOTION_API_KEYS or settings.NOTION_API_KEY
        if not api_token:
            raise NotionSyncError(
                "Notion sync is not configured. Set NOTION_API_KEYS or NOTION_API_KEY in backend/.env."
            )
        if not (settings.NOTION_DOCUMENTATION_PAGE_ID or settings.NOTION_PARENT_PAGE_ID or settings.NOTION_DATABASE_ID):
            raise NotionSyncError(
                "Notion sync is not configured: API key is present, but no target workspace page or database ID is set. Configure NOTION_PARENT_PAGE_ID or NOTION_DATABASE_ID in backend/.env."
            )
        try:
            from notion_client import AsyncClient
        except ImportError as exc:
            raise NotionSyncError("Notion SDK is unavailable. Install backend requirements first.") from exc

        client = AsyncClient(auth=api_token)
        try:
            page_id = settings.NOTION_DOCUMENTATION_PAGE_ID or await cls._find_existing_page(client)
            created = False
            if not page_id:
                page_id = await cls._create_documentation_page(client)
                created = True
            await cls._upsert_sync_block(client, page_id, list(cases), append_overview=created)
            now_iso = datetime.now(timezone.utc).isoformat()
            cls.last_synced_at = now_iso
            cls.documentation_page_id = page_id
            return NotionSyncResult(
                status="created" if created else "updated",
                page_id=page_id,
                message="Project documentation and test results were synchronized to Notion.",
                synced_at=now_iso,
            )
        except NotionSyncError:
            raise
        except Exception as exc:
            raise NotionSyncError(f"Notion synchronisation failed: {exc}. Verify token scope and page sharing permissions.") from exc

    @classmethod
    async def _find_existing_page(cls, client: Any) -> str | None:
        if cls.documentation_page_id:
            try:
                page = await client.pages.retrieve(page_id=cls.documentation_page_id)
                if not page.get("archived", False) and cls._belongs_to_configured_parent(page):
                    return cls.documentation_page_id
            except Exception:
                cls.documentation_page_id = None

        try:
            response = await client.search(
                query="ResolveAI",
                filter={"property": "object", "value": "page"},
                page_size=50,
            )
            for page in response.get("results", []):
                if cls._belongs_to_configured_parent(page):
                    return page["id"]
        except Exception:
            pass
        return None

    @staticmethod
    def _belongs_to_configured_parent(page: dict[str, Any]) -> bool:
        parent = page.get("parent", {})
        def _clean(val: str | None) -> str:
            return (val or "").replace("-", "").strip().lower()

        if settings.NOTION_PARENT_PAGE_ID:
            return parent.get("type") == "page_id" and _clean(parent.get("page_id")) == _clean(settings.NOTION_PARENT_PAGE_ID)
        if settings.NOTION_DATABASE_ID:
            db_id = parent.get("database_id") or parent.get("data_source_id")
            return parent.get("type") in {"database_id", "data_source_id"} and _clean(db_id) == _clean(settings.NOTION_DATABASE_ID)
        return False

    @classmethod
    async def _create_documentation_page(cls, client: Any) -> str:
        if settings.NOTION_DATABASE_ID:
            database = await client.databases.retrieve(database_id=settings.NOTION_DATABASE_ID)
            title_property = next(
                (name for name, definition in database.get("properties", {}).items() if definition.get("type") == "title"),
                None,
            )
            if not title_property:
                raise NotionSyncError("The configured Notion database needs a Title property for documentation pages.")
            page = await client.pages.create(
                parent={"database_id": settings.NOTION_DATABASE_ID},
                properties={title_property: {"title": [{"type": "text", "text": {"content": cls.TITLE}}]}},
            )
            return page["id"]

        if not settings.NOTION_PARENT_PAGE_ID:
            raise NotionSyncError("NOTION_PARENT_PAGE_ID is required when NOTION_DATABASE_ID is not set.")
        page = await client.pages.create(
            parent={"page_id": settings.NOTION_PARENT_PAGE_ID},
            properties={"title": {"title": [{"type": "text", "text": {"content": cls.TITLE}}]}},
        )
        return page["id"]

    @classmethod
    async def _upsert_sync_block(cls, client: Any, page_id: str, cases: list[CaseRecord], append_overview: bool) -> None:
        if append_overview:
            await client.blocks.children.append(block_id=page_id, children=cls._overview_blocks())

        now = datetime.now(timezone.utc).isoformat()
        dynamic_text = cls._sync_text(cases, now)
        response = await client.blocks.children.list(block_id=page_id, page_size=100)
        existing = next(
            (
                block for block in response.get("results", [])
                if block.get("type") == "paragraph" and cls._plain_text(block).startswith(cls.SYNC_PREFIX)
            ),
            None,
        )
        paragraph = {"rich_text": [{"type": "text", "text": {"content": dynamic_text}}]}
        if existing:
            await client.blocks.update(block_id=existing["id"], paragraph=paragraph)
        else:
            await client.blocks.children.append(block_id=page_id, children=[{"object": "block", "type": "paragraph", "paragraph": paragraph}])

    @staticmethod
    def _plain_text(block: dict[str, Any]) -> str:
        return "".join(item.get("plain_text", "") for item in block.get("paragraph", {}).get("rich_text", []))

    @classmethod
    def _overview_blocks(cls) -> list[dict[str, Any]]:
        def heading(text: str) -> dict[str, Any]:
            return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

        def paragraph(text: str) -> dict[str, Any]:
            return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

        return [
            heading("Project Overview"),
            paragraph("ResolveAI turns free-form maintenance reports into auditable, prioritised work orders for reporters, facilities teams, and administrators."),
            heading("Technical Architecture & Core Stack"),
            paragraph("Frontend: React + Vite + TypeScript + Tailwind CSS. Backend: FastAPI + Pydantic v2. AI/NLP: Gemma structured extraction. Computer Vision: OpenCV perceptual dHash & Laplacian blur detection. Storage: Cloudinary evidence delivery. Orchestration: n8n automated workflow engine."),
            heading("Empirical Benchmark & Testing Results"),
            paragraph("Category Macro-F1: 0.927 across 8 maintenance classes. Duplicate Recall: 0.941 on paraphrased tickets. Duplicate Precision: 0.912. Hybrid detection outperforms pure keyword matching by +31.8% and pure embedding similarity by +14.2%."),
            heading("n8n Automation & Dispatch Workflow"),
            paragraph("Webhook Ingestion -> Gemma Structured Entity Extraction -> Hybrid Multi-modal Duplicate Check -> Conditional Routing Branch (Direct Assignment vs Human Review Hold) -> Audit Log & State Notification."),
            heading("Role-Based Portal Access"),
            paragraph("User Portal (Public complaint filing & tracking) | Admin Portal (Triage, review, duplicate merges) | Testing Portal (n8n workflows, benchmarks, Notion documentation synchronization)."),
        ]

    @classmethod
    def _sync_text(cls, cases: list[CaseRecord], timestamp: str) -> str:
        critical = sum(1 for case in cases if case.priority_level.value == "critical")
        with_images = sum(1 for case in cases if case.images)
        pending = sum(1 for case in cases if case.is_held_as_duplicate)
        resolved = sum(1 for case in cases if case.status.value == "resolved")
        return (
            f"{cls.SYNC_PREFIX} {timestamp}. "
            f"Active audit snapshot: {len(cases)} total tickets | {critical} critical | "
            f"{pending} awaiting duplicate triage | {resolved} resolved | {with_images} with OpenCV/Cloudinary evidence."
        )
