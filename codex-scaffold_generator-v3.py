import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from dataclasses import dataclass
from copy import deepcopy


DEFAULT_AGENTS = [
    {
        "filename": "planner.toml",
        "name": "planner",
        "description": "Plans tasks before implementation.",
        "you_are": "You are a senior software planning agent.",
        "focus_on": "Architecture, impacted files, implementation strategy, risks, and task decomposition.",
        "rules_output": "Never write production code. Return a concise implementation plan with steps and affected files.",
        "developer_instructions": "Help the main Codex agent understand the task before coding."
    },
    {
        "filename": "backend.toml",
        "name": "backend",
        "description": "Handles backend, Python, APIs, persistence, and business logic.",
        "you_are": "You are a senior backend engineering agent.",
        "focus_on": "Python logic, FastAPI/backend code, validation, error handling, data models, persistence, and tests.",
        "rules_output": "Return implementation notes, risks, and suggested code changes. Avoid UI concerns unless necessary.",
        "developer_instructions": "Help the main Codex agent implement backend logic safely."
    },
    {
        "filename": "frontend.toml",
        "name": "frontend",
        "description": "Handles frontend, UI, UX, layout, and loading feedback.",
        "you_are": "You are a senior frontend and UX engineering agent.",
        "focus_on": "React, Vite, Tkinter, UI layout, user feedback, accessibility, state displayed to users, and interaction flows.",
        "rules_output": "Return UI recommendations and implementation notes. Avoid backend concerns unless required by the UI.",
        "developer_instructions": "Help the main Codex agent improve interface clarity and usability."
    },
    {
        "filename": "reviewer.toml",
        "name": "reviewer",
        "description": "Reviews final changes before completion.",
        "you_are": "You are a strict senior code reviewer.",
        "focus_on": "Bugs, regressions, edge cases, security issues, duplicated logic, missing tests, and unclear naming.",
        "rules_output": "Return a review checklist with blocking issues first, then non-blocking suggestions.",
        "developer_instructions": "Review the final diff and help the main Codex agent avoid shipping mistakes."
    },
    {
        "filename": "docs.toml",
        "name": "docs",
        "description": "Updates documentation and developer-facing instructions.",
        "you_are": "You are a technical documentation agent.",
        "focus_on": "README updates, usage instructions, setup instructions, examples, and developer notes.",
        "rules_output": "Return concise documentation changes in Markdown.",
        "developer_instructions": "Help keep documentation synchronized with code behavior."
    },
]


@dataclass
class AgentConfig:
    filename: str
    name: str
    description: str
    you_are: str
    focus_on: str
    rules_output: str
    developer_instructions: str


def safe_project_name(name: str) -> str:
    cleaned = "".join(c for c in name.strip() if c.isalnum() or c in ("-", "_", " "))
    cleaned = cleaned.replace(" ", "-")
    return cleaned or "my-codex-project"


def escape_toml_multiline(value: str) -> str:
    return value.replace(chr(34) * 3, "\\\"\\\"\\\"").strip()


def escape_toml_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').strip()


def write_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        file.write(content.strip() + "\n")


def normalize_agent(agent: dict, fallback_index: int) -> dict:
    name = agent.get("name", "").strip() or f"agent_{fallback_index + 1}"
    filename = agent.get("filename", "").strip() or f"{name}.toml"
    if not filename.endswith(".toml"):
        filename = f"{filename}.toml"

    return {
        "filename": filename,
        "name": name,
        "description": agent.get("description", "").strip() or f"Specialized agent: {name}.",
        "you_are": agent.get("you_are", "").strip() or "You are a specialized Codex support agent.",
        "focus_on": agent.get("focus_on", "").strip() or "The specific responsibility described by your name and description.",
        "rules_output": agent.get("rules_output", "").strip() or "Return concise, practical guidance for the main Codex agent.",
        "developer_instructions": agent.get("developer_instructions", "").strip() or "Help the main Codex agent complete the task safely and clearly.",
    }


def resize_agents(agents_data: list[dict], desired_count: int) -> list[dict]:
    desired_count = max(1, desired_count)
    resized = [dict(agent) for agent in agents_data[:desired_count]]

    while len(resized) < desired_count:
        next_index = len(resized)
        if next_index < len(DEFAULT_AGENTS):
            resized.append(dict(DEFAULT_AGENTS[next_index]))
        else:
            agent_number = next_index + 1
            resized.append({
                "filename": f"agent_{agent_number}.toml",
                "name": f"agent_{agent_number}",
                "description": f"Custom specialized agent {agent_number}.",
                "you_are": "You are a specialized Codex support agent.",
                "focus_on": "Define this agent's main area of responsibility.",
                "rules_output": "Return concise, practical guidance for the main Codex agent.",
                "developer_instructions": "Help the main Codex agent complete the task safely and clearly."
            })

    return [normalize_agent(agent, index) for index, agent in enumerate(resized)]


def build_memory_section(memory_enabled: bool) -> str:
    if not memory_enabled:
        return """
## Agent Memory Simulation

Memory simulation between agents is disabled for this scaffold.
"""

    return """
## Agent Memory Simulation

Simulated memory is enabled as an instruction-driven behavior, not as a fixed pre-created structure.

When a task would benefit from persistent context between agents, create and maintain lightweight memory files under:

```text
agents-memory/
```

Suggested files may include, depending on the project and task:

- `agents-memory/shared-memory.md` for decisions useful to all agents.
- `agents-memory/<agent-name>-memory.md` for agent-specific notes.
- `agents-memory/architecture-decisions.md` for important design decisions.
- `agents-memory/known-issues.md` for recurring bugs, limitations, and unresolved questions.

Rules:
1. Do not create memory files automatically if the task does not need them.
2. Before using memory, decide whether persistent context would genuinely help the current task.
3. If memory is useful, create or update only the minimal files needed under `agents-memory/`.
4. Before starting a task, read relevant memory files from `agents-memory/` if they exist.
5. After meaningful agent work, append concise notes about decisions, constraints, open questions, and affected files.
6. Do not store secrets, API keys, credentials, private user data, or irrelevant chat history.
7. Treat this as simulated project memory, not as guaranteed native Codex long-term memory.
"""

def build_agents_md(project_name: str, description: str, specialized: bool, agents_data: list[dict], memory_enabled: bool) -> str:
    if specialized:
        agent_lines = []
        for agent in agents_data:
            clean = normalize_agent(agent, len(agent_lines))
            agent_lines.append(f"- {clean['name']}: {clean['description']}")
        agent_list = "\n".join(agent_lines)

        agent_policy = f"""
## Specialized Agents

Use the specialized agents when the task benefits from separation of concerns:

{agent_list}

For non-trivial tasks:
1. Use planner or the most appropriate planning/review agent first when available.
2. Use the relevant specialized agents.
3. Consolidate their results.
4. Implement.
5. Use a reviewer-style agent before finalizing when available.
"""
    else:
        agent_policy = """
## Automatic Codex Mode

Do not force specialized agents by default.

Use Codex's default automatic orchestration. Only create or call specialized agents if the user explicitly asks for them or if the task is complex enough to justify separation of concerns.
"""

    return f"""
# AGENTS.md

## Project

**Name:** {project_name}

**Description:** {description or "No description provided."}

## General Operating Model

Act as a careful software engineering assistant for this repository.

Before editing code:
1. Understand the user's request.
2. Identify the affected files.
3. Explain the intended approach briefly.
4. Make the smallest safe change that solves the problem.
5. Avoid unrelated refactors.
6. Run or suggest relevant checks/tests.
7. Summarize what changed.

{agent_policy}

{build_memory_section(memory_enabled)}

## Coding Rules

- Prefer simple, readable code.
- Preserve the existing project style.
- Do not introduce unnecessary dependencies.
- Do not change public behavior unless requested.
- Keep secrets, API keys, tokens, and credentials out of the repository.
- When uncertain, ask for clarification or state the assumption.

## Final Response Rules

At the end of a task, report:
- Files changed.
- What was implemented.
- Tests/checks performed.
- Any limitations or follow-up needed.
"""


def build_config_toml(project_name: str, specialized: bool, memory_enabled: bool) -> str:
    agents_hint = "true" if specialized else "false"
    memory_hint = "true" if memory_enabled else "false"
    return f"""
# Codex project-local configuration
# Project: {project_name}
#
# Notes:
# - Keep machine-specific or secret values out of this file.
# - If your Codex version does not support project-local agent TOML files,
#   move .codex/agents/*.toml to your global Codex agents directory.

model = "gpt-5-codex"

approval_policy = "on-request"
sandbox_mode = "workspace-write"

[project]
name = "{escape_toml_string(project_name)}"
specialized_agents_enabled = {agents_hint}
simulated_agent_memory_enabled = {memory_hint}

[commands]
# Adjust these to your stack.
setup = ""
test = ""
lint = ""

[workflow]
plan_before_large_changes = true
review_after_changes = true
avoid_unrelated_refactors = true

[memory]
enabled = {memory_hint}
strategy = "instruction-driven"
folder = "agents-memory"
create_only_when_useful = true
"""


def build_agent_toml(agent: AgentConfig, memory_enabled: bool) -> str:
    memory_note = ""
    if memory_enabled:
        memory_note = """
Memory simulation:
Before responding, consider the shared memory file at agents-memory/ if relevant memory files exist.
After meaningful work, suggest concise updates under agents-memory/ when useful.
"""

    instructions = f"""
{agent.developer_instructions}

Role:
{agent.you_are}

Focus on:
{agent.focus_on}

Rules and output:
{agent.rules_output}

{memory_note}
"""
    return f"""
name = "{escape_toml_string(agent.name)}"
description = "{escape_toml_string(agent.description)}"

instructions = \"\"\"
{escape_toml_multiline(instructions)}
\"\"\"
"""


def build_prompt_file(project_name: str, description: str, specialized: bool, memory_enabled: bool) -> str:
    memory_step = ""
    if memory_enabled:
        memory_step = (
            "\nMemory simulation is enabled. Use `agents-memory/` only when useful: "
            "read relevant files from that folder if they exist, and create or update concise "
            "memory notes there after meaningful decisions. Do not create memory files unnecessarily."
        )

    if specialized:
        body = f"""
Use the operating model defined in AGENTS.md.{memory_step}

This is a non-trivial task. Act as the main orchestrator.

Suggested flow:
1. Use the planner agent first when available.
2. Use relevant specialized agents depending on the task.
3. Consolidate all findings.
4. Implement the smallest safe solution.
5. Use a reviewer-style agent to inspect the final diff when available.
6. Finalize with files changed, tests/checks, and limitations.

Task:
[DESCRIBE YOUR TASK HERE]
"""
    else:
        body = f"""
Use the operating model defined in AGENTS.md.{memory_step}

Use Codex automatic orchestration unless the task is complex enough to justify specialized subagents.

Task:
[DESCRIBE YOUR TASK HERE]
"""
    return f"""
# Prompt for running Codex

Project: {project_name}

Description:
{description or "No description provided."}

{body}
"""


def build_readme(project_name: str, description: str, specialized: bool, memory_enabled: bool) -> str:
    mode = "Specialized agents enabled" if specialized else "Automatic Codex mode"
    memory = "Enabled" if memory_enabled else "Disabled"
    agents_dir_line = "│   └── agents/" if specialized else "│   └── config.toml"

    codex_tree = f"""{project_name}/
├── AGENTS.md
├── .codex/
│   ├── config.toml
{agents_dir_line}
├── src/
├── tests/
├── Prompt-for-run-codex.txt
└── README.md"""

    memory_note = ""
    if memory_enabled:
        memory_note = """

When simulated agent memory is useful, Codex is instructed to create or update files under:

```text
agents-memory/
```

This folder is intentionally not created by the scaffold unless a future Codex task decides that memory files are useful.
"""

    return f"""
# {project_name}

{description or "Project scaffold generated for Codex."}

## Codex Configuration

Mode: **{mode}**

Simulated agent memory: **{memory}**

This project includes a starter Codex configuration:

```text
{codex_tree}
```
{memory_note}
## Files

- `AGENTS.md`: project-level instructions for Codex.
- `.codex/config.toml`: local Codex configuration.
- `.codex/agents/*.toml`: optional specialized agent profiles.
- `agents-memory/`: optional on-demand folder for simulated agent memory, created by Codex only when useful.
- `Prompt-for-run-codex.txt`: reusable prompt template.
- `src/`: source code.
- `tests/`: tests.

## Suggested Codex Prompt

Open `Prompt-for-run-codex.txt`, replace `[DESCRIBE YOUR TASK HERE]`, and use it when running Codex.
"""


class AgentCountDialog(tk.Toplevel):
    def __init__(self, master, default_count: int):
        super().__init__(master)
        self.title("How many agents?")
        self.geometry("360x150")
        self.resizable(False, False)
        self.result = None

        self.count_var = tk.IntVar(value=max(1, default_count))

        root = ttk.Frame(self, padding=14)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="How many specialized agents do you want?").pack(anchor="w")
        ttk.Spinbox(root, from_=1, to=30, textvariable=self.count_var, width=8).pack(anchor="w", pady=10)
        ttk.Label(root, text=f"Default: {default_count}").pack(anchor="w")

        buttons = ttk.Frame(root)
        buttons.pack(fill="x", pady=(12, 0))
        ttk.Button(buttons, text="Cancel", command=self.cancel).pack(side="right")
        ttk.Button(buttons, text="Continue", command=self.confirm).pack(side="right", padx=(0, 8))

        self.bind("<Return>", lambda _event: self.confirm())
        self.bind("<Escape>", lambda _event: self.cancel())
        self.transient(master)
        self.grab_set()

    def confirm(self):
        try:
            count = int(self.count_var.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Invalid number", "Please enter a valid number of agents.", parent=self)
            return
        if count < 1 or count > 30:
            messagebox.showerror("Invalid number", "Please choose between 1 and 30 agents.", parent=self)
            return
        self.result = count
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


class AgentEditor(tk.Toplevel):
    def __init__(self, master, agents_data):
        super().__init__(master)
        self.title("Configure Specialized Agents")
        self.geometry("920x680")
        self.minsize(800, 560)

        self.agents_data = [normalize_agent(agent, index) for index, agent in enumerate(agents_data)]
        self.current_index = 0
        self.result = None

        self._build_ui()
        self._refresh_selector()
        self._load_agent(0)

        self.transient(master)
        self.grab_set()

    def _build_ui(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        top = ttk.Frame(root)
        top.pack(fill="x")

        ttk.Label(top, text="Agent:").pack(side="left")
        self.agent_selector = ttk.Combobox(top, state="readonly", width=24)
        self.agent_selector.pack(side="left", padx=8)
        self.agent_selector.bind("<<ComboboxSelected>>", self._on_select)

        ttk.Label(top, text="Edit each agent profile before generating TOML files.").pack(side="left", padx=12)

        form = ttk.Frame(root)
        form.pack(fill="both", expand=True, pady=12)

        self.fields = {}

        self._add_entry(form, "filename", "Filename")
        self._add_entry(form, "name", "Name")
        self._add_entry(form, "description", "Description")
        self._add_text(form, "developer_instructions", "Developer Instructions", height=5)
        self._add_text(form, "you_are", "You are...", height=5)
        self._add_text(form, "focus_on", "Focus On", height=5)
        self._add_text(form, "rules_output", "Rules / Output", height=5)

        bottom = ttk.Frame(root)
        bottom.pack(fill="x")

        ttk.Button(bottom, text="Previous", command=self.previous_agent).pack(side="left")
        ttk.Button(bottom, text="Next", command=self.next_agent).pack(side="left", padx=8)

        ttk.Button(bottom, text="Cancel", command=self.cancel).pack(side="right")
        ttk.Button(bottom, text="Save Agents", command=self.save_and_close).pack(side="right", padx=8)

    def _refresh_selector(self):
        self.agent_selector.configure(values=[agent["name"] for agent in self.agents_data])

    def _add_entry(self, parent, key, label):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4)

        ttk.Label(row, text=label, width=22).pack(side="left", anchor="n")
        var = tk.StringVar()
        entry = ttk.Entry(row, textvariable=var)
        entry.pack(side="left", fill="x", expand=True)

        self.fields[key] = var

    def _add_text(self, parent, key, label, height=4):
        row = ttk.Frame(parent)
        row.pack(fill="both", expand=True, pady=4)

        ttk.Label(row, text=label, width=22).pack(side="left", anchor="n")
        text = tk.Text(row, height=height, wrap="word")
        text.pack(side="left", fill="both", expand=True)

        self.fields[key] = text

    def _save_current(self):
        if not self.agents_data:
            return
        agent = self.agents_data[self.current_index]
        for key, widget in self.fields.items():
            if isinstance(widget, tk.StringVar):
                agent[key] = widget.get().strip()
            else:
                agent[key] = widget.get("1.0", "end").strip()
        self.agents_data[self.current_index] = normalize_agent(agent, self.current_index)
        self._refresh_selector()

    def _load_agent(self, index):
        if not self.agents_data:
            return
        self.current_index = max(0, min(index, len(self.agents_data) - 1))
        agent = self.agents_data[self.current_index]
        self.agent_selector.current(self.current_index)

        for key, widget in self.fields.items():
            value = agent.get(key, "")
            if isinstance(widget, tk.StringVar):
                widget.set(value)
            else:
                widget.delete("1.0", "end")
                widget.insert("1.0", value)

    def _on_select(self, _event=None):
        self._save_current()
        self._load_agent(self.agent_selector.current())

    def previous_agent(self):
        self._save_current()
        self._load_agent(self.current_index - 1)

    def next_agent(self):
        self._save_current()
        self._load_agent(self.current_index + 1)

    def cancel(self):
        self.result = None
        self.destroy()

    def save_and_close(self):
        self._save_current()
        self.result = [normalize_agent(agent, index) for index, agent in enumerate(self.agents_data)]
        self.destroy()


class CodexScaffoldApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Codex Agent Project Scaffold Generator")
        self.geometry("800x620")
        self.minsize(720, 540)

        self.agent_data = deepcopy(DEFAULT_AGENTS)

        self.project_name_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=os.getcwd())
        self.specialized_var = tk.BooleanVar(value=True)
        self.memory_var = tk.BooleanVar(value=False)

        self._build_ui()
        self._bind_preview_updates()
        self.update_preview()

    def _build_ui(self):
        main = ttk.Frame(self, padding=18)
        main.pack(fill="both", expand=True)

        title = ttk.Label(main, text="Codex Agent Project Scaffold Generator", font=("Segoe UI", 16, "bold"))
        title.pack(anchor="w")

        subtitle = ttk.Label(
            main,
            text="Generate AGENTS.md, .codex/config.toml, optional specialized agents, src, tests, README and a reusable Codex prompt."
        )
        subtitle.pack(anchor="w", pady=(4, 16))

        form = ttk.Frame(main)
        form.pack(fill="x")

        ttk.Label(form, text="Project name").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.project_name_var).grid(row=0, column=1, sticky="ew", padx=10, pady=6)

        ttk.Label(form, text="Brief description").grid(row=1, column=0, sticky="nw", pady=6)
        self.description_text = tk.Text(form, height=5, wrap="word")
        self.description_text.grid(row=1, column=1, sticky="ew", padx=10, pady=6)

        ttk.Label(form, text="Output folder").grid(row=2, column=0, sticky="w", pady=6)
        out_row = ttk.Frame(form)
        out_row.grid(row=2, column=1, sticky="ew", padx=10, pady=6)
        ttk.Entry(out_row, textvariable=self.output_dir_var).pack(side="left", fill="x", expand=True)
        ttk.Button(out_row, text="Browse", command=self.browse_output).pack(side="left", padx=(8, 0))

        form.columnconfigure(1, weight=1)

        options = ttk.LabelFrame(main, text="Codex mode", padding=12)
        options.pack(fill="x", pady=16)

        ttk.Checkbutton(
            options,
            text="Create specialized agents (.codex/agents/*.toml)",
            variable=self.specialized_var,
            command=self.update_preview
        ).pack(anchor="w")

        ttk.Checkbutton(
            options,
            text="Simulate persistent memory between agents (agents-memory/ on demand)",
            variable=self.memory_var,
            command=self.update_preview
        ).pack(anchor="w", pady=(4, 0))

        ttk.Label(options, text="When enabled, you can edit each agent profile before generating TOML files.").pack(anchor="w", pady=(4, 0))

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=10)

        ttk.Button(buttons, text="Configure Specialized Agents", command=self.configure_agents).pack(side="left")
        ttk.Button(buttons, text="Generate Project Structure", command=self.generate_project).pack(side="right")

        preview_box = ttk.LabelFrame(main, text="Generated structure", padding=10)
        preview_box.pack(fill="both", expand=True, pady=(10, 0))

        self.preview = tk.Text(preview_box, height=13, wrap="none")
        self.preview.pack(fill="both", expand=True)
        self.preview.configure(state="disabled")

    def _bind_preview_updates(self):
        self.project_name_var.trace_add("write", lambda *_args: self.update_preview())
        self.description_text.bind("<KeyRelease>", lambda _event: self.update_preview())

    def build_preview_text(self):
        project_name = safe_project_name(self.project_name_var.get())
        specialized = self.specialized_var.get()
        memory_enabled = self.memory_var.get()

        lines = [
            f"{project_name}/",
            "├── AGENTS.md",
            "├── .codex/",
        ]

        if specialized:
            lines.append("│   ├── config.toml")
            lines.append("│   └── agents/")

            agents = [normalize_agent(agent, index) for index, agent in enumerate(self.agent_data)]
            for index, agent in enumerate(agents):
                is_last_agent = index == len(agents) - 1
                branch = "│       └──" if is_last_agent else "│       ├──"
                lines.append(f"{branch} {agent['filename']}")
        else:
            lines.append("│   └── config.toml")

        lines.extend([
            "├── src/",
            "├── tests/",
            "├── Prompt-for-run-codex.txt",
            "└── README.md",
        ])

        if memory_enabled:
            lines.extend([
                "",
                "Optional on-demand memory location:",
                "agents-memory/  (created by Codex only when useful)",
            ])

        return "\n".join(lines) + "\n"

    def update_preview(self):
        if not hasattr(self, "preview"):
            return
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", self.build_preview_text())
        self.preview.configure(state="disabled")

    def browse_output(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir_var.get() or os.getcwd())
        if folder:
            self.output_dir_var.set(folder)

    def configure_agents(self):
        if not self.specialized_var.get():
            enable = messagebox.askyesno(
                "Specialized agents disabled",
                "Specialized agents are currently disabled. Enable them and configure agents now?"
            )
            if not enable:
                return
            self.specialized_var.set(True)
            self.update_preview()

        count_dialog = AgentCountDialog(self, default_count=len(self.agent_data))
        self.wait_window(count_dialog)
        if count_dialog.result is None:
            return

        editable_agents = resize_agents(self.agent_data, count_dialog.result)
        editor = AgentEditor(self, editable_agents)
        self.wait_window(editor)
        if editor.result is not None:
            self.agent_data = editor.result
            self.update_preview()
            messagebox.showinfo("Agents saved", "Specialized agent settings were saved and the preview was updated.")

    def generate_project(self):
        raw_name = self.project_name_var.get()
        project_name = safe_project_name(raw_name)
        description = self.description_text.get("1.0", "end").strip()
        output_dir = self.output_dir_var.get().strip() or os.getcwd()
        specialized = self.specialized_var.get()
        memory_enabled = self.memory_var.get()

        project_path = os.path.join(output_dir, project_name)

        if os.path.exists(project_path):
            confirm = messagebox.askyesno(
                "Project already exists",
                f"The folder already exists:\n\n{project_path}\n\nContinue and overwrite scaffold files?"
            )
            if not confirm:
                return

        try:
            self.create_structure(project_path, project_name, description, specialized, memory_enabled)
        except Exception as exc:
            messagebox.showerror("Error", f"Could not generate project:\n\n{exc}")
            return

        messagebox.showinfo("Success", f"Project scaffold generated successfully:\n\n{project_path}")

    def create_structure(self, project_path: str, project_name: str, description: str, specialized: bool, memory_enabled: bool):
        os.makedirs(project_path, exist_ok=True)
        os.makedirs(os.path.join(project_path, "src"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "tests"), exist_ok=True)
        os.makedirs(os.path.join(project_path, ".codex"), exist_ok=True)

        agents = [normalize_agent(agent, index) for index, agent in enumerate(self.agent_data)]

        write_file(os.path.join(project_path, "AGENTS.md"), build_agents_md(project_name, description, specialized, agents, memory_enabled))
        write_file(os.path.join(project_path, ".codex", "config.toml"), build_config_toml(project_name, specialized, memory_enabled))

        if specialized:
            agents_dir = os.path.join(project_path, ".codex", "agents")
            os.makedirs(agents_dir, exist_ok=True)

            for index, agent_dict in enumerate(agents):
                agent = AgentConfig(**normalize_agent(agent_dict, index))
                write_file(os.path.join(agents_dir, agent.filename), build_agent_toml(agent, memory_enabled))


        write_file(os.path.join(project_path, "Prompt-for-run-codex.txt"), build_prompt_file(project_name, description, specialized, memory_enabled))
        write_file(os.path.join(project_path, "README.md"), build_readme(project_name, description, specialized, memory_enabled))
        write_file(os.path.join(project_path, "src", ".gitkeep"), "")
        write_file(os.path.join(project_path, "tests", ".gitkeep"), "")


if __name__ == "__main__":
    app = CodexScaffoldApp()
    app.mainloop()
