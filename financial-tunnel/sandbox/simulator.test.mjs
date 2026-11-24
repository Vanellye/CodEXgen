import test from'node:test';import assert from'node:assert/strict';import{runAllScenarios}from'./scenarios.mjs';
test('all 15 deterministic financial tunnel scenarios pass',()=>{const results=runAllScenarios();assert.equal(results.length,15);assert.deepEqual(results.filter(r=>r.status!=='PASSED'),[]);});
