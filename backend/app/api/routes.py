import datetime
import hmac
import uuid
from typing import List, Optional, Tuple

from fastapi import APIRouter, Header, HTTPException, Query, Request, Response, UploadFile, status
from pydantic import ValidationError
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.core.config import settings
from app.models.schemas import (
    AuthStatusResponse,
    CaseDecisionRequest,
    CaseRecord,
    CaseStatus,
    CaseStatusUpdate,
    ComplaintCreate,
    DispatchEvent,
    EvaluationMetrics,
    LoginRequest,
    LoginResponse,
    NotionStatusResponse,
    NotionSyncResult,
    ReviewStatus,
    UserSessionInfo,
)
from app.services.auth_service import (
    AuthService,
    SESSION_COOKIE_NAME,
    SESSION_DURATION_SECONDS,
    require_admin,
    require_tester,
)
from app.services.benchmark_service import get_benchmark_evaluation
from app.services.cloudinary_service import CloudinaryStorageError, CloudinaryStorageService
from app.services.db_service import db
from app.services.duplicate_service import DuplicateDetectionService
from app.services.gemma_service import GemmaExtractionService
from app.services.image_processing_service import ImageProcessingService, ImageValidationError
from app.services.n8n_service import N8NWorkflowService
from app.services.notion_service import NotionDocumentationService, NotionSyncError
from app.services.priority_service import PriorityService
from app.services.rate_limit_service import submission_rate_limiter


router = APIRouter()


# -----------------------------------------------------------------------------
# Role-Based Demo Authentication Endpoints
# -----------------------------------------------------------------------------

@router.post("/auth/login", response_model=LoginResponse)
def login(login_req: LoginRequest, response: Response):
    """Authenticate with demo credentials (admin_resolve / tester_resolve).
    
    Sets an HTTP-only, SameSite session cookie and returns session info.
    """
    auth_result = AuthService.authenticate(login_req.username, login_req.password)
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password. Check your demo credentials.",
        )
    username, role, display_name = auth_result
    signed_token = AuthService.create_session(username, role, display_name)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=signed_token,
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
        path="/",
        max_age=SESSION_DURATION_SECONDS,
    )
    # Also attach in header for programmatic or test clients
    response.headers["X-Session-Token"] = signed_token
    return LoginResponse(
        user=UserSessionInfo(username=username, role=role, display_name=display_name),
        demo_mode=True,
        message=f"Logged in successfully as {role} (Demo Mode).",
        token=signed_token,
    )


@router.post("/auth/logout")
def logout(request: Request, response: Response):
    """Terminate the active session and remove the session cookie."""
    token = AuthService.extract_token_from_request(request)
    if token:
        AuthService.destroy_session(token)
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    return {"message": "Logged out successfully. Demo session terminated."}


@router.get("/auth/me", response_model=AuthStatusResponse)
def get_current_user_status(request: Request):
    """Verify active session persistence from cookie or header."""
    token = AuthService.extract_token_from_request(request)
    session = AuthService.get_session(token)
    if not session:
        return AuthStatusResponse(authenticated=False, user=None, demo_mode=True)
    return AuthStatusResponse(
        authenticated=True,
        user=UserSessionInfo(
            username=session.username,
            role=session.role,
            display_name=session.display_name,
        ),
        demo_mode=True,
    )


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _require_admin(x_admin_token: Optional[str]) -> None:
    """Protect administrative mutations when a deployment token is configured."""
    if settings.ADMIN_API_TOKEN and not (
        x_admin_token and hmac.compare_digest(x_admin_token, settings.ADMIN_API_TOKEN)
    ):
        raise HTTPException(status_code=401, detail="A valid X-Admin-Token is required for this administrative action.")


async def _parse_complaint_request(request: Request) -> Tuple[ComplaintCreate, List[UploadFile]]:
    """Accept the legacy JSON body as well as browser multipart submissions."""
    content_type = request.headers.get("content-type", "").lower()
    try:
        if content_type.startswith("multipart/form-data"):
            form = await request.form()

            def value(name: str) -> Optional[str]:
                item = form.get(name)
                return item if isinstance(item, str) else None

            payload = {
                "raw_text": value("raw_text"),
                "student_name": value("student_name"),
                "student_email": value("student_email"),
                "reported_block": value("reported_block"),
                "reported_floor": value("reported_floor"),
                "affected_people": value("affected_people"),
            }
            files = [item for item in form.getlist("images") if isinstance(item, StarletteUploadFile)]
        else:
            payload = await request.json()
            files = []
        return ComplaintCreate.model_validate(payload), files
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Submit a valid JSON complaint or multipart form.") from exc


def _client_identity(request: Request) -> str:
    return request.client.host if request.client else "unknown-client"


def _top_duplicate_parent(case: CaseRecord) -> Optional[str]:
    return next(
        (candidate.matched_case_id for candidate in case.duplicate_candidates if candidate.is_duplicate_candidate),
        None,
    )


@router.post("/complaints", response_model=CaseRecord)
async def submit_complaint(request: Request):
    """Create a complaint, optionally with server-validated Cloudinary evidence.

    JSON-only clients remain supported. Multipart clients send normal complaint
    fields plus one or more `images` fields, each processed by OpenCV before any
    external upload occurs.
    """
    if not submission_rate_limiter.allow(_client_identity(request)):
        raise HTTPException(status_code=429, detail="Too many submissions. Please wait a minute and try again.")

    complaint, files = await _parse_complaint_request(request)
    case_id = f"case_{uuid.uuid4().hex[:8]}"
    assets = []
    try:
        prepared_images = await ImageProcessingService.prepare_uploads(files)
        if prepared_images:
            assets = await CloudinaryStorageService.upload_images(case_id, prepared_images)

        extraction = await GemmaExtractionService.extract(
            complaint.raw_text,
            reported_block=complaint.reported_block,
        )
        existing_cases = db.get_all()
        duplicates, is_held = DuplicateDetectionService.evaluate_candidate(
            complaint.raw_text,
            extraction,
            existing_cases,
            assets,
        )
        now_iso = _now()
        case = CaseRecord(
            id=case_id,
            case_number=f"RES-2026-{100 + len(existing_cases) + 1}",
            created_at=now_iso,
            last_updated_at=now_iso,
            raw_complaint=complaint.raw_text,
            student_name=complaint.student_name or "Anonymous Reporter",
            student_email=complaint.student_email or "reporter@example.com",
            extraction=extraction,
            images=assets,
            affected_people=complaint.affected_people,
            duplicate_candidates=duplicates,
            is_held_as_duplicate=is_held,
            status=CaseStatus.HELD_FOR_REVIEW if is_held else CaseStatus.ASSIGNED,
            review_status=ReviewStatus.PENDING_HUMAN_REVIEW if is_held else ReviewStatus.NOT_REQUIRED,
            history=[
                {"timestamp": now_iso, "event": f"Complaint submitted (RES-2026-{100 + len(existing_cases) + 1})"},
                {"timestamp": now_iso, "event": f"Gemma extracted: {extraction.issue_type.value} at {extraction.building_block} (base priority {extraction.estimated_priority_score}/10)"},
            ],
        )
        suspected_parent = _top_duplicate_parent(case)
        if suspected_parent:
            parent = db.get_by_id(suspected_parent)
            case.suspected_parent_case_id = suspected_parent
            case.corroborating_report_count = (parent.corroborating_report_count if parent else 1) + 1
            case.history.append({
                "timestamp": now_iso,
                "event": f"Likely duplicate linked to {suspected_parent}; held for human review without auto-merging.",
            })
        if assets:
            case.history.append({
                "timestamp": now_iso,
                "event": f"{len(assets)} image evidence item(s) validated with OpenCV and stored in Cloudinary.",
            })
        PriorityService.apply(case)

        dispatch_event = await N8NWorkflowService.dispatch_case_event(case)
        case.n8n_dispatch = dispatch_event
        case.assigned_team = dispatch_event.assigned_team
        case.history.append({
            "timestamp": dispatch_event.timestamp,
            "event": f"n8n Dispatch [{dispatch_event.workflow_branch}]: {dispatch_event.action_taken} -> {dispatch_event.assigned_team}",
        })
        db.add(case)
        if suspected_parent:
            db.refresh_corroboration(suspected_parent)
        return case
    except ImageValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except CloudinaryStorageError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        if assets:
            try:
                await CloudinaryStorageService.delete_images(assets)
            except CloudinaryStorageError:
                pass
        raise HTTPException(status_code=502, detail="The complaint could not be processed. No partial image evidence was retained.") from exc


@router.post("/complaints/{case_id}/images", response_model=CaseRecord)
async def attach_case_images(case_id: str, request: Request):
    """Attach more evidence to an existing report and re-evaluate visual matches."""
    case = db.get_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    new_assets = []
    try:
        form = await request.form()
        files = [item for item in form.getlist("images") if isinstance(item, StarletteUploadFile)]
        if not files:
            raise ImageValidationError("Select at least one image to attach.")
        available_slots = settings.MAX_IMAGES_PER_CASE - len(case.images)
        if available_slots <= 0 or len(files) > available_slots:
            raise ImageValidationError(f"This report can contain at most {settings.MAX_IMAGES_PER_CASE} images in total.")
        prepared_images = await ImageProcessingService.prepare_uploads(files)
        new_assets = await CloudinaryStorageService.upload_images(case_id, prepared_images)
        case.images.extend(new_assets)
        duplicates, is_held = DuplicateDetectionService.evaluate_candidate(
            case.raw_complaint,
            case.extraction,
            [existing for existing in db.get_all() if existing.id != case_id],
            case.images,
        )
        case.duplicate_candidates = duplicates
        if is_held and not case.parent_case_id:
            case.is_held_as_duplicate = True
            case.status = CaseStatus.HELD_FOR_REVIEW
            case.review_status = ReviewStatus.PENDING_HUMAN_REVIEW
            case.suspected_parent_case_id = _top_duplicate_parent(case)
            parent = db.get_by_id(case.suspected_parent_case_id) if case.suspected_parent_case_id else None
            case.corroborating_report_count = (parent.corroborating_report_count if parent else 1) + 1
        PriorityService.apply(case)
        case.last_updated_at = _now()
        case.history.append({"timestamp": case.last_updated_at, "event": f"Attached {len(new_assets)} Cloudinary image evidence item(s); visual duplicate evidence recalculated."})
        db.update(case)
        if case.suspected_parent_case_id:
            db.refresh_corroboration(case.suspected_parent_case_id)
        return case
    except ImageValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except CloudinaryStorageError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        if new_assets:
            try:
                await CloudinaryStorageService.delete_images(new_assets)
            except CloudinaryStorageError:
                pass
        raise HTTPException(status_code=502, detail="Evidence could not be attached. No partial image record was saved.") from exc


def _check_admin_auth(request: Request, x_admin_token: Optional[str] = None):
    """Enforce admin privileges via session cookie, bearer/session token, or deployment token."""
    token = AuthService.extract_token_from_request(request)
    session = AuthService.get_session(token) if token else None
    if session:
        if session.role == "admin":
            return session
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin role required for this action.",
        )
    if settings.ADMIN_API_TOKEN and x_admin_token and hmac.compare_digest(x_admin_token, settings.ADMIN_API_TOKEN):
        return None
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Please log in with admin demo credentials.",
    )


def _check_tester_auth(request: Request):
    """Enforce tester privileges via session cookie or bearer/session token."""
    token = AuthService.extract_token_from_request(request)
    session = AuthService.get_session(token) if token else None
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in with tester demo credentials.",
        )
    if session.role != "tester":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Testing & QA role required for this action.",
        )
    return session


@router.delete("/complaints/{case_id}/images/{image_id}", response_model=CaseRecord)
async def delete_case_image(
    case_id: str,
    image_id: str,
    request: Request,
    x_admin_token: Optional[str] = Header(None),
):
    """Delete evidence from Cloudinary first, then remove its local record."""
    _check_admin_auth(request, x_admin_token)
    case = db.get_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    image = next((item for item in case.images if item.id == image_id), None)
    if not image:
        raise HTTPException(status_code=404, detail="Image evidence not found")
    try:
        await CloudinaryStorageService.delete_images([image])
    except CloudinaryStorageError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    case.images = [item for item in case.images if item.id != image_id]
    case.last_updated_at = _now()
    case.history.append({"timestamp": case.last_updated_at, "event": f"Admin removed image evidence {image.id} from Cloudinary."})
    db.update(case)
    return case


@router.get("/cases", response_model=List[CaseRecord])
def list_cases(
    request: Request,
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by authoritative priority level"),
    location: Optional[str] = Query(None, description="Filter by building or room"),
    search: Optional[str] = Query(None, description="Search complaint text or number"),
    sort: str = Query("priority", pattern="^(priority|most_reported|recent)$"),
    x_admin_token: Optional[str] = Header(None),
):
    """Admin Triage: List, filter, and sort cases. Restricted to administrator role."""
    _check_admin_auth(request, x_admin_token)
    cases = db.get_all()
    if status and status != "all":
        cases = [case for case in cases if case.status.value == status]
    if category and category != "all":
        cases = [case for case in cases if case.extraction.issue_type.value == category]
    if priority and priority != "all":
        cases = [case for case in cases if case.priority_level.value == priority]
    if location:
        needle = location.lower()
        cases = [case for case in cases if needle in case.extraction.building_block.lower() or needle in (case.extraction.floor_or_room or "").lower()]
    if search:
        needle = search.lower()
        cases = [
            case for case in cases
            if needle in case.raw_complaint.lower()
            or needle in case.case_number.lower()
            or needle in case.extraction.clean_summary.lower()
            or needle in case.extraction.building_block.lower()
        ]
    if sort == "most_reported":
        return sorted(cases, key=lambda case: (case.corroborating_report_count, case.priority_score, case.created_at), reverse=True)
    if sort == "recent":
        return sorted(cases, key=lambda case: case.created_at, reverse=True)
    return sorted(cases, key=lambda case: (case.priority_score, case.corroborating_report_count, case.created_at), reverse=True)


@router.get("/testing/cases", response_model=List[CaseRecord])
def get_testing_cases(request: Request):
    """Testing Portal: Retrieve all cases and n8n execution dispatches. Restricted to testing role."""
    _check_tester_auth(request)
    return db.get_all()


@router.get("/cases/{case_id}", response_model=CaseRecord)
def get_case(case_id: str):
    """Public lookup: Retrieve a single complaint record by its case ID."""
    case = db.get_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.get("/cases/track/{identifier}", response_model=CaseRecord)
def track_case(identifier: str):
    """Public lookup: Track a complaint by Case Number (e.g. RES-2026-101) or Case ID."""
    needle = identifier.strip().lower()
    for case in db.get_all():
        if case.id.lower() == needle or case.case_number.lower() == needle:
            return case
    raise HTTPException(
        status_code=404,
        detail="Complaint ticket not found. Please verify your ticket number (e.g. RES-2026-101) and try again.",
    )


@router.get("/cases/{case_id}/duplicates")
def get_case_duplicates(
    case_id: str,
    request: Request,
    x_admin_token: Optional[str] = Header(None),
):
    """Admin duplicate inspection: View detailed matching evidence for candidate duplicates."""
    _check_admin_auth(request, x_admin_token)
    case = db.get_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {
        "case_id": case.id,
        "review_status": case.review_status,
        "suspected_parent_case_id": case.suspected_parent_case_id,
        "confirmed_parent_case_id": case.parent_case_id,
        "candidates": case.duplicate_candidates,
    }


@router.post("/cases/{case_id}/decision", response_model=CaseRecord)
def make_case_decision(
    case_id: str,
    decision_req: CaseDecisionRequest,
    request: Request,
    x_admin_token: Optional[str] = Header(None),
):
    """Facility-admin resolution; suspected duplicates are never silently merged."""
    _check_admin_auth(request, x_admin_token)
    case = db.get_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    now_iso = _now()
    previous_parent = case.suspected_parent_case_id
    if decision_req.decision == "approve":
        case.status = CaseStatus.ASSIGNED
        case.is_held_as_duplicate = False
        case.review_status = ReviewStatus.REJECTED_DUPLICATE if previous_parent else ReviewStatus.NOT_REQUIRED
        if decision_req.target_team:
            case.assigned_team = decision_req.target_team
        case.history.append({"timestamp": now_iso, "event": f"Admin approval: Assigned to {case.assigned_team}. Note: {decision_req.reviewer_notes}"})
    elif decision_req.decision == "merge_duplicate":
        target_parent = decision_req.parent_case_id or previous_parent
        if not target_parent or target_parent == case_id or not db.get_by_id(target_parent):
            raise HTTPException(status_code=422, detail="Choose a valid target case before confirming a duplicate merge.")
        case.status = CaseStatus.RESOLVED
        case.is_held_as_duplicate = False
        case.parent_case_id = target_parent
        case.suspected_parent_case_id = target_parent
        case.review_status = ReviewStatus.CONFIRMED_DUPLICATE
        case.history.append({"timestamp": now_iso, "event": f"Admin confirmed duplicate into parent #{target_parent}. Note: {decision_req.reviewer_notes}"})
        previous_parent = target_parent
    elif decision_req.decision == "reject":
        case.status = CaseStatus.REJECTED
        case.is_held_as_duplicate = False
        case.review_status = ReviewStatus.REJECTED_DUPLICATE if previous_parent else ReviewStatus.NOT_REQUIRED
        case.history.append({"timestamp": now_iso, "event": f"Admin rejected case. Note: {decision_req.reviewer_notes}"})
    else:
        raise HTTPException(status_code=422, detail="Unsupported decision.")

    case.human_review_notes = decision_req.reviewer_notes
    case.last_updated_at = now_iso
    PriorityService.apply(case)
    db.update(case)
    if previous_parent:
        db.refresh_corroboration(previous_parent)
    return case


@router.patch("/cases/{case_id}/status", response_model=CaseRecord)
def update_case_status(
    case_id: str,
    update: CaseStatusUpdate,
    request: Request,
    x_admin_token: Optional[str] = Header(None),
):
    """Admin update: Modify case status with audit note."""
    _check_admin_auth(request, x_admin_token)
    case = db.get_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    now_iso = _now()
    case.status = update.status
    if update.status != CaseStatus.HELD_FOR_REVIEW:
        case.is_held_as_duplicate = False
    case.last_updated_at = now_iso
    note = f" Note: {update.note}" if update.note else ""
    case.history.append({"timestamp": now_iso, "event": f"Admin updated status to {update.status.value}.{note}"})
    db.update(case)
    return case


@router.post("/integrations/notion/sync", response_model=NotionSyncResult)
async def sync_notion_documentation(request: Request):
    """Testing Portal: Sync documentation, empirical benchmark metrics, and workflow stats to Notion."""
    _check_tester_auth(request)
    try:
        return await NotionDocumentationService.sync(db.get_all())
    except NotionSyncError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/integrations/notion/status", response_model=NotionStatusResponse)
def get_notion_status(request: Request):
    """Testing Portal: Check Notion configuration and last sync timestamp."""
    _check_tester_auth(request)
    return NotionStatusResponse(**NotionDocumentationService.get_status())


@router.get("/integrations/cloudinary/status")
def get_cloudinary_status(request: Request):
    """Testing Portal: Check Cloudinary configuration status."""
    _check_tester_auth(request)
    return CloudinaryStorageService.get_configuration_status()


@router.get("/integrations/verify")
async def verify_external_integrations(request: Request):
    """Testing Portal: Perform minimal, non-destructive connection verification for Notion and Cloudinary."""
    _check_tester_auth(request)
    return {
        "cloudinary": CloudinaryStorageService.verify_connection(),
        "notion": await NotionDocumentationService.verify_connection(),
    }


@router.get("/metrics/benchmark", response_model=EvaluationMetrics)
def get_metrics(request: Request):
    """Testing Portal: Access empirical evaluation metrics and ablation study."""
    _check_tester_auth(request)
    return get_benchmark_evaluation()


@router.get("/stats")
def get_dashboard_stats():
    """Public high-level status metrics for campus landing overview."""
    cases = db.get_all()
    return {
        "total_cases": len(cases),
        "held_for_review": sum(1 for case in cases if case.status == CaseStatus.HELD_FOR_REVIEW),
        "in_progress_or_assigned": sum(1 for case in cases if case.status in {CaseStatus.ASSIGNED, CaseStatus.IN_PROGRESS}),
        "resolved": sum(1 for case in cases if case.status == CaseStatus.RESOLVED),
        "duplicates_detected": sum(1 for case in cases if case.duplicate_candidates),
        "critical_priority_cases": sum(1 for case in cases if case.priority_level.value == "critical"),
        "n8n_webhook_health": "operational",
        "gemma_extraction_health": "operational",
        "cloudinary_configured": CloudinaryStorageService.is_configured(),
        "notion_configured": NotionDocumentationService.is_configured(),
    }


@router.post("/reset-demo")
def reset_demo(request: Request):
    """Testing Portal: Reset demo cases and rate limiter back to clean baseline."""
    _check_tester_auth(request)
    db.reset()
    submission_rate_limiter.reset()
    return {"message": "Demo state reset successfully to initial state"}
