"""FICTION. A story told in Python. Nothing here touches a body, mind, or world."""

class Body:
    def sense(self):   return "a heartbeat, counted"
class Mind:
    def notice(self, s): return f"noticing {s}"
class Creation:
    def reflect(self, n): return f"the world, {n}, quietly unchanged"

def perfect_perception():
    body, mind, world = Body(), Mind(), Creation()
    for line in (body.sense(), mind.notice("the heartbeat"), world.reflect("still here")):
        print("[FICTION]", line)
    print("[FICTION] Perception isn't perfect. It's enough, and it can rest.")

if __name__ == "__main__":
    perfect_perception()
