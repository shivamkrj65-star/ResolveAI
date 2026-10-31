from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


def test_manual_assignment_and_status_reach_public_tracker():
    admin = TestClient(app)
    assert admin.post('/api/v1/auth/login', json={
        'username': settings.ADMIN_USERNAME, 'password': settings.ADMIN_PASSWORD,
    }).status_code == 200
    case = admin.get('/api/v1/cases').json()[0]
    assigned = admin.post(f"/api/v1/cases/{case['id']}/decision", json={
        'decision': 'approve', 'target_team': 'Carpentry & Facilities Maintenance Unit',
        'reviewer_notes': 'Report acknowledged; carpenter assigned.',
    })
    assert assigned.status_code == 200
    updated = admin.patch(f"/api/v1/cases/{case['id']}/status", json={
        'status': 'in_progress', 'note': 'Technician has arrived.',
    })
    assert updated.status_code == 200
    public = TestClient(app)
    tracked = public.get(f"/api/v1/cases/track/{case['case_number']}").json()
    assert tracked['assigned_team'] == 'Carpentry & Facilities Maintenance Unit'
    assert tracked['status'] == 'in_progress'
    assert not tracked['is_held_as_duplicate']
    assert tracked['last_updated_at'] == updated.json()['last_updated_at']
    assert any('Report acknowledged' in event['event'] for event in tracked['history'])
    assert any('Technician has arrived' in event['event'] for event in tracked['history'])
    assert public.patch(f"/api/v1/cases/{case['id']}/status", json={'status': 'resolved'}).status_code == 401
