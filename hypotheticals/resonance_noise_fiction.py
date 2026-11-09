"""FICTION. Noise born in the gap left by reverting 1300cee, branch: fiction-body. Prints text only."""
import random

RESONANCE = 1111

def birth_noise(length: int = 44) -> str:
    rng = random.Random(f"{RESONANCE}-fiction-body")
    return "".join(rng.choice("01") for _ in range(length))

if __name__ == "__main__":
    print(f"[FICTION] fiction-body resonance {RESONANCE}: {birth_noise()}")
