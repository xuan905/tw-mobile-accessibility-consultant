import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

from scripts.skillctl import build_parser


class SkillCtlTest(unittest.TestCase):
    def run_cli(self, *argv):
        output = StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            code = build_parser().parse_args(list(argv)).func(build_parser().parse_args(list(argv)))
        return code, output.getvalue()

    def write_skill(self, root: Path, name="demo-skill", description="A useful demo skill.") -> Path:
        skill = root / name
        (skill / "scripts").mkdir(parents=True)
        (skill / "references").mkdir()
        (skill / "templates").mkdir()
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n\nUse this skill.\n",
            encoding="utf-8",
        )
        return skill

    def test_validate_valid_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = self.write_skill(Path(directory))
            code, output = self.run_cli("validate", str(skill))
            self.assertEqual(code, 0)
            self.assertIn("VALID", output)

    def test_validate_rejects_bad_name_and_missing_description(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = self.write_skill(Path(directory), "Bad_Name", "")
            code, output = self.run_cli("validate", str(skill))
            self.assertEqual(code, 1)
            self.assertIn("kebab-case", output)
            self.assertIn("description", output)

    def test_inventory_json_lists_nested_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(root, "one-skill")
            self.write_skill(root / "group", "two-skill")
            code, output = self.run_cli("inventory", str(root), "--json")
            payload = json.loads(output)
            self.assertEqual(code, 0)
            self.assertEqual(payload["count"], 2)
            self.assertEqual({item["name"] for item in payload["skills"]}, {"one-skill", "two-skill"})

    def test_init_creates_expected_skeleton(self):
        with tempfile.TemporaryDirectory() as directory:
            code, _ = self.run_cli("init", "new-skill", "--output", directory)
            root = Path(directory) / "new-skill"
            self.assertEqual(code, 0)
            self.assertTrue((root / "SKILL.md").is_file())
            self.assertTrue((root / "scripts").is_dir())
            self.assertIn("name: new-skill", (root / "SKILL.md").read_text(encoding="utf-8"))

    def test_validate_rejects_dead_internal_markdown_link(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = self.write_skill(Path(directory))
            (skill / "SKILL.md").write_text(
                "---\nname: demo-skill\ndescription: A useful demo skill.\n---\n\n[Missing](references/missing.md)\n",
                encoding="utf-8",
            )
            code, output = self.run_cli("validate", str(skill))
            self.assertEqual(code, 1)
            self.assertIn("Markdown 死鏈", output)

    def test_validate_rejects_link_outside_skill_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = self.write_skill(Path(directory))
            (skill / "SKILL.md").write_text(
                "---\nname: demo-skill\ndescription: A useful demo skill.\n---\n\n[Outside](../secret.txt)\n",
                encoding="utf-8",
            )
            code, output = self.run_cli("validate", str(skill))
            self.assertEqual(code, 1)
            self.assertIn("超出 Skill 目錄", output)

    def test_publish_dry_run_never_requires_network_or_token(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = self.write_skill(Path(directory))
            code, output = self.run_cli(
                "publish", str(skill), "--target", "github-release", "--repo", "owner/repo",
                "--tag", "v1.0.0", "--dry-run", "--asset", str(Path(directory) / "out.zip"),
            )
            payload = json.loads(output)
            self.assertEqual(code, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["target"], "github-release")
            self.assertTrue(Path(payload["asset"]).is_file())

    def test_publish_requires_explicit_confirm(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = self.write_skill(Path(directory))
            code, output = self.run_cli(
                "publish", str(skill), "--target", "registry", "--registry-url", "https://registry.invalid",
                "--asset", str(Path(directory) / "out.zip"),
            )
            self.assertEqual(code, 2)
            self.assertIn("--confirm", output)

    def test_package_excludes_cache_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = self.write_skill(Path(directory))
            (skill / "scripts" / "run.py").write_text("print('ok')\n", encoding="utf-8")
            (skill / "__pycache__").mkdir()
            (skill / "__pycache__" / "bad.pyc").write_bytes(b"cache")
            (skill / "README.md").write_text("repository docs\n", encoding="utf-8")
            output = Path(directory) / "demo.zip"
            code, _ = self.run_cli("package", str(skill), "--output", str(output))
            with zipfile.ZipFile(output) as archive:
                names = archive.namelist()
            self.assertEqual(code, 0)
            self.assertIn("demo-skill/SKILL.md", names)
            self.assertNotIn("demo-skill/__pycache__/bad.pyc", names)
            self.assertNotIn("demo-skill/README.md", names)


if __name__ == "__main__":
    unittest.main()
