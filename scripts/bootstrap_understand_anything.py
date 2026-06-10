#!/usr/bin/env python3
"""Bootstrap Understand-Anything skills for Hermes without vendoring the repo.

This script keeps hermes-harness as the method/control-plane source of truth and
installs the external Understand-Anything checkout under the user's home dir.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

DEFAULT_REPO_URL = "git@github.com:Lum1104/Understand-Anything.git"
DEFAULT_CHECKOUT = Path.home() / ".understand-anything" / "repo"
DEFAULT_PLUGIN_LINK = Path.home() / ".understand-anything-plugin"
SKILLS_RELATIVE_PATH = "understand-anything-plugin/skills"
DEFAULT_HERMES_SKILLS_RELATIVE = ".hermes/skills/understand-anything"
CORE_BUILD_COMMAND_TEXT = "pnpm --filter @understand-anything/core build"
CORE_TEST_COMMAND_TEXT = "pnpm --filter @understand-anything/core test"


class BootstrapError(RuntimeError):
    """Raised when the bootstrap cannot proceed safely."""


def display_path(path: Path) -> str:
    try:
        return str(path.expanduser().absolute())
    except OSError:
        return str(path.expanduser())


def run(command: list[str], cwd: Path | None = None, dry_run: bool = False, check: bool = True) -> subprocess.CompletedProcess[str]:
    prefix = f"[{display_path(cwd)}] " if cwd else ""
    print(prefix + "$ " + " ".join(command))
    if dry_run:
        return subprocess.CompletedProcess(command, 0, "", "")
    return subprocess.run(command, cwd=cwd, check=check, text=True)


def require_commands(commands: Iterable[str]) -> None:
    missing = [command for command in commands if shutil.which(command) is None]
    if missing:
        raise BootstrapError(f"missing required command(s): {', '.join(missing)}")


def path_from_cli(value: str) -> Path:
    return Path(value).expanduser()


def hermes_home_from_args(value: str | None) -> Path:
    if value:
        return path_from_cli(value)
    return Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))).expanduser()


def ensure_checkout(args: argparse.Namespace) -> None:
    checkout_dir: Path = args.checkout_dir
    if (checkout_dir / ".git").is_dir():
        print(f"Using existing Understand-Anything checkout: {display_path(checkout_dir)}")
        run(["git", "remote", "set-url", "origin", args.repo_url], cwd=checkout_dir, dry_run=args.dry_run)
        if args.update or args.revision:
            if not args.allow_dirty and not args.dry_run:
                status = subprocess.check_output(["git", "status", "--short"], cwd=checkout_dir, text=True)
                if status.strip():
                    raise BootstrapError(
                        "checkout has uncommitted changes; commit/stash them or rerun with --allow-dirty"
                    )
            run(["git", "fetch", "--all", "--prune"], cwd=checkout_dir, dry_run=args.dry_run)
            if args.update and not args.revision:
                run(["git", "pull", "--ff-only"], cwd=checkout_dir, dry_run=args.dry_run)
    elif checkout_dir.exists() and any(checkout_dir.iterdir()):
        raise BootstrapError(f"checkout directory exists and is not an Understand-Anything git checkout: {checkout_dir}")
    else:
        if not args.dry_run:
            checkout_dir.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", args.repo_url, str(checkout_dir)], dry_run=args.dry_run)

    if args.revision:
        run(["git", "checkout", args.revision], cwd=checkout_dir, dry_run=args.dry_run)


def replace_symlink(link: Path, target: Path, force: bool, dry_run: bool) -> None:
    if link.is_symlink():
        current = link.readlink()
        if current == target:
            print(f"OK symlink already exists: {display_path(link)} -> {display_path(target)}")
            return
        if not force:
            raise BootstrapError(f"symlink exists but points elsewhere: {link} -> {current}; rerun with --force")
        print(f"Replacing symlink: {display_path(link)}")
        if not dry_run:
            link.unlink()
    elif link.exists():
        raise BootstrapError(f"path exists and is not a symlink: {link}; move it away or handle manually")

    if not dry_run:
        link.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(target, link)
    print(f"Linked: {display_path(link)} -> {display_path(target)}")


def link_hermes_skills(args: argparse.Namespace) -> None:
    checkout_dir: Path = args.checkout_dir
    plugin_root = checkout_dir / "understand-anything-plugin"
    skills_src = plugin_root / "skills"
    if not args.dry_run and not skills_src.is_dir():
        raise BootstrapError(f"Understand-Anything skills directory not found: {skills_src}")

    skills_link = args.hermes_home / "skills" / "understand-anything"
    replace_symlink(skills_link, skills_src, force=args.force, dry_run=args.dry_run)
    replace_symlink(args.plugin_link, plugin_root, force=args.force, dry_run=args.dry_run)


def run_readiness_checks(args: argparse.Namespace) -> None:
    if args.skip_build:
        print("Skipping pnpm build/test checks (--skip-build).")
        return

    require_commands(["pnpm"])
    checkout_dir: Path = args.checkout_dir
    if args.allow_pnpm_install_fallback:
        frozen = run(["pnpm", "install", "--frozen-lockfile"], cwd=checkout_dir, dry_run=args.dry_run, check=False)
        if frozen.returncode != 0:
            run(["pnpm", "install"], cwd=checkout_dir, dry_run=args.dry_run)
    else:
        run(["pnpm", "install", "--frozen-lockfile"], cwd=checkout_dir, dry_run=args.dry_run)
    run(["pnpm", "--filter", "@understand-anything/core", "build"], cwd=checkout_dir, dry_run=args.dry_run)
    if not args.skip_tests:
        run(["pnpm", "--filter", "@understand-anything/core", "test"], cwd=checkout_dir, dry_run=args.dry_run)


def print_summary(args: argparse.Namespace) -> None:
    skills_link = args.hermes_home / "skills" / "understand-anything"
    print("\nUnderstand-Anything Hermes bootstrap complete.")
    print(f"Checkout: {display_path(args.checkout_dir)}")
    print(f"Universal plugin link: {display_path(args.plugin_link)}")
    print(f"Hermes skills link: {display_path(skills_link)}")
    print("\nVerify in a fresh Hermes session with:")
    print("  hermes skills list | grep -i understand")
    print("  hermes -s understand chat -q 'Confirm the understand skill is loadable'")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install or refresh Understand-Anything skills for Hermes from an external checkout."
    )
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL, help="Understand-Anything git remote URL")
    parser.add_argument("--checkout-dir", type=path_from_cli, default=DEFAULT_CHECKOUT, help="local checkout path")
    parser.add_argument("--hermes-home", type=path_from_cli, default=None, help="Hermes home; defaults to $HERMES_HOME or ~/.hermes")
    parser.add_argument("--plugin-link", type=path_from_cli, default=DEFAULT_PLUGIN_LINK, help="universal plugin symlink path")
    parser.add_argument("--revision", help="optional git branch, tag, or commit to checkout after clone/fetch")
    parser.add_argument("--update", action="store_true", help="fetch/pull an existing checkout before linking")
    parser.add_argument("--allow-dirty", action="store_true", help="allow updating/checking out when the checkout has local changes")
    parser.add_argument("--force", action="store_true", help="replace existing mismatched symlinks")
    parser.add_argument("--skip-build", action="store_true", help="skip pnpm install/build/test readiness checks")
    parser.add_argument("--skip-tests", action="store_true", help="run pnpm install/build but skip core tests")
    parser.add_argument(
        "--allow-pnpm-install-fallback",
        action="store_true",
        help="if pnpm install --frozen-lockfile fails, retry with plain pnpm install",
    )
    parser.add_argument("--dry-run", action="store_true", help="print actions without modifying files")
    args = parser.parse_args(argv)
    args.hermes_home = hermes_home_from_args(str(args.hermes_home) if args.hermes_home else None)
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        require_commands(["git"])
        ensure_checkout(args)
        link_hermes_skills(args)
        run_readiness_checks(args)
        print_summary(args)
        return 0
    except (BootstrapError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
