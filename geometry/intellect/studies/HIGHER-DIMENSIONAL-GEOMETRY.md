# Study 04 — Higher-Dimensional Geometry

**Status:** Established mathematics  
**Scope:** Finite-dimensional real vector spaces, Euclidean n-space, coordinate systems, hypercubes, and projections.  
**Purpose:** Build precise mathematics for dimensions beyond the familiar plane and ordinary 3D space.

## 1. Euclidean n-space

The standard n-dimensional Euclidean space is

\[
\mathbb R^n=\{(x_1,\ldots,x_n):x_i\in\mathbb R\}.
\]

Its standard inner product is

\[
\langle x,y\rangle=\sum_{i=1}^{n}x_i y_i,
\]

and the induced norm and distance are

\[
\|x\|=\sqrt{\sum_{i=1}^{n}x_i^2},
\qquad
d(x,y)=\|x-y\|.
\]

The standard basis consists of the n coordinate vectors \(e_1,\ldots,e_n\). Every vector has a unique expression as a linear combination of this basis.

## 2. Dimension is not a picture

The dimension of a finite-dimensional vector space is the number of vectors in any basis. It is an algebraic property, independent of how the space is drawn.

A 4D object cannot be displayed directly in a 2D screen. A visualization must use a projection, cross-section, coordinate table, or another encoding. Such representations can be useful, but they discard or distort information.

## 3. The n-dimensional hypercube

The unit n-cube is

\[
[0,1]^n=\{x\in\mathbb R^n:0\le x_i\le1\text{ for all }i\}.
\]

Its vertices are all binary coordinate tuples, so the number of vertices is

\[
V_n=2^n.
\]

Its edges connect pairs of vertices that differ in exactly one coordinate. There are n choices of coordinate direction, and for each direction there are \(2^{n-1}\) choices of the remaining binary coordinates. Therefore

\[
E_n=n2^{n-1}.
\]

Examples: square (n=2): 4 vertices, 4 edges; cube (n=3): 8 vertices, 12 edges; tesseract (n=4): 16 vertices, 32 edges.

## 4. Pythagorean theorem in n dimensions

For vectors x and y in \(\mathbb R^n\), the Euclidean distance is the square root of the sum of squared coordinate differences:

\[
d(x,y)^2=\sum_{i=1}^{n}(x_i-y_i)^2.
\]

This follows directly from the standard inner product. It is the n-dimensional extension of the familiar coordinate distance formula.

## 5. Volume of an n-dimensional ball

The n-ball of radius R is

\[
B_n(R)=\{x\in\mathbb R^n:\|x\|\le R\}.
\]

Its volume (n-dimensional Lebesgue measure) is

\[
V_n(R)=\frac{\pi^{n/2}}{\Gamma(n/2+1)}R^n,
\]

where \(\Gamma\) is the gamma function. For positive integers n this recovers the familiar formulas: interval length for n=1, disk area for n=2, and sphere-enclosed volume for n=3.

This is volume in the mathematical n-dimensional measure, not a claim that a higher-dimensional object can be physically measured by ordinary 3D volume.

## 6. Projections and cross-sections

A linear projection is a linear map from one vector space to another. A coordinate projection, for example, can discard selected coordinates:

\[
\pi(x_1,\ldots,x_n)=(x_1,\ldots,x_k),\quad k<n.
\]

Projection generally loses information. A cross-section instead intersects an object with a subspace or affine subspace. These operations are different and should not be described interchangeably.

## 7. Worked example: tesseract counts

For n=4:

\[
V_4=2^4=16,\qquad E_4=4\cdot2^3=32.
\]

A tesseract has 16 vertices and 32 edges. A common 3D drawing uses a projected inner cube and outer cube connected by edges. That drawing is a projection, not a literal 3D containment of one cube inside another in the full 4D geometry.

## 8. Coordinate systems and transformations

A basis change changes coordinates while representing the same vector. In Euclidean space, orthogonal transformations preserve the inner product and hence preserve distances and angles. General invertible linear transformations need not preserve either.

State the transformation class and the invariants it preserves whenever a higher-dimensional object is drawn or manipulated.

## 9. Study questions

1. Why is the number of vertices of an n-cube \(2^n\)?
2. Derive the edge-count formula \(n2^{n-1}\) by counting coordinate directions.
3. What information does a projection from \(\mathbb R^4\) to \(\mathbb R^3\) discard?
4. How does a basis change differ from a projection?
5. Which transformations preserve Euclidean distances?

Related: [Dimensions and coordinates](../DIMENSIONS-COORDINATES.md), [Dimension and projection map](../../visuals/dimension-projection-map.svg), [Shape atlas](../../visuals/shape-atlas.svg).

## 10. Further reading

- John M. Lee, *Introduction to Smooth Manifolds*, 2nd edition.
- John M. Lee, *Riemannian Manifolds: An Introduction to Curvature*.
- H. S. M. Coxeter, *Regular Polytopes*, 3rd edition.
