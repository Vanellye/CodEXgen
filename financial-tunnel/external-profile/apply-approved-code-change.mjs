#!/usr/bin/env node
/**
 * Apply one ADMIN-approved ERIA code-change proposal to a clean local feature branch.
 * This tool never pushes, merges, changes branches, or writes to main.
 */
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const REPOSITORY = "Vanellye/CodEXgen";
const BRANCH = "feature/eria-financial-tunnel";
const API_BASE = (process.env.ERIA_API_BASE ?? "http://127.0.0.1:8787").replace(/\/$/, "");
const token = process.env.ERIA_API_TOKEN;
const args = process.argv.slice(2);
const checkOnly = args.includes("--check");
const proposalId = args.find((arg) => arg !== "--check");

function fail(message) {
  process.stderr.write(`REFUSED: ${message}\n`);
  process.exit(1);
}
let repoRoot;
function git(args) {
  return execFileSync("git", args, { cwd: repoRoot ?? process.cwd(), encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
}
function validPath(path) {
  return typeof path === "string" &&
    /^(financial-tunnel|financial)\/[A-Za-z0-9._\/-]+$/.test(path) &&
    !path.split("/").some((part) => !part || part === "." || part === "..") &&
    !/(^|\/)(\.env(?:\.|$)|\.git|secrets?)(\/|$)/i.test(path);
}
function sortedEqual(a, b) {
  return [...a].sort().join("\n") === [...b].sort().join("\n");
}

if (!token) fail("Set ERIA_API_TOKEN to a sandbox-issued Auth0 access token. Do not paste it into chat.");
if (!proposalId || !/^[0-9a-f-]{36}$/i.test(proposalId)) {
  fail("Usage: ERIA_API_TOKEN=<token> node financial-tunnel/external-profile/apply-approved-code-change.mjs <proposal-id> [--check]");
}

const response = await fetch(`${API_BASE}/v1/code-change-proposals/${proposalId}`, {
  headers: { authorization: `Bearer ${token}`, accept: "application/json" },
});
if (!response.ok) fail(`Proposal lookup returned HTTP ${response.status}.`);
const result = await response.json();
const proposal = result.proposal;
const decision = result.decision;
if (!proposal || !decision || result.status !== "APPROVED_NOT_APPLIED" || decision.decision !== "ALLOW") {
  fail("Proposal does not have a recorded ADMIN ALLOW decision.");
}
if (proposal.repository !== REPOSITORY || proposal.branch !== BRANCH) fail("Proposal repository or target branch is not permitted.");
if (proposal.proposerProfileId === decision.approverProfileId || proposal.proposerSubject === decision.approverSubject) {
  fail("Maker-checker identity separation is not satisfied.");
}
if (!/^[0-9a-f]{40}$/i.test(proposal.baseSha) || !Array.isArray(proposal.files) ||
    proposal.files.length < 1 || proposal.files.length > 20 || !proposal.files.every(validPath)) {
  fail("Proposal base SHA or file allowlist is invalid.");
}
if (typeof proposal.patch !== "string" || Buffer.byteLength(proposal.patch, "utf8") > 128 * 1024) {
  fail("Patch is missing or exceeds the 128 KiB limit.");
}
const digest = createHash("sha256").update(proposal.patch, "utf8").digest("hex");
if (digest !== proposal.patchSha256) fail("Patch digest does not match the approved proposal.");
const headers = [...proposal.patch.matchAll(/^diff --git a\/([^\n]+) b\/([^\n]+)$/gm)];
const patchFiles = headers.map((match) => match[1]);
const contentHeaders = [...proposal.patch.matchAll(/^(---|\+\+\+) (?:([ab]\/[^\n]+)|(\/dev\/null))$/gm)];
if (!headers.length || headers.some((match) => match[1] !== match[2] || !validPath(match[1])) ||
    !sortedEqual(patchFiles, proposal.files) || contentHeaders.length !== headers.length * 2 ||
    contentHeaders.some((match) => match[1] === "+++" ? !match[2] || !validPath(match[2].slice(2)) || !proposal.files.includes(match[2].slice(2)) :
      (match[3] !== "/dev/null" && (!match[2] || !validPath(match[2].slice(2)) || !proposal.files.includes(match[2].slice(2)))))) {
  fail("Patch file headers do not exactly match the approved file allowlist.");
}

let root, currentBranch, head, remoteHead, status, remoteUrl;
try {
  root = git(["rev-parse", "--show-toplevel"]);
  repoRoot = root;
  remoteUrl = git(["remote", "get-url", "origin"]).replace(/\.git$/, "").toLowerCase();
  currentBranch = git(["branch", "--show-current"]);
  head = git(["rev-parse", "HEAD"]);
  remoteHead = git(["ls-remote", "origin", `refs/heads/${BRANCH}`]).split(/\s+/)[0];
  status = git(["status", "--porcelain"]);
} catch {
  fail("Run this script inside a Git checkout with an origin remote.");
}
if (!["https://github.com/vanellye/codexgen", "git@github.com:vanellye/codexgen", "ssh://git@github.com/vanellye/codexgen"].includes(remoteUrl)) fail("Origin remote is not Vanellye/CodEXgen.");
if (currentBranch !== BRANCH) fail(`Current branch must be ${BRANCH}; no branch switching is performed.`);
if (head !== proposal.baseSha || remoteHead !== proposal.baseSha) {
  fail("Local HEAD and remote feature-branch HEAD must both equal the proposal base SHA. Rebase or submit a fresh proposal.");
}
if (status) fail("Working tree is not clean. Preserve or commit your existing changes before applying this proposal.");

const tempDir = mkdtempSync(join(tmpdir(), "eria-approved-change-"));
const patchFile = join(tempDir, "approved.patch");
try {
  writeFileSync(patchFile, proposal.patch, { encoding: "utf8", mode: 0o600 });
  execFileSync("git", ["apply", "--check", "--index", patchFile], { cwd: root, stdio: "inherit" });
  if (checkOnly) {
    process.stdout.write(`CHECK PASS: proposal ${proposalId} is approved and applies cleanly to ${BRANCH} at ${head}. No files changed.\n`);
  } else {
    execFileSync("git", ["apply", "--index", patchFile], { cwd: root, stdio: "inherit" });
    const staged = git(["diff", "--cached", "--name-only"]).split("\n").filter(Boolean);
    if (!sortedEqual(staged, proposal.files)) throw new Error("Staged file list differs from the approved allowlist; inspect the working tree before proceeding.");
    execFileSync("git", ["diff", "--cached", "--check"], { cwd: root, stdio: "inherit" });
    const message = [
      `Apply ADMIN-approved code change ${proposalId}`,
      "",
      `ERIA-Admin-Decision: ${decision.id}`,
      `ERIA-Patch-SHA256: ${digest}`,
      `ERIA-Base-SHA: ${proposal.baseSha}`,
    ].join("\n");
    execFileSync("git", ["commit", "-m", message], { cwd: root, stdio: "inherit" });
    process.stdout.write(`LOCAL COMMIT CREATED: ${git(["rev-parse", "HEAD"])}\n`);
    process.stdout.write("Not pushed. Review the commit before any separate push or PR action.\n");
  }
} finally {
  rmSync(tempDir, { recursive: true, force: true });
}
