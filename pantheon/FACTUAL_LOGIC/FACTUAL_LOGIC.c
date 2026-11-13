#include "FACTUAL_LOGIC.h"
#include <stdio.h>
EriaFactStatus eria_fact_describe(const EriaFactClaim *c,char *out,unsigned long cap)
{
 const char *label; int n;
 if(!c||!out||!cap||!c->claim_id||!c->claim_id[0]||!c->claim_text||!c->claim_text[0]) return ERIA_FACT_INVALID;
 if(!c->source_reference||!c->source_reference[0]||!c->provenance_reference||!c->provenance_reference[0]) return ERIA_FACT_PROVENANCE_MISSING;
 switch(c->classification) {
 case ERIA_CLAIM_OBSERVED: label="OBSERVED; scope and method must be stated"; break;
 case ERIA_CLAIM_SOURCE_REPORTED: label="SOURCE-REPORTED; not independently corroborated"; break;
 case ERIA_CLAIM_CORROBORATED:
  if(!c->support_reference||!c->support_reference[0]) return ERIA_FACT_SUPPORT_MISSING;
  label="CORROBORATED; supporting reference supplied, not infallible"; break;
 case ERIA_CLAIM_HYPOTHESIS: label="HYPOTHESIS; not established fact"; break;
 case ERIA_CLAIM_INTERPRETATION: label="INTERPRETATION; not established fact"; break;
 default: return ERIA_FACT_NOT_ESTABLISHED;
 }
 n=snprintf(out,(size_t)cap,"Claim: %s\nClass: %s\nSource: %s\nProvenance: %s\nSupport: %s\n",c->claim_text,label,c->source_reference,c->provenance_reference,(c->support_reference&&c->support_reference[0])?c->support_reference:"NONE");
 if(n<0||(unsigned long)n>=cap) return ERIA_FACT_OUTPUT_TOO_SMALL;
 return ERIA_FACT_OK;
}
