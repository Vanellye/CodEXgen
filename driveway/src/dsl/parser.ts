export interface DrivewayAccount {
  id: string;
  type: "asset" | "liability" | "equity" | "income" | "expense";
  source?: string; network?: string; unit?: string;
}
export interface DrivewayRule { name: string; expression?: string; valuationOnly: boolean; }
export interface DrivewayWorkflow { name: string; steps: string[]; }
export interface DrivewaySpec {
  project?: string; ledger?: string; currency?: string; mode?: "double_entry"; immutable?: boolean;
  accounts: DrivewayAccount[]; rules: DrivewayRule[]; workflows: DrivewayWorkflow[];
}
export function parseDriveway(source: string): DrivewaySpec {
  const result: DrivewaySpec = { accounts: [], rules: [], workflows: [] };
  let section: "root" | "ledger" | "account" | "rule" | "workflow" = "root";
  let account: DrivewayAccount | undefined, rule: DrivewayRule | undefined, workflow: DrivewayWorkflow | undefined;
  const lines = source.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i], line = raw.trim(), indent = raw.length - raw.trimStart().length;
    if (!line || line.startsWith("#")) continue;
    if (indent === 0) {
      account = undefined; rule = undefined; workflow = undefined;
      let m: RegExpExecArray | null;
      if ((m = /^project\s+"([^"]+)"$/.exec(line))) { result.project = m[1]; section = "root"; continue; }
      if ((m = /^ledger\s+"([^"]+)":$/.exec(line))) { result.ledger = m[1]; section = "ledger"; continue; }
      if ((m = /^account\s+"([^"]+)":$/.exec(line))) { account = { id:m[1], type:"asset" }; result.accounts.push(account); section="account"; continue; }
      if ((m = /^rule\s+"([^"]+)":$/.exec(line))) { rule = { name:m[1], valuationOnly:false }; result.rules.push(rule); section="rule"; continue; }
      if ((m = /^workflow\s+"([^"]+)":$/.exec(line))) { workflow = { name:m[1], steps:[] }; result.workflows.push(workflow); section="workflow"; continue; }
      throw new Error(\`Line \${i+1}: unrecognized declaration: \${line}\`);
    }
    if (indent < 2) throw new Error(\`Line \${i+1}: nested statements must be indented by at least two spaces\`);
    const pair = /^([a-z_]+)\s+(.+)$/.exec(line);
    if (section === "ledger" && pair) {
      const [,key,value] = pair;
      if (key === "currency") result.currency = value;
      else if (key === "mode" && value === "double_entry") result.mode = "double_entry";
      else if (key === "immutable" && value === "true") result.immutable = true;
      else throw new Error(\`Line \${i+1}: unsupported ledger setting: \${line}\`);
      continue;
    }
    if (section === "account" && account && pair) {
      const [,key,value] = pair;
      if (key === "type" && ["asset","liability","equity","income","expense"].includes(value)) account.type = value as DrivewayAccount["type"];
      else if (key === "source") account.source = value;
      else if (key === "network") account.network = value;
      else if (key === "unit") account.unit = value;
      else throw new Error(\`Line \${i+1}: unsupported account setting: \${line}\`);
      continue;
    }
    if (section === "rule" && rule) {
      const v = /^valuation_only\s+(true|false)$/.exec(line);
      if (v) { rule.valuationOnly = v[1] === "true"; continue; }
      if (/^\d+(?:\.\d+)?\s+[A-Z][A-Z0-9_]*\s*=\s*\d+(?:\.\d+)?\s+[A-Z][A-Z0-9_]*$/.test(line)) { rule.expression = line; continue; }
      throw new Error(\`Line \${i+1}: invalid rule statement: \${line}\`);
    }
    if (section === "workflow" && workflow) {
      if (/^requireles?$/i.test(line)) throw new Error(\`Line \${i+1}: incomplete approval statement; use "require approval before posting"\`);
      if (/^require approval before posting$/.test(line) || /^(read|verify|check)\s+[a-z_]+$/.test(line)) { workflow.steps.push(line); continue; }
      throw new Error(\`Line \${i+1}: unsupported workflow step: \${line}\`);
    }
    throw new Error(\`Line \${i+1}: statement is not valid in the current block: \${line}\`);
  }
  if (!result.project || !result.ledger) throw new Error("A project and ledger declaration are required");
  if (!result.currency || result.mode !== "double_entry" || result.immutable !== true) throw new Error("Ledger must declare currency, double_entry mode, and immutable true");
  return result;
}
