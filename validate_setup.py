"""Workshop prerequisite validator.

Checks that all required tools and environment variables are configured
for the Real Agents Workshop. Uses only the Python standard library so
it can run before `uv sync` installs dependencies.
"""

import os
import pathlib
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MINIMUM_PYTHON_VERSION = (3, 11)

LLM_KEY_NAMES = [
    ("OPENROUTER_API_KEY", "OpenRouter (preferred)"),
    ("OPENAI_API_KEY", "OpenAI"),
    ("ANTHROPIC_API_KEY", "Anthropic"),
    ("GEMINI_API_KEY", "Gemini"),
]

LANGFUSE_KEY_NAMES = [
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_SECRET_KEY",
    "LANGFUSE_HOST",
]

# ---------------------------------------------------------------------------
# Color / formatting helpers
# ---------------------------------------------------------------------------

def _supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    return True


if _supports_color():
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"
else:
    GREEN = RED = YELLOW = BOLD = DIM = RESET = ""


def _unicode_safe() -> bool:
    try:
        "\u2714\u2718\u26A0".encode(sys.stdout.encoding or "utf-8")
        return True
    except (UnicodeEncodeError, LookupError):
        return False


if _unicode_safe():
    TICK = "\u2714"
    CROSS = "\u2718"
    WARN_SYMBOL = "\u26A0"
else:
    TICK = "+"
    CROSS = "X"
    WARN_SYMBOL = "!"

SEPARATOR = "=" * 60

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    fix_hint: Optional[str] = None
    critical: bool = True          # False → shown as warning, not failure
    extra_info: list[str] = field(default_factory=list)

# ---------------------------------------------------------------------------
# .env parser (stdlib only)
# ---------------------------------------------------------------------------

def parse_dotenv(path: pathlib.Path) -> dict[str, str]:
    result: dict[str, str] = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if not key or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
                continue
            if len(value) >= 2 and (
                (value[0] == '"' and value[-1] == '"')
                or (value[0] == "'" and value[-1] == "'")
            ):
                value = value[1:-1]
            if value:
                result[key] = value
    return result

# ---------------------------------------------------------------------------
# Environment loader
# ---------------------------------------------------------------------------

def load_env(project_root: pathlib.Path) -> tuple[dict[str, str], set[str]]:
    """Return (merged_env, keys_from_dotenv)."""
    env = dict(os.environ)
    dotenv_keys: set[str] = set()
    dotenv_path = project_root / ".env"
    if dotenv_path.is_file():
        for key, value in parse_dotenv(dotenv_path).items():
            if key not in env:
                env[key] = value
                dotenv_keys.add(key)
    return env, dotenv_keys

# ---------------------------------------------------------------------------
# Command runner
# ---------------------------------------------------------------------------

def run_cmd(cmd: list[str], timeout: int = 10) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
        )
        output = result.stdout.strip() or result.stderr.strip()
        return (result.returncode == 0, output)
    except FileNotFoundError:
        return (False, f"Command not found: {cmd[0]}")
    except subprocess.TimeoutExpired:
        return (False, f"Command timed out: {' '.join(cmd)}")
    except Exception as exc:
        return (False, str(exc))

# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_git() -> CheckResult:
    ok, output = run_cmd(["git", "--version"])
    if ok:
        return CheckResult("Git", True, output)
    return CheckResult(
        "Git", False, output,
        fix_hint="Install Git: https://git-scm.com/install/",
    )


def check_python() -> CheckResult:
    v = sys.version_info
    version_str = f"Python {v.major}.{v.minor}.{v.micro}"
    binary = sys.executable
    if (v.major, v.minor) >= MINIMUM_PYTHON_VERSION:
        return CheckResult("Python", True, f"{version_str} ({binary})")
    return CheckResult(
        "Python", False,
        f"{version_str} ({binary}) — requires >= {MINIMUM_PYTHON_VERSION[0]}.{MINIMUM_PYTHON_VERSION[1]}",
        fix_hint="Install Python 3.11+: https://www.python.org/downloads/",
    )


def check_uv() -> CheckResult:
    ok, output = run_cmd(["uv", "--version"])
    if ok:
        return CheckResult("uv", True, output)
    return CheckResult(
        "uv", False, output,
        fix_hint="Install uv: https://docs.astral.sh/uv/getting-started/installation/",
    )


def check_duckdb() -> CheckResult:
    ok, output = run_cmd(["duckdb", "--version"])
    if ok:
        return CheckResult("DuckDB", True, output)
    return CheckResult(
        "DuckDB", False, output,
        fix_hint="Install DuckDB CLI: https://duckdb.org/install/?environment=cli",
    )


def check_llm_keys(env: dict[str, str], dotenv_keys: set[str]) -> CheckResult:
    found: list[tuple[str, str, str]] = []  # (key, label, source)
    for key, label in LLM_KEY_NAMES:
        val = env.get(key, "").strip()
        if val:
            source = "via .env" if key in dotenv_keys else "via environment"
            found.append((key, label, source))

    if found:
        primary_key, primary_label, primary_source = found[0]
        msg = f"Found: {primary_key} ({primary_source})"
        extras = [f"Also found: {k}" for k, _, _ in found[1:]]
        return CheckResult("LLM API key", True, msg, extra_info=extras)

    return CheckResult(
        "LLM API key", False,
        "No LLM API key found",
        fix_hint=(
            "Set one of: OPENROUTER_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY\n"
            "\n"
            "         Recommended — OpenRouter (works with multiple providers):\n"
            "           Sign up:  https://openrouter.ai/sign-up\n"
            "           API keys: https://openrouter.ai/settings/keys\n"
            "           Credits:  https://openrouter.ai/settings/credits (~$10 recommended)\n"
            "\n"
            "         Set the key in a .env file in the project root, or export it in your shell."
        ),
    )


def check_langfuse_keys(env: dict[str, str], dotenv_keys: set[str]) -> CheckResult:
    present = []
    missing = []
    for key in LANGFUSE_KEY_NAMES:
        val = env.get(key, "").strip()
        if val:
            source = "via .env" if key in dotenv_keys else "via environment"
            present.append((key, source))
        else:
            missing.append(key)

    if not missing:
        sources = ", ".join(f"{k} ({s})" for k, s in present)
        return CheckResult("Langfuse keys", True, f"All set: {sources}", critical=False)

    if present:
        msg = f"Missing: {', '.join(missing)}"
    else:
        msg = "No Langfuse keys found"

    return CheckResult(
        "Langfuse keys", False, msg,
        fix_hint="Set up Langfuse: https://langfuse.com/docs/observability/get-started",
        critical=False,
    )

# ---------------------------------------------------------------------------
# uv sync
# ---------------------------------------------------------------------------

def run_uv_sync(project_root: pathlib.Path) -> CheckResult:
    print(f"\n{BOLD}Installing dependencies ...{RESET}")
    print(f"  Running: uv sync\n", flush=True)
    try:
        result = subprocess.run(
            ["uv", "sync"],
            cwd=project_root,
            timeout=120,
        )
        if result.returncode == 0:
            return CheckResult("uv sync", True, "Dependencies installed successfully")
        return CheckResult(
            "uv sync", False,
            f"uv sync exited with code {result.returncode}",
            fix_hint="Run 'uv sync' manually to see detailed errors.",
        )
    except subprocess.TimeoutExpired:
        return CheckResult(
            "uv sync", False, "uv sync timed out after 120s",
            fix_hint="Run 'uv sync' manually.",
        )
    except Exception as exc:
        return CheckResult(
            "uv sync", False, str(exc),
            fix_hint="Run 'uv sync' manually.",
        )

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_header() -> None:
    print(f"\n{BOLD}{SEPARATOR}")
    print("  Workshop Prerequisite Validator")
    print(f"  Build & Optimise AI Agents That Survive Production")
    print(f"{SEPARATOR}{RESET}\n")


def print_result(result: CheckResult) -> None:
    if result.passed:
        prefix = f"  {GREEN}{TICK} PASS{RESET} "
    elif not result.critical:
        prefix = f"  {YELLOW}{WARN_SYMBOL} WARN{RESET} "
    else:
        prefix = f"  {RED}{CROSS} FAIL{RESET} "

    print(f"{prefix} {result.message}")

    for info in result.extra_info:
        print(f"          {DIM}{info}{RESET}")

    if result.fix_hint and not result.passed:
        for i, line in enumerate(result.fix_hint.split("\n")):
            if i == 0:
                print(f"          {BOLD}\u2192 {line}{RESET}")
            else:
                print(f"          {line}")


def print_summary(results: list[CheckResult]) -> None:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    warnings = sum(1 for r in results if not r.passed and not r.critical)
    failures = sum(1 for r in results if not r.passed and r.critical)

    parts = []
    if warnings:
        parts.append(f"{warnings} warning{'s' if warnings != 1 else ''}")
    if failures:
        parts.append(f"{failures} failure{'s' if failures != 1 else ''}")
    suffix = f" ({', '.join(parts)})" if parts else ""

    print(f"\n{BOLD}{SEPARATOR}")
    print(f"  Summary: {passed} of {total} checks passed{suffix}")
    print(f"{SEPARATOR}{RESET}")

    critical_fails = [r for r in results if not r.passed and r.critical]
    if critical_fails:
        print(f"\n  {RED}{BOLD}Must fix before workshop:{RESET}")
        for r in critical_fails:
            hint = r.fix_hint.split("\n")[0] if r.fix_hint else ""
            print(f"    {RED}{CROSS}{RESET} {r.name}: {hint}")

    warns = [r for r in results if not r.passed and not r.critical]
    if warns:
        print(f"\n  {YELLOW}{BOLD}Warnings (needed for some modules):{RESET}")
        for r in warns:
            hint = r.fix_hint.split("\n")[0] if r.fix_hint else ""
            print(f"    {YELLOW}{WARN_SYMBOL}{RESET} {r.name}: {hint}")

    if not critical_fails and not warns:
        print(f"\n  {GREEN}{BOLD}All checks passed — you're ready for the workshop!{RESET}")

    print()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    project_root = pathlib.Path(__file__).resolve().parent

    print_header()

    # Load environment
    dotenv_path = project_root / ".env"
    if dotenv_path.is_file():
        print(f"  Found .env file: {dotenv_path}\n")
    else:
        print(f"  No .env file found (looked in {project_root})\n")

    env, dotenv_keys = load_env(project_root)

    # Run checks
    results: list[CheckResult] = []
    uv_passed = False

    checks: list[tuple[str, object]] = [
        ("Git", check_git),
        ("Python", check_python),
        ("uv", check_uv),
        ("DuckDB", check_duckdb),
        ("LLM API key", lambda: check_llm_keys(env, dotenv_keys)),
        ("Langfuse keys", lambda: check_langfuse_keys(env, dotenv_keys)),
    ]

    for label, check_fn in checks:
        print(f"Checking {label} ...")
        result = check_fn()
        results.append(result)
        print_result(result)
        print()
        if label == "uv" and result.passed:
            uv_passed = True

    # Summary of checks
    print_summary(results)

    # Run uv sync if uv is available
    if uv_passed:
        sync_result = run_uv_sync(project_root)
        print_result(sync_result)
        print()
    else:
        print(f"  {DIM}Skipping dependency install (uv not available){RESET}\n")

    critical_failures = [r for r in results if not r.passed and r.critical]
    return 1 if critical_failures else 0


if __name__ == "__main__":
    sys.exit(main())
