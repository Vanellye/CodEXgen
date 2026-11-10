# Study 02 — Non-Euclidean Geometry

**Status:** Established mathematics  
**Scope:** Spherical geometry and hyperbolic geometry as two standard geometries that differ from the Euclidean plane.  
**Purpose:** Understand how changing curvature and the parallel postulate changes distance, geodesics, and triangle geometry.

## 1. The central distinction

In Euclidean geometry, the sum of the interior angles of a triangle is \(\pi\) radians. In curved geometries, this sum depends on curvature and triangle area.

A **geodesic** is a locally length-minimizing path (more generally, a path satisfying the geodesic equation). In a curved space, geodesics play the role that straight lines play in the Euclidean plane.

## 2. Spherical geometry

A sphere of radius R in \(\mathbb R^3\) is

\[
S_R^2=\{x\in\mathbb R^3:\|x\|=R\}.
\]

Its geodesics are great circles: intersections of the sphere with planes through its center. The shortest geodesic segment between two non-antipodal points is the shorter great-circle arc.

For central angle \(\theta\in[0,\pi]\), the spherical distance is

\[
d(P,Q)=R\theta.
\]

### Triangle angle excess

For a nondegenerate spherical triangle with interior angles A, B, C,

\[
A+B+C>\pi.
\]

Its area is

\[
\operatorname{Area}=R^2(A+B+C-\pi),
\]

where angles are in radians. The quantity \(E=A+B+C-\pi\) is the spherical excess.

**Example.** A spherical triangle with three right angles has excess \(3\pi/2-\pi=\pi/2\), so its area is \(\pi R^2/2\), one-eighth of the sphere's total area \(4\pi R^2\).

There are no globally distinct parallel great circles: any two great circles intersect at antipodal points.

## 3. Hyperbolic geometry

Hyperbolic geometry has constant negative curvature. A useful model is the Poincaré disk

\[
D=\{(x,y):x^2+y^2<1\}
\]

with metric

\[
ds^2=\frac{4R^2(dx^2+dy^2)}{(1-x^2-y^2)^2}.
\]

This metric has constant Gaussian curvature \(-1/R^2\). Its geodesics are diameters or circular arcs meeting the boundary circle orthogonally. The boundary circle is not part of the hyperbolic plane; points near it are infinitely far away in the hyperbolic metric.

### Triangle angle defect

For a hyperbolic triangle with angles A, B, C,

\[
A+B+C<\pi,
\]

and its area is

\[
\operatorname{Area}=R^2(\pi-A-B-C).
\]

The angle defect is positive and proportional to area.

Through any point outside a given line, hyperbolic geometry admits more than one line that does not meet the given line. This contrasts with the Euclidean uniqueness statement.

## 4. Curvature comparison

| Geometry | Constant curvature | Triangle angle sum |
|---|---:|---|
| Euclidean plane | 0 | exactly \(\pi\) |
| Sphere of radius R | \(+1/R^2\) | greater than \(\pi\) |
| Hyperbolic plane, scale R | \(-1/R^2\) | less than \(\pi\) |

For constant-curvature surfaces, the angle-sum deviation records curvature through the Gauss–Bonnet theorem. The spherical and hyperbolic area formulas above are special constant-curvature cases.

## 5. Why the geometry matters

- **Spherical:** global navigation on Earth or idealized planetary surfaces; shortest routes follow great circles, not generally straight lines on a flat map.
- **Hyperbolic:** models of negatively curved spaces, idealized networks, and geometric structures where exponential divergence of geodesics is important.
- **Euclidean:** flat-space designs and local approximations.

A map projection can preserve selected properties while distorting others. It cannot preserve all spherical distances, areas, and angles globally in a flat map.

## 6. Coordinate and interpretation cautions

- State whether distances are intrinsic (measured within the surface) or extrinsic (measured through the surrounding space).
- The Poincaré disk preserves angles locally (conformal) but does not preserve Euclidean lengths.
- A disk picture is a model of the entire hyperbolic plane; its circular edge is an ideal boundary, not a physical wall.
- Curved geometry is mathematical structure; it does not, by itself, establish a physical cosmological model.

## 7. Study questions

1. Why do great circles serve as spherical geodesics?
2. How does the spherical excess formula scale when R is doubled?
3. What does the Poincaré disk preserve, and what does it distort?
4. How can triangle angle measurements reveal the sign of constant curvature?

Related: [Dimensions and coordinates](../DIMENSIONS-COORDINATES.md), [Conjectures and open questions](../CONJECTURES-OPEN-QUESTIONS.md), [Dimension and projection map](../../visuals/dimension-projection-map.svg).

## 8. Further reading

- H. S. M. Coxeter, *Non-Euclidean Geometry*, 6th edition.
- James W. Anderson, *Hyperbolic Geometry*, 2nd edition.
- John M. Lee, *Riemannian Manifolds: An Introduction to Curvature*.
