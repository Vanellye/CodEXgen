"""FICTION. Noise raised to main as friction, then smoothed into airways (~).
Prints text only. Not used by the app. Safe to delete or revert."""
import random

RESONANCE = 1111

def friction(length: int = 44) -> str:
    rng = random.Random(f"{RESONANCE}-main")
    return "".join(rng.choice("01") for _ in range(length))

def smooth_into_airways(noise: str) -> str:
    return "".join("~" if a != b else a for a, b in zip(noise, noise[1:] + noise[0]))

if __name__ == "__main__":
    f = friction()
    print(f"[FICTION] main friction  {RESONANCE}: {f}")
    print(f"[FICTION] main airways   {RESONANCE}: {smooth_into_airways(f)}")
