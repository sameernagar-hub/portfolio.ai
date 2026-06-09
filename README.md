# Sameer Nagar AI Dev Portfolio

AI-first portfolio app for Sameer Nagar. The main experience is now a dark, CLI-inspired Python app with a ChatGPT-style homepage, sidebar navigation, responsive layouts, animated dev-tool panels, and a resume-aware AI assistant.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints in the terminal, usually:

```text
http://localhost:8501
```

## AI Assistant

The homepage is the AI assistant. It can answer questions about Sameer's resume, projects, skills, Salesforce credentials, research, education, contact details, and fit for a role.

It works in two modes:

- Local fallback mode: always available, no API key required.
- Live Gemini mode: enabled when `GEMINI_API_KEY` is configured.

Create `.env` from `.env.example` and set:

```bash
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash
```

The assistant uses `profile_context.py` as its grounded resume context and avoids inventing employers, dates, credentials, metrics, or project outcomes.

## Project Structure

```text
.
|-- app.py                      # Main Streamlit portfolio app
|-- profile_context.py          # Resume context and AI system instruction
|-- requirements.txt            # Python dependencies
|-- .streamlit/config.toml      # Dark Streamlit theme defaults
|-- assets/
|   |-- generated/              # Runtime-generated dev-tool graphics
|   |-- css/style.css           # Legacy static portfolio CSS
|   |-- js/script.js            # Legacy static portfolio JS
|   `-- images/                 # Portfolio images and icons
|-- main.py                     # Legacy/optional FastAPI backend
|-- api/                        # Legacy/optional Vercel serverless API
|-- index.html                  # Legacy static portfolio
`-- Profile (3).pdf             # Resume source file
```

## Design Direction

- AI Chat is the default homepage.
- Sidebar navigation exposes About, Resume, Projects, Research, and Contact.
- Dark dev-tool theme with terminal panels, status chips, command prompts, and compact cards.
- Responsive layout adapts across desktop, laptop, tablet, and phone widths.
- CSS animations add panel scans, scroll reveals, pulsing status, chat message entry, and blinking cursor effects.
- `Pillow` generates high-resolution dev-tool graphics used in the app.

## Legacy Static Site

The previous static portfolio remains in `index.html`, `assets/css/style.css`, and `assets/js/script.js`. The recommended viewing path is now:

```bash
streamlit run app.py
```

## Contact

- Email: nagarsam8989@gmail.com
- LinkedIn: https://www.linkedin.com/in/aavonsameer/
- GitHub: https://github.com/sameernagar-hub
- Google Scholar: https://scholar.google.com/citations?user=FfTfe3gAAAAJ&hl=en

## License

MIT. Original template attribution is preserved in `LICENSE`; portfolio modifications are attributed to Sameer Nagar.
