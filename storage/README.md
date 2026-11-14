# ERIA Bash M*ASH SSD Rhythm Engine

This module provides conservative filesystem-level storage operations. It does
**not** access SSD firmware, issue ATA/NVMe commands, format devices, change
partitions, or claim control over physical drive behavior.

## Commands

Run with Bash 4+ and GNU coreutils (\`sha256sum\`, \`sync\`, \`mktemp\`):

\`\`\`bash
bash storage/rhythm-engine.sh read FILE
bash storage/rhythm-engine.sh write SOURCE DESTINATION
bash storage/rhythm-engine.sh write --overwrite SOURCE DESTINATION
bash storage/rhythm-engine.sh verify SOURCE DESTINATION
bash storage/rhythm-engine.sh sync SOURCE DESTINATION
bash storage/rhythm-engine.sh checkpoint FILE [LABEL]
\`\`\`

\`write\` stages bytes in the destination directory before committing. By
default it refuses to replace an existing destination; \`--overwrite\` is an
explicit opt-in. \`sync\` writes and then verifies SHA-256 equality. A checkpoint
is a timestamped SHA-256 manifest, not a copy or restorable backup.

Set \`ERIA_STORAGE_ROOT\` to choose where the operation log and checkpoint
manifests are stored. The default is \`./eria-storage\`.

## Tests

\`\`\`bash
bash -n storage/rhythm-engine.sh
bash storage/tests/test-rhythm-engine.sh
\`\`\`

The tests use a temporary directory and never access a block device.
