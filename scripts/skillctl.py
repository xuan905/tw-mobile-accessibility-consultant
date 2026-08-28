#!/usr/bin/env python3
"""Local CLI for organizing and validating Manus-style skills."""
from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_DIRS = ("scripts", "references", "templates")
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDED_FILES = {"README.md", "CHANGELOG.md"}


@dataclass
class SkillInfo:
    path: str
    name: str | None
    description: str | None
    status: str
    errors: list[str]
    resources: dict[str, int]
    body_lines: int


def discover_skills(path: Path) -> list[Path]:
    path = path.expanduser().resolve()
    if path.is_file() and path.name == "SKILL.md":
        return [path.parent]
    if path.is_dir() and (path / "SKILL.md").is_file():
        return [path]
    if not path.exists():
        return []
    return sorted({p.parent for p in path.rglob("SKILL.md") if not any(part in EXCLUDED_PARTS for part in p.parts)})


def parse_frontmatter(skill_file: Path) -> tuple[dict[str, str], str, list[str]]:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []
    if not lines or lines[0].strip() != "---":
        return {}, text, ["SKILL.md 必須以 YAML frontmatter 開始（---）。"]
    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return {}, text, ["YAML frontmatter 缺少結束標記（---）。"]
    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"frontmatter 無法解析：{line}")
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip().strip("\"'")
        if not key or not value:
            errors.append(f"frontmatter 欄位不可為空：{line}")
        else:
            metadata[key] = value
    return metadata, "\n".join(lines[end + 1 :]).strip(), errors


def inspect_skill(skill_dir: Path, strict_package: bool = False) -> SkillInfo:
    skill_dir = skill_dir.resolve()
    skill_file = skill_dir / "SKILL.md"
    errors: list[str] = []
    metadata: dict[str, str] = {}
    body = ""
    if not skill_file.is_file():
        errors.append("缺少 SKILL.md。")
    else:
        metadata, body, errors = parse_frontmatter(skill_file)
    name = metadata.get("name")
    description = metadata.get("description")
    if not name:
        errors.append("frontmatter 缺少 name。")
    elif not NAME_RE.fullmatch(name):
        errors.append("name 必須是小寫 kebab-case，例如 accessibility-audit。")
    if not description:
        errors.append("frontmatter 缺少 description。")
    if skill_file.is_file() and len(skill_file.read_text(encoding="utf-8").splitlines()) > 500:
        errors.append("SKILL.md 不應超過 500 行。")
    if skill_file.is_file() and not body:
        errors.append("SKILL.md body 不可為空。")
    if strict_package:
        for forbidden in ("README.md", "CHANGELOG.md"):
            if (skill_dir / forbidden).exists():
                errors.append(f"Skill package 不應包含 {forbidden}；請將使用者文件移到 repository 文件區。")
    resources = {directory: len(list((skill_dir / directory).rglob("*") if (skill_dir / directory).is_dir() else [])) for directory in REQUIRED_DIRS}
    return SkillInfo(str(skill_dir), name, description, "valid" if not errors else "invalid", errors, resources, len(body.splitlines()))


def print_result(value: object, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, ensure_ascii=False, indent=2))
    else:
        print(value)


def cmd_validate(args: argparse.Namespace) -> int:
    skills = [inspect_skill(p, args.strict_package) for root in discover_skills(Path(args.path)) for p in [root]]
    if not skills:
        print(f"找不到 Skill：{args.path}", file=sys.stderr)
        return 2
    payload = {"valid": all(item.status == "valid" for item in skills), "skills": [asdict(item) for item in skills]}
    if args.json:
        print_result(payload, True)
    else:
        for item in skills:
            print(f"{item.status.upper():7} {item.path}")
            for error in item.errors:
                print(f"  - {error}")
    return 0 if payload["valid"] else 1


def cmd_inventory(args: argparse.Namespace) -> int:
    skills = [asdict(inspect_skill(p)) for p in discover_skills(Path(args.path))]
    payload = {"root": str(Path(args.path).expanduser().resolve()), "count": len(skills), "skills": skills}
    if args.json:
        print_result(payload, True)
    else:
        print(f"Skills: {len(skills)}")
        for item in skills:
            print(f"{item['status'].upper():7} {item['name'] or '(unnamed)':32} {item['path']}")
    return 0 if skills else 2


def cmd_init(args: argparse.Namespace) -> int:
    destination = Path(args.output).expanduser().resolve() / args.name
    if destination.exists() and any(destination.iterdir()):
        print(f"目標目錄非空：{destination}", file=sys.stderr)
        return 2
    destination.mkdir(parents=True, exist_ok=True)
    for directory in REQUIRED_DIRS:
        (destination / directory).mkdir(exist_ok=True)
    skill_md = destination / "SKILL.md"
    skill_md.write_text(textwrap.dedent(f"""\
        ---
        name: {args.name}
        description: Describe what this skill does and when to use it.
        ---

        # {args.name}

        Write concise, imperative instructions for the agent here.
        """), encoding="utf-8")
    print(f"Created {destination}")
    return 0


def cmd_package(args: argparse.Namespace) -> int:
    roots = discover_skills(Path(args.path))
    if len(roots) != 1:
        print("package 必須指向單一 Skill 目錄或 SKILL.md。", file=sys.stderr)
        return 2
    root = roots[0]
    result = Path(args.output).expanduser().resolve()
    result.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(result, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(root.rglob("*")):
            if not file.is_file() or file.name in EXCLUDED_FILES or any(part in EXCLUDED_PARTS for part in file.relative_to(root).parts):
                continue
            archive.write(file, Path(root.name) / file.relative_to(root))
    print(f"Packaged {root.name} -> {result}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillctl", description="Organize and validate local Skill packages.")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="Validate one Skill or a directory of Skills.")
    validate.add_argument("path")
    validate.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    validate.add_argument("--strict-package", action="store_true", help="Reject repository-only files inside a distributable Skill package.")
    validate.set_defaults(func=cmd_validate)
    inventory = sub.add_parser("inventory", help="List Skills under a directory.")
    inventory.add_argument("path")
    inventory.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    inventory.set_defaults(func=cmd_inventory)
    init = sub.add_parser("init", help="Create a new Skill skeleton.")
    init.add_argument("name")
    init.add_argument("--output", default=".")
    init.set_defaults(func=cmd_init)
    package = sub.add_parser("package", help="Create a ZIP package for one Skill.")
    package.add_argument("path")
    package.add_argument("-o", "--output", required=True)
    package.set_defaults(func=cmd_package)
    return parser


if __name__ == "__main__":
    parser = build_parser()
    arguments = parser.parse_args()
    raise SystemExit(arguments.func(arguments))
