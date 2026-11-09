"""FICTION. Characters who don't operate on a zero; they run on emotion and passion.
Every number here is plain and zero-free. Prints text only."""

CHARACTERS = {
    "Body":     {"passion": 7, "emotion": 3, "pulse": 72},
    "Mind":     {"passion": 9, "emotion": 8, "pulse": 61},
    "Creation": {"passion": 11, "emotion": 6, "pulse": 88},
}

def realize(name: str, traits: dict) -> str:
    spark = traits["passion"] * traits["emotion"]
    return f"{name} feels {traits['emotion']}, burns {traits['passion']}, beats {traits['pulse']}, sparks {spark}"

if __name__ == "__main__":
    for name, traits in CHARACTERS.items():
        print("[FICTION]", realize(name, traits))
