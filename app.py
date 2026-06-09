import os
import re
import textwrap
from pathlib import Path
from typing import Dict, List

import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFilter, ImageFont

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:  # Streamlit can still render the local portfolio without Gemini.
    genai = None
    genai_types = None

from profile_context import PROFILE_CONTEXT, SYSTEM_INSTRUCTION


ROOT = Path(__file__).parent
ASSET_DIR = ROOT / "assets"
IMAGE_DIR = ASSET_DIR / "images"
GENERATED_DIR = ASSET_DIR / "generated"
RESUME_PATH = ROOT / "Profile (3).pdf"

load_dotenv()

st.set_page_config(
    page_title="Sameer Nagar | AI Dev Portfolio",
    page_icon=str(IMAGE_DIR / "logo.ico"),
    layout="wide",
    initial_sidebar_state="expanded",
)


PROFILE: Dict[str, object] = {
    "name": "Sameer Nagar",
    "role": "Software Development Engineer",
    "tagline": "AI-powered backend systems, enterprise automation, Salesforce, and cloud applications.",
    "location": "Fullerton, California",
    "email": "nagarsam8989@gmail.com",
    "phone": "+1 (657) 751-9425",
    "linkedin": "https://www.linkedin.com/in/aavonsameer/",
    "github": "https://github.com/sameernagar-hub",
    "scholar": "https://scholar.google.com/citations?user=FfTfe3gAAAAJ&hl=en",
    "stats": [
        ("~3", "Years SDE experience"),
        ("May 2026", "MS Computer Science, CSUF"),
        ("5", "Salesforce credentials"),
        ("2", "Published ML/NLP papers"),
    ],
    "skills": [
        "Python",
        "Java",
        "C++",
        "JavaScript",
        "React",
        "Node.js",
        "Flask",
        "FastAPI",
        "REST APIs",
        "MongoDB",
        "MySQL",
        "AWS",
        "Azure",
        "Docker",
        "CI/CD",
        "LLMs",
        "Prompt engineering",
        "Agentic AI",
        "Salesforce",
        "Apex concepts",
        "Agentforce",
        "NLP",
    ],
    "certifications": [
        "Salesforce Platform Developer II",
        "Salesforce Platform Developer I",
        "Salesforce Advanced Administrator",
        "Salesforce Administrator",
        "Agentforce Specialist",
    ],
}

EXPERIENCE = [
    {
        "title": "Jr. Associate Software Engineer",
        "org": "Unthinkable Solutions",
        "time": "2021 - 2024",
        "body": "Built backend services, full-stack applications, enterprise workflows, AI-powered features, LLM integrations, and automation-focused software across the SDLC.",
    },
    {
        "title": "Teaching Associate",
        "org": "California State University, Fullerton",
        "time": "2025 - 2026",
        "body": "Mentored students, supported computer science coursework, graded assignments, and collaborated with faculty to improve student learning outcomes.",
    },
    {
        "title": "Service Associate",
        "org": "California State University, Fullerton",
        "time": "2025 - 2026",
        "body": "Delivered customer service, transactions, inventory support, and team operations in a fast-paced university environment.",
    },
]

EDUCATION = [
    {
        "title": "MS Computer Science",
        "org": "California State University, Fullerton",
        "time": "Graduated May 2026",
        "body": "GPA 3.70/4.00. Focused on software engineering, backend systems, cloud-ready architecture, and AI-enabled applications.",
    },
    {
        "title": "BTech Computer Science",
        "org": "Rajiv Gandhi Proudyogiki Vishwavidyalaya",
        "time": "2018 - 2022",
        "body": "Built a strong computer science foundation across programming, data structures, algorithms, and software development.",
    },
]

PROJECTS = [
    {
        "name": "Anomaly Detection Workbench",
        "type": "AI/ML + Backend",
        "status": "Reviewable intelligence",
        "repo": "https://github.com/sameernagar-hub/anomaly-detection-workbench",
        "body": "Detects unusual data patterns, structures review workflows, and makes model-assisted outputs easier to inspect and act on.",
        "tags": ["Python", "ML", "Backend", "Decision support"],
    },
    {
        "name": "Titan Smart Scheduler",
        "type": "Product workflow",
        "status": "Planning logic",
        "repo": "https://github.com/sameernagar-hub/titan-smart-scheduler",
        "body": "Scheduling-focused application work showing planning logic, user workflows, and maintainable interactive software structure.",
        "tags": ["Scheduling", "Application logic", "UX", "Systems"],
    },
    {
        "name": "Portfolio AI Assistant",
        "type": "LLM application",
        "status": "Resume-aware AI",
        "repo": "",
        "body": "Chat interface with prompt UX, local fallback answers, saved chat history, and a backend proxy so API keys stay server-side.",
        "tags": ["LLM", "Gemini", "FastAPI", "Streamlit"],
    },
    {
        "name": "Salesforce / Agentforce Automation",
        "type": "Enterprise systems",
        "status": "CRM workflow",
        "repo": "",
        "body": "Automation stories around CRM workflows, stakeholder needs, service routing, approvals, and enterprise process improvement.",
        "tags": ["Salesforce", "Agentforce", "CRM", "Automation"],
    },
]

PUBLICATIONS = [
    {
        "title": "Logistic Regression Based Approach for Human Sentiment Analysis Across Domains",
        "venue": "IEEE Xplore Digital Library",
        "date": "Nov 12, 2024",
        "link": "https://ieeexplore.ieee.org/document/10743868",
    },
    {
        "title": "Cross Domain and Decision Tree Based Approach for Human Sentiment Analysis",
        "venue": "Springer Learning and Analytics in Intelligent Systems",
        "date": "Jul 13, 2024",
        "link": "https://link.springer.com/book/10.1007/978-981-97-9855-1",
    },
]

PROMPTS = [
    "Why should we hire Sameer?",
    "Summarize Sameer for an AI engineering role.",
    "What are Sameer's strongest backend signals?",
    "How does Sameer match a Salesforce or Agentforce role?",
    "Compare Sameer to this job description: ",
    "What projects should a recruiter look at first?",
]

NAV_ITEMS = {
    "AI Chat": "Ask the resume-aware assistant first.",
    "About": "A command-center overview.",
    "Resume": "Experience, education, and credentials.",
    "Projects": "Selected work and engineering themes.",
    "Research": "Publications and ML/NLP signal.",
    "Contact": "Links, resume, and outreach.",
}


def safe_key(value: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", value.lower()).strip("_")


def get_font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/CascadiaMono.ttf",
        "C:/Windows/Fonts/CascadiaMono-SemiBold.ttf" if bold else "",
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)

    return ImageFont.load_default()


@st.cache_resource(show_spinner=False)
def ensure_visual_assets() -> Dict[str, Path]:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    hero_path = GENERATED_DIR / "devtool-hero.png"
    avatar_card_path = GENERATED_DIR / "agent-avatar-card.png"

    if not hero_path.exists():
        width, height = 1800, 1120
        img = Image.new("RGB", (width, height), "#05070b")
        draw = ImageDraw.Draw(img)

        for y in range(height):
            ratio = y / height
            r = int(5 + 4 * ratio)
            g = int(8 + 18 * ratio)
            b = int(13 + 25 * ratio)
            draw.line((0, y, width, y), fill=(r, g, b))

        grid_color = (24, 41, 54)
        for x in range(0, width, 72):
            draw.line((x, 0, x, height), fill=grid_color, width=1)
        for y in range(0, height, 72):
            draw.line((0, y, width, y), fill=grid_color, width=1)

        glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        glow = ImageDraw.Draw(glow_layer)
        glow.ellipse((1060, 80, 1880, 840), fill=(34, 211, 238, 34))
        glow.ellipse((-180, 560, 540, 1320), fill=(16, 185, 129, 24))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(70))
        img = Image.alpha_composite(img.convert("RGBA"), glow_layer)
        draw = ImageDraw.Draw(img)

        panel = (185, 120, 1565, 910)
        draw.rounded_rectangle(panel, radius=34, fill=(8, 12, 20, 232), outline=(41, 58, 76), width=2)
        draw.rounded_rectangle((panel[0], panel[1], panel[2], panel[1] + 78), radius=34, fill=(12, 19, 31, 255))
        draw.rectangle((panel[0], panel[1] + 48, panel[2], panel[1] + 78), fill=(12, 19, 31, 255))

        for i, color in enumerate([(239, 68, 68), (245, 158, 11), (34, 197, 94)]):
            draw.ellipse((230 + i * 38, 146, 252 + i * 38, 168), fill=color)

        mono = get_font(34)
        mono_small = get_font(26)
        mono_bold = get_font(42, bold=True)
        draw.text((360, 137), "sameer-nagar.dev/agent", fill=(148, 163, 184), font=mono_small)

        lines = [
            ("$ boot portfolio --mode ai-first --theme cli-dark", (94, 234, 212)),
            ("initializing resume-aware assistant...", (148, 163, 184)),
            ("loading skills: python, backend, llms, salesforce, aws", (125, 211, 252)),
            ("routing visitor to /ai-chat", (250, 204, 21)),
            ("ready. ask anything about fit, projects, research, contact.", (74, 222, 128)),
        ]
        y = 265
        for line, color in lines:
            draw.text((245, y), line, fill=color, font=mono)
            y += 68

        draw.rounded_rectangle((245, 660, 1505, 805), radius=24, fill=(15, 23, 42, 230), outline=(45, 212, 191), width=2)
        draw.text((285, 690), "AI Agent", fill=(250, 250, 250), font=mono_bold)
        draw.text(
            (285, 748),
            "ChatGPT-style homepage for recruiters and hiring managers",
            fill=(203, 213, 225),
            font=mono_small,
        )

        for i, text in enumerate(["SDE", "AI/LLM", "Backend", "Salesforce", "Cloud"]):
            x = 245 + i * 246
            draw.rounded_rectangle((x, 845, x + 210, 902), radius=18, fill=(17, 24, 39), outline=(51, 65, 85))
            draw.text((x + 26, 858), text, fill=(226, 232, 240), font=mono_small)

        img.convert("RGB").save(hero_path, quality=95)

    if not avatar_card_path.exists():
        width, height = 1200, 1200
        img = Image.new("RGB", (width, height), "#05070b")
        draw = ImageDraw.Draw(img)
        for y in range(height):
            draw.line((0, y, width, y), fill=(4, int(9 + y / 120), int(15 + y / 80)))

        avatar_path = IMAGE_DIR / "sameer-avatar.png"
        if avatar_path.exists():
            avatar = Image.open(avatar_path).convert("RGBA").resize((470, 470), Image.LANCZOS)
            mask = Image.new("L", avatar.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, 470, 470), radius=56, fill=255)
            img.paste(avatar, (365, 170), mask)

        mono = get_font(38)
        mono_bold = get_font(54, bold=True)
        draw.rounded_rectangle((110, 730, 1090, 1055), radius=32, fill=(9, 14, 24), outline=(45, 212, 191), width=3)
        draw.text((155, 775), "sameer.agent", fill=(94, 234, 212), font=mono)
        draw.text((155, 835), "Software Development Engineer", fill=(248, 250, 252), font=mono_bold)
        draw.text((155, 920), "AI | Backend | Salesforce | Cloud", fill=(203, 213, 225), font=mono)
        draw.text((155, 985), "status: open_to_2026_roles", fill=(250, 204, 21), font=mono)
        img.save(avatar_card_path, quality=95)

    return {"hero": hero_path, "avatar_card": avatar_card_path}


def inject_css() -> None:
    st.markdown(
        """
        <style>
          :root {
            --bg: #030712;
            --bg-2: #050816;
            --panel: rgba(10, 15, 28, 0.88);
            --panel-2: rgba(15, 23, 42, 0.9);
            --panel-3: rgba(2, 6, 23, 0.78);
            --border: rgba(148, 163, 184, 0.18);
            --border-strong: rgba(45, 212, 191, 0.35);
            --text: #f8fafc;
            --soft: #cbd5e1;
            --muted: #94a3b8;
            --green: #22c55e;
            --cyan: #22d3ee;
            --teal: #2dd4bf;
            --amber: #facc15;
            --red: #fb7185;
            --radius: 8px;
            --shadow: 0 24px 80px rgba(0, 0, 0, 0.32);
          }

          html, body, [data-testid="stAppViewContainer"] {
            color: var(--text);
            background:
              radial-gradient(circle at 84% 12%, rgba(34, 211, 238, 0.13), transparent 34vw),
              radial-gradient(circle at 8% 74%, rgba(34, 197, 94, 0.08), transparent 34vw),
              linear-gradient(135deg, #030712 0%, #050816 50%, #020617 100%);
          }

          [data-testid="stHeader"] {
            background: transparent;
          }

          [data-testid="stSidebar"] {
            background: rgba(2, 6, 23, 0.94);
            border-right: 1px solid var(--border);
          }

          [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
          [data-testid="stSidebar"] label,
          [data-testid="stSidebar"] span {
            color: var(--soft);
          }

          .block-container {
            max-width: 1280px;
            padding: 2.2rem 2rem 5.5rem;
          }

          h1, h2, h3 {
            letter-spacing: 0;
          }

          h1 {
            font-size: clamp(2.15rem, 5vw, 4.8rem);
            line-height: 1.02;
          }

          h2 {
            font-size: clamp(1.55rem, 3vw, 2.6rem);
          }

          h3 {
            font-size: clamp(1.05rem, 1.6vw, 1.28rem);
          }

          p, li, div {
            overflow-wrap: anywhere;
          }

          .stButton > button,
          .stDownloadButton > button,
          [data-testid="stBaseButton-secondary"],
          [data-testid="stBaseButton-primary"] {
            min-height: 42px;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius) !important;
            color: var(--text) !important;
            background: rgba(15, 23, 42, 0.88) !important;
            box-shadow: none !important;
            transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
          }

          .stButton > button:hover,
          .stDownloadButton > button:hover {
            border-color: var(--border-strong) !important;
            background: rgba(17, 34, 46, 0.96) !important;
            transform: translateY(-1px);
          }

          .stChatFloatingInputContainer {
            background: linear-gradient(180deg, transparent, rgba(3, 7, 18, 0.96) 35%);
          }

          [data-testid="stChatInput"] {
            border: 1px solid var(--border-strong);
            border-radius: var(--radius);
            background: rgba(15, 23, 42, 0.92);
          }

          [data-testid="stChatInput"] textarea {
            color: var(--text) !important;
          }

          [data-testid="stChatMessage"] {
            border-radius: var(--radius);
            animation: message-in 280ms ease both;
          }

          [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: rgba(20, 184, 166, 0.08);
            border: 1px solid rgba(45, 212, 191, 0.18);
          }

          [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
            background: rgba(15, 23, 42, 0.66);
            border: 1px solid rgba(148, 163, 184, 0.14);
          }

          .hero-terminal,
          .dev-card,
          .metric-tile,
          .timeline-item,
          .project-card,
          .contact-panel {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            background:
              linear-gradient(180deg, rgba(15, 23, 42, 0.92), rgba(2, 6, 23, 0.78)),
              linear-gradient(90deg, rgba(45, 212, 191, 0.08), rgba(34, 211, 238, 0.04));
            box-shadow: var(--shadow);
          }

          .hero-terminal::before,
          .dev-card::before,
          .project-card::before {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background:
              linear-gradient(90deg, transparent, rgba(45, 212, 191, 0.08), transparent),
              repeating-linear-gradient(0deg, rgba(255,255,255,0.02) 0, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 7px);
            transform: translateX(-100%);
            animation: panel-scan 5.5s ease-in-out infinite;
          }

          .hero-terminal {
            min-height: min(72vh, 760px);
            display: grid;
            grid-template-columns: minmax(0, 1.05fr) minmax(280px, 0.95fr);
            gap: clamp(1rem, 4vw, 3rem);
            align-items: center;
            padding: clamp(1rem, 4vw, 3.25rem);
          }

          .hero-copy {
            position: relative;
            z-index: 1;
          }

          .kicker {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            width: fit-content;
            max-width: 100%;
            margin-bottom: 1rem;
            padding: 0.42rem 0.62rem;
            border: 1px solid rgba(45, 212, 191, 0.28);
            border-radius: var(--radius);
            color: var(--teal);
            background: rgba(20, 184, 166, 0.08);
            font-family: "Cascadia Mono", "Consolas", monospace;
            font-size: 0.78rem;
          }

          .cursor {
            display: inline-block;
            width: 0.65em;
            height: 1.15em;
            margin-left: 0.16em;
            vertical-align: -0.16em;
            background: var(--teal);
            animation: blink 1s steps(2, start) infinite;
          }

          .hero-title {
            margin: 0;
            color: var(--text);
          }

          .hero-title span {
            color: var(--teal);
          }

          .hero-subtitle {
            max-width: 70ch;
            margin-top: 1.1rem;
            color: var(--soft);
            font-size: clamp(1rem, 1.4vw, 1.15rem);
            line-height: 1.75;
          }

          .terminal-window {
            position: relative;
            z-index: 1;
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: var(--radius);
            background: rgba(2, 6, 23, 0.72);
          }

          .terminal-bar {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            min-height: 42px;
            padding: 0 0.9rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.15);
            color: var(--muted);
            font-family: "Cascadia Mono", "Consolas", monospace;
            font-size: 0.76rem;
          }

          .terminal-dot {
            width: 10px;
            height: 10px;
            flex: 0 0 auto;
            border-radius: 50%;
          }

          .terminal-body {
            padding: 1rem;
            font-family: "Cascadia Mono", "Consolas", monospace;
            font-size: clamp(0.78rem, 1vw, 0.92rem);
            line-height: 1.85;
          }

          .log-green { color: #86efac; }
          .log-cyan { color: #67e8f9; }
          .log-amber { color: #fde68a; }
          .log-muted { color: #94a3b8; }

          .status-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.8rem;
            margin-top: 1.2rem;
          }

          .metric-tile {
            min-height: 112px;
            padding: 1rem;
            box-shadow: none;
          }

          .metric-value {
            color: var(--amber);
            font-family: "Cascadia Mono", "Consolas", monospace;
            font-size: clamp(1.35rem, 2.5vw, 2.05rem);
            font-weight: 700;
          }

          .metric-label {
            margin-top: 0.4rem;
            color: var(--soft);
            font-size: 0.88rem;
            line-height: 1.45;
          }

          .section-shell {
            margin-top: 1rem;
          }

          .section-heading {
            margin: 1.8rem 0 0.75rem;
            color: var(--text);
            font-family: "Cascadia Mono", "Consolas", monospace;
          }

          .section-heading small {
            display: block;
            margin-bottom: 0.35rem;
            color: var(--teal);
            font-size: 0.78rem;
            font-weight: 500;
          }

          .dev-card,
          .project-card,
          .timeline-item,
          .contact-panel {
            min-height: 100%;
            padding: 1rem;
            box-shadow: none;
            transition: transform 180ms ease, border-color 180ms ease, background 180ms ease;
            animation: float-in 520ms ease both;
          }

          .dev-card:hover,
          .project-card:hover,
          .timeline-item:hover,
          .contact-panel:hover {
            border-color: var(--border-strong);
            transform: translateY(-3px);
          }

          .card-label {
            color: var(--teal);
            font-family: "Cascadia Mono", "Consolas", monospace;
            font-size: 0.76rem;
            text-transform: uppercase;
          }

          .card-title {
            margin: 0.35rem 0;
            color: var(--text);
            font-size: 1.08rem;
            font-weight: 700;
          }

          .card-copy {
            color: var(--soft);
            font-size: 0.92rem;
            line-height: 1.65;
          }

          .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.7rem;
          }

          .chip {
            display: inline-flex;
            min-height: 28px;
            align-items: center;
            max-width: 100%;
            padding: 0.22rem 0.55rem;
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: var(--radius);
            color: var(--soft);
            background: rgba(15, 23, 42, 0.72);
            font-family: "Cascadia Mono", "Consolas", monospace;
            font-size: 0.73rem;
          }

          .prompt-stack {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.65rem;
            margin-bottom: 1.1rem;
          }

          .chat-topline {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1rem;
          }

          .chat-status {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.38rem 0.58rem;
            border: 1px solid rgba(45, 212, 191, 0.28);
            border-radius: var(--radius);
            color: var(--soft);
            background: rgba(15, 23, 42, 0.72);
            font-family: "Cascadia Mono", "Consolas", monospace;
            font-size: 0.76rem;
          }

          .pulse-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--green);
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
            animation: pulse 1.7s infinite;
          }

          .sidebar-brand {
            padding: 0.75rem 0.35rem 1rem;
            border-bottom: 1px solid var(--border);
            margin-bottom: 1rem;
          }

          .sidebar-brand h2 {
            margin: 0;
            color: var(--text);
            font-size: 1.24rem;
          }

          .sidebar-brand p {
            margin: 0.35rem 0 0;
            color: var(--muted);
            font-size: 0.82rem;
            line-height: 1.45;
          }

          .sidebar-status {
            padding: 0.7rem;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            background: rgba(15, 23, 42, 0.65);
            font-family: "Cascadia Mono", "Consolas", monospace;
            font-size: 0.75rem;
          }

          .timeline-item + .timeline-item {
            margin-top: 0.8rem;
          }

          .terminal-image {
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: var(--radius);
            background: rgba(2, 6, 23, 0.86);
          }

          .terminal-image img {
            width: 100%;
            display: block;
          }

          @keyframes blink {
            0%, 45% { opacity: 1; }
            46%, 100% { opacity: 0; }
          }

          @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
            100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
          }

          @keyframes panel-scan {
            0%, 52% { transform: translateX(-100%); opacity: 0; }
            58% { opacity: 1; }
            86%, 100% { transform: translateX(100%); opacity: 0; }
          }

          @keyframes float-in {
            from { opacity: 0; transform: translateY(16px); }
            to { opacity: 1; transform: translateY(0); }
          }

          @keyframes message-in {
            from { opacity: 0; transform: translateY(8px) scale(0.99); }
            to { opacity: 1; transform: translateY(0) scale(1); }
          }

          @supports (animation-timeline: view()) {
            .dev-card,
            .project-card,
            .timeline-item,
            .metric-tile,
            .contact-panel {
              animation: reveal-on-scroll linear both;
              animation-timeline: view();
              animation-range: entry 0% cover 28%;
            }

            @keyframes reveal-on-scroll {
              from { opacity: 0; transform: translateY(28px) scale(0.985); filter: blur(6px); }
              to { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
            }
          }

          @media (max-width: 980px) {
            .block-container {
              padding: 1.4rem 1rem 5rem;
            }

            .hero-terminal {
              grid-template-columns: 1fr;
              min-height: auto;
            }

            .status-grid,
            .prompt-stack {
              grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .chat-topline {
              align-items: flex-start;
              flex-direction: column;
            }
          }

          @media (max-width: 560px) {
            .block-container {
              padding: 1rem 0.75rem 4.75rem;
            }

            .hero-terminal {
              padding: 1rem;
            }

            .status-grid,
            .prompt-stack {
              grid-template-columns: 1fr;
            }

            .terminal-body {
              font-size: 0.76rem;
            }

            .kicker,
            .chat-status {
              width: 100%;
            }
          }

          @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
              animation-duration: 1ms !important;
              animation-iteration-count: 1 !important;
              scroll-behavior: auto !important;
              transition-duration: 1ms !important;
            }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_metric_grid() -> None:
    tiles = "".join(
        f"""
        <div class="metric-tile">
          <div class="metric-value">{html_escape(value)}</div>
          <div class="metric-label">{html_escape(label)}</div>
        </div>
        """
        for value, label in PROFILE["stats"]
    )
    st.markdown(f'<div class="status-grid">{tiles}</div>', unsafe_allow_html=True)


def render_chips(items: List[str]) -> str:
    return '<div class="chip-row">' + "".join(f'<span class="chip">{html_escape(item)}</span>' for item in items) + "</div>"


def render_card(label: str, title: str, copy: str, chips: List[str] | None = None) -> None:
    st.markdown(
        f"""
        <div class="dev-card">
          <div class="card-label">{html_escape(label)}</div>
          <div class="card-title">{html_escape(title)}</div>
          <div class="card-copy">{html_escape(copy)}</div>
          {render_chips(chips or [])}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_heading(kicker: str, title: str) -> None:
    st.markdown(
        f"""
        <div class="section-heading">
          <small>{html_escape(kicker)}</small>
          {html_escape(title)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_model():
    api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if not api_key or genai is None or genai_types is None:
        return None

    return genai.Client(api_key=api_key)


def includes_any(message: str, keywords: List[str]) -> bool:
    return any(keyword in message for keyword in keywords)


def local_assistant_response(user_message: str) -> str:
    message = user_message.lower()
    contact_line = (
        f"You can reach Sameer at {PROFILE['email']}, LinkedIn at {PROFILE['linkedin']}, "
        f"GitHub at {PROFILE['github']}, or Google Scholar at {PROFILE['scholar']}."
    )

    if includes_any(message, ["hello", "hi", "hey"]):
        return "Hi, I'm Sameer's resume-aware portfolio assistant. Ask me about AI/LLM work, backend systems, Salesforce credentials, AWS experience, research, projects, leadership, or fit for a role."

    if includes_any(message, ["hire", "why should we hire", "why hire"]):
        return "\n".join(
            [
                "Why hire Sameer:",
                "- Around 3 years of Software Development Engineer experience.",
                "- MS Computer Science from CSUF, graduated May 2026.",
                "- Strong backend, AI/LLM, Salesforce, AWS, and enterprise automation positioning.",
                "- Salesforce Platform Developer II, Platform Developer I, Advanced Admin, Admin, and Agentforce Specialist.",
                "- Leadership as Vice President, Student Alumni Ambassadors.",
            ]
        )

    if includes_any(message, ["ai engineering role", "ai engineer", "llm role", "summarize sameer for an ai"]):
        return "Sameer is a strong AI engineering candidate because he combines LLM application work, prompt engineering, backend API skills, anomaly detection workflow thinking, cloud deployment awareness, and published ML/NLP research."

    if includes_any(message, ["backend skills", "backend project", "api skills"]):
        return "Best backend signals: Titan Smart Scheduler, AWS Intelligent Interaction Services, the secure Portfolio AI Assistant backend proxy, and enterprise automation workflows involving API integration, validation, and maintainable service logic."

    if includes_any(message, ["salesforce", "agentforce", "certification", "certified", "crm"]):
        return f"Sameer's Salesforce credentials include {', '.join(PROFILE['certifications'])}. His Salesforce story is strongest for platform development, administration, Agentforce-aware automation, CRM workflow improvement, and enterprise technology consulting."

    if includes_any(message, ["job description", "jd", "match sameer", "match this"]):
        return "Paste the job description and I can compare it against Sameer's resume-aligned strengths: software development engineering, AI/LLMs, backend systems, Salesforce credentials, Agentforce, AWS, enterprise automation, CSUF MS Computer Science, publications, and leadership."

    if includes_any(message, ["publication", "research", "scholar", "ieee", "springer", "sentiment"]):
        return "\n".join(
            [
                "Publications:",
                f"- {PUBLICATIONS[0]['title']} - {PUBLICATIONS[0]['venue']}, {PUBLICATIONS[0]['date']}",
                f"- {PUBLICATIONS[1]['title']} - {PUBLICATIONS[1]['venue']}, {PUBLICATIONS[1]['date']}",
                f"Google Scholar: {PROFILE['scholar']}",
            ]
        )

    if includes_any(message, ["titan", "scheduler", "schedule"]):
        return "Titan Smart Scheduler is a scheduling-focused project showing Sameer's application logic, planning workflow design, and ability to organize interactive software around practical user needs. GitHub: https://github.com/sameernagar-hub/titan-smart-scheduler"

    if includes_any(message, ["anomaly", "detection", "workbench"]):
        return "Anomaly Detection Workbench is one of Sameer's strongest AI/backend projects. It focuses on unusual pattern detection, review workflows, and making model-assisted outputs easier to inspect and act on. GitHub: https://github.com/sameernagar-hub/anomaly-detection-workbench"

    if includes_any(message, ["contact", "email", "phone", "linkedin", "github", "reach"]):
        return f"You can reach Sameer at {PROFILE['email']}, call {PROFILE['phone']}, view LinkedIn at {PROFILE['linkedin']}, see GitHub at {PROFILE['github']}, or review Google Scholar at {PROFILE['scholar']}."

    if includes_any(message, ["resume", "cv", "download"]):
        return "Sameer's resume is available from the sidebar and contact page as Sameer_Nagar_Resume.pdf."

    if includes_any(message, ["education", "school", "degree", "gpa", "csuf", "university", "graduate"]):
        return "Sameer earned an MS in Computer Science from California State University, Fullerton, graduating in May 2026 with a 3.70/4.00 GPA. He also earned a BTech in Computer Science from Rajiv Gandhi Proudyogiki Vishwavidyalaya."

    if includes_any(message, ["experience", "work", "job", "unthinkable", "teaching", "associate"]):
        return "Sameer worked as a Jr. Associate Software Engineer at Unthinkable Solutions from 2021 to 2024, and at CSUF as a Teaching Associate and Service Associate from 2025 to 2026."

    if includes_any(message, ["skill", "stack", "technology", "tech", "tools"]):
        return f"Sameer's core stack includes {', '.join(PROFILE['skills'])}. His strongest hiring narrative is SDE work with AI/LLM, backend, Salesforce, cloud, enterprise automation, and applied ML/NLP research."

    if includes_any(message, ["cloud", "aws", "azure", "docker", "ci/cd", "devops"]):
        return "Sameer has cloud and delivery experience across AWS, Azure exposure, Docker, CI/CD, deployment automation, and intelligent cloud application patterns."

    if includes_any(message, ["project", "portfolio", "case study", "built", "application"]):
        return "Featured case studies include Anomaly Detection Workbench, Titan Smart Scheduler, Portfolio AI Assistant, AWS Intelligent Interaction Services, and Salesforce/Agentforce Enterprise Automation."

    return f"Sameer is a Software Development Engineer focused on AI-powered backend systems, Salesforce and Agentforce automation, AWS/cloud applications, research-backed ML/NLP work, and production-grade enterprise software. {contact_line}"


def ask_assistant(message: str, history: List[Dict[str, str]]) -> str:
    model = get_model()
    if model is None:
        return f"Live AI is unavailable, so here is the local resume-aware answer:\n\n{local_assistant_response(message)}"

    gemini_history = [
        genai_types.Content(
            role="model" if item["role"] == "assistant" else "user",
            parts=[genai_types.Part(text=item["content"][:1200])],
        )
        for item in history[-8:]
        if item.get("content")
    ]
    gemini_history.append(
        genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=message[:3000])],
        )
    )

    try:
        response = model.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
            contents=gemini_history,
            config=genai_types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
        )
        reply = getattr(response, "text", "") or ""
        if not reply.strip():
            raise ValueError("Empty model reply")
        return reply.strip()
    except Exception:
        return f"Live AI hit an issue, so here is the local resume-aware answer:\n\n{local_assistant_response(message)}"


def init_state() -> None:
    st.session_state.setdefault("page", "AI Chat")
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("chat_sessions", [{"title": "New chat", "messages": []}])
    st.session_state.setdefault("active_session", 0)
    st.session_state.setdefault("pending_prompt", "")


def sync_active_session() -> None:
    sessions = st.session_state.chat_sessions
    active = max(0, min(st.session_state.active_session, len(sessions) - 1))
    st.session_state.active_session = active
    st.session_state.messages = sessions[active]["messages"]


def persist_active_session() -> None:
    active = st.session_state.active_session
    st.session_state.chat_sessions[active]["messages"] = st.session_state.messages
    first_user = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), "")
    st.session_state.chat_sessions[active]["title"] = first_user[:38] + ("..." if len(first_user) > 38 else "") if first_user else "New chat"


def new_chat() -> None:
    st.session_state.chat_sessions.insert(0, {"title": "New chat", "messages": []})
    st.session_state.active_session = 0
    st.session_state.messages = []
    st.session_state.page = "AI Chat"


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
              <h2>sameer.dev</h2>
              <p>AI-first CLI portfolio shell</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected = st.radio(
            "Navigate",
            list(NAV_ITEMS.keys()),
            index=list(NAV_ITEMS.keys()).index(st.session_state.page),
            label_visibility="collapsed",
        )
        st.session_state.page = selected

        st.markdown(
            f"""
            <div class="sidebar-status">
              <span class="log-green">status</span>: open_to_roles<br>
              <span class="log-cyan">focus</span>: ai/backend/cloud<br>
              <span class="log-amber">agent</span>: {'live' if get_model() else 'local_fallback'}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        if st.button("New chat", width="stretch"):
            new_chat()
            st.rerun()

        if st.session_state.chat_sessions:
            titles = [session["title"] for session in st.session_state.chat_sessions]
            active_title = st.selectbox(
                "Saved chats",
                titles,
                index=st.session_state.active_session,
            )
            st.session_state.active_session = titles.index(active_title)
            sync_active_session()

        st.write("")
        st.link_button("LinkedIn", PROFILE["linkedin"], width="stretch")
        st.link_button("GitHub", PROFILE["github"], width="stretch")
        st.link_button("Google Scholar", PROFILE["scholar"], width="stretch")
        if RESUME_PATH.exists():
            with RESUME_PATH.open("rb") as resume_file:
                st.download_button(
                    "Download resume",
                    resume_file,
                    file_name="Sameer_Nagar_Resume.pdf",
                    mime="application/pdf",
                    width="stretch",
                )


def render_chat_page() -> None:
    assets = ensure_visual_assets()
    left, right = st.columns([1.08, 0.92], gap="large")

    with left:
        st.markdown(
            """
            <div class="chat-topline">
              <div>
                <div class="kicker">/ai-chat home <span class="cursor"></span></div>
                <h1 class="hero-title">Ask Sameer's AI agent first.</h1>
              </div>
              <div class="chat-status"><span class="pulse-dot"></span> agent ready</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        prompt_cols = st.columns(3)
        for index, prompt in enumerate(PROMPTS):
            with prompt_cols[index % 3]:
                if st.button(prompt, key=f"prompt_{safe_key(prompt)}", width="stretch"):
                    st.session_state.pending_prompt = prompt
                    st.session_state.page = "AI Chat"
                    st.rerun()

        if not st.session_state.messages:
            st.chat_message("assistant").markdown(
                "Hi, I'm Sameer's resume-aware AI assistant. Ask about backend engineering, AI/LLM apps, Salesforce credentials, AWS work, CSUF education, publications, leadership, or fit for a role."
            )

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        pending = st.session_state.pop("pending_prompt", "")
        user_input = pending or st.chat_input("Ask about Sameer's fit, projects, publications, or paste a job description...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("running sameer.agent..."):
                    reply = ask_assistant(user_input, st.session_state.messages[:-1])
                    st.markdown(reply)

            st.session_state.messages.append({"role": "assistant", "content": reply})
            persist_active_session()
            st.rerun()

    with right:
        st.markdown('<div class="terminal-image">', unsafe_allow_html=True)
        st.image(str(assets["avatar_card"]), width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)
        render_section_heading("agent context", "What the assistant knows")
        render_card(
            "context.locked",
            "Resume-aware answers",
            "The assistant is grounded in Sameer's portfolio context and avoids inventing employers, dates, metrics, credentials, or project outcomes.",
            ["Gemini when configured", "Local fallback", "Recruiter-friendly"],
        )
        render_card(
            "fast paths",
            "Questions to try",
            "Ask why Sameer is a fit, paste a job description, compare Salesforce credentials, or inspect AI/backend project signals.",
            ["JD match", "Projects", "Credentials"],
        )


def render_about_page() -> None:
    assets = ensure_visual_assets()
    st.markdown(
        """
        <div class="hero-terminal">
          <div class="hero-copy">
            <div class="kicker">$ open sameer.profile <span class="cursor"></span></div>
            <h1 class="hero-title">Developer portfolio, rebuilt as a dark AI command center.</h1>
            <p class="hero-subtitle">
              Sameer Nagar is a Software Development Engineer building AI-powered backend systems,
              enterprise automation, Salesforce/Agentforce workflows, and intelligent cloud applications.
            </p>
          </div>
          <div class="terminal-window">
            <div class="terminal-bar">
              <span class="terminal-dot" style="background:#fb7185"></span>
              <span class="terminal-dot" style="background:#facc15"></span>
              <span class="terminal-dot" style="background:#22c55e"></span>
              <span>portfolio.log</span>
            </div>
            <div class="terminal-body">
              <div class="log-green">$ run hiring-summary</div>
              <div class="log-cyan">role: Software Development Engineer</div>
              <div class="log-muted">stack: Python, Java, JS, APIs, cloud, LLMs</div>
              <div class="log-amber">signal: MS CSUF 2026, Salesforce x5, ML/NLP publications</div>
              <div class="log-green">ready: ask the AI agent first</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_metric_grid()

    render_section_heading("visual system", "Upscaled dev-tool graphics")
    st.image(str(assets["hero"]), width="stretch")

    render_section_heading("focus", "Engineering lanes")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_card("backend", "Systems and APIs", "API design, scalable service architecture, database-backed workflows, and production-grade business logic.", ["Python", "Java", "REST"])
    with col2:
        render_card("ai", "LLM applications", "Resume-aware assistants, prompt engineering, fallback logic, anomaly workflows, and practical AI integration.", ["Gemini", "Prompts", "ML"])
    with col3:
        render_card("cloud", "Delivery discipline", "AWS services, Azure exposure, Docker, CI/CD, deployment automation, and reliable environment configuration.", ["AWS", "Docker", "CI/CD"])
    with col4:
        render_card("crm", "Salesforce automation", "Salesforce development, administration, Agentforce-aware automation, CRM workflow improvement, and stakeholder focus.", ["Salesforce", "Agentforce", "CRM"])


def render_resume_page() -> None:
    st.markdown('<div class="kicker">$ cat resume.timeline <span class="cursor"></span></div>', unsafe_allow_html=True)
    st.title("Resume")

    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        render_section_heading("experience", "Professional timeline")
        for item in EXPERIENCE:
            st.markdown(
                f"""
                <div class="timeline-item">
                  <div class="card-label">{html_escape(item['time'])}</div>
                  <div class="card-title">{html_escape(item['title'])}</div>
                  <div class="card-copy"><strong>{html_escape(item['org'])}</strong><br>{html_escape(item['body'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        render_section_heading("education", "Academic foundation")
        for item in EDUCATION:
            st.markdown(
                f"""
                <div class="timeline-item">
                  <div class="card-label">{html_escape(item['time'])}</div>
                  <div class="card-title">{html_escape(item['title'])}</div>
                  <div class="card-copy"><strong>{html_escape(item['org'])}</strong><br>{html_escape(item['body'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        render_section_heading("credentials", "Salesforce and leadership")
        render_card(
            "certifications",
            "Salesforce credentials",
            ", ".join(PROFILE["certifications"]),
            ["Platform Dev II", "Agentforce", "Advanced Admin"],
        )
        render_card(
            "leadership",
            "Student Alumni Ambassadors",
            "Vice President role strengthening stakeholder communication, representation, leadership, and team collaboration.",
            ["VP", "CSUF", "Leadership"],
        )

    render_section_heading("stack", "Technical skill matrix")
    st.markdown(render_chips(PROFILE["skills"]), unsafe_allow_html=True)


def render_projects_page() -> None:
    st.markdown('<div class="kicker">$ ls selected-work <span class="cursor"></span></div>', unsafe_allow_html=True)
    st.title("Projects")

    cols = st.columns(2)
    for index, project in enumerate(PROJECTS):
        with cols[index % 2]:
            link = f'<p class="card-copy"><a href="{project["repo"]}" target="_blank">Open repository</a></p>' if project["repo"] else ""
            st.markdown(
                f"""
                <div class="project-card">
                  <div class="card-label">{html_escape(project['type'])} / {html_escape(project['status'])}</div>
                  <div class="card-title">{html_escape(project['name'])}</div>
                  <div class="card-copy">{html_escape(project['body'])}</div>
                  {render_chips(project['tags'])}
                  {link}
                </div>
                """,
                unsafe_allow_html=True,
            )

    render_section_heading("business bridge", "How the work maps to outcomes")
    c1, c2, c3 = st.columns(3)
    with c1:
        render_card("automation", "Workflow clarity", "Translates stakeholder needs into repeatable workflows, routing logic, and system behavior that teams can operate.", ["CRM", "Routing", "SLA"])
    with c2:
        render_card("reliability", "Maintainable services", "Focuses on APIs, validation, separation of concerns, environment configuration, and backend reliability.", ["APIs", "Validation", "Ops"])
    with c3:
        render_card("ai product", "Usable intelligence", "Frames AI output around reviewability, grounding, fallback behavior, and user-facing decision support.", ["Grounding", "Review", "Fallback"])


def render_research_page() -> None:
    st.markdown('<div class="kicker">$ grep publications sameer.profile <span class="cursor"></span></div>', unsafe_allow_html=True)
    st.title("Research")

    for publication in PUBLICATIONS:
        st.markdown(
            f"""
            <div class="project-card">
              <div class="card-label">{html_escape(publication['venue'])} / {html_escape(publication['date'])}</div>
              <div class="card-title">{html_escape(publication['title'])}</div>
              <div class="card-copy">
                Classical machine learning and sentiment analysis work focused on cross-domain classification,
                preprocessing, feature extraction, and interpretable model evaluation.
              </div>
              <p class="card-copy"><a href="{publication['link']}" target="_blank">Open publication</a></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_section_heading("research signal", "Why it matters")
    col1, col2, col3 = st.columns(3)
    with col1:
        render_card("ml", "Interpretable models", "Sentiment work using approaches such as logistic regression and decision trees for efficient, explainable classification.", ["LR", "Decision trees"])
    with col2:
        render_card("evaluation", "Model discipline", "Preprocessing, feature extraction, and evaluation with metrics such as accuracy, precision, and recall.", ["Metrics", "NLP"])
    with col3:
        render_card("product", "Bridge to AI apps", "Research experience complements practical LLM integration by grounding AI work in evaluation and behavior.", ["AI apps", "Evaluation"])


def render_contact_page() -> None:
    st.markdown('<div class="kicker">$ open contact.channels <span class="cursor"></span></div>', unsafe_allow_html=True)
    st.title("Contact")

    c1, c2 = st.columns([0.9, 1.1], gap="large")
    with c1:
        st.markdown(
            f"""
            <div class="contact-panel">
              <div class="card-label">direct</div>
              <div class="card-title">Let's build useful systems.</div>
              <div class="card-copy">
                Email: {PROFILE['email']}<br>
                Phone: {PROFILE['phone']}<br>
                Location: {PROFILE['location']}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.link_button("Email Sameer", f"mailto:{PROFILE['email']}", width="stretch")
        st.link_button("LinkedIn", PROFILE["linkedin"], width="stretch")
        st.link_button("GitHub", PROFILE["github"], width="stretch")
        st.link_button("Google Scholar", PROFILE["scholar"], width="stretch")
        if RESUME_PATH.exists():
            with RESUME_PATH.open("rb") as resume_file:
                st.download_button(
                    "Download resume",
                    resume_file,
                    file_name="Sameer_Nagar_Resume.pdf",
                    mime="application/pdf",
                    width="stretch",
                )

    with c2:
        render_section_heading("quick message", "Recruiter prompt")
        default_message = textwrap.dedent(
            f"""
            Hi Sameer,

            I saw your AI-first portfolio and wanted to connect about a software engineering role involving AI, backend systems, Salesforce, cloud, or enterprise automation.
            """
        ).strip()
        st.text_area("Message draft", default_message, height=210)
        render_card(
            "tip",
            "Use the AI first",
            "The homepage assistant can summarize Sameer's background, compare a job description, or explain the strongest project signals before you reach out.",
            ["AI Chat", "JD match", "Recruiter mode"],
        )


def main() -> None:
    init_state()
    inject_css()
    ensure_visual_assets()
    sync_active_session()
    render_sidebar()

    page = st.session_state.page
    if page == "AI Chat":
        render_chat_page()
    elif page == "About":
        render_about_page()
    elif page == "Resume":
        render_resume_page()
    elif page == "Projects":
        render_projects_page()
    elif page == "Research":
        render_research_page()
    elif page == "Contact":
        render_contact_page()


if __name__ == "__main__":
    main()
