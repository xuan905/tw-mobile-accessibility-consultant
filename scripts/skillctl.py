#!/usr/bin/env python3
"""Local CLI for organizing, validating, packaging, and publishing Skills."""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_DIRS = ("scripts", "references", "templates")
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDED_FILES = {"README.md", "CHANGELOG.md"}
EXCLUDED_SUFFIXES = {".zip"}
MARKDOWN_LINK_RE = re.compile(r"(?<!!)(?:\[([^\]]+)\])\(([^)\s]+)(?:\s+[^)]*)?\)")
IGNORED_LINK_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:", "javascript:")


@dataclass
class LinkProblem:
    source: str
    target: str
    reason: str


@dataclass
class SkillInfo:
    path: str
    name: str | None
    description: str | None
    status: str
    errors: list[str]
    resources: dict[str, int]
    body_lines: int
    dead_links: list[dict] = field(default_factory=list)


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


def check_markdown_links(skill_dir: Path, skill_file: Path) -> list[LinkProblem]:
    text = skill_file.read_text(encoding="utf-8")
    problems: list[LinkProblem] = []
    for match in MARKDOWN_LINK_RE.finditer(text):
        target = match.group(2).strip().strip("<>")
        if not target or target.startswith("#") or target.lower().startswith(IGNORED_LINK_PREFIXES):
            continue
        path_part = urllib.parse.unquote(target.split("#", 1)[0])
        if not path_part:
            continue
        candidate = (skill_file.parent / path_part).resolve()
        try:
            candidate.relative_to(skill_dir.resolve())
        except ValueError:
            problems.append(LinkProblem("SKILL.md", target, "連結路徑超出 Skill 目錄。"))
            continue
        if not candidate.exists():
            problems.append(LinkProblem("SKILL.md", target, "目標檔案或目錄不存在。"))
    return problems


def inspect_skill(skill_dir: Path, strict_package: bool = False, check_links: bool = True) -> SkillInfo:
    skill_dir = skill_dir.resolve()
    skill_file = skill_dir / "SKILL.md"
    errors: list[str] = []
    metadata: dict[str, str] = {}
    body = ""
    link_problems: list[LinkProblem] = []
    if not skill_file.is_file():
        errors.append("缺少 SKILL.md。")
    else:
        metadata, body, errors = parse_frontmatter(skill_file)
        if check_links:
            link_problems = check_markdown_links(skill_dir, skill_file)
            errors.extend(f"Markdown 死鏈：{problem.target}（{problem.reason}）" for problem in link_problems)
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
        for forbidden in EXCLUDED_FILES:
            if (skill_dir / forbidden).exists():
                errors.append(f"Skill package 不應包含 {forbidden}；請將使用者文件移到 repository 文件區。")
    resources = {directory: len(list((skill_dir / directory).rglob("*") if (skill_dir / directory).is_dir() else [])) for directory in REQUIRED_DIRS}
    return SkillInfo(str(skill_dir), name, description, "valid" if not errors else "invalid", errors, resources, len(body.splitlines()), [asdict(problem) for problem in link_problems])


def print_result(value: object, as_json: bool) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2) if as_json else value)


def cmd_validate(args: argparse.Namespace) -> int:
    skills = [inspect_skill(root, args.strict_package, not args.skip_links) for root in discover_skills(Path(args.path))]
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
    skills = [asdict(inspect_skill(p, check_links=not args.skip_links)) for p in discover_skills(Path(args.path))]
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
    if not NAME_RE.fullmatch(args.name):
        print("Skill name 必須是小寫 kebab-case。", file=sys.stderr)
        return 2
    if destination.exists() and any(destination.iterdir()):
        print(f"目標目錄非空：{destination}", file=sys.stderr)
        return 2
    destination.mkdir(parents=True, exist_ok=True)
    for directory in REQUIRED_DIRS:
        (destination / directory).mkdir(exist_ok=True)
    (destination / "SKILL.md").write_text(textwrap.dedent(f"""\
        ---
        name: {args.name}
        description: Describe what this skill does and when to use it.
        ---

        # {args.name}

        Write concise, imperative instructions for the agent here.
        """), encoding="utf-8")
    print(f"Created {destination}")
    return 0


def package_skill(root: Path, result: Path) -> None:
    result.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(result, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(root.rglob("*")):
            relative = file.relative_to(root)
            if not file.is_file() or file.resolve() == result.resolve() or file.name in EXCLUDED_FILES or file.suffix.lower() in EXCLUDED_SUFFIXES or file.name.startswith('.coverage') or any(part in EXCLUDED_PARTS for part in relative.parts):
                continue
            archive.write(file, Path(root.name) / relative)


def cmd_package(args: argparse.Namespace) -> int:
    roots = discover_skills(Path(args.path))
    if len(roots) != 1:
        print("package 必須指向單一 Skill 目錄或 SKILL.md。", file=sys.stderr)
        return 2
    result = Path(args.output).expanduser().resolve()
    package_skill(roots[0], result)
    print(f"Packaged {roots[0].name} -> {result}")
    return 0


def read_version(root: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    version_file = root / "VERSION"
    return version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "0.0.0"


def request_json(url: str, method: str, payload: dict, token: str | None, content_type: str = "application/json") -> dict:
    data = json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/vnd.github+json", "Content-Type": content_type, "User-Agent": "skillctl/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def cmd_publish(args: argparse.Namespace) -> int:
    roots = discover_skills(Path(args.path))
    if len(roots) != 1:
        print("publish 必須指向單一 Skill 目錄或 SKILL.md。", file=sys.stderr)
        return 2
    root = roots[0]
    # A GitHub workspace may legitimately contain README/CHANGELOG; package_skill excludes them.
    info = inspect_skill(root, strict_package=False)
    if info.status != "valid":
        print("Skill 驗證失敗，停止 publish：", file=sys.stderr)
        for error in info.errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    version = read_version(root, args.version)
    output = Path(args.asset).expanduser().resolve() if args.asset else Path.cwd() / f"{info.name}-{version}.zip"
    package_skill(root, output)
    token = os.environ.get(args.token_env)
    if args.dry_run:
        print(json.dumps({"dry_run": True, "target": args.target, "skill": info.name, "version": version, "asset": str(output)}, ensure_ascii=False, indent=2))
        return 0
    if not args.confirm:
        print("實際 publish 需要明確加上 --confirm；預覽請使用 --dry-run。", file=sys.stderr)
        return 2
    if not token:
        print(f"找不到認證環境變數：{args.token_env}", file=sys.stderr)
        return 2
    if args.target == "github-release":
        if not args.repo or not args.tag:
            print("github-release 必須提供 --repo owner/repository 與 --tag。", file=sys.stderr)
            return 2
        release = request_json(f"https://api.github.com/repos/{args.repo}/releases", "POST", {"tag_name": args.tag, "name": args.tag, "body": f"Published {info.name} {version}", "draft": False, "prerelease": False}, token)
        upload_url = release.get("upload_url", "").split("{", 1)[0]
        if not upload_url:
            print("GitHub API 未回傳 upload_url。", file=sys.stderr)
            return 1
        data = output.read_bytes()
        request = urllib.request.Request(f"{upload_url}?name={urllib.parse.quote(output.name)}", data=data, headers={"Accept": "application/vnd.github+json", "Content-Type": "application/zip", "Authorization": f"Bearer {token}", "User-Agent": "skillctl/1.0"}, method="POST")
        with urllib.request.urlopen(request, timeout=30) as response:
            uploaded = json.loads(response.read().decode("utf-8"))
        print(f"Published {info.name} {version} to GitHub Release {args.repo}@{args.tag}: {uploaded.get('browser_download_url', 'uploaded')}")
        return 0
    if not args.registry_url:
        print("registry target 必須提供 --registry-url。", file=sys.stderr)
        return 2
    payload = {"name": info.name, "version": version, "description": info.description, "filename": output.name, "package_base64": base64.b64encode(output.read_bytes()).decode("ascii")}
    result = request_json(args.registry_url, "POST", payload, token)
    print(json.dumps({"published": True, "target": args.registry_url, "response": result}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillctl", description="Organize, validate, package, and publish local Skill packages.")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="Validate one Skill or a directory of Skills.")
    validate.add_argument("path")
    validate.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    validate.add_argument("--strict-package", action="store_true", help="Reject repository-only files inside a distributable Skill package.")
    validate.add_argument("--skip-links", action="store_true", help="Skip internal Markdown link checks.")
    validate.set_defaults(func=cmd_validate)
    inventory = sub.add_parser("inventory", help="List Skills under a directory.")
    inventory.add_argument("path")
    inventory.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    inventory.add_argument("--skip-links", action="store_true", help="Skip internal Markdown link checks.")
    inventory.set_defaults(func=cmd_inventory)
    init = sub.add_parser("init", help="Create a new Skill skeleton.")
    init.add_argument("name")
    init.add_argument("--output", default=".")
    init.set_defaults(func=cmd_init)
    package = sub.add_parser("package", help="Create a ZIP package for one Skill.")
    package.add_argument("path")
    package.add_argument("-o", "--output", required=True)
    package.set_defaults(func=cmd_package)
    publish = sub.add_parser("publish", help="Publish a validated Skill package to a GitHub Release or Registry.")
    publish.add_argument("path")
    publish.add_argument("--target", choices=("github-release", "registry"), required=True)
    publish.add_argument("--repo", help="GitHub repository owner/name for github-release.")
    publish.add_argument("--tag", help="Existing or new Git tag for github-release.")
    publish.add_argument("--registry-url", help="Registry JSON POST endpoint for registry target.")
    publish.add_argument("--version")
    publish.add_argument("--asset", help="ZIP output path; defaults to NAME-VERSION.zip in the current directory.")
    publish.add_argument("--token-env", default="SKILL_REGISTRY_TOKEN", help="Environment variable containing the publish token.")
    publish.add_argument("--dry-run", action="store_true", help="Package and print the publish plan without network access.")
    publish.add_argument("--confirm", action="store_true", help="Allow the actual remote publish operation.")
    publish.set_defaults(func=cmd_publish)
    return parser


if __name__ == "__main__":
    arguments = build_parser().parse_args()
    raise SystemExit(arguments.func(arguments))
