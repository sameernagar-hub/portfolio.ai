# Sameer Nagar Portfolio

Personal software development engineer portfolio for Sameer Nagar.

## Overview

This is a responsive static portfolio built with HTML, CSS, and JavaScript. It highlights Sameer's backend engineering, AI integration, cloud/devops, full-stack work, education, experience, selected project themes, and contact links.

## Files

- `index.html` - Main portfolio page.
- `assets/css/style.css` - Responsive visual system.
- `assets/js/script.js` - Navigation, filters, contact form, and chat widget.
- `api/chat.js` - Serverless Google Gemini API proxy for the AI assistant.
- `Sameer_Nagar_Resume.pdf` - Resume download linked from the portfolio.

## AI Assistant

The chat widget works in two modes:

1. Local profile mode: always available in the browser with resume-aware fallback answers.
2. Live AI mode: available when deployed with a serverless `/api/chat` endpoint and `GEMINI_API_KEY`.

Create an environment variable in your hosting provider:

```bash
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

`OPENAI_MODEL` is optional. The endpoint defaults to `gpt-5.4-mini`.

## Local Preview

Open `index.html` directly in a browser to preview the static portfolio. The live AI endpoint needs a serverless-capable host such as Vercel because API keys should not be exposed in browser JavaScript.

## Contact

- Email: nagarsam8989@gmail.com
- LinkedIn: https://www.linkedin.com/in/aavonsameer/
- GitHub: https://github.com/sameernagar-hub

## License

MIT. Original template attribution is preserved in `LICENSE`; portfolio modifications are attributed to Sameer Nagar.
