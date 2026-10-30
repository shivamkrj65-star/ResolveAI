import uuid
import datetime
from threading import RLock
from typing import List, Optional, Dict
from app.models.schemas import CaseRecord, CaseStatus, GemmaExtractionResult, IssueCategory, UrgencyLevel, DispatchEvent
from app.services.priority_service import PriorityService

class InMemoryDatabase:
    """
    In-memory case store preloaded with realistic campus benchmark scenarios
    to faithfully mirror PPT slides:
    - Case 1: "Water across B-block stairway"
    - Multiple existing complaints across Block A, Block B, Library
    """
    def __init__(self):
        self.cases: Dict[str, CaseRecord] = {}
        self._lock = RLock()
        self._seed_initial_cases()
        
    def _seed_initial_cases(self):
        # Case 1 from Slide 4
        c1_id = "case_b_leak_001"
        c1 = CaseRecord(
            id=c1_id,
            case_number="RES-2026-101",
            created_at=(datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat(),
            raw_complaint="Water across B-block stairway, puddles forming near the second landing and people are slipping.",
            student_name="Aarav Sharma",
            student_email="aarav.s@example.com",
            extraction=GemmaExtractionResult(
                issue_type=IssueCategory.WATER_LEAK,
                confidence=0.96,
                building_block="Block B",
                floor_or_room="2nd Floor Landing",
                specific_location_hint="Stairway landing between 1st & 2nd floor",
                clean_summary="Water leak causing puddles at Block B stairway",
                detected_urgency=UrgencyLevel.HIGH,
                estimated_priority_score=8,
                raw_entities={"source": "User Portal"}
            ),
            duplicate_candidates=[],
            is_held_as_duplicate=False,
            status=CaseStatus.ASSIGNED,
            assigned_team="Campus Plumbing & Water Infrastructure Team",
            history=[
                {"timestamp": (datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat(), "event": "Case submitted by reporter"},
                {"timestamp": (datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat(), "event": "Gemma extraction: water_leak @ Block B"},
                {"timestamp": (datetime.datetime.now() - datetime.timedelta(hours=1, minutes=58)).isoformat(), "event": "n8n Webhook: Route to Plumbing Team"}
            ],
            n8n_dispatch=DispatchEvent(
                event_id="evt_seed_001",
                timestamp=(datetime.datetime.now() - datetime.timedelta(hours=1, minutes=58)).isoformat(),
                idempotency_key="idemp_case_b_leak_001_water_leak",
                action_taken="assigned_to_team",
                assigned_team="Campus Plumbing & Water Infrastructure Team",
                n8n_execution_id="n8n_exec_9901a",
                workflow_branch="direct_assignment",
                status_code=200,
                details={"branch": "Branch_CategoryRouting", "rule": "Rule_WATER_LEAK_DIRECT"}
            )
        )
        PriorityService.apply(c1)
        self.cases[c1.id] = c1
        
        # Case 2: Electrical in Library
        c2_id = "case_lib_spark_002"
        c2 = CaseRecord(
            id=c2_id,
            case_number="RES-2026-102",
            created_at=(datetime.datetime.now() - datetime.timedelta(hours=5)).isoformat(),
            raw_complaint="Sparking power socket near reading table 14 on 3rd floor library. Smell of burning plastic.",
            student_name="Priya Patel",
            student_email="priya.p@example.com",
            extraction=GemmaExtractionResult(
                issue_type=IssueCategory.ELECTRICAL,
                confidence=0.98,
                building_block="Central Library",
                floor_or_room="3rd Floor Reading Hall",
                specific_location_hint="Table 14 perimeter socket",
                clean_summary="Sparking socket hazard in Central Library 3rd Floor",
                detected_urgency=UrgencyLevel.CRITICAL,
                estimated_priority_score=10,
                raw_entities={"source": "User Portal"}
            ),
            duplicate_candidates=[],
            is_held_as_duplicate=False,
            status=CaseStatus.IN_PROGRESS,
            assigned_team="High & Low Voltage Electrical Operations",
            history=[
                {"timestamp": (datetime.datetime.now() - datetime.timedelta(hours=5)).isoformat(), "event": "Case submitted"},
                {"timestamp": (datetime.datetime.now() - datetime.timedelta(hours=4, minutes=55)).isoformat(), "event": "Assigned to Electrical Operations"},
                {"timestamp": (datetime.datetime.now() - datetime.timedelta(hours=3)).isoformat(), "event": "Technician dispatched to Library"}
            ],
            n8n_dispatch=DispatchEvent(
                event_id="evt_seed_002",
                timestamp=(datetime.datetime.now() - datetime.timedelta(hours=4, minutes=55)).isoformat(),
                idempotency_key="idemp_case_lib_spark_002_electrical",
                action_taken="assigned_to_team",
                assigned_team="High & Low Voltage Electrical Operations",
                n8n_execution_id="n8n_exec_9902b",
                workflow_branch="direct_assignment",
                status_code=200,
                details={"branch": "Branch_CategoryRouting", "rule": "Rule_ELECTRICAL_DIRECT"}
            )
        )
        PriorityService.apply(c2)
        self.cases[c2.id] = c2

        # Case 3: Broken Desk in Block A
        c3_id = "case_block_a_furniture_003"
        c3 = CaseRecord(
            id=c3_id,
            case_number="RES-2026-103",
            created_at=(datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
            raw_complaint="Classroom 204 in Block A has 4 broken desks with loose screws and cracked plywood.",
            student_name="Karan Mehta",
            student_email="karan.m@example.com",
            extraction=GemmaExtractionResult(
                issue_type=IssueCategory.FURNITURE,
                confidence=0.94,
                building_block="Block A",
                floor_or_room="Room 204",
                specific_location_hint="Classroom 204 seating rows",
                clean_summary="Broken desks needing carpentry in Block A Room 204",
                detected_urgency=UrgencyLevel.LOW,
                estimated_priority_score=4,
                raw_entities={"source": "User Portal"}
            ),
            duplicate_candidates=[],
            is_held_as_duplicate=False,
            status=CaseStatus.RESOLVED,
            assigned_team="Carpentry & Facilities Maintenance Unit",
            history=[
                {"timestamp": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(), "event": "Case submitted"},
                {"timestamp": (datetime.datetime.now() - datetime.timedelta(hours=20)).isoformat(), "event": "Repaired and verified by carpentry supervisor"}
            ]
        )
        PriorityService.apply(c3)
        self.cases[c3.id] = c3

    def get_all(self) -> List[CaseRecord]:
        with self._lock:
            return sorted(
                list(self.cases.values()),
                key=lambda x: (x.priority_score, x.corroborating_report_count, x.created_at),
                reverse=True,
            )
        
    def get_by_id(self, case_id: str) -> Optional[CaseRecord]:
        with self._lock:
            return self.cases.get(case_id)
        
    def add(self, case: CaseRecord):
        with self._lock:
            self.cases[case.id] = case
        
    def update(self, case: CaseRecord):
        with self._lock:
            self.cases[case.id] = case

    def refresh_corroboration(self, parent_case_id: str) -> Optional[CaseRecord]:
        """Recompute a cluster count from auditable child records, not a blind increment."""
        with self._lock:
            parent = self.cases.get(parent_case_id)
            if not parent:
                return None
            related_reports = [
                case for case in self.cases.values()
                if case.id != parent_case_id and (
                    case.parent_case_id == parent_case_id
                    or (
                        case.suspected_parent_case_id == parent_case_id
                        and case.review_status.value == "pending_human_review"
                    )
                )
            ]
            parent.corroborating_report_count = 1 + len(related_reports)
            PriorityService.apply(parent)
            parent.last_updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
            self.cases[parent.id] = parent
            return parent

    def reset(self) -> None:
        with self._lock:
            self.cases = {}
            self._seed_initial_cases()

db = InMemoryDatabase()
