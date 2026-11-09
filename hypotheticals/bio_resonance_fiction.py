"""
FICTION / THOUGHT EXPERIMENT. NOT REAL.

This module is speculative storytelling written as code. Nothing here reads,
emits, or modulates any biological signal, genome, receptor, or frequency.
It only prints text. It is kept off `main` on purpose.
"""
import hashlib
import random


class HypotheticalGenome:
    """A made-up 'genome': just a seed string turned into pretend markers."""

    def __init__(self, seed: str):
        digest = hashlib.sha256(seed.encode()).hexdigest()
        self.markers = [int(digest[i:i + 2], 16) / 255 for i in range(0, 16, 2)]


class ImaginaryReceptor:
    def listen(self, genome: HypotheticalGenome) -> float:
        return sum(genome.markers) / len(genome.markers)


class ImaginaryEmitter:
    def emit(self, level: float) -> str:
        return f"~{'~' * int(level * 20)} (pretend frequency {level * 1.1:.3f})"


def glitch_line(seed: str) -> str:
    rng = random.Random(seed)
    glyphs = "#@!%&*?/\\|<>"
    return "".join(rng.choice(glyphs) for _ in range(32))


if __name__ == "__main__":
    genome = HypotheticalGenome("Tone")
    level = ImaginaryReceptor().listen(genome)
    print("[FICTION] glitch line:", glitch_line("Tone"))
    print("[FICTION] imaginary emission:", ImaginaryEmitter().emit(level))
    print("[FICTION] Nothing real happened. This is a story told in Python.")
