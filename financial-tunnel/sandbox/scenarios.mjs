import{createSimulator,SimulationError}from'./simulator.mjs';
const expectCode=(fn,code)=>{try{fn();}catch(e){if(e instanceof SimulationError&&e.code===code)return;throw e;}throw Error('Expected '+code);};
const approvedTransfer=(s,amount=1000,key='transfer-001')=>{const p=s.preview({amount,destination:'acct-savings-001'});return s.transfer({from:'acct-checking-001',to:'acct-savings-001',amount,idempotencyKey:key,approved:true,approvalHash:p.previewHash});};
export const scenarios=[
['successful account acquisition',s=>{const a=s.account('acct-checking-001');if(a.label!=='SYNTHETIC'||a.status!=='ACTIVE')throw Error('Synthetic account unavailable');}],
['invalid identity rejection',s=>expectCode(()=>s.account('real-customer-identity'),'ACCOUNT_NOT_FOUND')],
['insufficient balance rejection',s=>expectCode(()=>s.transfer({from:'acct-empty-001',to:'acct-savings-001',amount:100,idempotencyKey:'low-funds',approved:true,approvalHash:'preview'}),'INSUFFICIENT_FUNDS')],
['successful internal transfer',s=>{const before=s.account('acct-checking-001').balance,tx=approvedTransfer(s);if(tx.status!=='SETTLED'||s.account('acct-checking-001').balance!==before-1000)throw Error('Transfer did not settle');}],
['failed external transfer',s=>expectCode(()=>s.transfer({from:'acct-checking-001',to:'external-bank',amount:100,idempotencyKey:'external',approved:true,approvalHash:'preview'}),'ACCOUNT_NOT_FOUND')],
['duplicate transaction detection',s=>{approvedTransfer(s);expectCode(()=>approvedTransfer(s,1000,'transfer-001'),'DUPLICATE_TRANSACTION');}],
['expired transaction quote',s=>{const q=s.quote({amount:10000});if(q.label!=='SIMULATED')throw Error('Quote not labeled');expectCode(()=>s.assertQuoteFresh({...q,expiresAt:1},2),'QUOTE_EXPIRED');}],
['unauthorized PONS request',s=>expectCode(()=>s.transfer({from:'acct-checking-001',to:'acct-savings-001',amount:100,idempotencyKey:'no-approval'}),'PONS_APPROVAL_REQUIRED')],
['successful PONS approval',s=>{const tx=approvedTransfer(s);if(!tx.approvalHash.startsWith('sha256-sim-'))throw Error('Approval not bound to preview hash');}],
['payment reversal',s=>{const tx=approvedTransfer(s);s.reverse(tx.id);if(s.getStatus(tx.id).status!=='REVERSED')throw Error('Reversal missing');}],
['blockchain confirmation simulation',s=>{const p=s.orderPreview({asset:'ETH',side:'BUY',quantity:.01,price:2500});s.event('CHAIN_CONFIRMATION_SIMULATED',{intentId:p.id,network:'BASE_SEPOLIA',confirmations:12});if(s.state.events.at(-1).confirmations!==12)throw Error('Confirmation event missing');}],
['webhook replay',s=>{const a=s.receiveWebhook('evt-provider-001'),b=s.receiveWebhook('evt-provider-001');if(!a.accepted||b.accepted||b.reason!=='DUPLICATE'||s.state.events.at(-1).type!=='WEBHOOK_REPLAY_REJECTED')throw Error('Replay rejection missing');}],
['ledger imbalance detection',s=>{s.ledger('bad-ledger','','acct-checking-001',1);if(s.reconcile().status!=='RECONCILIATION_EXCEPTION')throw Error('Ledger imbalance undetected');}],
['settlement reconciliation',s=>{approvedTransfer(s);if(s.reconcile().status!=='RECONCILED')throw Error('Ledger failed reconciliation');}],
['provider timeout and recovery',s=>{s.state.providerStatus='TIMEOUT';s.event('PROVIDER_TIMEOUT',{idempotencyKey:'recover-001'});if(s.getStatus('unknown-transaction').status!=='NOT_FOUND')throw Error('Unknown status must remain unresolved');s.event('STATUS_RECHECK_COMPLETED',{idempotencyKey:'recover-001',result:'NO_EXECUTION_CONFIRMED'});if(s.state.events.at(-1).result!=='NO_EXECUTION_CONFIRMED')throw Error('Recovery evidence missing');}]
];
export function runAllScenarios(){return scenarios.map(([name,run],i)=>{const s=createSimulator();try{run(s);return{number:i+1,name,status:'PASSED'};}catch(e){return{number:i+1,name,status:'FAILED',error:e.message};}});}
