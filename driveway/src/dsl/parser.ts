export interface DrivewaySpec { project?: string; ledger?: string; accounts: Array<{id:string;name:string;kind:string;currency:string}>; rules: string[]; workflows: string[]; }
export function parseDriveway(source: string): DrivewaySpec {
  const result: DrivewaySpec = { accounts: [], rules: [], workflows: [] };
  let section: "none" | "accounts" | "rules" | "workflows" = "none";
  for (const raw of source.split(/\\r?\\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    let match: RegExpExecArray | null;
    if ((match = /^project\\s+"([^"]+)"$/.exec(line))) { result.project = match[1]; section = "none"; continue; }
    if ((match = /^ledger\\s+"([^"]+)":$/.exec(line))) { result.ledger = match[1]; section = "none"; continue; }
    if (/^accounts:$/.test(line)) { section = "accounts"; continue; }
    if (/^rules:$/.test(line)) { section = "rules"; continue; }
    if (/^workflow\\s+"([^"]+)":$/.test(line)) { result.workflows.push(RegExp.$1); section = "workflows"; continue; }
    if (section === "accounts" && (match = /^-\\s+([\\w-]+)\\s+(.+)$/.exec(line))) {
      const [name, kind, currency] = match[2].split(/\\s+/);
      if (!name || !kind || !currency) throw new Error(`Invalid account declaration: ${line}`);
      result.accounts.push({ id: match[1], name, kind, currency }); continue;
    }
    if (section === "rules" || section === "workflows") { (section === "rules" ? result.rules : result.workflows).push(line); continue; }
    if (/^(currency|mode|immutable)\\s+/.test(line)) continue;
    throw new Error(`Unrecognized Driveway DSL statement: ${line}`);
  }
  return result;
}
