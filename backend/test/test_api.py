import asyncio
import io
import cv2
import numpy as np
import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.models.schemas import ProblemImage
from app.services.cloudinary_service import CloudinaryStorageService
from app.services.image_processing_service import ImageProcessingService

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_public_tracking_endpoint():
    """Students can track their own ticket by ticket number or case ID without login."""
    # RES-2026-101 is one of the initial seed cases
    response = client.get("/api/v1/cases/track/RES-2026-101")
    assert response.status_code == 200
    data = response.json()
    assert data["case_number"] == "RES-2026-101"
    assert "extraction" in data
    assert "status" in data

    # Non-existent ticket returns 404
    missing_resp = client.get("/api/v1/cases/track/RES-9999-999")
    assert missing_resp.status_code == 404


def test_unauthorized_endpoints_blocked():
    """Protected admin and tester endpoints must block unauthenticated requests."""
    unauth_client = TestClient(app)
    # Admin endpoints
    assert unauth_client.get("/api/v1/cases").status_code == 401
    assert unauth_client.post("/api/v1/cases/case_seed_1/decision", json={"decision": "approve"}).status_code == 401
    assert unauth_client.patch("/api/v1/cases/case_seed_1/status", json={"status": "resolved"}).status_code == 401

    # Tester endpoints
    assert unauth_client.get("/api/v1/metrics/benchmark").status_code == 401
    assert unauth_client.get("/api/v1/testing/cases").status_code == 401
    assert unauth_client.post("/api/v1/integrations/notion/sync").status_code == 401
    assert unauth_client.post("/api/v1/reset-demo").status_code == 401


def test_login_invalid_credentials():
    response = client.post("/api/v1/auth/login", json={"username": "wrong_user", "password": "wrong_password"})
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_admin_authentication_and_session_persistence():
    admin_client = TestClient(app)
    # Login with admin demo credentials
    login_resp = admin_client.post(
        "/api/v1/auth/login",
        json={"username": settings.ADMIN_USERNAME, "password": settings.ADMIN_PASSWORD},
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert data["user"]["role"] == "admin"
    assert data["user"]["username"] == settings.ADMIN_USERNAME
    assert data["token"] is not None

    # Verify session persistence via /auth/me using the cookie
    me_resp = admin_client.get("/api/v1/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["authenticated"] is True
    assert me_resp.json()["user"]["role"] == "admin"

    # Admin access to /cases
    cases_resp = admin_client.get("/api/v1/cases")
    assert cases_resp.status_code == 200
    cases = cases_resp.json()
    assert len(cases) >= 3
    numbers = [c["case_number"] for c in cases]
    assert "RES-2026-101" in numbers

    # Logout
    logout_resp = admin_client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 200

    # After logout, /cases must be blocked again
    assert admin_client.get("/api/v1/cases").status_code == 401


def test_tester_authentication_and_benchmark():
    tester_client = TestClient(app)
    # Login with tester demo credentials
    login_resp = tester_client.post(
        "/api/v1/auth/login",
        json={"username": settings.TESTER_USERNAME, "password": settings.TESTER_PASSWORD},
    )
    assert login_resp.status_code == 200
    assert login_resp.json()["user"]["role"] == "tester"

    # Tester access to /metrics/benchmark
    benchmark_resp = tester_client.get("/api/v1/metrics/benchmark")
    assert benchmark_resp.status_code == 200
    data = benchmark_resp.json()
    assert data["category_macro_f1"] > 0.90
    assert "ResolveAI Hybrid (Embeddings + Rules + Time)" in data["ablation_comparison"]

    # Tester access to /testing/cases
    test_cases_resp = tester_client.get("/api/v1/testing/cases")
    assert test_cases_resp.status_code == 200

    # Tester access to /integrations/notion/status
    notion_status_resp = tester_client.get("/api/v1/integrations/notion/status")
    assert notion_status_resp.status_code == 200


def test_role_isolation_enforcement():
    """Verify that admins cannot access tester routes, and testers cannot access admin routes."""
    admin_client = TestClient(app)
    admin_client.post("/api/v1/auth/login", json={"username": settings.ADMIN_USERNAME, "password": settings.ADMIN_PASSWORD})

    tester_client = TestClient(app)
    tester_client.post("/api/v1/auth/login", json={"username": settings.TESTER_USERNAME, "password": settings.TESTER_PASSWORD})

    # Admin attempting tester operations -> 403 Forbidden
    assert admin_client.get("/api/v1/metrics/benchmark").status_code == 403
    assert admin_client.get("/api/v1/testing/cases").status_code == 403
    assert admin_client.post("/api/v1/integrations/notion/sync").status_code == 403
    assert admin_client.post("/api/v1/reset-demo").status_code == 403

    # Tester attempting admin operations -> 403 Forbidden
    assert tester_client.get("/api/v1/cases").status_code == 403
    assert tester_client.post("/api/v1/cases/case_seed_1/decision", json={"decision": "approve"}).status_code == 403
    assert tester_client.patch("/api/v1/cases/case_seed_1/status", json={"status": "in_progress"}).status_code == 403


def test_case_1_unique_complaint():
    """Tests Slide 4 Case 1: Unique public complaint routes directly via n8n."""
    payload = {
        "raw_text": "Severe ceiling fan humming and sparks coming from switchboard in Lab 402, Block C.",
        "student_name": "Test Student",
        "student_email": "test@campus.edu",
        "reported_block": "Block C",
    }
    response = client.post("/api/v1/complaints", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["extraction"]["issue_type"] == "electrical"
    assert data["extraction"]["building_block"] == "Block C"
    assert data["is_held_as_duplicate"] is False
    assert data["status"] == "assigned"
    assert "Electrical" in data["assigned_team"]
    assert data["n8n_dispatch"]["workflow_branch"] == "direct_assignment"


def test_case_2_paraphrased_duplicate_complaint():
    """Tests Slide 4 Case 2:
    Paraphrased complaint of Case 1: 'Leaking pipe near the stairs in block B'
    Must trigger hybrid duplicate detection and hold for human review.
    """
    payload = {
        "raw_text": "Leaking pipe near the stairs in block B causing water all over the walkway",
        "student_name": "Second Witness",
        "student_email": "witness@campus.edu",
        "reported_block": "Block B",
    }
    response = client.post("/api/v1/complaints", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Must flag as duplicate
    assert data["is_held_as_duplicate"] is True
    assert data["status"] == "held_for_review"
    assert len(data["duplicate_candidates"]) > 0
    top_cand = data["duplicate_candidates"][0]
    assert top_cand["overall_hybrid_score"] > 0.60
    assert top_cand["is_duplicate_candidate"] is True
    assert data["n8n_dispatch"]["workflow_branch"] == "duplicate_hold"


def _evidence_bytes() -> bytes:
    """Generate a high-detail JPEG that passes the blur-quality detector."""
    image = np.zeros((160, 220, 3), dtype=np.uint8)
    cv2.rectangle(image, (20, 20), (195, 140), (30, 180, 240), thickness=-1)
    cv2.line(image, (0, 0), (219, 159), (255, 255, 255), thickness=4)
    cv2.putText(image, "LEAK", (45, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok
    return encoded.tobytes()


def test_opencv_image_processing_rejects_non_image_upload():
    upload = UploadFile(filename="not-an-image.jpg", file=io.BytesIO(b"not image bytes"))
    with pytest.raises(ValueError):
        asyncio.run(ImageProcessingService.prepare_upload(upload))


def test_opencv_image_processing_hashes_and_analyzes_valid_image():
    upload = UploadFile(filename="leak.jpg", file=io.BytesIO(_evidence_bytes()))
    prepared = asyncio.run(ImageProcessingService.prepare_upload(upload))
    assert prepared.content_type == "image/jpeg"
    assert len(prepared.perceptual_hash) == 16
    assert prepared.width == 220
    assert prepared.visual_analysis is not None
    assert "brightness" in prepared.visual_analysis
    assert "contrast" in prepared.visual_analysis
    assert "sharpness" in prepared.visual_analysis


def test_multipart_image_submission_uses_processed_evidence(monkeypatch):
    """The endpoint is testable without real cloud credentials; Cloudinary remains required in production."""
    async def fake_upload(case_id, prepared_images):
        return [
            ProblemImage(
                id=f"image_{index}",
                public_id=f"campus-problems/{case_id}/image_{index}",
                secure_url=f"https://example.invalid/{case_id}/{index}.jpg",
                thumbnail_url=f"https://example.invalid/{case_id}/{index}/thumbnail.jpg",
                original_filename=image.original_filename,
                content_type=image.content_type,
                byte_size=len(image.content),
                width=image.width,
                height=image.height,
                perceptual_hash=image.perceptual_hash,
                blur_variance=image.blur_variance,
                quality_warning=image.quality_warning,
                uploaded_at="2026-10-25T00:00:00+00:00",
                visual_analysis=image.visual_analysis,
            )
            for index, image in enumerate(prepared_images)
        ]

    monkeypatch.setattr(CloudinaryStorageService, "upload_images", staticmethod(fake_upload))
    response = client.post(
        "/api/v1/complaints",
        data={
            "raw_text": "Overflowing water from a pipe in Block C ground floor corridor.",
            "reported_block": "Block C",
            "affected_people": "40",
        },
        files=[("images", ("leak.jpg", _evidence_bytes(), "image/jpeg"))],
    )
    assert response.status_code == 200
    created = response.json()
    assert len(created["images"]) == 1
    assert created["images"][0]["perceptual_hash"]
    assert created["images"][0]["visual_analysis"]["sharpness"] > 0
    assert created["priority_score"] >= created["extraction"]["estimated_priority_score"]

    tracked = client.get(f"/api/v1/cases/track/{created['case_number']}")
    assert tracked.status_code == 200
    assert tracked.json()["images"] == created["images"]
    admin = TestClient(app)
    login = admin.post("/api/v1/auth/login", json={
        "username": settings.ADMIN_USERNAME, "password": settings.ADMIN_PASSWORD,
    })
    assert login.status_code == 200
    listing = admin.get("/api/v1/cases")
    assert listing.status_code == 200
    listed = next(case for case in listing.json() if case["id"] == created["id"])
    assert listed["images"] == created["images"]


def test_notion_sync_without_credentials_raises_graceful_error(monkeypatch):
    """When Notion credentials are not configured, sync fails gracefully with clear error without crashing."""
    monkeypatch.setattr(settings, "NOTION_API_KEY", "")
    monkeypatch.setattr(settings, "NOTION_API_KEYS", "")
    tester_client = TestClient(app)
    tester_client.post("/api/v1/auth/login", json={"username": settings.TESTER_USERNAME, "password": settings.TESTER_PASSWORD})
    response = tester_client.post("/api/v1/integrations/notion/sync")
    assert response.status_code == 503
    assert "Notion sync is not configured" in response.json()["detail"]


def test_cloudinary_and_notion_environment_variable_loading(monkeypatch):
    """Verify backend configuration cleanly loads CLOUDINARY_API_KEY and NOTION_API_KEYS."""
    test_c_key = "test_cloudinary_key_123"
    test_n_keys = "secret_notion_test_key_456"
    monkeypatch.setenv("CLOUDINARY_API_KEY", test_c_key)
    monkeypatch.setenv("NOTION_API_KEYS", test_n_keys)

    from app.core.config import Settings
    custom_settings = Settings()
    assert custom_settings.CLOUDINARY_API_KEY == test_c_key
    assert custom_settings.NOTION_API_KEYS == test_n_keys
    assert custom_settings.NOTION_API_KEY == test_n_keys


def test_cloudinary_missing_credentials_reported(monkeypatch):
    """When only CLOUDINARY_API_KEY is present, missing cloud_name and api_secret are reported cleanly."""
    monkeypatch.setattr(settings, "CLOUDINARY_API_KEY", "test_key")
    monkeypatch.setattr(settings, "CLOUDINARY_CLOUD_NAME", "")
    monkeypatch.setattr(settings, "CLOUDINARY_API_SECRET", "")
    monkeypatch.setattr(settings, "CLOUDINARY_URL", "")

    status = CloudinaryStorageService.get_configuration_status()
    assert status["configured"] is False
    assert status["has_api_key"] is True
    assert "CLOUDINARY_CLOUD_NAME" in status["missing_credentials"]
    assert "CLOUDINARY_API_SECRET" in status["missing_credentials"]

    upload = UploadFile(filename="leak.jpg", file=io.BytesIO(_evidence_bytes()))
    prepared = asyncio.run(ImageProcessingService.prepare_upload(upload))
    with pytest.raises(Exception) as exc_info:
        asyncio.run(CloudinaryStorageService.upload_images("case_test", [prepared]))
    assert "CLOUDINARY_CLOUD_NAME" in str(exc_info.value) or "CLOUDINARY_API_SECRET" in str(exc_info.value)


def test_notion_missing_target_page_reported(monkeypatch):
    """When NOTION_API_KEYS is present but target container is missing, an explicit error is reported."""
    from app.services.notion_service import NotionDocumentationService, NotionSyncError
    monkeypatch.setattr(settings, "NOTION_API_KEYS", "secret_test_key")
    monkeypatch.setattr(settings, "NOTION_API_KEY", "secret_test_key")
    monkeypatch.setattr(settings, "NOTION_PARENT_PAGE_ID", "")
    monkeypatch.setattr(settings, "NOTION_DATABASE_ID", "")
    monkeypatch.setattr(settings, "NOTION_DOCUMENTATION_PAGE_ID", "")

    assert NotionDocumentationService.has_api_key() is True
    assert NotionDocumentationService.is_configured() is False

    with pytest.raises(NotionSyncError) as exc_info:
        asyncio.run(NotionDocumentationService.sync([]))
    assert "target workspace page or database ID is set" in str(exc_info.value)


def test_integration_status_and_verify_endpoints():
    """Verify testing role can inspect integration status and execute minimal safe verification."""
    tester_client = TestClient(app)
    tester_client.post("/api/v1/auth/login", json={"username": settings.TESTER_USERNAME, "password": settings.TESTER_PASSWORD})

    cloudinary_status = tester_client.get("/api/v1/integrations/cloudinary/status")
    assert cloudinary_status.status_code == 200
    assert "missing_credentials" in cloudinary_status.json()

    notion_status = tester_client.get("/api/v1/integrations/notion/status")
    assert notion_status.status_code == 200
    assert "configured" in notion_status.json()

    verify_resp = tester_client.get("/api/v1/integrations/verify")
    assert verify_resp.status_code == 200
    data = verify_resp.json()
    assert "cloudinary" in data
    assert "notion" in data

