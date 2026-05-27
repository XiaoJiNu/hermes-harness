import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "hermes_codex_runtime_recovery.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("hermes_codex_runtime_recovery", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_normalize_proxy_url_rewrites_socks_scheme():
    mod = _load_module()
    assert mod.normalize_proxy_url("socks://127.0.0.1:7897/") == "socks5://127.0.0.1:7897/"
    assert mod.normalize_proxy_url("http://127.0.0.1:7897") == "http://127.0.0.1:7897"


def test_upsert_managed_block_replaces_existing_content():
    mod = _load_module()
    old = (
        "alpha\n"
        f"{mod.PROFILE_BLOCK_START}\n"
        "old\n"
        f"{mod.PROFILE_BLOCK_END}\n"
    )
    new_block = (
        f"{mod.PROFILE_BLOCK_START}\n"
        "new\n"
        f"{mod.PROFILE_BLOCK_END}\n"
    )
    updated = mod.upsert_managed_block(old, new_block)
    assert updated.count(mod.PROFILE_BLOCK_START) == 1
    assert "new\n" in updated
    assert "old\n" not in updated


def test_parse_nested_value_reads_delegation_settings():
    mod = _load_module()
    text = (
        "model:\n"
        "  provider: openai-codex\n"
        "delegation:\n"
        "  model: gpt-5.4-mini\n"
        "  reasoning_effort: low\n"
        "  max_iterations: 24\n"
    )
    assert mod.parse_nested_value(text, "model", "provider") == "openai-codex"
    assert mod.parse_nested_value(text, "delegation", "model") == "gpt-5.4-mini"
    assert mod.parse_nested_value(text, "delegation", "reasoning_effort") == "low"
    assert mod.parse_nested_value(text, "delegation", "max_iterations") == "24"


def test_resolve_proxy_values_uses_proxy_port_when_env_missing():
    mod = _load_module()

    class Args:
        http_proxy = ""
        https_proxy = ""
        all_proxy = ""
        proxy_port = 7897
        no_proxy = "localhost,127.0.0.1,::1"

    resolved = mod.resolve_proxy_values(Args(), {})
    assert resolved["HTTP_PROXY"] == "http://127.0.0.1:7897"
    assert resolved["HTTPS_PROXY"] == "http://127.0.0.1:7897"
    assert resolved["ALL_PROXY"] == "socks5://127.0.0.1:7897"
    assert resolved["NO_PROXY"] == "localhost,127.0.0.1,::1"


def test_check_source_timeout_fix_accepts_legacy_and_current_markers(tmp_path):
    mod = _load_module()

    legacy_root = tmp_path / "legacy"
    legacy_root.mkdir()
    (legacy_root / "run_agent.py").write_text("_codex_stream_timeout\n", encoding="utf-8")
    assert mod.check_source_timeout_fix(legacy_root) is True

    current_root = tmp_path / "current"
    current_root.mkdir()
    (current_root / "run_agent.py").write_text(
        "request_timeout_seconds\n"
        "get_provider_request_timeout\n"
        "_create_request_openai_client\n"
        "_run_codex_stream\n",
        encoding="utf-8",
    )
    assert mod.check_source_timeout_fix(current_root) is True

    missing_root = tmp_path / "missing"
    missing_root.mkdir()
    (missing_root / "run_agent.py").write_text("_run_codex_stream\n", encoding="utf-8")
    assert mod.check_source_timeout_fix(missing_root) is False


def test_check_source_null_output_fix_requires_runtime_and_auxiliary_markers(tmp_path):
    mod = _load_module()

    fixed_root = tmp_path / "fixed"
    (fixed_root / "agent").mkdir(parents=True)
    (fixed_root / "agent" / "codex_runtime.py").write_text(
        "_responses_null_output_iterable_error\n"
        "_codex_backfilled_response\n"
        "response.output=None\n",
        encoding="utf-8",
    )
    (fixed_root / "agent" / "auxiliary_client.py").write_text(
        "_responses_null_output_iterable_error\n"
        "_responses_backfilled_response\n",
        encoding="utf-8",
    )
    assert mod.check_source_null_output_fix(fixed_root) is True

    missing_aux_root = tmp_path / "missing_aux"
    (missing_aux_root / "agent").mkdir(parents=True)
    (missing_aux_root / "agent" / "codex_runtime.py").write_text(
        "_responses_null_output_iterable_error\n"
        "_codex_backfilled_response\n"
        "response.output=None\n",
        encoding="utf-8",
    )
    assert mod.check_source_null_output_fix(missing_aux_root) is False
