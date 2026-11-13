# ERIA BAM/CRAM execution gate

## Parent and immutable anchor

- Repository: `Vanellye/CodEXgen`
- Immutable source baseline: `2cce68f258f46058f18c108c264db9cc85200590`
- Parent adapter proposal: PR #49, branch `eria/multiomics-format-adapters`
- This gate branch: `eria/bam-cram-execution-gate`
- Target for this proposal: PR #49 branch, not `main`.

The source baseline remains a fixed comparison anchor. This gate does not rewrite
history or alter the parent branch until separately reviewed and adopted.

## Behavior

An explicit call to `Eria.MultiOmics.Adapters.SAM.decode_file/2` with a BAM or
CRAM path performs conversion as part of that call:

1. Check that the input is a regular file and within the configured byte limit.
2. Compute a SHA-256 digest of the original binary input.
3. Resolve the format from the file extension; require a reference path for CRAM.
4. Invoke the configured `samtools` executable with an argv list via
   `System.cmd/3`, never via a shell command string.
5. Write to a unique temporary SAM path.
6. Require a successful process exit and a nonempty output within the configured
   byte limit.
7. Parse the generated SAM through the existing structural validator.
8. Return source format, source digest, tool/version, exit status, output digest,
   output byte count, and parsed records.
9. Remove the temporary SAM file on both success and failure.

This is automatic only inside the explicit ingestion call. There is no
background watcher, implicit trigger based on file presence, network dispatch,
or physical actuation.

## Validation

The CI job installs samtools and tests real BAM and CRAM fixture conversions,
including the explicit-reference requirement for CRAM. The parser still
performs structural SAM checks; it does not certify mapping quality, sequence
quality, variant significance, or clinical validity.

## Independent boundaries

- Instrument connections and vendor SDK adapters are not included.
- Calibration registries and calibration verification are not included.
- Clinical diagnosis and clinical recommendations are not produced.
- Biological modification and physical actuation are not authorized.
- Pantheon IC transmission remains a separate contract/integration gate.

## Review checklist

- [ ] Confirm exact source and branch SHAs.
- [ ] Review argument construction and ensure no shell interpolation.
- [ ] Review file-size bounds and temporary-file cleanup paths.
- [ ] Run BAM and CRAM integration fixtures on the declared samtools version.
- [ ] Verify error paths for missing reference, missing tool, failed conversion,
      malformed output, and size-limit violations.
- [ ] Confirm parent PR #49 and main remain unchanged until explicit adoption.
