from pathlib import Path

import pandas as pd
import streamlit as st

def compact_count(value: int) -> str:
    if value >= 1000:
        return f"{value / 1000:.1f}K"
    return str(int(value))


def get_dashboard_counts(raw_df, review_df, history_df) -> dict[str, int]:
    counts = {"teams": 0, "projects": 0, "reviews": 0}

    processed_dir = Path("data/processed")
    employee_file = processed_dir / "employee_synthesized.csv"
    project_file = processed_dir / "projects.csv"
    review_file = processed_dir / "performance_reviews.csv"

    if employee_file.exists():
        try:
            employee_df = pd.read_csv(employee_file)
            if "Department" in employee_df.columns:
                counts["teams"] = int(employee_df["Department"].nunique())
        except Exception:
            pass

    if project_file.exists():
        try:
            counts["projects"] = int(pd.read_csv(project_file).shape[0])
        except Exception:
            pass

    if review_file.exists():
        try:
            counts["reviews"] = int(pd.read_csv(review_file).shape[0])
        except Exception:
            pass

    if counts["teams"] == 0 and hasattr(raw_df, "empty") and not raw_df.empty and "Department" in raw_df.columns:
        counts["teams"] = int(raw_df["Department"].nunique())
    if counts["projects"] == 0 and hasattr(raw_df, "empty") and not raw_df.empty:
        counts["projects"] = 250
    if counts["reviews"] == 0 and hasattr(review_df, "empty") and not review_df.empty:
        counts["reviews"] = len(review_df)

    return counts


def render_sidebar(history_df, review_df, warehouse_review_df):
    with st.sidebar:
        st.markdown(
            """
            <div class='sidebar-brand'>
                <div class='sidebar-brand-mark'>HR</div>
                <div>
                    <div class='sidebar-brand-title'>Command Center</div>
                    <div class='sidebar-brand-sub'>People & performance</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div class='section-title'>Navigation</div>", unsafe_allow_html=True)

        nav_options = [
            "Overview",
            "Employee Onboarding",
            "Project Assignment",
            "Review Tracking",
            "Warehouse Analytics",
        ]
        if "selected_nav" not in st.session_state:
            st.session_state["selected_nav"] = "Overview"

        selected_nav = st.radio(
            "Go to",
            nav_options,
            index=nav_options.index(st.session_state["selected_nav"]),
            label_visibility="collapsed",
        )
        st.session_state["selected_nav"] = selected_nav

        if st.session_state.get("db_ready"):
            pass

        st.markdown("<div class='section-title' style='margin-top:1.2rem;'>Filters</div>", unsafe_allow_html=True)
        department_values = pd.concat(
            [
                history_df.get("department", pd.Series(dtype="object")),
                review_df.get("department", pd.Series(dtype="object")),
                warehouse_review_df.get("department", pd.Series(dtype="object")),
            ],
            ignore_index=True,
        ).dropna().astype(str).str.strip()
        departments = sorted(value for value in department_values.unique() if value)

        date_values = pd.to_datetime(
            pd.concat(
                [
                    review_df.get("review_date", pd.Series(dtype="object")),
                    warehouse_review_df.get("review_date", pd.Series(dtype="object")),
                ],
                ignore_index=True,
            ),
            errors="coerce",
        )
        years = sorted(date_values.dropna().dt.year.astype(str).unique().tolist())
        selected_department = st.selectbox("Department", ["All", *departments])
        selected_year = st.selectbox("Year", ["All", *years])

        return selected_department, selected_year


def render_hero(hero_team_count: int, hero_project_count: int, hero_review_count: int):
    st.markdown(
        f"""
        <div class="hero-panel anim-in delay-1">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap;">
                <div>
                    <h1>HR Analytics Command Center</h1>
                    <p>Employee lifecycle, project allocation, and performance intelligence</p>
                </div>
                <div class="status-pill"><span class="tiny-dot"></span> Live Ops</div>
            </div>
            <div class="hero-meta">
                <div class="status-pill"><span class="tiny-dot"></span> Workforce Pulse</div>
                <div class="status-pill"><span class="tiny-dot"></span> OLAP Ready</div>
                <div class="status-pill"><span class="tiny-dot"></span> Decision Support</div>
            </div>
            <div class="hero-stats">
                <div class="hero-stat">
                    <span class="label">Teams</span>
                    <span class="value">{compact_count(hero_team_count)}</span>
                </div>
                <div class="hero-stat">
                    <span class="label">Projects</span>
                    <span class="value">{compact_count(hero_project_count)}</span>
                </div>
                <div class="hero-stat">
                    <span class="label">Reviews</span>
                    <span class="value">{compact_count(hero_review_count)}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def animated_kpi_card(label: str, value: int, sub_label: str, history_key: str, is_simulated: bool = False):
    prev = st.session_state["kpi_prev"].get(history_key, value)
    st.session_state["kpi_prev"][history_key] = value

    hist = st.session_state["kpi_history"][history_key]
    hist.append(value)
    st.session_state["kpi_history"][history_key] = hist[-24:]
    points = st.session_state["kpi_history"][history_key]

    delta = value - prev
    if delta > 0:
        delta_html = f'<span class="delta-up">&#9650; {delta:,}</span>'
    elif delta < 0:
        delta_html = f'<span class="delta-down">&#9660; {abs(delta):,}</span>'
    else:
        delta_html = '<span class="delta-flat">&mdash; steady</span>'

    spark_svg = ""
    if len(points) >= 2:
        w, h, pad = 180, 34, 4
        lo, hi = min(points), max(points)
        span = (hi - lo) or 1
        step = (w - 2 * pad) / (len(points) - 1)
        coords = []
        for i, p in enumerate(points):
            x = pad + i * step
            y = pad + (1 - (p - lo) / span) * (h - 2 * pad)
            coords.append(f"{x:.1f},{y:.1f}")
        path = " ".join(coords)
        spark_svg = f"""
        <svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="margin-top:6px;">
            <polyline points="{path}" fill="none" stroke="#34d399" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>
        </svg>
        """

    html = f"""
    <div style="font-family:'Inter',sans-serif;">
        <div style="
            background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            min-height: 168px;
            padding: 1rem 1rem 0.9rem;
            box-shadow: 0 12px 22px rgba(15, 23, 42, 0.04);
            position: relative;
            overflow: hidden;
        ">
            <div style="position:absolute; inset:0 0 auto 0; height:3px;
                background:linear-gradient(90deg,#2563eb,#60a5fa,#a5b4fc);"></div>
            <div style="font-size:0.72rem; font-weight:700; letter-spacing:0.12em;
                text-transform:uppercase; color:#475569;">{label}</div>
            <div id="kpi-{history_key}" style="color:#0f172a; font-size:2.1rem; font-weight:800;
                letter-spacing:-0.06em; line-height:1.15; margin-top:0.4rem;">{prev:,}</div>
            <div style="margin-top:0.4rem; color:#475569; font-size:0.78rem;
                display:flex; align-items:center; gap:0.4rem;">
                {delta_html}<span>{sub_label}</span>
            </div>
            {spark_svg}
        </div>
    </div>
    <script>
        (function() {{
            const el = document.getElementById("kpi-{history_key}");
            const start = {prev};
            const end = {value};
            const duration = 900;
            const t0 = performance.now();
            function step(now) {{
                const p = Math.min((now - t0) / duration, 1);
                const eased = 1 - Math.pow(1 - p, 3);
                const val = Math.round(start + (end - start) * eased);
                el.textContent = val.toLocaleString();
                if (p < 1) requestAnimationFrame(step);
            }}
            requestAnimationFrame(step);
        }})();
    </script>
    """
    st.components.v1.iframe(
        f"data:text/html;charset=utf-8,{html}",
        height=210,
        scrolling=False,
    )


def style_chart(fig, title: str, y_title: str = "", x_title: str = ""):
    fig.update_layout(
        title={
            "text": title,
            "font": {"family": "Space Grotesk, sans-serif", "size": 18, "color": "#173d39"},
            "x": 0.02,
            "xanchor": "left",
        },
        paper_bgcolor="rgba(255,255,255,0.78)",
        plot_bgcolor="rgba(255,255,255,0)",
        font={"family": "DM Sans, sans-serif", "color": "#47635e", "size": 12},
        margin={"l": 18, "r": 18, "t": 58, "b": 24},
        hovermode="x unified",
        hoverlabel={"bgcolor": "#173d39", "font": {"color": "#f5fffb", "size": 12}},
        xaxis={
            "title": x_title,
            "showgrid": False,
            "linecolor": "#cfe0db",
            "tickfont": {"color": "#47635e"},
        },
        yaxis={
            "title": y_title,
            "showgrid": True,
            "gridcolor": "#e2eeeb",
            "zeroline": False,
            "tickfont": {"color": "#47635e"},
        },
        transition_duration=450,
        colorway=["#2563eb", "#4f46e5", "#0891b2", "#7c3aed", "#06b6d4", "#22d3ee"],
    )
    return fig
