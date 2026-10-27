"""ResolveAI — AI-Powered Campus Complaint Resolution System.

Streamlit Frontend Application.
Features:
- Three-Portal Architecture: User Portal, Admin Portal, Testing Portal
- Modern SaaS Dark Theme with interactive Plotly visualisations
- Secure server-validated Role-Based Access Control (Admin / Tester)
- Full OpenCV + Cloudinary evidence pipeline integration
- Live Notion documentation synchronisation
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add frontend directory to sys.path so modules resolve cleanly
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import streamlit as st

# Streamlit Page Configuration must be the first Streamlit command
st.set_page_config(
    page_title="ResolveAI — AI Campus Resolution Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from components.styles import apply_custom_css
from pages.admin_portal import render_admin_portal
from pages.testing_portal import render_testing_portal
from pages.user_portal import render_user_portal
from services.api_client import ResolveAIClient, get_backend_url


def init_session():
    if "active_portal" not in st.session_state:
        st.session_state.active_portal = "home"
    if "api_client" not in st.session_state:
        st.session_state.api_client = ResolveAIClient()


def render_navbar(client: ResolveAIClient):
    current = st.session_state.active_portal

    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        st.markdown(
            """<div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 2rem;">⚡</span>
                <div>
                    <span style="font-size: 1.4rem; font-weight: 800; background: linear-gradient(135deg, #a5b4fc, #6366f1, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">ResolveAI</span><br/>
                    <span style="font-size: 0.75rem; color: var(--resolve-muted); font-weight: 500;">AI-Powered Campus Resolution System</span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    with col2:
        # Backend connectivity badge
        ok, stats = client.get_stats()
        if ok:
            st.markdown(
                '<div style="text-align: center; margin-top: 0.5rem;"><span class="portal-badge badge-public">● Backend Connected</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="text-align: center; margin-top: 0.5rem;"><span class="portal-badge badge-restricted">⚠️ Backend Offline ({get_backend_url()})</span></div>',
                unsafe_allow_html=True,
            )

    with col3:
        if current != "home":
            if st.button("⬅️ Switch Portal", use_container_width=True, key="back_to_portals_btn"):
                st.session_state.active_portal = "home"
                st.rerun()

    st.markdown("<hr style='border: 0; border-top: 1px solid var(--resolve-border); margin: 0.8rem 0 1.5rem 0;'>", unsafe_allow_html=True)


def render_landing_page(client: ResolveAIClient):
    st.markdown(
        """<div style="text-align: center; max-width: 800px; margin: 1rem auto 3rem auto;">
            <h1 style="font-size: 2.8rem; font-weight: 800; line-height: 1.15; margin-bottom: 0.8rem;">
                Intelligent Campus Operations,<br/>
                <span style="background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    Automated & Dispatched in Seconds.
                </span>
            </h1>
            <p style="color: var(--resolve-muted); font-size: 1.1rem; line-height: 1.6;">
                ResolveAI eliminates campus maintenance backlogs by pairing Gemma AI classification with OpenCV visual evidence verification, Cloudinary cloud storage, and n8n facility workflows.
            </p>
        </div>""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    # 1. USER PORTAL CARD
    with col1:
        st.markdown(
            """<div class="portal-card">
                <span class="portal-badge badge-public">Public • No Login</span>
                <div class="portal-card-header">
                    <span class="portal-icon">🎓</span>
                    <h3 class="portal-title">User Portal</h3>
                </div>
                <p class="portal-desc">
                    Submit campus complaints, upload photo evidence via OpenCV & Cloudinary, and track your ticket resolution progress in real time.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )
        if st.button("🚀 Enter User Portal", key="btn_portal_user", use_container_width=True):
            st.session_state.active_portal = "user"
            st.rerun()

    # 2. ADMIN PORTAL CARD
    with col2:
        st.markdown(
            """<div class="portal-card">
                <span class="portal-badge badge-protected">Protected • Admin Role</span>
                <div class="portal-card-header">
                    <span class="portal-icon">🛡️</span>
                    <h3 class="portal-title">Admin Portal</h3>
                </div>
                <p class="portal-desc">
                    Facility triage console with interactive analytics, duplicate detection review, department assignments, and resolution controls.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )
        if st.button("🔑 Enter Admin Portal", key="btn_portal_admin", use_container_width=True):
            st.session_state.active_portal = "admin"
            st.rerun()

    # 3. TESTING PORTAL CARD
    with col3:
        st.markdown(
            """<div class="portal-card">
                <span class="portal-badge badge-restricted">Protected • QA Role</span>
                <div class="portal-card-header">
                    <span class="portal-icon">🧪</span>
                    <h3 class="portal-title">Testing Portal</h3>
                </div>
                <p class="portal-desc">
                    Diagnostics hub for evaluating Gemma AI extractions, Cloudinary uploads, empirical benchmark metrics, and Notion sync.
                </p>
            </div>""",
            unsafe_allow_html=True,
        )
        if st.button("🔬 Enter Testing Portal", key="btn_portal_testing", use_container_width=True):
            st.session_state.active_portal = "testing"
            st.rerun()

    st.markdown("<div style='margin-top: 3.5rem;'></div>", unsafe_allow_html=True)

    # Architecture Highlights Row
    c_arch1, c_arch2, c_arch3, c_arch4 = st.columns(4)
    with c_arch1:
        st.markdown(
            """<div style="background: var(--resolve-surface); border: 1px solid var(--resolve-border); border-radius: 12px; padding: 1rem; text-align: center;">
                <div style="font-size: 1.6rem;">👁️</div>
                <div style="font-weight: 700; color: inherit; margin-top: 0.3rem;">OpenCV Vision</div>
                <div style="font-size: 0.78rem; color: var(--resolve-muted); margin-top: 0.2rem;">Blur scoring & perceptual hashing</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c_arch2:
        st.markdown(
            """<div style="background: var(--resolve-surface); border: 1px solid var(--resolve-border); border-radius: 12px; padding: 1rem; text-align: center;">
                <div style="font-size: 1.6rem;">☁️</div>
                <div style="font-weight: 700; color: inherit; margin-top: 0.3rem;">Cloudinary CDN</div>
                <div style="font-size: 0.78rem; color: var(--resolve-muted); margin-top: 0.2rem;">Secure evidence photo storage</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c_arch3:
        st.markdown(
            """<div style="background: var(--resolve-surface); border: 1px solid var(--resolve-border); border-radius: 12px; padding: 1rem; text-align: center;">
                <div style="font-size: 1.6rem;">🤖</div>
                <div style="font-weight: 700; color: inherit; margin-top: 0.3rem;">Gemma 2B AI</div>
                <div style="font-size: 0.78rem; color: var(--resolve-muted); margin-top: 0.2rem;">Entity extraction & priority estimation</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c_arch4:
        st.markdown(
            """<div style="background: var(--resolve-surface); border: 1px solid var(--resolve-border); border-radius: 12px; padding: 1rem; text-align: center;">
                <div style="font-size: 1.6rem;">📓</div>
                <div style="font-weight: 700; color: inherit; margin-top: 0.3rem;">Notion Sync</div>
                <div style="font-size: 0.78rem; color: var(--resolve-muted); margin-top: 0.2rem;">Automated workspace docs update</div>
            </div>""",
            unsafe_allow_html=True,
        )


def main():
    init_session()
    apply_custom_css()
    client: ResolveAIClient = st.session_state.api_client

    render_navbar(client)

    portal = st.session_state.active_portal
    if portal == "user":
        render_user_portal(client)
    elif portal == "admin":
        render_admin_portal(client)
    elif portal == "testing":
        render_testing_portal(client)
    else:
        render_landing_page(client)


if __name__ == "__main__":
    main()
