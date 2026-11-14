import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.eria_os_sandbox import SandboxError, build_command


class SandboxPolicyTests(unittest.TestCase):
    def test_missing_bubblewrap_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch("eria_os_sandbox.platform.system", return_value="Linux"), \
                 patch("eria_os_sandbox.shutil.which", return_value=None):
                with self.assertRaises(SandboxError):
                    build_command(Path(folder), ["python", "-V"])

    def test_command_requires_network_namespace(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch("eria_os_sandbox.platform.system", return_value="Linux"), \
                 patch("eria_os_sandbox.shutil.which", return_value="/usr/bin/bwrap"):
                command = build_command(Path(folder), ["python", "-V"])
                self.assertIn("--unshare-net", command)
                self.assertIn("--ro-bind", command)
                self.assertIn("--cap-drop", command)
                self.assertEqual(command[-2:], ["python", "-V"])


if __name__ == "__main__":
    unittest.main()
