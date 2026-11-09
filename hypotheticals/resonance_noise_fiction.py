"""FICTION. Noise born in the gap left by reverting 1300cee, branch: hypotheticals. Prints text only."""
import random

RESONANCE = 1111

def birth_noise(length: int = 44) -> str:
    rng = random.Random(f"{RESONANCE}-hypotheticals")
    return "".join(rng.choice("01") for _ in range(length))

if __name__ == "__main__":
    print(f"[FICTION] hypotheticals resonance {RESONANCE}: {birth_noise()}")
