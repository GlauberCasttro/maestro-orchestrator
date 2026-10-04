"""Checagem do AC-1 da TASK-02-001-AGT e dos caminhos protegidos.

Substitui o `python3 -c` e o `$(...)` do brief original, bloqueados pelo cs-guard.
Rodar da raiz do repo: .venv/bin/python .specialists/checks/task_02_001_agt.py
"""
import asyncio
import os
import subprocess
import sys

sys.path.insert(0, os.getcwd())

from maestro.agents import Agent, GroqAgent  # noqa: E402

PROTECTED = ["tests", "maestro/aggregator.py", "maestro/cli.py", "maestro/tui", "backend"]

a = GroqAgent()
assert isinstance(a, Agent), "GroqAgent não é subclasse de Agent"
assert a.model == "llama-3.3-70b-versatile", f"modelo padrão errado: {a.model}"

b = GroqAgent(model="outro", timeout=5, temperature=0.1)
assert (b.model, b.timeout, b.temperature) == ("outro", 5, 0.1), "construtor não configura model/timeout/temperature"

os.environ.pop("GROQ_API_KEY", None)
missing = asyncio.run(a.fetch("ping"))
assert missing == "[Groq] API Key Missing", f"chave ausente retornou: {missing!r}"

status = subprocess.run(
    ["git", "status", "--porcelain", "--", *PROTECTED],
    capture_output=True, text=True, check=True,
).stdout
assert status == "", f"caminhos protegidos alterados:\n{status}"

print("AC-1 OK; caminhos protegidos intocados")
