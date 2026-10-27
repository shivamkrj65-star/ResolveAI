"""Theme-aware presentation styles with blue/purple accents for ResolveAI."""

import streamlit as st


def apply_custom_css():
    st.markdown(
        """
        <style>
        /* Global Background and Typography */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Inherit Streamlit's active theme, including its native theme switch.
           Relative colors work without private Streamlit theme attributes. */
        .stApp {
            --resolve-info: color-mix(in srgb, #3b82f6 35%, currentColor);
            --resolve-success: color-mix(in srgb, #10b981 35%, currentColor);
            --resolve-warning: color-mix(in srgb, #f59e0b 35%, currentColor);
            --resolve-danger: color-mix(in srgb, #ef4444 35%, currentColor);
            --resolve-accent: color-mix(in srgb, #8b5cf6 35%, currentColor);
            --resolve-surface: color-mix(in srgb, currentColor 5%, transparent);
            --resolve-border: color-mix(in srgb, currentColor 20%, transparent);
            --resolve-muted: color-mix(in srgb, currentColor 80%, transparent);
            background-image: radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.08) 0%, transparent 45%),
                              radial-gradient(circle at 85% 85%, rgba(139, 92, 246, 0.08) 0%, transparent 45%);
        }

        /* Modern Portal Cards */
        .portal-card {
            background: var(--resolve-surface);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 1.8rem;
            height: 100%;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }

        .portal-card:hover {
            transform: translateY(-4px);
            border-color: rgba(139, 92, 246, 0.5);
            box-shadow: 0 12px 30px -10px rgba(99, 102, 241, 0.3);
        }

        .portal-card-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        }

        .portal-icon {
            font-size: 2rem;
            padding: 0.6rem;
            background: rgba(99, 102, 241, 0.15);
            border-radius: 12px;
            display: inline-flex;
        }

        .portal-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: inherit;
            margin: 0;
        }

        .portal-desc {
            font-size: 0.9rem;
            color: var(--resolve-muted);
            line-height: 1.5;
            min-height: 48px;
            margin-bottom: 1.2rem;
        }

        .portal-badge {
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            margin-bottom: 0.8rem;
        }

        .badge-public {
            background: rgba(16, 185, 129, 0.15);
            color: var(--resolve-success);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .badge-protected {
            background: rgba(99, 102, 241, 0.15);
            color: var(--resolve-accent);
            border: 1px solid rgba(99, 102, 241, 0.3);
        }

        .badge-restricted {
            background: rgba(245, 158, 11, 0.15);
            color: var(--resolve-warning);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        /* Metric Highlights */
        .metric-card {
            background: var(--resolve-surface);
            border: 1px solid var(--resolve-border);
            border-radius: 14px;
            padding: 1.2rem;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        }

        .metric-value {
            font-size: 2.2rem;
            font-weight: 800;
            color: inherit;
            margin: 0.2rem 0;
        }

        .metric-label {
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--resolve-muted);
            font-weight: 600;
        }

        /* Status Pills */
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
        }
        .status-assigned { background: rgba(59, 130, 246, 0.2); color: var(--resolve-info); border: 1px solid rgba(59, 130, 246, 0.4); }
        .status-held { background: rgba(245, 158, 11, 0.2); color: var(--resolve-warning); border: 1px solid rgba(245, 158, 11, 0.4); }
        .status-resolved { background: rgba(16, 185, 129, 0.2); color: var(--resolve-success); border: 1px solid rgba(16, 185, 129, 0.4); }
        .status-rejected { background: rgba(239, 68, 68, 0.2); color: var(--resolve-danger); border: 1px solid rgba(239, 68, 68, 0.4); }
        .status-inprogress { background: rgba(139, 92, 246, 0.2); color: var(--resolve-accent); border: 1px solid rgba(139, 92, 246, 0.4); }

        /* Priority Pills */
        .priority-critical { background: rgba(239, 68, 68, 0.25); color: var(--resolve-danger); border: 1px solid rgba(239, 68, 68, 0.5); font-weight: 700; }
        .priority-high { background: rgba(249, 115, 22, 0.25); color: var(--resolve-warning); border: 1px solid rgba(249, 115, 22, 0.5); }
        .priority-medium { background: rgba(59, 130, 246, 0.25); color: var(--resolve-info); border: 1px solid rgba(59, 130, 246, 0.5); }
        .priority-low { background: rgba(16, 185, 129, 0.25); color: var(--resolve-success); border: 1px solid rgba(16, 185, 129, 0.5); }

        /* Timeline and History */
        .timeline-item {
            position: relative;
            padding-left: 1.6rem;
            padding-bottom: 1.2rem;
            border-left: 2px solid rgba(99, 102, 241, 0.3);
        }
        .timeline-item::before {
            content: '';
            position: absolute;
            left: -6px;
            top: 2px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #818cf8;
            box-shadow: 0 0 10px #6366f1;
        }

        /* Buttons Styling */
        div.stButton > button:first-child,
        div.stFormSubmitButton > button:first-child {
            border-radius: 10px;
            font-weight: 600;
            transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            border: 1px solid var(--resolve-border);
        }
        div.stButton > button:first-child:hover:not(:disabled),
        div.stFormSubmitButton > button:first-child:hover:not(:disabled) {
            border-color: #6366f1;
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
        }

        div.stButton > button:focus-visible,
        div.stFormSubmitButton > button:focus-visible {
            outline: 2px solid currentColor;
            outline-offset: 2px;
        }

        /* Streamlit Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 1px solid var(--resolve-border);
            margin-bottom: 1.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
            border-radius: 8px 8px 0 0;
            color: var(--resolve-muted);
            font-weight: 600;
        }

        .stTabs [aria-selected="true"] {
            color: inherit !important;
            border-bottom-color: #6366f1 !important;
        }

        .stApp :is(a, button, input, textarea, select, [tabindex]):focus-visible {
            outline: 2px solid currentColor;
            outline-offset: 2px;
        }

        @media (max-width: 640px) {
            .portal-card { padding: 1rem; overflow-wrap: anywhere; }
            .portal-card-header > * { min-width: 0; }
            .portal-card-header { flex-wrap: wrap; }
        }

        @media (prefers-reduced-motion: reduce) {
            .stApp *, .stApp *::before, .stApp *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }
            .portal-card:hover { transform: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
