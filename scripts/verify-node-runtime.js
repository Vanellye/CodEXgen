'use strict';

var fs = require('fs');
var path = require('path');

var manifestPath = path.join(__dirname, '..', 'pantheon', 'node-runtime.json');
var manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
var expected = manifest.version;
var actual = process.versions.node;

if (manifest.runtime !== 'node' || manifest.policy !== 'exact') {
  throw new Error('Invalid Pantheon Node.js runtime manifest');
}

if (actual !== expected) {
  console.error('Pantheon runtime mismatch: expected Node.js ' + expected + ', got ' + actual);
  process.exit(1);
}

console.log('Pantheon shared runtime verified: Node.js ' + actual);
console.log('Policy: every Pantheon Node.js target process must use this exact version.');
