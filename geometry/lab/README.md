# Interactive Mathematical Laboratory

A dependency-free, browser-based exploration tool for the Geometry & Design library.

## Open the lab

Open [the laboratory](index.html) in a modern browser. It is a single self-contained HTML file: CSS, SVG rendering, controls, and mathematical calculations are included inline. It requires no package install, build step, network connection, account, or backend.

## Workspaces

| Workspace | Adjustable inputs | Computed or rendered output |
|---|---|---|
| Curvature | Constant Gaussian curvature and geodesic radius | Geodesic-polar grid, circumference, disk area, and circumference-to-Euclidean ratio |
| Fractals | Sierpiński iteration depth (0–7) | Recursive triangle construction, remaining triangle count, scale, similarity dimension, and area fraction |
| Coordinates | Hypercube dimension (1–10) | Sign-vector coordinates, projected vertex/edge graph, vertex count, edge count, and square-face count |
| Projections | Hypercube dimension (2–8), rotation angle, coordinate rotation plane | Rotated orthographic 2D projection with projected vertices and edges |

## Mathematical model notes

### Constant curvature

For a 2D space of constant Gaussian curvature k, geodesic polar circumference is C(r) = 2π S_k(r), where:

- S_k(r) = r for k = 0.
- S_k(r) = sin(√k r) / √k for k > 0.
- S_k(r) = sinh(√−k r) / √−k for k < 0.

The disk area is A(r) = 2π ∫₀ʳ S_k(t) dt. Positive-curvature radius is capped below the antipodal distance for a stable local display. The SVG is a geodesic-polar coordinate illustration; it is not an embedding of every global surface.

### Fractal iteration

The Sierpiński triangle starts with one equilateral triangle and replaces each filled triangle by its three corner triangles at every iteration. At depth n, there are 3ⁿ filled triangles, each with side scale 2⁻ⁿ; the remaining area fraction is (3/4)ⁿ. Its similarity dimension is log(3) / log(2), under the standard self-similar construction.

### Coordinate hypercubes

An n-cube's vertices are all vectors in {−1,+1}ⁿ. Edges join pairs differing in one coordinate. Counts are 2ⁿ vertices, n·2ⁿ⁻¹ edges, and binomial(n,2)·2ⁿ⁻² square faces for n ≥ 2.

### Projections

The projection workspace rotates sign-vector vertices in a selected coordinate plane, then maps them into a two-dimensional orthographic view using a deterministic pair of view directions. A projection can overlap distinct vertices and edges and does not preserve all distances or angles. It must not be mistaken for the original n-dimensional object.

## Reproducibility and boundaries

- All calculations run in the browser using JavaScript and SVG; no remote service is called.
- Inputs and formulas are visible in the source file.
- Rendered diagrams are computational illustrations, not proofs.
- No biological, medical, or physical effect is implied by the mathematical models.
- Browser rendering has finite resolution; fractal depth is intentionally bounded to keep the interface responsive.
- This is a browser lab, not an Android-native screen or an APK.

## Related mathematics

- [Euclidean geometry](../intellect/studies/EUCLIDEAN-GEOMETRY.md)
- [Non-Euclidean geometry](../intellect/studies/NON-EUCLIDEAN-GEOMETRY.md)
- [Fractal geometry](../intellect/studies/FRACTAL-GEOMETRY.md)
- [Higher-dimensional geometry](../intellect/studies/HIGHER-DIMENSIONAL-GEOMETRY.md)
- [Geometrical Intellect](../intellect/README.md)
