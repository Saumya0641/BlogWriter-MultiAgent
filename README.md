# 📖 Overview

Traditional AI writing tools rely on a single prompt to generate an article, often leading to hallucinations, outdated information, and inconsistent structure.

This project solves those limitations by implementing an **Autonomous Multi-Agent Workflow** where each agent performs a dedicated responsibility, similar to a real editorial team.

Instead of asking one LLM to do everything, the pipeline performs:

- Topic Analysis
- Live Web Research
- Blog Planning
- Parallel Content Generation
- Content Reduction & Merging
- Evidence Tracking
- Markdown Export

The application is built using **LangGraph** and provides a transparent workflow where every decision made by the agents can be inspected.

---

# ✨ Features

- 🤖 Autonomous Multi-Agent Workflow
- 🔍 Live Web Research using Tavily Search
- 📝 AI Blog Planning
- 📑 Structured Outline Generation
- ⚡ Parallel Section Writing
- 📚 Evidence-backed Content
- 🌐 Citation Generation
- 📊 Transparent Agent Workflow
- 💾 Markdown & JSON Export
- 🎯 SEO-Friendly Blog Structure
- 🖥 Interactive Streamlit Dashboard

---

# 🚀 Why Multi-Agent Instead of a Single LLM?

| Single LLM | Multi-Agent Pipeline |
|------------|----------------------|
| Single Prompt | Multiple Specialized Agents |
| May Hallucinate | Evidence-backed Content |
| No Research | Live Web Search |
| Sequential Generation | Parallel Section Writing |
| Limited Transparency | Fully Auditable Workflow |
| No Planning | Structured Blog Plan |
| No Evidence Tracking | Evidence & Logs Available |

---

# 🏗 Pipeline Architecture

```text
                  User Topic
                       │
                       ▼
              ┌─────────────────┐
              │ Router Agent    │
              │ Topic Analysis  │
              └─────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Research Agent  │
              │ Tavily Search   │
              └─────────────────┘
                       │
                       ▼
             ┌───────────────────┐
             │ Planner Agent     │
             │ Blog Structure    │
             └───────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     Writer 1     Writer 2     Writer 3
          │            │            │
          └───────┬────┴─────┬──────┘
                  ▼
           ┌────────────────┐
           │ Reducer Agent  │
           │ Merge Sections │
           └────────────────┘
                  │
                  ▼
          Final Markdown Blog
```

---

# 🧠 Agent Responsibilities

## Router Agent

- Understands user intent
- Determines blog mode
- Generates optimized search queries

---

## Research Agent

- Searches the web using Tavily
- Collects trusted sources
- Removes duplicate information
- Filters recent content

---

## Planner Agent

Creates a structured blog plan including:

- Blog Sections
- Goals
- Bullet Points
- Word Targets
- Required References

---

## Writer Agents

Multiple writer agents execute simultaneously.

Each agent writes one section independently, making the workflow significantly faster than sequential generation.

---

## Reducer Agent

Responsible for:

- Combining all sections
- Maintaining flow
- Producing the final Markdown blog
- Saving metadata

---

# 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| LangGraph | Multi-Agent Workflow |
| LangChain | LLM Integration |
| OpenRouter | Language Models |
| Tavily Search API | Live Web Search |
| Streamlit | User Interface |
| Pydantic v2 | Data Validation |
| Markdown | Blog Storage |
| JSON | Metadata Storage |

---

# 📂 Project Structure

```text
BlogWriter-MultiAgent/
│
├── backend.py
├── frontend.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/Saumya0641/BlogWriter-MultiAgent.git
```

Navigate to the cloned project directory.

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file.

```env
OPENROUTER_API_KEY=your_openrouter_key

TAVILY_API_KEY=your_tavily_key
```

---

# ▶ Running the Application

```bash
streamlit run frontend.py
```

The Streamlit dashboard will open automatically.

---

# 🖥 Application Workflow

1. Enter a blog topic.
2. Router analyzes the topic.
3. Research agent gathers live information.
4. Planner creates a structured outline.
5. Writer agents generate sections in parallel.
6. Reducer combines all sections.
7. Final blog is displayed.
8. Markdown and metadata are saved.

---

# 📊 Outputs

The application generates:

- Markdown Blog (.md)
- Metadata (.json)
- Blog Plan
- Research Evidence
- Search Queries
- Logs

---

# 💡 Example Topics

- Artificial Intelligence in Healthcare
- Small Language Models
- Future of Robotics
- Quantum Computing
- Climate Change Technologies
- Indian Startup Ecosystem
- Cybersecurity Trends
- Generative AI Applications

---

# 🎯 Applications

- Technical Blogging
- AI Content Generation
- Research Writing
- Educational Content
- SEO Blog Creation
- Knowledge Base Articles
- Documentation Generation

---

# 🔮 Future Enhancements

- PDF Export
- DOCX Export
- Automatic Image Generation
- Multi-language Blogs
- WordPress Publishing
- Team Collaboration
- RAG Integration
- AI Fact Verification
- Citation Management

---

# 👨‍💻 Author

**Saumya Shah**

GitHub: https://github.com/Saumya0641

---

# 📄 License

This project is intended for educational, research, and demonstration purposes.

---

⭐ If you found this project useful, consider giving the repository a star.
