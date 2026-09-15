CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background: #eef4f3;
        color: #142525;
    }

    .stApp {
        background:
            radial-gradient(circle at 88% 4%, rgba(16, 185, 129, 0.09), transparent 25rem),
            linear-gradient(135deg, #f5f8f6 0%, #edf4f2 52%, #e8f0ef 100%);
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 0.35rem;
        padding-bottom: 3rem;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .anim-in {
        animation: fadeInUp 0.5s ease both;
    }
    .delay-1 { animation-delay: 0.05s; }
    .delay-2 { animation-delay: 0.12s; }
    .delay-3 { animation-delay: 0.18s; }
    .delay-4 { animation-delay: 0.24s; }
    .delay-5 { animation-delay: 0.30s; }
    .delay-6 { animation-delay: 0.36s; }

    .hero-panel {
        background: linear-gradient(120deg, #102d2b 0%, #184744 62%, #21675e 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 1.7rem 1.8rem;
        box-shadow: 0 18px 38px rgba(20, 56, 53, 0.18);
        margin-bottom: 0.35rem;
        position: relative;
        overflow: hidden;
    }

    .hero-panel::after {
        content: "";
        position: absolute;
        width: 18rem;
        height: 18rem;
        right: -5rem;
        top: -9rem;
        border: 1px solid rgba(167, 243, 208, 0.22);
        border-radius: 50%;
        box-shadow: 0 0 0 2rem rgba(167, 243, 208, 0.04), 0 0 0 4rem rgba(167, 243, 208, 0.03);
    }

    .hero-panel h1 {
        margin: 0;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.25rem;
        font-weight: 700;
        line-height: 1.1;
        letter-spacing: 0;
        color: #f5fffb;
    }

    .hero-panel p {
        margin: 0.7rem 0 0;
        font-size: 1rem;
        color: #c5e3dc;
    }

    .hero-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.7rem;
        margin-top: 1.1rem;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.4rem 0.8rem;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.18);
        background: rgba(255,255,255,0.08);
        color: #ebfffa;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .status-pill .tiny-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #7ef0c7;
        box-shadow: 0 0 0 4px rgba(126, 240, 199, 0.18);
    }

    .hero-stats {
        display: grid;
        grid-template-columns: repeat(3, minmax(110px, 1fr));
        gap: 0.8rem;
        margin-top: 1.3rem;
    }

    .hero-stat {
        background: rgba(10, 27, 27, 0.22);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 0.7rem 0.8rem;
        backdrop-filter: blur(5px);
    }

    .hero-stat .label {
        display: block;
        color: #c7efe4;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .hero-stat .value {
        display: block;
        margin-top: 0.3rem;
        color: #f5fffb;
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.05em;
    }

    .status-badge {
        display: flex;
        min-height: 120px;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.55rem;
        background: #e9f7f2;
        border: 1px solid #c4e8dc;
        border-radius: 20px;
        color: #176557;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        box-shadow: 0 10px 22px rgba(37, 99, 235, 0.05);
    }

    .live-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.18);
    }

    .live-dot.paused {
        background: #94a3b8;
        box-shadow: none;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.86);
        border: 1px solid #d7e5e1;
        border-radius: 14px;
        min-height: 160px;
        padding: 1rem 1rem 0.85rem;
        box-shadow: 0 10px 24px rgba(20, 56, 53, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 18px 30px rgba(30, 41, 59, 0.08);
    }

    .metric-card::after {
        content: "";
        position: absolute;
        inset: 0 0 auto 0;
        height: 3px;
        background: linear-gradient(90deg, #2563eb, #60a5fa, #a5b4fc);
    }

    .metric-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #475569;
    }

    .metric-value {
        color: #142525;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.06em;
        line-height: 1.15;
        margin-top: 0.45rem;
    }

    .metric-sub {
        margin-top: 0.55rem;
        color: #475569;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }

    .delta-up { color: #16a34a; font-weight: 700; }
    .delta-down { color: #dc2626; font-weight: 700; }
    .delta-flat { color: #64748b; font-weight: 700; }

    .section-title {
        color: #173d39;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: 0;
        margin-bottom: 0.8rem;
    }

    .feature-card {
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid #d7e5e1;
        border-radius: 14px;
        padding: 1rem;
        height: 100%;
        box-shadow: 0 8px 20px rgba(20, 56, 53, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }

    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 24px rgba(30, 41, 59, 0.08);
        border-color: #bfdbfe;
    }

    .feature-card h3 {
        color: #0f172a;
        font-size: 1rem;
        margin: 0 0 0.7rem;
    }

    .feature-card p {
        margin: 0.35rem 0;
        color: #475569;
        font-size: 0.92rem;
    }

    .form-shell {
        background: transparent;
        border: 0;
        border-radius: 0;
        padding: 0.25rem 0.35rem 0.5rem;
        height: 100%;
        box-shadow: none;
    }

    .form-shell::before {
        content: "";
        display: block;
        width: 2rem;
        height: 3px;
        margin-bottom: 0.7rem;
        border-radius: 3px;
        background: #3b82f6;
    }

    .form-shell [data-testid="stForm"] {
        border: 0;
        padding: 0;
    }

    .stSidebar {
        background: linear-gradient(180deg, #0f2a2b 0%, #123b39 100%);
        border-right: 1px solid #24534d;
    }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        padding: 0.4rem 0.5rem 0.9rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid rgba(167, 243, 208, 0.15);
    }

    .sidebar-brand-mark {
        width: 2.3rem;
        height: 2.3rem;
        display: grid;
        place-items: center;
        border-radius: 12px;
        background: linear-gradient(135deg, #7dd3fc 0%, #34d399 100%);
        color: #082f2f;
        font-weight: 800;
        box-shadow: 0 12px 25px rgba(52, 211, 153, 0.28);
    }

    .sidebar-brand-title {
        color: #f5fffb;
        font-size: 0.88rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .sidebar-brand-sub {
        color: #bfe6dd;
        font-size: 0.7rem;
        opacity: 0.8;
    }

    .stSidebar [data-testid="stMarkdownContainer"] p,
    .stSidebar label,
    .stSidebar .stCaption {
        color: #ffffff;
    }

    .stSidebar .section-title,
    .stSidebar [data-testid="stWidgetLabel"],
    .stSidebar [data-testid="stWidgetLabel"] p,
    .stSidebar .stRadio label,
    .stSidebar .stSelectbox label,
    .stSidebar .stToggle label {
        color: #ffffff !important;
    }

    .stSidebar .block-container {
        padding-top: 1.2rem;
    }

    .nav-stack {
        display: grid;
        gap: 0.55rem;
        margin-bottom: 1.2rem;
    }

    .nav-item {
        background: #173d39;
        border: 1px solid #285c55;
        border-left: 3px solid #75d7b8;
        border-radius: 12px;
        padding: 0.72rem 0.8rem;
        color: #effcf7;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.02);
    }

    .nav-item.active {
        background: #21675e;
        border-color: #75d7b8;
    }

    .stTextInput > div > div,
    .stSelectbox > div > div,
    .stNumberInput > div > div {
        background: #ffffff;
        border: 1px solid #bfd4cf;
        border-radius: 9px;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .stTextInput > div > div:focus-within,
    .stSelectbox > div > div:focus-within,
    .stNumberInput > div > div:focus-within {
        border-color: #329b83;
        box-shadow: 0 0 0 3px rgba(50, 155, 131, 0.13);
    }

    .stButton > button {
        background: #1f806c;
        color: white;
        border: none;
        border-radius: 9px;
        font-weight: 700;
        padding: 0.7rem 1.1rem;
        box-shadow: 0 8px 16px rgba(31, 128, 108, 0.2);
    }

    .stButton > button:hover {
        background: #176557;
        color: white;
    }

    @keyframes tabFadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .stTabs [role="tablist"] {
        background: #edf4ff;
        border-radius: 12px;
        border: 1px solid #dbeafe;
        padding: 0.25rem;
    }

    .stTabs [role="tab"] {
        color: #334155;
        border-radius: 10px;
        padding: 0.62rem 0.9rem;
        font-weight: 600;
    }

    .stTabs [role="tab"][aria-selected="true"] {
        background: #ffffff;
        border: 1px solid #bfdbfe;
        color: #0f172a;
        box-shadow: 0 6px 12px rgba(37, 99, 235, 0.08);
    }

    .stTabs [data-baseweb="tab-panel"] {
        animation: tabFadeIn 0.35s ease both;
    }

    .stDataFrame {
        background: #ffffff;
        border: 1px solid #d7e5e1;
        border-radius: 10px;
    }

    .stAlert {
        border-radius: 9px;
        border: 1px solid #c4e8dc;
    }

    .stRadio [role="radiogroup"] {
        gap: 0.35rem;
    }

    .stRadio [role="radio"] {
        padding: 0.45rem 0.55rem;
        border-radius: 8px;
    }

    @media (max-width: 900px) {
        .hero-panel h1 { font-size: 1.8rem; }
        .main .block-container { padding: 1rem 1rem 2rem; }
    }
</style>
"""
