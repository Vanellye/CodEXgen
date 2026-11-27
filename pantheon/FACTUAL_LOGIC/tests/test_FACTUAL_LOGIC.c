#include <assert.h>
#include <string.h>
#include <stdio.h>
#include "FACTUAL_LOGIC.h"
int main(void) {
 char out[512];
 EriaFactClaim c={"c1","A sample claim","src1","prov1","support1",ERIA_CLAIM_CORROBORATED};
 assert(eria_fact_describe(&c,out,sizeof out)==ERIA_FACT_OK);
 assert(strstr(out,"CORROBORATED")!=0);
 c.classification=ERIA_CLAIM_HYPOTHESIS;
 assert(eria_fact_describe(&c,out,sizeof out)==ERIA_FACT_OK);
 assert(strstr(out,"not established fact")!=0);
 c.classification=ERIA_CLAIM_CORROBORATED; c.support_reference=0;
 assert(eria_fact_describe(&c,out,sizeof out)==ERIA_FACT_SUPPORT_MISSING);
 c.support_reference="support1"; c.provenance_reference=0;
 assert(eria_fact_describe(&c,out,sizeof out)==ERIA_FACT_PROVENANCE_MISSING);
 c.provenance_reference="prov1"; c.classification=ERIA_CLAIM_UNCLASSIFIED;
 assert(eria_fact_describe(&c,out,sizeof out)==ERIA_FACT_NOT_ESTABLISHED);
 c.classification=ERIA_CLAIM_SOURCE_REPORTED;
 assert(eria_fact_describe(&c,out,4)==ERIA_FACT_OUTPUT_TOO_SMALL);
 assert(eria_fact_describe(0,out,sizeof out)==ERIA_FACT_INVALID);
 puts("PASS: ERIA factual-logic core tests"); return 0;
}
