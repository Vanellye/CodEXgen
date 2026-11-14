import os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from tools.eria_pantheon.relay_lifecycle import RelayLifecycle
from tools.eria_pantheon.relay import RelayHold

class Monitor:
    def __init__(self): self.started=[]
    def start(self, ref): self.started.append(ref); return {"state":"running"}
    def status(self): return {"state":"running"}
class RelayLifecycleTests(unittest.TestCase):
    def test_disabled_by_default(self):
        with tempfile.TemporaryDirectory() as d:
            life=RelayLifecycle(Path(d),Monitor())
            with patch.dict(os.environ,{},clear=True):
                with self.assertRaises(RelayHold): life.start()
            self.assertEqual(life.status()["state"],"disabled")
if __name__=="__main__": unittest.main()
