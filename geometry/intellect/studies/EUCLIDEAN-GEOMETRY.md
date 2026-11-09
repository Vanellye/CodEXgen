# Study 01 — Euclidean Geometry

**Status:** Established mathematics  
**Scope:** Plane and three-dimensional Euclidean geometry, with the plane as the primary worked setting.  
**Purpose:** Study geometry with a flat metric, ordinary distance, and the Euclidean parallel postulate.

## 1. Mathematical setting

The Euclidean plane is modeled as \(\mathbb R^2\) with its standard inner product

\[
\langle (x_1,y_1),(x_2,y_2)\rangle=x_1x_2+y_1y_2.
\]

The induced norm and distance are

\[
\|v\|=\sqrt{\langle v,v\rangle},\qquad
d(P,Q)=\sqrt{(x_Q-x_P)^2+(y_Q-y_P)^2}.
\]

A line is an affine set \(P+t v\), where \(v\ne 0\) and \(t\in\mathbb R\). A circle with center \(C\) and radius \(r>0\) is the set of points whose distance from C is r.

## 2. Axiomatic foundation

Euclidean geometry can be developed from several equivalent axiom systems. In the classical presentation, the parallel postulate distinguishes Euclidean geometry from many non-Euclidean alternatives. One modern formulation is:

**Parallel postulate (Playfair form).** Given a line \(\ell\) and a point P not on it, there is exactly one line through P that does not intersect \(\ell\).

The precise formal foundations depend on the chosen axiom system; this study uses familiar Euclidean results without claiming that one short list is a complete formalization.

## 3. The distance formula

**Theorem.** For points \(P=(x_1,y_1)\) and \(Q=(x_2,y_2)\) in the Euclidean plane,

\[
d(P,Q)^2=(x_2-x_1)^2+(y_2-y_1)^2.
\]

**Derivation.** The displacement vector is \(Q-P=(x_2-x_1,y_2-y_1)\). By the standard inner product, its squared norm is the sum of the squares of its coordinates. Distance is the norm of this displacement. This is the coordinate form of the Pythagorean theorem.

## 4. Pythagorean theorem

**Theorem.** In a right triangle with legs a and b and hypotenuse c,

\[
a^2+b^2=c^2.
\]

**Proof by similarity.** Drop the altitude from the right-angle vertex to the hypotenuse. Let the hypotenuse segments be p and q, so \(p+q=c\). The two smaller right triangles are similar to the original triangle. Similarity gives \(a^2=cp\) and \(b^2=cq\) (with a and b assigned to their corresponding opposite segments). Adding,

\[
a^2+b^2=c(p+q)=c^2.
\]

The proof assumes a nondegenerate right triangle with positive side lengths.

## 5. Circle geometry

For radius r:

- Circumference: \(C=2\pi r\).
- Area: \(A=\pi r^2\).
- In Cartesian coordinates with center \((h,k)\): \((x-h)^2+(y-k)^2=r^2\).

The formulas depend on the Euclidean metric. They should not be transferred unchanged to spherical or hyperbolic geometry.

## 6. Worked coordinate example

Let \(P=(1,2)\) and \(Q=(4,6)\). Then

\[
d(P,Q)=\sqrt{(4-1)^2+(6-2)^2}
=\sqrt{9+16}=5.
\]

The calculation is an exact consequence of the metric, not a measurement.

## 7. Geometric reasoning and construction

A compass-and-straightedge construction is specified by allowed operations, not by the visual appearance of the finished diagram. For example, the perpendicular bisector of segment AB is the locus of points X satisfying \(d(X,A)=d(X,B)\). It can be constructed by intersecting equal-radius circles centered at A and B, with radius greater than half the segment length.

## 8. Design rationale

Euclidean geometry is appropriate when the model assumes a flat space and when ordinary distances, angles, parallelism, and rigid motions are the intended invariants. It is often suitable for local engineering drawings, planar layouts, and ordinary-scale designs where curvature is negligible.

It may be unsuitable for global navigation on a sphere, spacetime models, or phenomena where curvature is essential.

## 9. Limitations and links

- Euclidean parallelism is an axiom-level feature of this geometry, not a universal truth for every geometric space.
- A drawing can distort scale; proofs must use definitions and logical steps.
- The coordinate model is one representation of Euclidean geometry, not the only one.

Related: [Definitions and notation](../DEFINITIONS-NOTATION.md), [Axioms and proofs](../AXIOMS-THEOREMS-PROOFS.md), [Shape atlas](../../visuals/shape-atlas.svg).

## 10. Further reading

- Euclid, *Elements*, especially Books I–IV.
- H. S. M. Coxeter, *Introduction to Geometry*, 2nd edition.
- Robin Hartshorne, *Geometry: Euclid and Beyond*.
