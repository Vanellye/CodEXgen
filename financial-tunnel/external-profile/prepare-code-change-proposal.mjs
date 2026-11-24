#!/usr/bin/env node
/**
 * Build a JSON proposal payload from selected local changes.
 * Does not stage, commit, push, or modify source files.
 */
import { execFileSync } from "node:child_process";
import { existsSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const REPOSITORY = "Vanellye/CodEXgen";
const BRANCH = "feature/eria-financial-tunnel";
const args = process.argv.slice(2);
const outputIndex = args.indexOf("--output");
const outputPath = outputIndex >= 0 ? args[outputIndex + 1] : "/tmp/eria-code-change-proposal.json";
const files = args.filter((arg, index) => arg !== "--output" && index !== outputIndex + 1);

function fail(message) {
  process.stderr.write(`REFUSED: ${message}\n`);
  process.exit(1);
}
let repoRoot;
function git(command, options = {}) {
  return execFileSync("git", command, { cwd: repoRoot ?? process.cwd(), encoding: "utf8", stdio: ["ignore", "pipe", "pipe"], ...options }).trimEnd();
}
function validPath(path) {
  return typeof path === "string" &&
    /^(financial-tunnel|financial)\/[A-Za-z0-9._\/-]+$/.test(path) &&
    !path.split("/").some((part) => !part || part === "." || part === "..") &&
    !/(^|\/)(\.env(?:\.|$)|\.git|secrets?)(\/|$)/i.test(path);
}

if (!files.length || files.length > 20 || new Set(files).size !== files.length || !files.every(validPath)) {
  fail("Provide 1-20 unique paths under financial-tunnel/ or financial/; environment and secret paths are excluded.");
}
const root = git(["rev-parse", "--show-toplevel"]);
repoRoot = root;
const remoteUrl = git(["remote", "get-url", "origin"]).replace(/\\.git$/, "").toLowerCase();
const branch = git(["branch", "--show-current"]);
if (!["https://github.com/vanellye/codexgen", "git@github.com:vanellye/codexgen", "ssh://git@github.com/vanellye/codexgen"].includes(remoteUrl)) fail("Origin remote is not Vanellye/CodEXgen.");
if (branch !== BRANCH) fail(`Checkout ${BRANCH} before preparing a proposal.`);
const baseSha = git(["rev-parse", "HEAD"]);
const remoteHead = git(["ls-remote", "origin", `refs/heads/${BRANCH}`]).split(/\s+/)[0];
if (remoteHead !== baseSha) fail("Local HEAD must equal the current remote feature-branch HEAD before proposing changes.");
let patch = "";
try {
  patch = git(["diff", "--no-ext-diff", "--no-color", "--no-renames", "HEAD", "--", ...files]);
} catch {
  fail("Could not generate a Git diff for the selected paths.");
}

// Include untracked, non-ignored new files without staging them.
for (const path of files) {
  if (!existsSync(resolve(root, path))) fail(`Selected path does not exist: ${path}`);
  let tracked = true;
  try { git(["ls-files", "--error-unmatch", "--", path]); } catch { tracked = false; }
  if (!tracked) {
    let addedDiff = "";
    try {
      addedDiff = execFileSync("git", ["diff", "--no-index", "--no-ext-diff", "--no-color", "--", "/dev/null", path], {
        cwd: root, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"],
      });
    } catch (error) {
      if (error.status !== 1) fail(`Could not diff new file: ${path}`);
      addedDiff = error.stdout ?? "";
    }
    addedDiff = addedDiff.replace(`diff --git a/dev/null b/${path}`, `diff --git a/${path} b/${path}`);
    patch += (patch && !patch.endsWith("\n") ? "\n" : "") + addedDiff;
  }
}
if (!patch.trim()) fail("No changes found in the selected paths.");
if (!patch.endsWith("\n")) patch += "\n";
const headers = [...patch.matchAll(/^diff --git a\/([^\n]+) b\/([^\n]+)$/gm)];
const patchFiles = headers.map((match) => match[1]);
if (headers.some((match) => match[1] !== match[2]) ||
    patchFiles.length !== files.length || new Set(patchFiles).size !== files.length || files.some((path) => !patchFiles.includes(path))) {
  fail("Generated patch does not exactly match the selected file list. Renames and deletions are not supported.");
}
const payload = { repository: REPOSITORY, branch: BRANCH, baseSha, files, patch };
const destination = resolve(outputPath);
writeFileSync(destination, JSON.stringify(payload, null, 2) + "\n", { encoding: "utf8", mode: 0o600 });
process.stdout.write(`Proposal payload prepared: ${destination}\n`);
process.stdout.write(`Base SHA: ${baseSha}\nFiles: ${files.join(", ")}\n`);
process.stdout.write("No source files were changed and nothing was staged, committed, or pushed.\n");
