"""Tests for the rules and for rules.py / install.sh. Every run points HOME at a throwaway
folder, so your real ~/.claude/CLAUDE.md is never read or written.

    python3 -m unittest discover -s tests -v
"""
import glob
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "rules.py")
INSTALL = os.path.join(ROOT, "install.sh")
RULES_DIR = os.path.join(ROOT, "rules")


def load_module():
    spec = importlib.util.spec_from_file_location("claude_rules", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rules = load_module()
MANIFEST = rules.load_rules()
NO_TOOL_IDS = [r["id"] for r in MANIFEST if not (r.get("companion") or {}).get("required")]


class TempHome(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="claude-rules-")
        self.old_home = os.environ.get("HOME")
        os.environ["HOME"] = self.home  # for the functions called in-process
        self.claude_md = os.path.join(self.home, ".claude", "CLAUDE.md")

    def tearDown(self):
        os.environ["HOME"] = self.old_home
        shutil.rmtree(self.home, ignore_errors=True)

    def run_install(self, *args):
        env = dict(os.environ, HOME=self.home)
        return subprocess.run(["bash", INSTALL] + list(args), env=env,
                              capture_output=True, text=True, timeout=60)

    def write(self, text, path=None):
        path = path or self.claude_md
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def read(self, path=None):
        with open(path or self.claude_md, encoding="utf-8") as fh:
            return fh.read()

    def backups(self):
        return glob.glob(self.claude_md + ".bak-*")

    def fake_tool(self, rule_id):
        rule = next(r for r in MANIFEST if r["id"] == rule_id)
        path = rules.expand(rule["companion"]["detect"][0])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").close()


class RuleFiles(unittest.TestCase):
    def test_manifest_lists_every_rule_file_once(self):
        on_disk = sorted(os.path.basename(p) for p in glob.glob(os.path.join(RULES_DIR, "*.md")))
        listed = sorted(r["file"] for r in MANIFEST)
        self.assertEqual(listed, on_disk)
        ids = [r["id"] for r in MANIFEST]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_rule_starts_with_a_unique_heading(self):
        headings = []
        for rule in MANIFEST:
            with open(os.path.join(RULES_DIR, rule["file"]), encoding="utf-8") as fh:
                first = fh.readline()
            self.assertTrue(first.startswith("## "), rule["file"])
            headings.append(first.strip().lower())
        self.assertEqual(len(headings), len(set(headings)))

    def test_every_rule_has_a_summary(self):
        for rule in MANIFEST:
            self.assertTrue(rule.get("summary"), rule["id"])

    def test_companion_paragraphs_only_where_a_tool_is_optional(self):
        for rule in MANIFEST:
            _body, extra = rules.read_rule(rule)
            companion = rule.get("companion") or {}
            if companion and not companion.get("required"):
                self.assertTrue(extra, "%s mentions its tool unconditionally" % rule["id"])
            else:
                self.assertFalse(extra, "%s has a companion part it can never use" % rule["id"])
            if companion:
                self.assertTrue(companion["detect"] and companion["url"].startswith("https://"))

    def test_rendered_rules_have_no_placeholders_or_markers(self):
        for rule in MANIFEST:
            text = rules.render_rule(rule, "iPhone 17 Pro", "all")
            self.assertNotIn("{{", text, rule["id"])
            self.assertNotIn("<!--", text, rule["id"])

    def test_simulator_name_is_substituted(self):
        rule = next(r for r in MANIFEST if r["id"] == "build-output")
        text = rules.render_rule(rule, "iPad Pro 13-inch (M5)", "detect")
        self.assertIn("Use the existing iPad Pro 13-inch (M5) simulator", text)
        self.assertNotIn("iPhone 17 Pro", text)

    def test_example_matches_the_rules(self):
        # --rules all and --companions all ignore what is installed, so HOME does not matter here.
        result = subprocess.run([sys.executable, SCRIPT, "--print", "--rules", "all", "--companions", "all"],
                                capture_output=True, text=True, timeout=30)
        with open(os.path.join(ROOT, "examples", "CLAUDE.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), result.stdout,
                             "examples/CLAUDE.md is stale: python3 rules.py --print --rules all "
                             "--companions all > examples/CLAUDE.md")


class Selection(TempHome):
    def ids(self, spec=None):
        return [r["id"] for r in rules.select(MANIFEST, spec)]

    def test_default_skips_rules_whose_tool_is_missing(self):
        self.assertEqual(self.ids(), NO_TOOL_IDS)
        self.assertNotIn("idle-reaper", self.ids())
        self.assertNotIn("sim-audio", self.ids())

    def test_default_adds_a_rule_once_its_tool_is_installed(self):
        self.fake_tool("idle-reaper")
        self.assertIn("idle-reaper", self.ids())
        self.assertNotIn("sim-audio", self.ids())

    def test_all_and_explicit_lists_keep_manifest_order(self):
        self.assertEqual(self.ids("all"), [r["id"] for r in MANIFEST])
        self.assertEqual(self.ids("em-dashes, git"), ["git", "em-dashes"])

    def test_unknown_rule_is_an_error(self):
        with self.assertRaises(rules.RulesError):
            rules.select(MANIFEST, "git,nope")

    def test_companion_paragraph_follows_the_tool(self):
        git = next(r for r in MANIFEST if r["id"] == "git")
        self.assertNotIn("git-guard.py", rules.render_rule(git, "x", "detect"))
        self.fake_tool("git")
        self.assertIn("git-guard.py", rules.render_rule(git, "x", "detect"))
        self.assertNotIn("git-guard.py", rules.render_rule(git, "x", "none"))


class Install(TempHome):
    def test_fresh_install_writes_the_default_rules(self):
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        text = self.read()
        self.assertTrue(text.startswith(rules.BEGIN))
        self.assertTrue(text.endswith(rules.END + "\n"))
        self.assertIn("wrote %d rules" % len(NO_TOOL_IDS), result.stdout)
        self.assertIn("## Writing: never use em dashes", text)
        self.assertNotIn("## Simulator audio", text)
        self.assertEqual(self.backups(), [])

    def test_second_run_changes_nothing(self):
        self.run_install()
        result = self.run_install()
        self.assertIn("already up to date", result.stdout)
        self.assertEqual(self.backups(), [])

    def test_keeps_your_own_text_and_backs_it_up(self):
        mine = "# My rules\n\nBe brief.\n"
        self.write(mine)
        result = self.run_install("--rules", "git")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = self.read()
        self.assertTrue(text.startswith(mine + "\n" + rules.BEGIN))
        self.assertEqual(len(self.backups()), 1)

    def test_uninstall_restores_the_file_exactly(self):
        mine = "# My rules\n\nBe brief.\n"
        self.write(mine)
        self.run_install()
        self.write(self.read() + "\n## Added later by hand\n\nKeep me.\n")
        result = self.run_install("--uninstall")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read(), mine + "\n## Added later by hand\n\nKeep me.\n")

    def test_uninstall_removes_a_file_it_created(self):
        self.run_install()
        self.run_install("--uninstall")
        self.assertFalse(os.path.exists(self.claude_md))

    def test_uninstall_without_a_block_changes_nothing(self):
        self.write("# Mine\n")
        result = self.run_install("--uninstall")
        self.assertIn("no managed block", result.stdout)
        self.assertEqual(self.read(), "# Mine\n")
        self.assertEqual(self.backups(), [])

    def test_rule_you_already_wrote_is_skipped(self):
        self.write("# Mine\n\n## Writing: NEVER use em dashes\n\nMy own words.\n")
        result = self.run_install("--rules", "em-dashes,git")
        self.assertIn("skipped em-dashes", result.stdout)
        text = self.read()
        self.assertEqual(text.count("em dashes"), 1)
        self.assertIn("## Git: never commit or push", text)

    def test_nothing_to_add_leaves_the_file_alone(self):
        original = "## Writing: never use em dashes\n\nmine"  # no trailing newline on purpose
        self.write(original)
        result = self.run_install("--rules", "em-dashes")
        self.assertIn("nothing to add", result.stdout)
        self.assertEqual(self.read(), original)
        self.assertEqual(self.backups(), [])

    def test_changing_the_selection_replaces_the_block(self):
        self.run_install("--rules", "all")
        self.assertIn("## Simulator audio", self.read())
        self.run_install("--rules", "git")
        text = self.read()
        self.assertNotIn("## Simulator audio", text)
        self.assertEqual(text.count(rules.BEGIN), 1)

    def test_edits_inside_the_block_are_replaced(self):
        self.run_install("--rules", "git")
        self.write(self.read().replace("This is absolute.", "This is optional."))
        self.run_install("--rules", "git")
        self.assertIn("This is absolute.", self.read())

    def test_broken_markers_are_refused(self):
        broken = "# Mine\n\n" + rules.BEGIN + "\nhalf a block\n"
        self.write(broken)
        result = self.run_install()
        self.assertEqual(result.returncode, 2)
        self.assertIn("markers are broken", result.stderr)
        self.assertEqual(self.read(), broken)

    def test_markers_in_the_wrong_order_are_refused(self):
        broken = "# Mine\n\n" + rules.END + "\nstray text\n" + rules.BEGIN + "\n"
        self.write(broken)
        result = self.run_install()
        self.assertEqual(result.returncode, 2)
        self.assertIn("markers are broken", result.stderr)
        self.assertEqual(self.read(), broken)

    def test_installing_again_keeps_what_you_wrote_around_the_block(self):
        self.write("# Mine\n\nBe brief.\n")
        self.run_install("--rules", "git")
        after = "\n## Added later by hand\n\nKeep me.\n"
        self.write(self.read() + after)
        result = self.run_install("--rules", "git,em-dashes")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = self.read()
        self.assertTrue(text.startswith("# Mine\n\nBe brief.\n\n" + rules.BEGIN), text[:80])
        self.assertTrue(text.endswith(rules.END + "\n" + after), text[-80:])
        self.assertIn("## Writing: never use em dashes", text)

    def test_print_writes_nothing(self):
        result = self.run_install("--print", "--rules", "attribution")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Git: never credit Claude", result.stdout)
        self.assertFalse(os.path.exists(self.claude_md))

    def test_file_option_targets_a_project(self):
        project = os.path.join(self.home, "code", "app", "CLAUDE.md")
        result = self.run_install("--file", "~/code/app/CLAUDE.md", "--rules", "em-dashes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("never use em dashes", self.read(project))
        self.assertFalse(os.path.exists(self.claude_md))

    def test_simulator_option(self):
        self.run_install("--rules", "simulator", "--simulator", "iPhone Air")
        self.assertIn("## Simulator: always use the iPhone Air", self.read())

    def test_list_shows_what_is_installed(self):
        self.fake_tool("notifications")
        result = self.run_install("--list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Claude Code Notify installed", result.stdout)
        self.assertIn("Claude Code Sim Audio not installed, required", result.stdout)

    def test_unknown_rule_exits_2(self):
        result = self.run_install("--rules", "nope")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown rule: nope", result.stderr)

    def test_help(self):
        result = self.run_install("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("managed block", result.stdout)


if __name__ == "__main__":
    unittest.main()
