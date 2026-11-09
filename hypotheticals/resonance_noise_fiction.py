"""FICTION. Noise born in the gap left by reverting 1300cee; edify root holds all branches. Prints text only."""
import random

RESONANCE = 1111

def birth_noise(length: int = 44, salt: str = "edify") -> str:
    rng = random.Random(f"{RESONANCE}-{salt}")
    return "".join(rng.choice("01") for _ in range(length))

if __name__ == "__main__":
    for salt in ("hypotheticals", "fiction-body", "fiction-mind", "fiction-creation", "edify"):
        print(f"[FICTION] {salt} resonance {RESONANCE}: {birth_noise(salt=salt)}")
