#ifndef ERIA_FACTUAL_LOGIC_H
#define ERIA_FACTUAL_LOGIC_H
#ifdef __cplusplus
extern "C" {
#endif
typedef enum {
 ERIA_CLAIM_UNCLASSIFIED=0, ERIA_CLAIM_OBSERVED=1,
 ERIA_CLAIM_SOURCE_REPORTED=2, ERIA_CLAIM_CORROBORATED=3,
 ERIA_CLAIM_HYPOTHESIS=4, ERIA_CLAIM_INTERPRETATION=5
} EriaClaimClass;
typedef enum {
 ERIA_FACT_OK=0, ERIA_FACT_INVALID=1, ERIA_FACT_PROVENANCE_MISSING=2,
 ERIA_FACT_SUPPORT_MISSING=3, ERIA_FACT_NOT_ESTABLISHED=4,
 ERIA_FACT_OUTPUT_TOO_SMALL=5
} EriaFactStatus;
typedef struct {
 const char *claim_id, *claim_text, *source_reference, *provenance_reference, *support_reference;
 EriaClaimClass classification;
} EriaFactClaim;
/* Formats an evidence label; does not authenticate source or prove truth. */
EriaFactStatus eria_fact_describe(const EriaFactClaim *, char *, unsigned long);
#ifdef __cplusplus
}
#endif
#endif
