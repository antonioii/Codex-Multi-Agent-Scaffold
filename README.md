# Codex-Multi-Agent-Scaffold

A desktop tool built with Python + Tkinter to quickly generate structured multi-agent Codex projects, including agent configurations and a ready-to-use Codex prompt, inspired by Claude’s agent system and designed to simplify and automate the creation of agent-based pipelines for Codex (especially Codex-CLI) workflows.

---

## ✨ Features

* 🧠 Optional **multi-agent architecture**
* ⚙️ Custom agent configuration (planner, backend, frontend, etc.)
* 🔁 Dynamic project structure preview
* 🧩 Flexible agent editing via UI popup
* 🧠 **Simulated memory system (instruction-based)**

  * Uses `agents-memory/` as a conceptual memory layer
  * No rigid structure — agents decide when/how to use memory
* 📁 Generates a **complete Codex-ready project scaffold**

  * `AGENTS.md`
  * `.codex/config.toml`
  * optional `.codex/agents/*.toml`
  * `Prompt-for-run-codex.txt` (pre-built execution prompt)

---

## 🧠 Simulated Agent Memory (v3)

When enabled, the system instructs Codex agents to optionally use a shared memory approach.

Instead of forcing a rigid structure, agents are guided to:

* Create memory files only when useful
* Store decisions, constraints, and relevant context
* Use a convention-based folder:

```id="m4d9v1"
agents-memory/
```

Examples of possible files (created by agents if needed):

* `shared.md`
* `architecture.md`
* `decisions.md`
* `known_issues.md`

This keeps the system:

* flexible
* scalable
* aligned with different project types

---

## 🏗️ Generated Structure

```id="o3h7k2"
my-project/
├── AGENTS.md
├── .codex/
│   ├── config.toml
│   └── agents/
├── src/
├── tests/
├── Prompt-for-run-codex.txt
└── README.md
```

---

## 🚀 How to Use

1. Run the application:

```bash
python codex-scaffold_generator-v3.py
```

2. Fill in:

   * Project name
   * Description
   * Output folder

3. (Optional) Enable:

   * Specialized agents
   * Simulated memory

4. Configure agents via popup (optional)

5. Click **Generate Project Structure**

---

## 🧩 Use Case

This tool is especially useful for:

* Multi-agent AI workflows
* Structured LLM-driven development
* Codex-based automation pipelines
* Experimental AI architectures

---

## 🛠️ Tech Stack

* Python 3
* Tkinter (GUI)
* TOML (configuration)
* Codex-compatible structure

---

## 🤝 Credits

This project was developed by **Antonio Sergio C C II**
with assistance from **ChatGPT (OpenAI)**.

The design, architecture, and evolution of the tool were collaboratively refined through iterative development and technical discussion.

---

## 📄 License

This project is licensed under **Creative Commons**.

You are free to:

* Share
* Adapt
* Modify

As long as proper credit is given.

---

## 🌱 Future Ideas

* Agent templates (ML, API, SaaS, etc.)
* Persistent memory (real implementation)
* Integration with local LLMs
* Visual agent workflow builder
* Export/import agent configurations

---

## 💡 Final Note

This is not just a scaffold generator.

It is a step toward **programmable multi-agent systems**.

---
