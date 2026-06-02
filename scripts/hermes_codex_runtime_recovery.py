#!/usr/bin/env python3
"""Diagnose and remediate common Hermes + Codex runtime instability locally.

Default mode is check-only. Use ``--apply`` to write the recommended
delegation settings through ``hermes config set``. Use ``--apply-profile`` to
persist proxy exports into the selected shell profile.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional


RECOMMENDED_DELEGATION = {
    "model": "gpt-5.4-mini",
    "reasoning_effort": "low",
    "max_iterations": "24",
}

PROXY_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "NO_PROXY",
)

DEFAULT_NO_PROXY = (
    "localhost,127.0.0.1,::1,"
    "192.168.15.143,192.168.15.0/24,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12"
)

PROFILE_BLOCK_START = "# >>> Hermes Codex Recovery >>>"
PROFILE_BLOCK_END = "# <<< Hermes Codex Recovery <<<"

DEFAULT_SOURCE_ROOT_CANDIDATES = [
    Path("~/.hermes/hermes-agent").expanduser(),
    Path("~/yr/code/harness-engineering-all/hermes-agent").expanduser(),
    Path("~/code/harness-engineering-all/hermes-agent").expanduser(),
]


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str


def normalize_proxy_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        return None
    value = str(url).strip()
    if not value:
        return value
    if value.lower().startswith("socks://"):
        return "socks5://" + value[len("socks://") :]
    return value


def shell_profile_for(shell_path: str) -> Path:
    shell_name = Path(shell_path or "").name
    if shell_name == "zsh":
        return Path("~/.zshrc").expanduser()
    return Path("~/.bashrc").expanduser()


def detect_source_root(explicit: Optional[str]) -> Optional[Path]:
    if explicit:
        path = Path(explicit).expanduser()
        return path if path.exists() else path
    env_root = os.getenv("HERMES_AGENT_SOURCE_ROOT", "").strip()
    if env_root:
        path = Path(env_root).expanduser()
        return path if path.exists() else path
    for candidate in DEFAULT_SOURCE_ROOT_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def parse_nested_value(text: str, section: str, key: str) -> Optional[str]:
    pattern = rf"(?ms)^{re.escape(section)}:\n(?P<body>(?:^[ \t]+.*\n)*)"
    match = re.search(pattern, text)
    if not match:
        return None
    body = match.group("body")
    key_match = re.search(rf"(?m)^[ \t]+{re.escape(key)}:\s*(.+?)\s*$", body)
    if not key_match:
        return None
    raw = key_match.group(1).strip()
    return raw.strip("'\"")


def config_observations(config_path: Path) -> Dict[str, Optional[str]]:
    if not config_path.exists():
        return {}
    text = config_path.read_text(encoding="utf-8")
    return {
        "model_provider": parse_nested_value(text, "model", "provider"),
        "model_base_url": parse_nested_value(text, "model", "base_url"),
        "delegation_model": parse_nested_value(text, "delegation", "model"),
        "delegation_reasoning_effort": parse_nested_value(text, "delegation", "reasoning_effort"),
        "delegation_max_iterations": parse_nested_value(text, "delegation", "max_iterations"),
    }


def current_proxy_env() -> Dict[str, Optional[str]]:
    result: Dict[str, Optional[str]] = {}
    for key in PROXY_KEYS:
        value = os.getenv(key)
        result[key] = normalize_proxy_url(value)
    return result


def resolve_proxy_values(args: argparse.Namespace, env: Dict[str, Optional[str]]) -> Dict[str, str]:
    http_proxy = normalize_proxy_url(args.http_proxy) or env.get("HTTP_PROXY") or env.get("http_proxy")
    https_proxy = normalize_proxy_url(args.https_proxy) or env.get("HTTPS_PROXY") or env.get("https_proxy")
    all_proxy = normalize_proxy_url(args.all_proxy) or env.get("ALL_PROXY") or env.get("all_proxy")

    if args.proxy_port:
        port = str(args.proxy_port)
        http_proxy = http_proxy or f"http://127.0.0.1:{port}"
        https_proxy = https_proxy or f"http://127.0.0.1:{port}"
        all_proxy = all_proxy or f"socks5://127.0.0.1:{port}"

    values: Dict[str, str] = {}
    if http_proxy:
        values["HTTP_PROXY"] = http_proxy
    if https_proxy:
        values["HTTPS_PROXY"] = https_proxy
    if all_proxy:
        values["ALL_PROXY"] = all_proxy
    values["NO_PROXY"] = args.no_proxy
    return values


def render_profile_block(proxy_values: Dict[str, str]) -> str:
    lines = [
        PROFILE_BLOCK_START,
        "# Hermes / Codex proxy — managed by scripts/hermes_codex_runtime_recovery.py",
    ]
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"):
        value = proxy_values.get(key)
        if value:
            lines.append(f'export {key}="{value}"')
            lines.append(f'export {key.lower()}="{value}"')
    lines.append(PROFILE_BLOCK_END)
    return "\n".join(lines) + "\n"


def upsert_managed_block(existing: str, block: str) -> str:
    pattern = re.compile(
        rf"(?ms)^{re.escape(PROFILE_BLOCK_START)}\n.*?^{re.escape(PROFILE_BLOCK_END)}\n?"
    )
    if pattern.search(existing):
        return pattern.sub(block, existing)
    if existing and not existing.endswith("\n"):
        existing += "\n"
    if existing and not existing.endswith("\n\n"):
        existing += "\n"
    return existing + block


def read_hermes_launcher(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    try:
        return Path(path).read_text(encoding="utf-8").splitlines()[0]
    except Exception:
        return None


def run_subprocess(cmd: List[str], *, cwd: Optional[Path] = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )


def check_live_install_imports() -> Dict[str, Optional[str]]:
    venv_python = Path("~/.hermes/hermes-agent/venv/bin/python").expanduser()
    if not venv_python.exists():
        return {"python": None, "hermes_cli": None, "hermes_constants": None}
    probe = run_subprocess(
        [
            str(venv_python),
            "-c",
            (
                "import inspect, json, hermes_cli, hermes_constants; "
                "print(json.dumps({'hermes_cli': inspect.getfile(hermes_cli), "
                "'hermes_constants': inspect.getfile(hermes_constants)}))"
            ),
        ]
    )
    if probe.returncode != 0:
        return {"python": str(venv_python), "hermes_cli": None, "hermes_constants": None}
    try:
        data = json.loads(probe.stdout.strip())
    except json.JSONDecodeError:
        data = {"hermes_cli": None, "hermes_constants": None}
    data["python"] = str(venv_python)
    return data


def check_source_timeout_fix(source_root: Optional[Path]) -> Optional[bool]:
    if source_root is None:
        return None
    run_agent = source_root / "run_agent.py"
    if not run_agent.exists():
        return None
    text = run_agent.read_text(encoding="utf-8")
    # Older local fix used a dedicated _codex_stream_timeout helper.  Hermes
    # v0.11+ moved timeout handling into the general provider/model
    # request_timeout_seconds path and rebuilt request clients, so accept either
    # marker as evidence that the Responses/Codex path is no longer relying only
    # on opaque SDK defaults.
    legacy_marker = "_codex_stream_timeout" in text
    current_marker = (
        "request_timeout_seconds" in text
        and "get_provider_request_timeout" in text
        and "_create_request_openai_client" in text
        and "_run_codex_stream" in text
    )
    return legacy_marker or current_marker


def check_source_null_output_fix(source_root: Optional[Path]) -> Optional[bool]:
    if source_root is None:
        return None
    codex_runtime = source_root / "agent" / "codex_runtime.py"
    auxiliary_client = source_root / "agent" / "auxiliary_client.py"
    if not codex_runtime.exists():
        return None
    runtime_text = codex_runtime.read_text(encoding="utf-8")
    auxiliary_text = auxiliary_client.read_text(encoding="utf-8") if auxiliary_client.exists() else ""
    # Older fix shape: detect and backfill the SDK helper's typed response
    # reconstruction when ``response.output=None`` crashes iteration.
    legacy_runtime_marker = (
        "_responses_null_output_iterable_error" in runtime_text
        and "_codex_backfilled_response" in runtime_text
        and "response.output=None" in runtime_text
    )
    legacy_auxiliary_marker = (
        "_responses_null_output_iterable_error" in auxiliary_text
        and "_responses_backfilled_response" in auxiliary_text
    )

    # Hermes v0.15.1+ fix shape: avoid the SDK helper entirely.  The runtime
    # consumes raw ``responses.create(stream=True)`` events and reconstructs
    # content from ``response.output_item.done``, so it never depends on the
    # terminal ``response.completed.response.output`` field that can be null.
    raw_event_runtime_marker = (
        "_consume_codex_event_stream" in runtime_text
        and "responses.create" in runtime_text
        and "response.output_item.done" in runtime_text
        and "response.completed.response.output" in runtime_text
        and "TypeError: 'NoneType' object is not iterable" in runtime_text
    )
    raw_event_auxiliary_marker = (
        "_consume_codex_event_stream" in auxiliary_text
        and "responses.create" in auxiliary_text
        and "response.output_item.done" in auxiliary_text
        and "TypeError: 'NoneType' object is not iterable" in auxiliary_text
    )

    return (legacy_runtime_marker and legacy_auxiliary_marker) or (
        raw_event_runtime_marker and raw_event_auxiliary_marker
    )


def apply_delegation_settings(hermes_bin: str) -> List[str]:
    actions: List[str] = []
    for key, value in RECOMMENDED_DELEGATION.items():
        result = run_subprocess([hermes_bin, "config", "set", f"delegation.{key}", value])
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"failed to set delegation.{key}")
        actions.append(f"set delegation.{key}={value}")
    return actions


def apply_profile(profile_path: Path, proxy_values: Dict[str, str]) -> str:
    existing = profile_path.read_text(encoding="utf-8") if profile_path.exists() else ""
    new_text = upsert_managed_block(existing, render_profile_block(proxy_values))
    profile_path.write_text(new_text, encoding="utf-8")
    return f"updated {profile_path}"


def repoint_live_install(source_root: Path) -> str:
    script_path = source_root / "scripts" / "repoint_live_install.sh"
    if not script_path.exists():
        raise RuntimeError(f"repoint script not found: {script_path}")
    result = run_subprocess(["bash", str(script_path)], cwd=source_root)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "repoint failed")
    return "repointed live install"


def run_smoke_test(hermes_bin: str) -> str:
    result = run_subprocess([hermes_bin, "chat", "-q", "请只回复：ok"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "smoke test failed")
    if "ok" not in result.stdout.lower():
        raise RuntimeError(f"unexpected smoke test output: {result.stdout.strip()}")
    return "smoke test passed"


def build_checks(args: argparse.Namespace) -> Dict[str, object]:
    hermes_bin = shutil.which("hermes")
    config_path = Path(args.config_path).expanduser()
    profile_path = Path(args.profile).expanduser() if args.profile else shell_profile_for(os.getenv("SHELL", "bash"))
    source_root = detect_source_root(args.hermes_agent_root)
    config = config_observations(config_path)
    env = current_proxy_env()
    proxy_values = resolve_proxy_values(args, env)
    live_imports = check_live_install_imports()
    timeout_fix = check_source_timeout_fix(source_root)
    null_output_fix = check_source_null_output_fix(source_root)

    checks: List[CheckResult] = []
    warnings: List[str] = []

    provider = config.get("model_provider")
    base_url = config.get("model_base_url")
    if provider == "openai-codex":
        checks.append(CheckResult("main_provider", "ok", f"main provider is {provider}"))
    else:
        checks.append(CheckResult("main_provider", "warn", f"main provider is {provider or 'unset'}"))

    if base_url and "chatgpt.com/backend-api/codex" in base_url:
        checks.append(CheckResult("main_base_url", "ok", base_url))
    else:
        checks.append(CheckResult("main_base_url", "warn", base_url or "unset"))

    if env.get("HTTPS_PROXY") or env.get("https_proxy"):
        checks.append(CheckResult("proxy_env", "ok", "HTTPS_PROXY present in current environment"))
    else:
        checks.append(CheckResult("proxy_env", "warn", "HTTPS_PROXY missing in current environment"))
        warnings.append("current shell has no HTTPS_PROXY")

    if proxy_values.get("ALL_PROXY", "").startswith("socks5://"):
        checks.append(CheckResult("proxy_scheme", "ok", proxy_values["ALL_PROXY"]))
    else:
        checks.append(CheckResult("proxy_scheme", "warn", proxy_values.get("ALL_PROXY", "unset")))

    delegation_ok = (
        config.get("delegation_model") == RECOMMENDED_DELEGATION["model"]
        and config.get("delegation_reasoning_effort") == RECOMMENDED_DELEGATION["reasoning_effort"]
        and config.get("delegation_max_iterations") == RECOMMENDED_DELEGATION["max_iterations"]
    )
    if delegation_ok:
        checks.append(CheckResult("delegation_settings", "ok", "delegation settings already match recommended stable values"))
    else:
        detail = (
            f"model={config.get('delegation_model') or 'unset'}, "
            f"reasoning_effort={config.get('delegation_reasoning_effort') or 'unset'}, "
            f"max_iterations={config.get('delegation_max_iterations') or 'unset'}"
        )
        checks.append(CheckResult("delegation_settings", "warn", detail))
        warnings.append("delegation settings are not using the recommended stable values")

    launcher = read_hermes_launcher(hermes_bin)
    if hermes_bin:
        checks.append(CheckResult("hermes_binary", "ok", hermes_bin))
    else:
        checks.append(CheckResult("hermes_binary", "error", "hermes not found on PATH"))
        warnings.append("hermes CLI is not available")

    if launcher:
        checks.append(CheckResult("hermes_launcher", "ok", launcher))

    live_cli = live_imports.get("hermes_cli")
    if live_cli:
        checks.append(CheckResult("live_import", "ok", live_cli))
    else:
        checks.append(CheckResult("live_import", "warn", "could not inspect live hermes_cli import path"))

    if timeout_fix is True:
        checks.append(CheckResult("codex_timeout_fix", "ok", "source repo contains Codex/Responses timeout handling"))
    elif timeout_fix is False:
        checks.append(CheckResult("codex_timeout_fix", "warn", "source repo does not contain recognized Codex/Responses timeout handling"))
        warnings.append("source repo appears to be missing recognized Codex/Responses timeout handling")
    else:
        checks.append(CheckResult("codex_timeout_fix", "warn", "no Hermes source root detected"))

    if null_output_fix is True:
        checks.append(CheckResult("codex_null_output_fix", "ok", "source repo contains Codex null-output stream recovery"))
    elif null_output_fix is False:
        checks.append(CheckResult("codex_null_output_fix", "warn", "source repo does not contain recognized Codex null-output stream recovery"))
        warnings.append("source repo appears to be missing Codex null-output stream recovery")
    else:
        checks.append(CheckResult("codex_null_output_fix", "warn", "no Hermes source root detected"))

    if source_root is not None:
        checks.append(CheckResult("hermes_agent_root", "ok", str(source_root)))

    recommendations = [
        "Run this script with --apply to set stable delegation defaults.",
        "Use --apply-profile with --proxy-port or explicit proxy URLs to persist proxy exports.",
        "Use --repoint-live-install when the live Hermes install is not aligned to the intended source tree.",
    ]
    if warnings:
        recommendations.insert(0, "Detected runtime risks: " + "; ".join(warnings))

    return {
        "hermes_bin": hermes_bin,
        "config_path": str(config_path),
        "profile_path": str(profile_path),
        "source_root": str(source_root) if source_root else None,
        "checks": [asdict(item) for item in checks],
        "recommendations": recommendations,
        "proxy_values": proxy_values,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diagnose and remediate common Hermes + Codex runtime instability."
    )
    parser.add_argument("--apply", action="store_true", help="Apply recommended delegation settings via hermes config set.")
    parser.add_argument("--apply-profile", action="store_true", help="Persist proxy exports into the shell profile.")
    parser.add_argument("--repoint-live-install", action="store_true", help="Run scripts/repoint_live_install.sh in the detected Hermes source root.")
    parser.add_argument("--smoke-test", action="store_true", help="Run a minimal hermes chat smoke test after apply.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--profile", default="", help="Shell profile to update. Defaults to ~/.bashrc or ~/.zshrc based on $SHELL.")
    parser.add_argument("--config-path", default="~/.hermes/config.yaml", help="Hermes config path to inspect.")
    parser.add_argument("--proxy-port", type=int, default=0, help="Proxy port used to synthesize HTTP/HTTPS/ALL proxy URLs when env vars are absent.")
    parser.add_argument("--http-proxy", default="", help="Explicit HTTP_PROXY value for profile writes.")
    parser.add_argument("--https-proxy", default="", help="Explicit HTTPS_PROXY value for profile writes.")
    parser.add_argument("--all-proxy", default="", help="Explicit ALL_PROXY value for profile writes.")
    parser.add_argument("--no-proxy", default=DEFAULT_NO_PROXY, help="NO_PROXY value for profile writes.")
    parser.add_argument("--hermes-agent-root", default="", help="Path to the Hermes source repo for repoint checks.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_checks(args)
    actions: List[str] = []

    try:
        if args.apply:
            hermes_bin = report.get("hermes_bin")
            if not hermes_bin:
                raise RuntimeError("cannot apply delegation settings because hermes is not on PATH")
            actions.extend(apply_delegation_settings(str(hermes_bin)))

        if args.apply_profile:
            proxy_values = report.get("proxy_values", {})
            if not isinstance(proxy_values, dict) or not proxy_values.get("HTTP_PROXY") or not proxy_values.get("HTTPS_PROXY") or not proxy_values.get("ALL_PROXY"):
                raise RuntimeError("cannot write profile block because proxy values are incomplete; pass --proxy-port or explicit proxy URLs")
            actions.append(apply_profile(Path(report["profile_path"]), proxy_values))

        if args.repoint_live_install:
            source_root = report.get("source_root")
            if not source_root:
                raise RuntimeError("cannot repoint live install because no Hermes source root was detected")
            actions.append(repoint_live_install(Path(source_root)))

        if args.smoke_test:
            hermes_bin = report.get("hermes_bin")
            if not hermes_bin:
                raise RuntimeError("cannot run smoke test because hermes is not on PATH")
            actions.append(run_smoke_test(str(hermes_bin)))
    except Exception as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc), "report": report, "actions": actions}, ensure_ascii=False, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"ok": True, "report": report, "actions": actions}, ensure_ascii=False, indent=2))
        return 0

    print("Hermes + Codex Runtime Recovery")
    print(f"- config:  {report['config_path']}")
    print(f"- profile: {report['profile_path']}")
    if report.get("source_root"):
        print(f"- source:  {report['source_root']}")
    print("")
    for item in report["checks"]:
        status = item["status"].upper()
        print(f"[{status}] {item['name']}: {item['detail']}")
    if actions:
        print("")
        print("Actions applied:")
        for action in actions:
            print(f"- {action}")
    print("")
    print("Recommendations:")
    for recommendation in report["recommendations"]:
        print(f"- {recommendation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
