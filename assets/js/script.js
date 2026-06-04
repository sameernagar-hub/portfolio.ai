'use strict';

const toggleActive = (element) => {
  if (element) element.classList.toggle('active');
};

const sidebar = document.querySelector('[data-sidebar]');
const sidebarBtn = document.querySelector('[data-sidebar-btn]');

if (sidebarBtn) {
  sidebarBtn.addEventListener('click', () => toggleActive(sidebar));
}

const navigationLinks = document.querySelectorAll('[data-nav-link]');
const pages = document.querySelectorAll('[data-page]');

navigationLinks.forEach((link) => {
  link.addEventListener('click', () => {
    const targetPage = link.dataset.target;

    pages.forEach((page) => {
      page.classList.toggle('active', page.dataset.page === targetPage);
    });

    navigationLinks.forEach((navLink) => {
      navLink.classList.toggle('active', navLink === link);
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
});

const filterButtons = document.querySelectorAll('[data-filter-btn]');
const filterItems = document.querySelectorAll('[data-filter-item]');
const select = document.querySelector('[data-select]');
const selectItems = document.querySelectorAll('[data-select-item]');
const selectValue = document.querySelector('[data-select-value]');

const filterProjects = (filter) => {
  filterItems.forEach((item) => {
    const isVisible = filter === 'all' || item.dataset.category === filter;
    item.classList.toggle('active', isVisible);
  });
};

filterButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const filter = button.dataset.filter;

    filterButtons.forEach((filterButton) => {
      filterButton.classList.toggle('active', filterButton === button);
    });

    if (selectValue) selectValue.textContent = button.textContent.trim();
    filterProjects(filter);
  });
});

if (select) {
  select.addEventListener('click', () => toggleActive(select));
}

selectItems.forEach((item) => {
  item.addEventListener('click', () => {
    const filter = item.dataset.filter;
    const label = item.textContent.trim();

    if (selectValue) selectValue.textContent = label;
    if (select) select.classList.remove('active');

    filterButtons.forEach((button) => {
      button.classList.toggle('active', button.dataset.filter === filter);
    });

    filterProjects(filter);
  });
});

const form = document.querySelector('[data-form]');
const formInputs = document.querySelectorAll('[data-form-input]');
const formBtn = document.querySelector('[data-form-btn]');

const updateFormState = () => {
  if (!form || !formBtn) return;
  formBtn.toggleAttribute('disabled', !form.checkValidity());
};

formInputs.forEach((input) => input.addEventListener('input', updateFormState));

if (form) {
  form.addEventListener('submit', (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const name = String(formData.get('fullname') || '').trim();
    const email = String(formData.get('email') || '').trim();
    const message = String(formData.get('message') || '').trim();
    const subject = encodeURIComponent(`Portfolio message from ${name}`);
    const body = encodeURIComponent(`${message}\n\nFrom: ${name}\nEmail: ${email}`);

    window.location.href = `mailto:nagarsam8989@gmail.com?subject=${subject}&body=${body}`;
    form.reset();
    updateFormState();
  });
}

// --- Full-Page Agent Logic ---
const agentMessages = document.getElementById('agentMessages');
const agentInput = document.getElementById('agentInput');
const agentForm = document.getElementById('agentForm');
const agentSendBtn = document.getElementById('agentSendBtn');
const newChatBtn = document.getElementById('newChatBtn');

// Quick Widget (kept for backwards compatibility)
const chatWidget = document.getElementById('chatWidget'); 
const chatWidgetBtn = document.getElementById('chatWidgetBtn'); 
const chatToggleBtn = document.getElementById('chatToggleBtn'); 
const chatMessages = document.getElementById('chatMessages'); 
const chatInput = document.getElementById('chatInput'); 
const chatForm = document.getElementById('chatForm'); 
const chatSendBtn = document.getElementById('chatSendBtn');

const profileContext = { 
  name: 'Sameer Nagar',
  role: 'Software Development Engineer focused on backend systems, AI integration, cloud platforms, and full-stack delivery.',
  contact: {
    email: 'nagarsam8989@gmail.com',
    phone: '+1 (657) 751-9425',
    location: 'Fullerton, California',
    linkedin: 'https://www.linkedin.com/in/aavonsameer/',
    github: 'https://github.com/sameernagar-hub'
  },
  education: [
    'MS in Computer Science, California State University, Fullerton. Graduated May 2026, GPA 3.70/4.00.',
    'BTech in Computer Science, Rajiv Gandhi Proudyogiki Vishwavidyalaya, India, 2018 - 2022, GPA 3.66/4.00.'
  ],
  experience: [
    'Jr. Associate Software Engineer at Unthinkable Solutions, 2021 - 2024.',
    'Teaching Associate at California State University, Fullerton, 2025 - 2026.',
    'Service Associate at California State University, Fullerton, 2025 - 2026.'
  ],
  skills: [
    'Python',
    'Java',
    'C++',
    'JavaScript',
    'React',
    'Node.js',
    'Flask',
    'MySQL',
    'MongoDB',
    'AWS',
    'Azure',
    'Docker',
    'CI/CD',
    'LLMs',
    'Prompt Engineering',
    'Agentic AI',
    'Salesforce Development'
  ],
  projects: [
    'Scalable API services',
    'LLM portfolio assistant',
    'Task manager application',
    'ML pipeline automation',
    'Data pipeline services',
    'Cloud operations dashboard'
  ]
};

let conversationHistory = JSON.parse(localStorage.getItem('agent_history')) || [];

const saveHistory = () => {
  localStorage.setItem('agent_history', JSON.stringify(conversationHistory));
};

const clearHistory = () => {
  localStorage.removeItem('agent_history');
};

const openChat = () => {
  if (!chatWidget || !chatWidgetBtn) return;
  chatWidget.classList.add('active');
  chatWidgetBtn.style.display = 'none';
  if (chatInput) chatInput.focus();
};

const closeChat = () => {
  if (!chatWidget || !chatWidgetBtn) return;
  chatWidget.classList.remove('active');
  chatWidgetBtn.style.display = 'flex';
};

if (chatWidgetBtn) chatWidgetBtn.addEventListener('click', openChat);
if (chatToggleBtn) chatToggleBtn.addEventListener('click', closeChat);

const appendMessage = (container, message, type, options = {}) => {
  if (!container) return null;

  const messageElement = document.createElement('div');
  messageElement.className = container.id === 'agentMessages' ? `agent-${type}-message` : `message ${type}-message`;
  if (options.pending) messageElement.classList.add('is-pending');

  const paragraph = document.createElement('p');
  paragraph.textContent = message;
  messageElement.appendChild(paragraph);
  container.appendChild(messageElement);
  container.scrollTop = container.scrollHeight;

  return messageElement;
};

const removeMessage = (messageElement) => {
  if (messageElement && messageElement.parentElement) {
    messageElement.parentElement.removeChild(messageElement);
  }
};

const includesAny = (message, keywords) => {
  return keywords.some((keyword) => message.includes(keyword));
};

const localAssistantResponse = (userMessage) => {
  const message = userMessage.toLowerCase();

  if (includesAny(message, ['hello', 'hi', 'hey'])) {
    return "Hi, I'm Sameer's portfolio assistant. Ask me about his backend work, AI integration, cloud experience, education, projects, or contact details.";
  }

  if (includesAny(message, ['contact', 'email', 'phone', 'linkedin', 'github', 'reach'])) {
    return `You can reach Sameer at ${profileContext.contact.email}, call ${profileContext.contact.phone}, view LinkedIn at ${profileContext.contact.linkedin}, or see GitHub at ${profileContext.contact.github}.`;
  }

  if (includesAny(message, ['resume', 'cv', 'download'])) {
    return 'Sameer has a resume download linked on the portfolio sidebar and hero section: Sameer_Nagar_Resume.pdf.';
  }

  if (includesAny(message, ['education', 'school', 'degree', 'gpa', 'csuf', 'university'])) {
    return profileContext.education.join(' ');
  }

  if (includesAny(message, ['experience', 'work', 'job', 'unthinkable', 'teaching', 'associate'])) {
    return `${profileContext.experience.join(' ')} His work centers on scalable backend services, full-stack applications, AI-powered solutions, and mentoring computer science students.`;
  }

  if (includesAny(message, ['skill', 'stack', 'technology', 'tech', 'tools'])) {
    return `Sameer's core stack includes ${profileContext.skills.join(', ')}. His strongest focus areas are backend engineering, AI integration, cloud/devops, and full-stack delivery.`;
  }

  if (includesAny(message, ['backend', 'api', 'server', 'microservice'])) {
    return 'Sameer focuses on backend systems: REST APIs, service architecture, database-backed workflows, Python, Java, Node.js, Flask, and scalable enterprise application logic.';
  }

  if (includesAny(message, ['ai', 'ml', 'llm', 'chatgpt', 'openai', 'prompt'])) {
    return 'Sameer works with LLM-powered applications, prompt engineering, Agentic AI patterns, conversational assistants, TensorFlow, Pandas, and automation workflows.';
  }

  if (includesAny(message, ['cloud', 'aws', 'azure', 'docker', 'ci/cd', 'devops'])) {
    return 'Sameer has experience with AWS, Azure, Docker, CI/CD pipelines, deployment automation, and cloud-oriented dashboards.';
  }

  if (includesAny(message, ['project', 'portfolio', 'built', 'application'])) {
    return `Highlighted project areas include ${profileContext.projects.join(', ')}. The portfolio Work section organizes them by backend, AI/ML, full-stack, and cloud.`;
  }

  return 'Sameer is a software development engineer focused on backend systems, AI integration, cloud platforms, and full-stack applications. Try asking about his experience, skills, education, projects, or contact details.';
};

const askLiveAssistant = async (message) => {
  // Use relative path for production; fallback to localhost for local FastAPI dev
  const origin = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000' 
    : '';
  console.log(`Connecting to AI Assistant at: ${origin || 'Relative Path'}/api/chat`);
  const response = await fetch(`${origin}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      history: conversationHistory.slice(-8)
    })
  });

  if (!response.ok) {
    throw new Error('AI endpoint unavailable');
  }

  const data = await response.json();
  if (!data || typeof data.reply !== 'string' || !data.reply.trim()) {
    throw new Error('AI endpoint returned an empty response');
  }

  return data.reply.trim();
};

const setChatLoading = (isLoading) => {
  if (chatSendBtn) chatSendBtn.disabled = isLoading;
  if (chatInput) chatInput.disabled = isLoading;
};

const setAgentLoading = (isLoading) => {
  if (agentSendBtn) agentSendBtn.disabled = isLoading;
  if (agentInput) agentInput.disabled = isLoading;
};

const sendChatMessage = async (event) => {
  event.preventDefault();
  const isWidget = event.currentTarget.id === 'chatForm';
  const input = isWidget ? chatInput : agentInput;
  const container = isWidget ? chatMessages : agentMessages;
  const setLoading = isWidget ? setChatLoading : setAgentLoading;

  if (!input) return;
  const userMessage = input.value.trim();
  if (!userMessage) return;

  appendMessage(container, userMessage, 'user');
  conversationHistory.push({ role: 'user', content: userMessage });
  saveHistory();
  input.value = '';
  setLoading(true);

  const pendingMessage = appendMessage(container, 'Thinking...', 'bot', { pending: true });

  try {
    const reply = await askLiveAssistant(userMessage);
    removeMessage(pendingMessage);
    appendMessage(container, reply, 'bot');
    conversationHistory.push({ role: 'assistant', content: reply });
    saveHistory();
  } catch (error) {
    const fallbackReply = localAssistantResponse(userMessage);
    removeMessage(pendingMessage);
    appendMessage(container, fallbackReply, 'bot');
    conversationHistory.push({ role: 'assistant', content: fallbackReply });
    saveHistory();
  } finally {
    setLoading(false);
    if (input) input.focus();
  }
};

// Initialize agent history on load
window.addEventListener('DOMContentLoaded', () => {
  if (agentMessages && conversationHistory.length > 0) {
    agentMessages.innerHTML = '';
    conversationHistory.forEach(msg => {
      appendMessage(agentMessages, msg.content, msg.role === 'user' ? 'user' : 'bot');
    });
  }
});

if (chatForm) chatForm.addEventListener('submit', sendChatMessage);
if (agentForm) agentForm.addEventListener('submit', sendChatMessage);

if (newChatBtn) {
  newChatBtn.addEventListener('click', () => {
    if (confirm('Start a new conversation? Previous history will be cleared.')) {
      clearHistory();
      conversationHistory = [];
      if (agentMessages) {
        agentMessages.innerHTML = `
          <div class="agent-bot-message">
            <p>Hi! I'm Sameer's AI Agent. I've been reset. How can I help you today?</p>
          </div>
        `;
      }
    }
  });
}
