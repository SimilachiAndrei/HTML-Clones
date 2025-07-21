# 🧠 HTML Document Clustering by Visual & Structural Similarity

## 📝 Problem Statement

The task is to design an algorithm that groups together **HTML documents which are visually and structurally similar**, as perceived by a human user opening them in a browser. This means:
- Pages that may differ in raw code but look alike should be clustered together.
- Pages that share layout, structure, and design but with different content should still be grouped.

The dataset contains 4 subdirectories (`tier1`, `tier2`, etc.) with increasing levels of complexity.

---

## 🚀 My Approach

### 🔄 Dual-Modality Clustering

I approached the problem by combining two powerful perspectives:

1. **Structural & Textual Similarity (SimHash)**  
   Extracted semantic content, DOM tags, and CSS class tokens from each HTML page using `readability-lxml` and `lxml`. Then, generated a SimHash fingerprint to capture overall structure and textual features.

2. **Visual Perceptual Similarity (pHash + Screenshot Rendering)**  
   Rendered each HTML file in a headless browser (via Playwright), captured a full-page screenshot, and computed a perceptual hash (`pHash`) using `imagehash`. This allowed grouping based on *how pages look* rather than just *what they contain*.

### 🔗 Graph-Based Clustering

- Constructed a **similarity graph** where each node is an HTML file.
- Edges are drawn between files if **either**:
  - Their SimHash distance ≤ `k` (default: 3)
  - Their pHash distance ≤ threshold (default: 8)
- Extracted connected components as final clusters.

This ensures pages that are similar **in any modality** (textual or visual) are grouped.

---

## 🤯 Reasoning & Tradeoffs

### ❌ Approaches I Rejected
- **Raw DOM tree comparison** – fragile to code formatting, tag nesting, or dynamic scripts.
- **Only using screenshots & CNNs** – expensive to scale, overkill for small datasets, and harder to interpret or debug.
- **Levenshtein/Tree Edit Distance** – computationally heavy and doesn’t reflect layout similarity well.

### ✅ Why This Worked Well
- SimHash offers fast, scalable similarity detection for text + structural tokens.
- Perceptual hashing is robust to minor design changes (colors, spacing, fonts).
- The dual-feature system is **resilient to noise** and **generalizes well across tiers**.

