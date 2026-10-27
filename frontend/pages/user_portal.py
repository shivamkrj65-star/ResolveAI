"""User Portal (Public) for ResolveAI.

Allows students and campus members to view the public dashboard, register new
complaints with OpenCV image processing & Cloudinary storage, track existing tickets,
and inspect resolution progress without requiring login.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional
import streamlit as st
from services.api_client import ResolveAIClient
from utils.helpers import (
    build_category_chart,
    build_status_chart,
    render_priority_badge,
    render_status_badge,
)


def render_user_portal(client: ResolveAIClient):
    # Session storage for tickets submitted by this user in current session
    if "my_tickets" not in st.session_state:
        st.session_state.my_tickets = []
    if "tracking_target" not in st.session_state:
        st.session_state.tracking_target = ""

    tabs = st.tabs([
        "📊 Dashboard",
        "📝 Register Complaint",
        "🔍 Track Complaint",
        "📁 My Complaints",
        "📋 Complaint Details",
    ])

    # =========================================================================
    # TAB 1: DASHBOARD
    # =========================================================================
    with tabs[0]:
        st.markdown("### Campus Problem Overview")
        st.markdown(
            "Welcome to the **ResolveAI Campus Portal**. Submit infrastructure, electrical, "
            "plumbing, or sanitation issues. Gemma AI classifies reports instantly, while OpenCV "
            "and Cloudinary securely process and store photographic evidence."
        )

        ok, stats = client.get_stats()
        if ok and isinstance(stats, dict):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(
                    f"""<div class="metric-card">
                        <div class="metric-label">Total Reports</div>
                        <div class="metric-value">{stats.get('total_cases', 0)}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f"""<div class="metric-card">
                        <div class="metric-label">In Resolution</div>
                        <div class="metric-value" style="color: var(--resolve-info);">{stats.get('in_progress_or_assigned', 0)}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with c3:
                st.markdown(
                    f"""<div class="metric-card">
                        <div class="metric-label">Resolved</div>
                        <div class="metric-value" style="color: var(--resolve-success);">{stats.get('resolved', 0)}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with c4:
                st.markdown(
                    f"""<div class="metric-card">
                        <div class="metric-label">Duplicates Caught</div>
                        <div class="metric-value" style="color: var(--resolve-warning);">{stats.get('duplicates_detected', 0)}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                # To populate charts, let's fetch testing cases if accessible or show stats overview
                pass
        else:
            st.info("Backend statistics are currently loading or unavailable.")

        # Quick guide cards
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown(
                """<div class="portal-card">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📸</div>
                    <h4 style="margin: 0; color: inherit;">1. Upload Evidence</h4>
                    <p style="color: var(--resolve-muted); font-size: 0.85rem; margin-top: 0.4rem;">
                        Attach photos of the issue. OpenCV checks blur and extracts visual features.
                    </p>
                </div>""",
                unsafe_allow_html=True,
            )
        with g2:
            st.markdown(
                """<div class="portal-card">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🧠</div>
                    <h4 style="margin: 0; color: inherit;">2. Gemma Extraction</h4>
                    <p style="color: var(--resolve-muted); font-size: 0.85rem; margin-top: 0.4rem;">
                        Our fine-tuned Gemma model determines urgency, location, and hazard level.
                    </p>
                </div>""",
                unsafe_allow_html=True,
            )
        with g3:
            st.markdown(
                """<div class="portal-card">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⚡</div>
                    <h4 style="margin: 0; color: inherit;">3. n8n Fast Dispatch</h4>
                    <p style="color: var(--resolve-muted); font-size: 0.85rem; margin-top: 0.4rem;">
                        Tickets are routed automatically to the right facility response teams.
                    </p>
                </div>""",
                unsafe_allow_html=True,
            )

    # =========================================================================
    # TAB 2: REGISTER COMPLAINT
    # =========================================================================
    with tabs[1]:
        st.markdown("### 📝 Submit a New Campus Problem Report")
        st.markdown("Provide details about the issue. Visual evidence is validated and stored securely.")

        with st.form("complaint_form", clear_on_submit=False):
            col_t1, col_t2 = st.columns([2, 1])
            with col_t1:
                raw_text = st.text_area(
                    "Complaint Description *",
                    placeholder="Describe the problem in detail (e.g. Water leaking heavily from ceiling in 3rd floor corridor, Block C)...",
                    height=130,
                    help="Include specific symptoms, exact room/hallway, and any visible hazards.",
                )
            with col_t2:
                reported_block = st.selectbox(
                    "Campus Block / Building *",
                    [
                        "Block C (Engineering)",
                        "Block A (Main Admin)",
                        "Block B (Science Wing)",
                        "Block D (Hostels)",
                        "Library Complex",
                        "Sports Arena",
                        "Dining Hall",
                        "Campus Grounds",
                        "Other / Unspecified",
                    ],
                )
                reported_floor = st.text_input("Floor / Room Number", placeholder="e.g. 3rd Floor, Lab 304")
                affected_people = st.selectbox(
                    "Number of People Affected",
                    ["Few (1-5)", "Moderate (5-20)", "High (20-100)", "Entire Facility / Wing (>100)"],
                )

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                student_name = st.text_input("Your Name (Optional)", placeholder="e.g. Aditya Sharma")
            with col_s2:
                student_email = st.text_input("Your Email (For status notifications)", placeholder="e.g. aditya@campus.edu")

            st.markdown("#### 📷 Attach Evidence Photos (OpenCV Validated & Stored via Cloudinary)")
            uploaded_files = st.file_uploader(
                "Upload up to 4 images (.jpg, .jpeg, .png, .webp)",
                type=["jpg", "jpeg", "png", "webp"],
                accept_multiple_files=True,
                help="Evidence images undergo blur variance analysis and perceptual hashing via OpenCV before upload to Cloudinary.",
            )

            submit_button = st.form_submit_button("🚀 Submit Problem Report", use_container_width=True)

        if submit_button:
            if not raw_text.strip():
                st.error("Please enter a complaint description.")
            else:
                files_payload = []
                if uploaded_files:
                    for f in uploaded_files:
                        files_payload.append((f.name, f.getvalue(), f.type))

                with st.spinner("Processing complaint with Gemma AI and OpenCV..."):
                    success, res = client.submit_complaint(
                        raw_text=raw_text.strip(),
                        student_name=student_name.strip() if student_name else None,
                        student_email=student_email.strip() if student_email else None,
                        reported_block=reported_block,
                        reported_floor=reported_floor.strip() if reported_floor else None,
                        affected_people=affected_people,
                        files=files_payload if files_payload else None,
                    )

                if success and isinstance(res, dict):
                    case_num = res.get("case_number", "Unknown")
                    case_id = res.get("id", "")
                    st.success(f"🎉 Complaint successfully registered! Ticket ID: **{case_num}**")

                    # Add to session tracking
                    if case_num not in st.session_state.my_tickets:
                        st.session_state.my_tickets.append(case_num)

                    # Summary Card
                    ext = res.get("extraction", {})
                    p_level = res.get("priority_level", "medium")
                    p_score = res.get("priority_score", 5.0)

                    col_res1, col_res2, col_res3 = st.columns(3)
                    with col_res1:
                        st.metric("Ticket Number", case_num)
                    with col_res2:
                        st.metric("Assigned Priority", f"{p_level.upper()} ({p_score}/10)")
                    with col_res3:
                        st.metric("Assigned Facility Team", res.get("assigned_team", "General Maintenance"))

                    # OpenCV / Cloudinary Details
                    images = res.get("images", [])
                    if images:
                        st.markdown("##### 📸 Validated Cloudinary Evidence")
                        cols = st.columns(min(len(images), 4))
                        for idx, img in enumerate(images):
                            with cols[idx]:
                                st.image(img.get("secure_url"), caption=f"{img.get('original_filename')} ({img.get('width')}x{img.get('height')})", use_container_width=True)
                                va = img.get("visual_analysis") or {}
                                st.caption(f"Sharpness Score: {va.get('sharpness', 'N/A')} | Blur: {round(img.get('blur_variance', 0), 1)}")

                    # Quick navigation button to track
                    if st.button(f"🔍 Track {case_num} in Real-Time", key="quick_track_btn"):
                        st.session_state.tracking_target = case_num
                        st.rerun()
                else:
                    st.error(f"Submission failed: {res}")

    # =========================================================================
    # TAB 3: TRACK COMPLAINT
    # =========================================================================
    with tabs[2]:
        st.markdown("### 🔍 Track Your Complaint")
        st.markdown("Enter your Ticket Number (e.g. `RES-2026-101`) or Case ID to inspect live progress.")

        col_search, col_btn = st.columns([3, 1])
        with col_search:
            search_query = st.text_input(
                "Ticket ID or Case ID",
                value=st.session_state.tracking_target,
                placeholder="e.g. RES-2026-101",
                label_visibility="collapsed",
            )
        with col_btn:
            track_click = st.button("🔎 Track Ticket", use_container_width=True)

        target_ticket = search_query.strip()
        if track_click or target_ticket:
            if target_ticket:
                with st.spinner("Fetching ticket record..."):
                    ok, case = client.track_case(target_ticket)

                if ok and isinstance(case, dict):
                    st.markdown("---")
                    # Header Info
                    c_num = case.get("case_number", target_ticket)
                    c_id = case.get("id", "")
                    status = case.get("status", "unknown")
                    priority = case.get("priority_level", "medium")
                    created_at = case.get("created_at", "")

                    col_h1, col_h2 = st.columns([2, 1])
                    with col_h1:
                        st.markdown(f"## 🎫 Ticket #{c_num}")
                        st.caption(f"System Case ID: `{c_id}` | Submitted: `{created_at}`")
                    with col_h2:
                        st.markdown(f"<div style='text-align: right; margin-top: 0.5rem;'>{render_status_badge(status)} {render_priority_badge(priority)}</div>", unsafe_allow_html=True)

                    # Details Grid
                    d1, d2, d3, d4 = st.columns(4)
                    with d1:
                        st.markdown("**Assigned Team**")
                        st.write(case.get("assigned_team") or "Facilities Triage")
                    with d2:
                        ext = case.get("extraction", {})
                        st.markdown("**Location**")
                        st.write(f"{ext.get('building_block', 'Campus')} ({ext.get('floor_or_room') or 'Main'})")
                    with d3:
                        st.markdown("**Issue Category**")
                        st.write(ext.get("issue_type", "Other").replace("_", " ").title())
                    with d4:
                        st.markdown("**Corroborating Reports**")
                        st.write(f"{case.get('corroborating_report_count', 1)} Student Report(s)")

                    st.markdown("#### Description & Gemma AI Analysis")
                    st.info(f"**Clean Summary**: {ext.get('clean_summary', case.get('raw_complaint'))}")

                    with st.expander("📄 View Full Submitted Raw Text"):
                        st.write(case.get("raw_complaint"))

                    # Cloudinary Images
                    images = case.get("images", [])
                    if images:
                        st.markdown("#### 📸 Uploaded Evidence Photos")
                        img_cols = st.columns(min(len(images), 4))
                        for idx, img in enumerate(images):
                            with img_cols[idx]:
                                st.image(img.get("secure_url"), caption=img.get("original_filename"), use_container_width=True)
                                st.markdown(f"[🔗 Open Full Size]({img.get('secure_url')})")

                    # Audit History Timeline
                    st.markdown("#### 🕒 Resolution Timeline & Audit History")
                    history = case.get("history", [])
                    if history:
                        for entry in reversed(history):
                            ts = entry.get("timestamp", "")
                            ev = entry.get("event", "")
                            st.markdown(
                                f"""<div class="timeline-item">
                                    <div style="font-size: 0.75rem; color: var(--resolve-muted);">{ts}</div>
                                    <div style="font-weight: 500; color: inherit; margin-top: 2px;">{ev}</div>
                                </div>""",
                                unsafe_allow_html=True,
                            )
                    else:
                        st.write("No history events recorded yet.")
                else:
                    st.warning(f"Could not find ticket '{target_ticket}'. Please verify the ticket number (e.g. RES-2026-101).")

    # =========================================================================
    # TAB 4: MY COMPLAINTS
    # =========================================================================
    with tabs[3]:
        st.markdown("### 📁 Complaints Submitted in this Session")
        if st.session_state.my_tickets:
            st.markdown(f"You have registered **{len(st.session_state.my_tickets)}** complaint(s) in this browsing session:")
            for ticket_num in st.session_state.my_tickets:
                col_m1, col_m2 = st.columns([3, 1])
                with col_m1:
                    st.markdown(f"**Ticket #{ticket_num}**")
                with col_m2:
                    if st.button("Track Live", key=f"track_my_{ticket_num}"):
                        st.session_state.tracking_target = ticket_num
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No complaints submitted in this session yet. Use the 'Register Complaint' tab to file a report.")

    # =========================================================================
    # TAB 5: COMPLAINT DETAILS
    # =========================================================================
    with tabs[4]:
        st.markdown("### 📋 Complaint Technical Inspection")
        st.markdown("Inspect underlying AI parameters, OpenCV perceptual hash signatures, and n8n dispatch details.")

        detail_id = st.text_input("Enter Ticket ID to inspect technical details", value=st.session_state.tracking_target, placeholder="e.g. RES-2026-101")
        if detail_id.strip():
            ok, c = client.track_case(detail_id.strip())
            if ok and isinstance(c, dict):
                st.json({
                    "ticket": c.get("case_number"),
                    "case_id": c.get("id"),
                    "status": c.get("status"),
                    "priority_score": c.get("priority_score"),
                    "priority_level": c.get("priority_level"),
                    "assigned_team": c.get("assigned_team"),
                    "gemma_extraction": c.get("extraction"),
                    "images_opencv_analysis": [
                        {
                            "filename": im.get("original_filename"),
                            "dimensions": f"{im.get('width')}x{im.get('height')}",
                            "perceptual_hash": im.get("perceptual_hash"),
                            "blur_variance": im.get("blur_variance"),
                            "secure_url": im.get("secure_url"),
                        }
                        for im in c.get("images", [])
                    ],
                    "duplicate_candidates_count": len(c.get("duplicate_candidates", [])),
                    "n8n_dispatch": c.get("n8n_dispatch"),
                })
            else:
                st.warning("Please enter a valid ticket number.")
