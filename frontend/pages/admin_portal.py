"""Admin Portal (Protected) for ResolveAI.

Role-gated administration dashboard with live triage, search, filtering,
interactive charts, duplicate candidate reviews, decision actions, and status updates.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st
from services.api_client import ResolveAIClient
from utils.helpers import (
    build_category_chart,
    build_location_chart,
    build_priority_chart,
    build_status_chart,
    render_priority_badge,
    render_status_badge,
)


def render_admin_portal(client: ResolveAIClient):
    if "admin_token" not in st.session_state:
        st.session_state.admin_token = None
    if "admin_user" not in st.session_state:
        st.session_state.admin_user = None

    # Check session
    token = st.session_state.admin_token
    if not token:
        _render_admin_login(client)
        return

    # Verify session is still valid
    ok, me = client.get_me(token)
    if not ok or not me.get("authenticated") or me.get("user", {}).get("role") != "admin":
        st.session_state.admin_token = None
        st.session_state.admin_user = None
        st.warning("Admin session expired or unauthorized. Please log in again.")
        _render_admin_login(client)
        return

    # Render Logged In Admin Dashboard
    user = me.get("user", {})
    col_u1, col_u2 = st.columns([3, 1])
    with col_u1:
        st.markdown(
            f"### 🛡️ Admin Triage Dashboard — <span style='color: var(--resolve-accent);'>{user.get('display_name', 'Administrator')}</span>",
            unsafe_allow_html=True,
        )
        st.caption(f"Role: `admin` | Username: `{user.get('username')}` | Server-Enforced RBAC Active")
    with col_u2:
        if st.button("🚪 Logout Admin", use_container_width=True, key="admin_logout_btn"):
            client.logout(token)
            st.session_state.admin_token = None
            st.session_state.admin_user = None
            st.rerun()

    # Load Cases
    ok, cases = client.list_cases(token=token, sort="priority")
    if not ok:
        st.error(f"Failed to load cases: {cases}")
        return

    if not isinstance(cases, list):
        cases = []

    # =========================================================================
    # METRICS ROW
    # =========================================================================
    total_cases = len(cases)
    pending_cases = sum(1 for c in cases if c.get("status") == "held_for_review")
    in_progress = sum(1 for c in cases if c.get("status") in {"assigned", "in_progress"})
    resolved_cases = sum(1 for c in cases if c.get("status") == "resolved")
    critical_cases = sum(1 for c in cases if (c.get("priority_level") or "").lower() == "critical")

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Cases</div><div class="metric-value">{total_cases}</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Pending Review</div><div class="metric-value" style="color: var(--resolve-warning);">{pending_cases}</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">In Resolution</div><div class="metric-value" style="color: var(--resolve-info);">{in_progress}</div></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Resolved</div><div class="metric-value" style="color: var(--resolve-success);">{resolved_cases}</div></div>""", unsafe_allow_html=True)
    with m5:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Critical Priority</div><div class="metric-value" style="color: var(--resolve-danger);">{critical_cases}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # =========================================================================
    # VISUALIZATION CHARTS
    # =========================================================================
    with st.expander("📈 Analytics & Problem Distribution Charts", expanded=True):
        ch1, ch2 = st.columns(2)
        with ch1:
            st.plotly_chart(build_status_chart(cases), use_container_width=True)
        with ch2:
            st.plotly_chart(build_priority_chart(cases), use_container_width=True)

        ch3, ch4 = st.columns(2)
        with ch3:
            st.plotly_chart(build_category_chart(cases), use_container_width=True)
        with ch4:
            st.plotly_chart(build_location_chart(cases), use_container_width=True)

    st.markdown("---")

    # =========================================================================
    # FILTERS AND SEARCH
    # =========================================================================
    st.markdown("### 📋 Complaint Management & Triage")

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        search_kw = st.text_input("🔍 Search", placeholder="Search text, student, or ticket...")
    with f2:
        filter_status = st.selectbox(
            "Filter by Status",
            ["all", "assigned", "held_for_review", "in_progress", "resolved", "rejected"],
            format_func=lambda x: x.replace("_", " ").title() if x != "all" else "All Statuses",
        )
    with f3:
        filter_priority = st.selectbox(
            "Filter by Priority",
            ["all", "critical", "high", "medium", "low"],
            format_func=lambda x: x.upper() if x != "all" else "All Priorities",
        )
    with f4:
        sort_by = st.selectbox(
            "Sort Order",
            ["priority", "recent", "most_reported"],
            format_func=lambda x: {"priority": "Authoritative Priority", "recent": "Most Recent", "most_reported": "Most Corroborated"}[x],
        )

    # Refetch with active filters
    ok_filtered, filtered_cases = client.list_cases(
        token=token,
        status=filter_status,
        priority=filter_priority,
        search=search_kw.strip() if search_kw else None,
        sort=sort_by,
    )
    if ok_filtered and isinstance(filtered_cases, list):
        cases_to_show = filtered_cases
    else:
        cases_to_show = cases

    st.caption(f"Displaying **{len(cases_to_show)}** matching cases")

    # =========================================================================
    # CASES LIST & ACTION INTERFACE
    # =========================================================================
    for case in cases_to_show:
        c_num = case.get("case_number", "Unknown")
        c_id = case.get("id", "")
        status = case.get("status", "assigned")
        priority = case.get("priority_level", "medium")
        p_score = case.get("priority_score", 5.0)
        ext = case.get("extraction", {})
        summary = ext.get("clean_summary") or case.get("raw_complaint", "")
        loc = f"{ext.get('building_block', 'Campus')} ({ext.get('floor_or_room') or 'Main'})"
        team = case.get("assigned_team") or "Unassigned"
        images = case.get("images", [])
        corroboration = case.get("corroborating_report_count", 1)
        is_held = case.get("is_held_as_duplicate", False)

        with st.container():
            col_row1, col_row2 = st.columns([3, 1])
            with col_row1:
                st.markdown(
                    f"**{c_num}** — **{ext.get('issue_type', 'Issue').replace('_', ' ').title()}** at `{loc}`"
                )
                st.write(summary)
            with col_row2:
                st.markdown(
                    f"<div style='text-align: right;'>{render_status_badge(status)}<br/>{render_priority_badge(priority)}</div>",
                    unsafe_allow_html=True,
                )
                st.caption(f"Priority Score: **{p_score}/10** | Reports: **{corroboration}**")

            with st.expander(f"⚙️ Triage & Actions for #{c_num}", expanded=False):
                col_det1, col_det2 = st.columns(2)
                with col_det1:
                    st.markdown("##### 📌 Report Details")
                    st.write(f"**Student**: {case.get('student_name', 'Anonymous')} ({case.get('student_email', 'N/A')})")
                    st.write(f"**Submitted At**: {case.get('created_at')}")
                    st.write(f"**Assigned Department**: {team}")
                    st.write(f"**Affected Population**: {case.get('affected_people') or 'Few'}")

                    if images:
                        st.markdown(f"##### 📸 Cloudinary Evidence ({len(images)} photos)")
                        img_c = st.columns(min(len(images), 3))
                        for i, img in enumerate(images):
                            with img_c[i]:
                                st.image(img.get("secure_url"), caption=img.get("original_filename"), use_container_width=True)
                                if st.button("🗑️ Delete Image", key=f"del_img_{c_id}_{img.get('id')}"):
                                    with st.spinner("Deleting image from Cloudinary..."):
                                        del_ok, del_res = client.delete_case_image(c_id, img.get("id"), token=token)
                                    if del_ok:
                                        st.success("Evidence image removed.")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to delete: {del_res}")

                with col_det2:
                    st.markdown("##### 🔍 Duplicate Detection & Corroboration Review")
                    duplicates = case.get("duplicate_candidates", [])
                    if duplicates:
                        st.warning(f"⚠️ {len(duplicates)} duplicate candidate(s) identified by hybrid analysis:")
                        for cand in duplicates:
                            sim_t = round(cand.get("semantic_similarity", 0) * 100, 1)
                            sim_v = round(cand.get("visual_similarity", 0) * 100, 1)
                            st.markdown(
                                f"- Match with **{cand.get('matched_case_number')}**: Text similarity `{sim_t}%`, Visual similarity `{sim_v}%`"
                            )
                    else:
                        st.success("✅ No duplicate complaints detected.")

                    st.markdown("##### 🛠️ Facility Administrator Action")
                    action_type = st.radio(
                        "Select Resolution Decision:",
                        ["Update Status Only", "Approve & Reassign", "Confirm & Merge Duplicate", "Reject Report"],
                        key=f"act_type_{c_id}",
                    )

                    if action_type == "Update Status Only":
                        new_st = st.selectbox(
                            "New Status:",
                            ["assigned", "in_progress", "resolved", "rejected", "held_for_review"],
                            index=["assigned", "in_progress", "resolved", "rejected", "held_for_review"].index(status) if status in ["assigned", "in_progress", "resolved", "rejected", "held_for_review"] else 0,
                            key=f"new_st_{c_id}",
                        )
                        note = st.text_input("Status Change Audit Note", placeholder="e.g. Technician dispatched to site", key=f"note_st_{c_id}")
                        if st.button("💾 Apply Status Update", key=f"btn_st_{c_id}"):
                            with st.spinner("Updating status..."):
                                upd_ok, upd_res = client.update_case_status(c_id, new_st, note=note, token=token)
                            if upd_ok:
                                st.success("Status updated.")
                                st.rerun()
                            else:
                                st.error(f"Update failed: {upd_res}")

                    elif action_type == "Approve & Reassign":
                        target_team = st.selectbox(
                            "Target Department Team:",
                            ["Electrical Maintenance", "Plumbing & Drainage", "Civil & Structural", "HVAC & Climate Control", "Sanitation & Janitorial", "Campus Security"],
                            key=f"team_{c_id}",
                        )
                        rev_notes = st.text_input("Reviewer Notes", placeholder="e.g. Verified by admin; authorized priority dispatch", key=f"rev_{c_id}")
                        if st.button("✅ Approve & Dispatch", key=f"btn_app_{c_id}"):
                            with st.spinner("Processing approval..."):
                                dec_ok, dec_res = client.make_case_decision(c_id, "approve", reviewer_notes=rev_notes, target_team=target_team, token=token)
                            if dec_ok:
                                st.success("Case approved and assigned.")
                                st.rerun()
                            else:
                                st.error(f"Approval failed: {dec_res}")

                    elif action_type == "Confirm & Merge Duplicate":
                        parent_case_id = st.text_input("Parent Case ID to Merge Into", value=case.get("suspected_parent_case_id") or "", key=f"p_id_{c_id}")
                        rev_notes = st.text_input("Reviewer Notes", placeholder="e.g. Confirmed duplicate of existing incident", key=f"merge_rev_{c_id}")
                        if st.button("🔗 Confirm Duplicate Merge", key=f"btn_mrg_{c_id}"):
                            with st.spinner("Merging duplicate..."):
                                mrg_ok, mrg_res = client.make_case_decision(c_id, "merge_duplicate", reviewer_notes=rev_notes, parent_case_id=parent_case_id, token=token)
                            if mrg_ok:
                                st.success("Case marked as confirmed duplicate.")
                                st.rerun()
                            else:
                                st.error(f"Merge failed: {mrg_res}")

                    elif action_type == "Reject Report":
                        rev_notes = st.text_input("Reason for Rejection", placeholder="e.g. Duplicate test submission or invalid report", key=f"rej_rev_{c_id}")
                        if st.button("❌ Reject Case", key=f"btn_rej_{c_id}"):
                            with st.spinner("Rejecting case..."):
                                rej_ok, rej_res = client.make_case_decision(c_id, "reject", reviewer_notes=rev_notes, token=token)
                            if rej_ok:
                                st.success("Case rejected.")
                                st.rerun()
                            else:
                                st.error(f"Rejection failed: {rej_res}")

            st.markdown("---")


def _render_admin_login(client: ResolveAIClient):
    st.markdown("### 🔒 Administrator Authentication")
    st.markdown("Access to **Admin Triage** is restricted to facility and administrative staff.")

    col_l1, col_l2 = st.columns([1, 1])
    with col_l1:
        with st.form("admin_login_form"):
            username = st.text_input("Admin ID", value="admin_resolve", placeholder="admin_resolve")
            password = st.text_input("Password", type="password", value="MapleFox47", placeholder="MapleFox47")
            login_btn = st.form_submit_button("🔑 Log In to Admin Portal", use_container_width=True)

        if login_btn:
            with st.spinner("Authenticating with ResolveAI security service..."):
                ok, res = client.login(username.strip(), password.strip())

            if ok and isinstance(res, dict):
                token = res.get("token")
                user = res.get("user")
                if user and user.get("role") == "admin":
                    st.session_state.admin_token = token
                    st.session_state.admin_user = user
                    st.success("Authenticated as Administrator.")
                    st.rerun()
                else:
                    st.error("Account does not have administrator privileges.")
            else:
                st.error(f"Authentication failed: {res}")

    with col_l2:
        st.markdown(
            """<div class="portal-card">
                <div class="portal-badge badge-protected">Demo Access</div>
                <h4 style="color: inherit; margin: 0 0 0.5rem 0;">Demo Credentials</h4>
                <p style="color: var(--resolve-muted); font-size: 0.85rem;">
                    Credentials configured in <code>backend/.env</code>:
                </p>
                <div style="background: var(--resolve-surface); padding: 0.8rem; border-radius: 8px; font-family: monospace; font-size: 0.85rem;">
                    ID: <b>admin_resolve</b><br/>
                    Password: <b>MapleFox47</b>
                </div>
                <p style="color: var(--resolve-muted); font-size: 0.75rem; margin-top: 0.8rem;">
                    Sessions use signed HTTP-only cookies and cryptographic bearer tokens validated on every backend route.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )
