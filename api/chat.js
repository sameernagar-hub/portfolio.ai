const PROFILE_CONTEXT = `
Sameer Nagar is a Software Development Engineer focused on backend systems, AI integration, cloud platforms, and full-stack delivery.

Contact:
- Email: nagarsam8989@gmail.com
- Phone: +1 (657) 751-9425
- Location: Fullerton, California
- LinkedIn: https://www.linkedin.com/in/aavonsameer/
- GitHub: https://github.com/sameernagar-hub

Education:
- Master of Science in Computer Science, California State University, Fullerton. Graduated May 2026, GPA 3.70/4.00.
- Bachelor of Technology in Computer Science, Rajiv Gandhi Proudyogiki Vishwavidyalaya, India, 2018 - 2022, GPA 3.66/4.00.

Experience:
- Jr. Associate Software Engineer, Unthinkable Solutions, Gurugram, India, 2021 - 2024. Built scalable backend services, full-stack applications, enterprise workflows, AI-powered solutions, LLM integrations, and automation.
- Teaching Associate, California State University, Fullerton, 2025 - 2026. Mentored students, supported computer science coursework, graded assignments, and collaborated with faculty.
- Service Associate, California State University, Fullerton, 2025 - 2026. Delivered customer service, transactions, inventory support, and team operations.

Skills:
- Python, Java, C++, JavaScript, React, Node.js, Flask, MySQL, MongoDB, AWS, Azure, Docker, CI/CD, LLMs, Prompt Engineering, Agentic AI, Salesforce Development.

Project themes:
- Scalable API services, LLM portfolio assistant, task manager application, ML pipeline automation, data pipeline services, cloud operations dashboard.
`;

function parseBody(req) {
  if (!req.body) return {};
  if (typeof req.body === 'object') return req.body;

  try {
    return JSON.parse(req.body);
  } catch (error) {
    return {};
  }
}

function formatHistoryForGemini(history) {
  if (!Array.isArray(history)) return [];

  return history
    .slice(-8)
    .map((entry) => ({
      role: entry.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: String(entry.content || '').slice(0, 1000) }]
    }));
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  
  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.GEMINI_API_KEY;

  if (!apiKey) {
    return res.status(503).json({ error: 'Gemini API key is not configured' });
  }

  const body = parseBody(req);
  const message = body.message ? String(body.message).trim().slice(0, 1200) : '';

  if (!message) {
    return res.status(400).json({ error: 'Message is required' });
  }

  const history = formatHistoryForGemini(body.history || []);
  const modelName = process.env.GEMINI_MODEL || 'gemini-1.5-flash';
  
  const systemInstruction = `You are Sameer Nagar's portfolio assistant. 
  Answer only from the portfolio context provided. Be concise, warm, and specific.
  If a detail is not in the context, say that the portfolio does not list it and offer Sameer's contact details.
  Context: ${PROFILE_CONTEXT}`;

  const contents = [
    ...history,
    { role: 'user', parts: [{ text: message }] }
  ];

  const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${apiKey}`;

  const geminiResponse = await fetch(geminiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents,
      systemInstruction: {
        parts: [{ text: systemInstruction }]
      },
      generationConfig: {
        maxOutputTokens: 400,
        temperature: 0.7
      }
    })
  });

  const data = await geminiResponse.json().catch(() => ({}));

  if (!geminiResponse.ok) {
    return res.status(geminiResponse.status).json({
      error: data.error?.message || 'Gemini request failed'
    });
  }

  const reply = data.candidates?.[0]?.content?.parts?.[0]?.text;

  return res.status(200).json({
    reply: reply || "I could not generate a response. You can contact Sameer at nagarsam8989@gmail.com."
  });
};
