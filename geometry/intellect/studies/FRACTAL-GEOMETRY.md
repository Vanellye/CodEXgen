# Study 03 — Fractal Geometry

**Status:** Established mathematical framework; each dimension claim below is tied to its stated definition and hypotheses.  
**Scope:** Self-similarity, iterated constructions, Hausdorff dimension, and similarity-dimension examples.  
**Purpose:** Study sets whose geometric complexity is not adequately described by ordinary integer dimension alone.

## 1. What is a fractal?

There is no single definition that captures every object called a fractal in all mathematical contexts. Common features include structure across scales, recursive construction, and non-integer dimension. A rigorous study must name the dimension concept being used.

A fractal may be an exact mathematical set or an approximation used in modeling. Natural coastlines, clouds, and biological branching are not automatically exact mathematical fractals; their scaling behavior is assessed over finite measurement ranges.

## 2. Similarity maps and iterated function systems

A similarity with ratio r (where \(0<r<1\)) scales all distances by r, possibly followed by a rigid motion.

An iterated function system (IFS) is a finite collection of contractions \(f_1,\ldots,f_m\). Under standard contraction hypotheses, there is a unique nonempty compact attractor K satisfying

\[
K=\bigcup_{i=1}^{m}f_i(K).
\]

This equation expresses recursive self-similarity.

## 3. Similarity dimension

For m similarities with a common contraction ratio r, the similarity dimension s is defined by

\[
m r^s=1
\quad\Longrightarrow\quad
s=\frac{\log m}{\log(1/r)}.
\]

For systems with unequal ratios \(r_i\), the corresponding similarity-dimension equation is

\[
\sum_i r_i^s=1.
\]

Under an appropriate separation condition (for example, the open set condition), the Hausdorff dimension of the self-similar attractor equals this similarity dimension. Without suitable separation assumptions, the equation need not give the Hausdorff dimension.

## 4. Worked examples

### Middle-third Cantor set

At each stage, retain two copies, each scaled by \(1/3\). Thus

\[
2(1/3)^s=1,
\qquad s=\frac{\log 2}{\log 3}\approx0.6309.
\]

The set is uncountable but has zero one-dimensional length (Lebesgue measure).

### Sierpiński triangle

The standard construction retains three copies scaled by \(1/2\):

\[
3(1/2)^s=1,
\qquad s=\frac{\log 3}{\log 2}\approx1.585.
\]

Its Hausdorff dimension lies strictly between the dimension of a line and the dimension of a plane.

### Koch curve

Each segment is replaced by four segments of one-third the original length:

\[
4(1/3)^s=1,
\qquad s=\frac{\log 4}{\log 3}\approx1.262.
\]

The limiting curve has infinite length, despite being contained in a bounded region.

## 5. Hausdorff dimension

For a set X in a metric space, the s-dimensional Hausdorff measure is built by covering X with sets of small diameter and taking the limiting infimum of the sums of the s-th powers of those diameters. The Hausdorff dimension is the critical exponent at which this measure changes from infinite to zero.

Informally, Hausdorff dimension generalizes the familiar integer dimensions of points, curves, surfaces, and volumes. The formal definition is based on coverings and limits, not on visual roughness alone.

## 6. Important distinctions

- **Topological dimension** and **Hausdorff dimension** measure different properties.
- **Similarity dimension** is a calculation from contraction ratios; it equals Hausdorff dimension only under suitable conditions.
- A finite digital image has a resolution limit. Its estimated dimension can depend on scale range and method.
- A natural object may exhibit approximate scaling over a limited range without being exactly self-similar at every scale.

## 7. Study questions

1. Why does the Cantor set have a non-integer Hausdorff dimension?
2. Which separation assumptions justify identifying similarity dimension with Hausdorff dimension?
3. How does finite measurement resolution affect a box-counting estimate?
4. What is lost when a recursive mathematical construction is represented by a finite raster image?

Related: [Conjectures and open questions](../CONJECTURES-OPEN-QUESTIONS.md), [Geometric reasoning](../GEOMETRIC-REASONING.md).

## 8. Further reading

- Kenneth Falconer, *Fractal Geometry: Mathematical Foundations and Applications*, 3rd edition.
- Benoît B. Mandelbrot, *The Fractal Geometry of Nature*.
- Gerald A. Edgar, *Measure, Topology, and Fractal Geometry*, 2nd edition.
