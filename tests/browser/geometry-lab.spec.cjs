const { test, expect } = require("@playwright/test");

async function setRange(page, selector, value) {
  await page.locator(selector).evaluate((el, next) => {
    el.value = String(next);
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }, value);
}

test.beforeEach(async ({ page }) => {
  await page.goto("/geometry/lab/index.html");
});

test("all four workspaces render and respond to their controls", async ({ page }) => {
  for (const id of ["curvature", "fractal", "coordinates", "projection"]) {
    await page.locator('[data-tab="' + id + '"]').click();
    await expect(page.locator("#" + id)).toBeVisible();
    await expect(page.locator("#" + id + " svg.canvas")).toBeVisible();
    await expect(page.locator("#" + id + " svg.canvas > *")).not.toHaveCount(0);
  }

  await page.locator('[data-tab="curvature"]').click();
  await setRange(page, "#curv", -0.5);
  await expect(page.locator("#curvType")).toHaveText("Hyperbolic");
  await expect(page.locator("#circumference")).not.toHaveText("6.28");

  await page.locator('[data-tab="fractal"]').click();
  await setRange(page, "#depth", 3);
  await expect(page.locator("#triangles")).toHaveText("27");
  await expect(page.locator("#fractalSvg polygon")).toHaveCount(27);

  await page.locator('[data-tab="coordinates"]').click();
  await setRange(page, "#dimension", 5);
  await expect(page.locator("#vertexCount")).toHaveText("32");
  await expect(page.locator("#edgeCount")).toHaveText("80");

  await page.locator('[data-tab="projection"]').click();
  await setRange(page, "#projDim", 5);
  await setRange(page, "#angle", 72);
  await expect(page.locator("#projVertices")).toHaveText("32");
  await expect(page.locator("#projEdges")).toHaveText("80");
  await expect(page.locator("#projectionSvg line")).toHaveCount(80);
});

test("experiment recorder saves, exports, persists, imports, and restores settings", async ({ page }) => {
  await page.locator('[data-tab="fractal"]').click();
  await setRange(page, "#depth", 5);
  await page.locator("#experimentName").fill("Sierpinski depth five");
  await page.locator("#saveExperiment").click();
  await expect(page.locator("#recorderStatus")).toContainText("Saved locally");
  await expect(page.locator("#savedExperiments option")).toHaveCount(2);

  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.locator("#exportExperiment").click()
  ]);
  const filePath = await download.path();
  const fs = require("fs");
  const record = JSON.parse(fs.readFileSync(filePath, "utf8"));
  expect(record.schema).toBe("codexgen-geometry-experiment-v1");
  expect(record.workspace).toBe("fractal");
  expect(record.parameters.fractalDepth).toBe(5);
  expect(record.results.some(x => x.value === "243")).toBeTruthy();
  expect(record.diagram).toContain("<svg");

  await page.reload();
  await expect(page.locator("#savedExperiments option")).toHaveCount(2);
  await page.locator("#savedExperiments").selectOption("0");
  await page.locator("#restoreExperiment").click();
  await expect(page.locator("#fractal")).toBeVisible();
  await expect(page.locator("#depth")).toHaveValue("5");
  await expect(page.locator("#triangles")).toHaveText("243");

  const imported = { ...record, title: "Imported reproducibility check" };
  await page.locator("#importFile").setInputFiles({
    name: "imported-experiment.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(imported))
  });
  await expect(page.locator("#recorderStatus")).toContainText("Imported");
  await expect(page.locator("#savedExperiments option")).toHaveCount(3);
  await page.locator("#savedExperiments").selectOption("0");
  await page.locator("#restoreExperiment").click();
  await expect(page.locator("#experimentName")).toHaveValue("Imported reproducibility check");
});

test("dimension changes keep the selected projection plane valid", async ({ page }) => {
  await page.locator('[data-tab="projection"]').click();
  await page.locator("#plane").selectOption("13");
  await setRange(page, "#projDim", 2);
  await expect(page.locator("#plane")).toHaveValue("01");
  await expect(page.locator("#projectionSvg circle")).toHaveCount(4);
});
