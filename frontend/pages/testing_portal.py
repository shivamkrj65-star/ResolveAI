"""Testing Portal (Protected) for ResolveAI.

Restricted to QA & Reliability testing roles. Provides 6 functional diagnostic sections:
1. Backend Health
2. API Testing
3. AI/ML Testing
4. Cloudinary Testing
5. Notion Testing
6. System Logs & Diagnostics (Benchmark metrics & n8n workflow execution)
"""

from __future__ import annotations

import io
from typing import Any, Dict, List, Optional
from PIL import Image, ImageDraw
import streamlit as st
from services.api_client import ResolveAIClient
from utils.helpers import render_priority_badge, render_status_badge


def render_testing_portal(client: ResolveAIClient):
    if "tester_token" not in st.session_state:
        st.session_state.tester_token = None
    if "tester_user" not in st.session_state:
        st.session_state.tester_user = None

    token = st.session_state.tester_token
    if not token:
        _render_tester_login(client)
        return

    # Verify session validity and role
    ok, me = client.get_me(token)
    if not ok or not me.get("authenticated") or me.get("user", {}).get("role") != "tester":
        st.session_state.tester_token = None
        st.session_state.tester_user = None
        st.warning("Testing session expired or unauthorized. Please log in again.")
        _render_tester_login(client)
        return

    user = me.get("user", {})
    col_u1, col_u2 = st.columns([3, 1])
    with col_u1:
        st.markdown(
            f"### 🧪 QA & Reliability Testing Portal — <span style='color: var(--resolve-accent);'>{user.get('display_name', 'QA Tester')}</span>",
            unsafe_allow_html=True,
        )
        st.caption(f"Role: `tester` | Username: `{user.get('username')}` | System Testing Suite")
    with col_u2:
        if st.button("🚪 Logout Tester", use_container_width=True, key="tester_logout_btn"):
            client.logout(token)
            st.session_state.tester_token = None
            st.session_state.tester_user = None
            st.rerun()

    test_tabs = st.tabs([
        "🩺 1. Backend Health",
        "⚡ 2. API Testing",
        "🧠 3. AI/ML Testing",
        "📸 4. Cloudinary Testing",
        "📓 5. Notion Testing",
        "📊 6. System Logs & Diagnostics",
    ])

    # =========================================================================
    # TAB 1: BACKEND HEALTH
    # =========================================================================
    with test_tabs[0]:
        st.markdown("### 🩺 Service Health & Operational Status")
        st.markdown("Real-time telemetry and component connectivity.")

        if st.button("🔄 Refresh System Health", key="refresh_health_btn"):
            st.rerun()

        ok, stats = client.get_stats()
        if ok and isinstance(stats, dict):
            h1, h2, h3, h4 = st.columns(4)
            with h1:
                st.success("🟢 FastAPI Backend: Operational")
            with h2:
                st.success(f"🟢 n8n Engine: {stats.get('n8n_webhook_health', 'operational').title()}")
            with h3:
                c_conf = stats.get("cloudinary_configured", False)
                if c_conf:
                    st.success("🟢 Cloudinary Storage: Configured")
                else:
                    st.warning("🟡 Cloudinary Storage: Unconfigured")
            with h4:
                n_conf = stats.get("notion_configured", False)
                if n_conf:
                    st.success("🟢 Notion Sync: Configured")
                else:
                    st.warning("🟡 Notion Sync: Unconfigured")

            st.markdown("#### Database Case Breakdown")
            st.json(stats)
        else:
            st.error(f"Backend connectivity check failed: {stats}")

    # =========================================================================
    # TAB 2: API TESTING
    # =========================================================================
    with test_tabs[1]:
        st.markdown("### ⚡ Interactive Backend Endpoint Testing")
        st.markdown("Execute authenticated requests against core backend API endpoints.")

        api_endpoint = st.selectbox(
            "Select API Endpoint to Test:",
            [
                "GET /api/v1/stats (Public Stats)",
                "GET /api/v1/auth/me (Active Session Verify)",
                "GET /api/v1/testing/cases (Retrieve All Cases)",
                "GET /api/v1/metrics/benchmark (Benchmark & Ablation Data)",
                "GET /api/v1/integrations/verify (Safe Integrations Verification)",
            ],
        )

        if st.button("🚀 Execute API Call", key="exec_api_btn"):
            with st.spinner("Invoking endpoint..."):
                if "GET /api/v1/stats" in api_endpoint:
                    res_ok, res_data = client.get_stats()
                elif "GET /api/v1/auth/me" in api_endpoint:
                    res_ok, res_data = client.get_me(token)
                elif "GET /api/v1/testing/cases" in api_endpoint:
                    res_ok, res_data = client.get_testing_cases(token)
                elif "GET /api/v1/metrics/benchmark" in api_endpoint:
                    res_ok, res_data = client.get_benchmark_metrics(token)
                elif "GET /api/v1/integrations/verify" in api_endpoint:
                    res_ok, res_data = client.verify_integrations(token)
                else:
                    res_ok, res_data = False, "Unknown endpoint"

            if res_ok:
                st.success("HTTP 200 OK — Response received successfully:")
                st.json(res_data)
            else:
                st.error(f"API Call Failed: {res_data}")

    # =========================================================================
    # TAB 3: AI/ML TESTING
    # =========================================================================
    with test_tabs[2]:
        st.markdown("### 🧠 Gemma AI & OpenCV Model Pipeline Testing")
        st.markdown(
            "Test the multi-stage machine learning inference pipeline on arbitrary campus complaint text. "
            "Gemma extracts structured attributes, OpenCV validates visual integrity, and the priority algorithm assigns authoritative severity scores."
        )

        test_prompt = st.text_area(
            "Sample Complaint Text for Model Evaluation:",
            value="High voltage spark and smoke coming from circuit breaker box near 2nd floor library. Sparks visible!",
            height=100,
        )
        sample_loc = st.selectbox("Simulated Building Location:", ["Library Complex", "Block C", "Block A", "Hostels"])

        if st.button("🧪 Run Gemma Model Extraction", key="run_ai_btn"):
            with st.spinner("Running inference through backend extraction pipeline..."):
                # Submit a dry-run complaint
                sub_ok, sub_data = client.submit_complaint(
                    raw_text=test_prompt.strip(),
                    student_name="QA Synthetic Test Agent",
                    student_email="tester@resolveai.internal",
                    reported_block=sample_loc,
                    reported_floor="2nd Floor",
                    affected_people="High (20-100)",
                )

            if sub_ok and isinstance(sub_data, dict):
                st.success("✅ Extraction Pipeline Completed Successfully!")
                ext = sub_data.get("extraction", {})

                col_a1, col_a2, col_a3 = st.columns(3)
                with col_a1:
                    st.metric("Extracted Issue Type", ext.get("issue_type", "N/A").replace("_", " ").title())
                with col_a2:
                    st.metric("Safety Risk Detected", "CRITICAL / YES" if ext.get("safety_risk") else "NO")
                with col_a3:
                    st.metric("Estimated Priority Score", f"{sub_data.get('priority_score', 0)} / 10")

                st.markdown("##### Gemma Extracted JSON Output")
                st.json(ext)

                st.markdown("##### Assigned Dispatch Route via n8n")
                st.json(sub_data.get("n8n_dispatch"))
            else:
                st.error(f"Inference failed: {sub_data}")

    # =========================================================================
    # TAB 4: CLOUDINARY TESTING
    # =========================================================================
    with test_tabs[3]:
        st.markdown("### 📸 Cloudinary Media Pipeline Verification")
        st.markdown("Inspect Cloudinary configuration and test live media uploads through the backend processing service.")

        col_c_st, col_c_up = st.columns(2)
        with col_c_st:
            st.markdown("#### Cloudinary Configuration Status")
            c_ok, c_status = client.get_cloudinary_status(token)
            if c_ok and isinstance(c_status, dict):
                st.json(c_status)
                if c_status.get("configured"):
                    st.success("Cloudinary is fully configured on the backend.")
                else:
                    st.warning(f"Missing Cloudinary credentials: {c_status.get('missing_credentials')}")
            else:
                st.error(f"Failed to fetch Cloudinary status: {c_status}")

        with col_c_up:
            st.markdown("#### Test Synthetic Image Upload")
            st.caption("Generates a non-destructive test image, processes it via OpenCV, and uploads to Cloudinary.")

            if st.button("📤 Upload Test Image to Cloudinary", key="test_cloud_upload_btn"):
                # Create a synthetic test image using PIL
                img = Image.new("RGB", (320, 240), color=(30, 41, 59))
                d = ImageDraw.Draw(img)
                d.rectangle([(20, 20), (300, 220)], outline=(99, 102, 241), width=4)
                d.text((40, 110), "ResolveAI Test Evidence", fill=(255, 255, 255))

                buf = io.BytesIO()
                img.save(buf, format="JPEG")
                img_bytes = buf.getvalue()

                with st.spinner("Uploading evidence via backend Cloudinary service..."):
                    up_ok, up_res = client.submit_complaint(
                        raw_text="Automated test complaint for Cloudinary storage verification.",
                        student_name="QA Automated Tester",
                        student_email="qa@resolveai.internal",
                        reported_block="Block B (Science Wing)",
                        files=[("qa_test_evidence.jpg", img_bytes, "image/jpeg")],
                    )

                if up_ok and isinstance(up_res, dict):
                    imgs = up_res.get("images", [])
                    if imgs:
                        test_img = imgs[0]
                        st.success("✅ Test image uploaded to Cloudinary successfully!")
                        st.markdown(f"**Public ID**: `{test_img.get('public_id')}`")
                        st.markdown(f"**Secure URL**: [{test_img.get('secure_url')}]({test_img.get('secure_url')})")
                        st.image(test_img.get("secure_url"), caption="Returned Cloudinary Evidence", width=300)
                    else:
                        st.warning("Report created, but no image returned. Verify backend configuration.")
                else:
                    st.error(f"Cloudinary test upload failed: {up_res}")

    # =========================================================================
    # TAB 5: NOTION TESTING
    # =========================================================================
    with test_tabs[4]:
        st.markdown("### 📓 Notion Documentation & Results Synchronization")
        st.markdown(
            "Inspect Notion configuration, run live authentication pings, and trigger workspace documentation synchronisation."
        )

        n_col1, n_col2 = st.columns(2)
        with n_col1:
            st.markdown("#### Notion Configuration Status")
            n_ok, n_status = client.get_notion_status(token)
            if n_ok and isinstance(n_status, dict):
                st.json(n_status)
                if n_status.get("configured"):
                    st.success("Notion workspace documentation sync is configured.")
                else:
                    st.info(f"Notion sync configuration note: {n_status.get('missing_configuration')}")
            else:
                st.error(f"Failed to fetch Notion status: {n_status}")

        with n_col2:
            st.markdown("#### Notion Live Verification")
            if st.button("🔗 Verify Notion Connection", key="verify_notion_btn"):
                with st.spinner("Pinging Notion API..."):
                    v_ok, v_res = client.verify_integrations(token)
                if v_ok and isinstance(v_res, dict):
                    st.json(v_res.get("notion", {}))
                    if v_res.get("notion", {}).get("connected"):
                        st.success("✅ Notion API connected successfully!")
                    else:
                        st.warning(f"Notion verification note: {v_res.get('notion', {}).get('error') or v_res.get('notion', {}).get('reason')}")
                else:
                    st.error(f"Verification call failed: {v_res}")

        st.markdown("---")
        st.markdown("#### 🚀 Trigger Live Documentation Sync")
        st.caption("Generates and synchronizes project architecture, metrics, and active case logs to the Notion workspace page.")

        if st.button("⚡ Synchronize Documentation to Notion", key="sync_notion_btn", use_container_width=True):
            with st.spinner("Synchronizing test records and system documentation to Notion..."):
                sync_ok, sync_res = client.sync_notion(token)

            if sync_ok and isinstance(sync_res, dict):
                st.success(f"🎉 {sync_res.get('message')}")
                st.markdown(f"- **Status**: `{sync_res.get('status')}`")
                st.markdown(f"- **Notion Page ID**: `{sync_res.get('page_id')}`")
                st.markdown(f"- **Synced At**: `{sync_res.get('synced_at')}`")
            else:
                st.error(f"Notion synchronization error: {sync_res}")

    # =========================================================================
    # TAB 6: SYSTEM LOGS & DIAGNOSTICS
    # =========================================================================
    with test_tabs[5]:
        st.markdown("### 📊 System Logs, Empirical Benchmarks & Diagnostics")

        b_col1, b_col2 = st.columns([3, 1])
        with b_col1:
            st.markdown("#### Empirical Evaluation Metrics & Ablation Study")
        with b_col2:
            if st.button("🔄 Reset Demo State", key="reset_demo_btn", help="Cleans test cases and resets rate limiters back to clean baseline."):
                rst_ok, rst_res = client.reset_demo(token)
                if rst_ok:
                    st.success("Demo dataset reset to initial state.")
                    st.rerun()
                else:
                    st.error(f"Reset failed: {rst_res}")

        m_ok, benchmark = client.get_benchmark_metrics(token)
        if m_ok and isinstance(benchmark, dict):
            st.markdown(f"**Benchmark Dataset Size**: `{benchmark.get('dataset_size', 0)}` annotated campus test cases")

            c_met1, c_met2, c_met3 = st.columns(3)
            with c_met1:
                st.metric("Priority Accuracy", f"{round(benchmark.get('priority_accuracy', 0) * 100, 1)}%")
            with c_met2:
                st.metric("Duplicate F1 Score", f"{round(benchmark.get('duplicate_f1_score', 0) * 100, 1)}%")
            with c_met3:
                st.metric("Average Latency", f"{round(benchmark.get('average_latency_ms', 0), 1)} ms")

            st.markdown("##### Ablation Study Comparison")
            ablation = benchmark.get("ablation_study", [])
            if ablation:
                st.dataframe(ablation, use_container_width=True)

            with st.expander("📄 View Full Benchmark JSON Payload"):
                st.json(benchmark)
        else:
            st.error(f"Failed to load benchmark metrics: {benchmark}")


def _render_tester_login(client: ResolveAIClient):
    st.markdown("### 🔒 QA & Testing Authentication")
    st.markdown("Access to the **Testing Portal** is restricted to system QA and evaluation engineers.")

    col_l1, col_l2 = st.columns([1, 1])
    with col_l1:
        with st.form("tester_login_form"):
            username = st.text_input("Tester ID", value="tester_resolve", placeholder="tester_resolve")
            password = st.text_input("Password", type="password", value="OrbitPanda82", placeholder="OrbitPanda82")
            login_btn = st.form_submit_button("🔑 Log In to Testing Portal", use_container_width=True)

        if login_btn:
            with st.spinner("Authenticating with ResolveAI QA security service..."):
                ok, res = client.login(username.strip(), password.strip())

            if ok and isinstance(res, dict):
                token = res.get("token")
                user = res.get("user")
                if user and user.get("role") == "tester":
                    st.session_state.tester_token = token
                    st.session_state.tester_user = user
                    st.success("Authenticated as QA Tester.")
                    st.rerun()
                else:
                    st.error("Account does not have QA / tester privileges.")
            else:
                st.error(f"Authentication failed: {res}")

    with col_l2:
        st.markdown(
            """<div class="portal-card">
                <div class="portal-badge badge-restricted">Demo Credentials</div>
                <h4 style="color: inherit; margin: 0 0 0.5rem 0;">Testing Credentials</h4>
                <p style="color: var(--resolve-muted); font-size: 0.85rem;">
                    Configured in <code>backend/.env</code>:
                </p>
                <div style="background: var(--resolve-surface); padding: 0.8rem; border-radius: 8px; font-family: monospace; font-size: 0.85rem;">
                    ID: <b>tester_resolve</b><br/>
                    Password: <b>OrbitPanda82</b>
                </div>
                <p style="color: var(--resolve-muted); font-size: 0.75rem; margin-top: 0.8rem;">
                    Provides access to backend health, API tests, Gemma AI prompt evaluation, Cloudinary validation, and Notion sync.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )
