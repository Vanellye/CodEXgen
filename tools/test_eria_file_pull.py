import tempfile
import unittest
from pathlib import Path
from eria_file_pull import FilePullService

class FilePullTests(unittest.TestCase):
    def test_local_version_history_and_missing_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"repo"; root.mkdir()
            (root/"README.md").write_text("first",encoding="utf-8")
            db=Path(tmp)/"eria.sqlite3"
            service=FilePullService(root,db)
            first=service.pull_local()
            self.assertEqual(first["imported"],1)
            (root/"README.md").write_text("second",encoding="utf-8")
            second=service.pull_local()
            self.assertEqual(second["imported"],1)
            with service._connect() as conn:
                versions=conn.execute("SELECT COUNT(*) FROM pull_file_versions WHERE source='local' AND path='README.md'").fetchone()[0]
                blobs=conn.execute("SELECT COUNT(*) FROM pull_blobs").fetchone()[0]
            self.assertEqual(versions,2)
            self.assertEqual(blobs,2)
            (root/"README.md").unlink()
            third=service.pull_local()
            self.assertEqual(third["missing"],1)
            with service._connect() as conn:
                status=conn.execute("SELECT status FROM pull_files WHERE source='local' AND path='README.md'").fetchone()[0]
            self.assertEqual(status,"missing")

    def test_secret_files_are_not_ingested(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"repo"; root.mkdir()
            (root/".env").write_text("PRIVATE=not-for-index",encoding="utf-8")
            service=FilePullService(root,Path(tmp)/"db.sqlite3")
            result=service.pull_local()
            self.assertEqual(result["imported"],0)
            with service._connect() as conn:
                count=conn.execute("SELECT COUNT(*) FROM pull_files").fetchone()[0]
            self.assertEqual(count,0)

if __name__ == "__main__":
    unittest.main()
