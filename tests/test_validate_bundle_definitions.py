import unittest
import os
import tempfile
import sys
from unittest.mock import patch
from io import StringIO

# Add repository root to sys.path to import tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.bundle.validate_bundle_definitions import check_bundle

class TestValidateBundleDefinitions(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        # Create a dummy file for path existence check
        self.dummy_path = "tools/validate_all.py" # Use a file that definitely exists in the repo

    def tearDown(self):
        self.test_dir.cleanup()

    def create_yaml(self, content):
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, dir=self.test_dir.name)
        tmp.write(content)
        tmp.close()
        return tmp.name

    def test_valid_bundle(self):
        content = f"""schemaVersion: 1
bundle:
  name: test-bundle
  kind: skill
  source: skills/
  outputBranch: dist/test-bundle
include:
  - from: {self.dummy_path}
    to: ./script.py
    mode: copy
generate:
  lockFile: bundle-lock.json
"""
        yaml_path = self.create_yaml(content)
        with patch('sys.stdout', new=StringIO()):
            errors = check_bundle(yaml_path)
        self.assertEqual(errors, 0)

    def test_missing_schema_version(self):
        content = """bundle:
  name: test-bundle
"""
        yaml_path = self.create_yaml(content)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            errors = check_bundle(yaml_path)
        self.assertGreater(errors, 0)
        self.assertIn("missing schemaVersion", fake_out.getvalue())

    def test_missing_bundle_block(self):
        content = "schemaVersion: 1\n"
        yaml_path = self.create_yaml(content)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            errors = check_bundle(yaml_path)
        self.assertGreater(errors, 0)
        self.assertIn("missing bundle block", fake_out.getvalue())

    def test_missing_bundle_fields(self):
        content = """schemaVersion: 1
bundle:
  # missing name, kind, source, outputBranch
"""
        yaml_path = self.create_yaml(content)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            errors = check_bundle(yaml_path)
        self.assertGreater(errors, 0)
        self.assertIn("missing bundle.name", fake_out.getvalue())
        self.assertIn("missing bundle.kind", fake_out.getvalue())
        self.assertIn("missing bundle.source", fake_out.getvalue())
        self.assertIn("missing bundle.outputBranch", fake_out.getvalue())

    def test_invalid_output_branch(self):
        content = """schemaVersion: 1
bundle:
  name: test
  kind: skill
  source: .
  outputBranch: main
"""
        yaml_path = self.create_yaml(content)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            errors = check_bundle(yaml_path)
        self.assertGreater(errors, 0)
        self.assertIn("outputBranch must start with dist/", fake_out.getvalue())

    def test_missing_include_block(self):
        content = """schemaVersion: 1
bundle:
  name: test
  kind: skill
  source: .
  outputBranch: dist/test
"""
        yaml_path = self.create_yaml(content)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            errors = check_bundle(yaml_path)
        self.assertGreater(errors, 0)
        self.assertIn("missing include block", fake_out.getvalue())

    def test_unsafe_paths(self):
        content = """schemaVersion: 1
bundle:
  name: test
  kind: skill
  source: .
  outputBranch: dist/test
include:
  - from: /etc/passwd
    to: ../outside.txt
    mode: copy
"""
        yaml_path = self.create_yaml(content)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            errors = check_bundle(yaml_path)
        self.assertGreater(errors, 0)
        self.assertIn("includes unsafe source path: /etc/passwd", fake_out.getvalue())
        self.assertIn("includes unsafe target path: ../outside.txt", fake_out.getvalue())

    def test_non_existent_path(self):
        content = """schemaVersion: 1
bundle:
  name: test
  kind: skill
  source: .
  outputBranch: dist/test
include:
  - from: non_existent_file.txt
    to: ./file.txt
    mode: copy
"""
        yaml_path = self.create_yaml(content)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            errors = check_bundle(yaml_path)
        self.assertGreater(errors, 0)
        self.assertIn("includes non-existent path: non_existent_file.txt", fake_out.getvalue())

    def test_unsupported_mode(self):
        content = """schemaVersion: 1
bundle:
  name: test
  kind: skill
  source: .
  outputBranch: dist/test
include:
  - from: tools/validate_all.py
    to: ./script.py
    mode: symlink
"""
        yaml_path = self.create_yaml(content)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            errors = check_bundle(yaml_path)
        self.assertGreater(errors, 0)
        self.assertIn("unsupported mode: symlink", fake_out.getvalue())

    def test_missing_generate_block(self):
        content = """schemaVersion: 1
bundle:
  name: test
  kind: skill
  source: .
  outputBranch: dist/test
include:
  - from: tools/validate_all.py
    to: ./script.py
    mode: copy
"""
        yaml_path = self.create_yaml(content)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            errors = check_bundle(yaml_path)
        self.assertGreater(errors, 0)
        self.assertIn("missing generate block", fake_out.getvalue())

    def test_missing_lockfile(self):
        content = """schemaVersion: 1
bundle:
  name: test
  kind: skill
  source: .
  outputBranch: dist/test
include:
  - from: tools/validate_all.py
    to: ./script.py
    mode: copy
generate:
  readme: README.md
"""
        yaml_path = self.create_yaml(content)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            errors = check_bundle(yaml_path)
        self.assertGreater(errors, 0)
        self.assertIn("missing generate.lockFile", fake_out.getvalue())

    def test_invalid_lockfile(self):
        content = """schemaVersion: 1
bundle:
  name: test
  kind: skill
  source: .
  outputBranch: dist/test
include:
  - from: tools/validate_all.py
    to: ./script.py
    mode: copy
generate:
  lockFile: wrong-name.json
"""
        yaml_path = self.create_yaml(content)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            errors = check_bundle(yaml_path)
        self.assertGreater(errors, 0)
        self.assertIn("generate.lockFile must end with bundle-lock.json", fake_out.getvalue())

if __name__ == '__main__':
    unittest.main()
