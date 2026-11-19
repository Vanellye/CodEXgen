# Ɣơ/2 cross-platform adapter validation

The canonical byte corpus is `test-vectors/yoro-star-v2.tsv`. Each row contains a name, source bytes as hexadecimal, and the expected canonical encoding. Python, Kotlin/JVM, and JavaScript adapters must consume this exact file; do not maintain platform-specific copies.

## Run

From the repository root:

```bash
python3 language/og/python/yoro_star_codec.py language/og/test-vectors/yoro-star-v2.tsv
node language/og/javascript/test-yoro.mjs
kotlinc language/og/kotlin/YoroStarCodec.kt -include-runtime -d /tmp/yoro-codec.jar
java -jar /tmp/yoro-codec.jar language/og/test-vectors/yoro-star-v2.tsv
```

The vector set covers empty input, zero, one, boundary values, mixed bytes, and ASCII bytes. Each adapter also round-trips all 256 possible one-byte values. The Python unit test additionally checks malformed input. Kotlin/JVM and JavaScript require the same vector file path supplied at runtime.

A successful local run is evidence only for the environment in which it ran. CI should run the three commands on their respective supported runtimes before this branch is considered merge-ready.
