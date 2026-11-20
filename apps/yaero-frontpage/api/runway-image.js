export default async function handler(req, res) {
  if (req.method === "GET") {
    return res.status(200).json({ configured: Boolean(process.env.RUNWAYML_API_SECRET) });
  }
  if (req.method !== "POST") {
    res.setHeader("Allow", "GET, POST");
    return res.status(405).json({ error: "Method not allowed" });
  }
  const apiKey = process.env.RUNWAYML_API_SECRET;
  if (!apiKey) {
    return res.status(503).json({ error: "Runway Dev is not configured. Add RUNWAYML_API_SECRET to the Vercel project's server environment." });
  }
  const promptText = typeof req.body?.promptText === "string" ? req.body.promptText.trim() : "";
  if (!promptText || promptText.length > 2000) {
    return res.status(400).json({ error: "promptText must contain 1–2000 characters." });
  }
  try {
    const response = await fetch("https://api.dev.runwayml.com/v1/text_to_image", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "X-Runway-Version": "2024-11-06",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ model: "gen4_image", ratio: "1920:1080", promptText })
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      return res.status(response.status).json({ error: payload.error || payload.message || "Runway Dev rejected the request." });
    }
    return res.status(202).json({ id: payload.id, status: payload.status || "PENDING" });
  } catch {
    return res.status(502).json({ error: "Could not reach Runway Dev. No source files were changed." });
  }
}
