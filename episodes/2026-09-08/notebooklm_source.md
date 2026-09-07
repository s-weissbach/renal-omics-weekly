# Renal Omics Weekly — source guide for 8 September 2026

## Editorial brief

Audience: an industry computational biologist working in renal translational research. Explain what is new, how the evidence was generated, what could change in analysis or translational strategy, and the strongest limitation. Distinguish reported results from interpretation. End with **Today's Classic**.

## 1. COAST: image-guided alignment of consecutive multi-modal tissue slides

- Authors: Benedetta Manzato, Claudio Novella Rausell, Gangqi Wang, et al.; Ton J. Rabelink and Ahmed Mahfouz
- Published online: 3 September 2026, *Cell Reports Methods*
- DOI: https://doi.org/10.1016/j.crmeth.2026.101575
- Full article landing page: https://www.sciencedirect.com/science/article/pii/S2667237526002766
- Why it matters: COAST registers consecutive tissue sections using only their associated images, without requiring shared molecular features or prior cell annotations. The authors benchmark across spatial technologies, tissues and resolutions. In mouse kidney ischemia-reperfusion injury, they align spatial transcriptomics with metabolomics/lipidomics, enabling molecular features on adjacent sections to be studied as one multi-modal tissue map.
- Questions for the hosts: When does image-only registration outperform feature-based methods? How should uncertainty from non-identical consecutive sections propagate downstream? What validation is needed before trusting cell-type-specific metabolite assignments?

## 2. IRAP inhibition and kidney ageing

- Authors: Sarah L. Walton, Ayesha Ansari, Karin M. Mirabito Colafella, et al.; Kate M. Denton
- Published: 3 September 2026, *Clinical Science*
- DOI: https://doi.org/10.1042/CS20261576
- PubMed: https://pubmed.ncbi.nlm.nih.gov/42690146/
- Why it matters: In aged mice, loss of insulin-regulated aminopeptidase (IRAP) protected against decline in glomerular filtration, fibrosis and renal senescence. A four-week IRAP-inhibitor intervention in very old wild-type mice recapitulated parts of the protective phenotype. Proximal-tubule experiments suggest that mitigation of oxidative-stress-induced senescence may involve mitochondrial metabolic state.
- Questions for the hosts: How convincing is the pharmacology versus the knockout? What is the causal chain between IRAP, mitochondrial function and senescence? Which safety and target-engagement studies would be needed for translation?

## 3. Ageas: time-agnostic cell-fate inference

- Authors: Jiaqi Jiang, Ang Kong and Guanghua Yu
- Posted: 3 September 2026, bioRxiv preprint
- DOI/stable page: https://doi.org/10.64898/2026.08.30.748098
- Why it matters: Ageas learns a representation of fate memory from terminal populations and transfers it to progenitor or intermediate cells, aiming to infer fate bias from a static molecular snapshot. It uses an adaptive ensemble with automated model selection to generalize across transcriptomic, epigenomic and spatial modalities. Benchmarks use lineage-traced datasets; a 3D human embryo application reports spatial gradients of fate priming.
- Questions for the hosts: What biological assumptions make terminal-to-progenitor transfer identifiable? How does it compare with RNA velocity, optimal transport and lineage-tracing-aware models? What failure modes matter in injured kidney, where terminal states may be reversible or pathologic?

## 4. Immature neutrophils and MPO in cardio-renal disease

- Authors: Sabrina Vondenhoff, Alexandra Antwerpen, Carlos V. C. Junho, et al.; Joachim Jankowski, Rafael Kramann and colleagues
- Published: 1 September 2026, *Acta Physiologica*
- DOI: https://doi.org/10.1111/apha.70290
- Full article: https://onlinelibrary.wiley.com/doi/full/10.1111/apha.70290
- PubMed: https://pubmed.ncbi.nlm.nih.gov/42613304/
- Why it matters: Two male cohorts with moderate-to-advanced CKD showed lower neutrophil CD10 and increased circulating myeloperoxidase relative to controls, without clear increases in common surface-activation markers or ex-vivo NET formation. The phenotype was not explained by measured CRP, IL-6 or NT-proBNP. It suggests altered neutrophil maturation as a candidate contributor to cardiovascular risk in CKD.
- Questions for the hosts: How strong is the evidence that the signal is kidney-driven rather than age, medication or cardiovascular comorbidity? What single-cell, proteomic or longitudinal study would separate mechanism from association? Emphasize the all-male and small-cohort limitations.

## Today's Classic — Park et al., 2018

- Title: Single-cell transcriptomics of the mouse kidney reveals potential cellular targets of kidney disease
- Authors: Jihwan Park, Rahul Shrestha, Chen Qiu, et al.; Katalin Susztak
- Published: 2018, *Science*
- DOI: https://doi.org/10.1126/science.aar2131
- Free full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC6188645/
- Why it remains foundational: The study profiled 57,979 healthy mouse kidney cells, mapped disease genes to differentiated cell types, and described a collecting-duct transitional population. Trajectory analysis and lineage tracing implicated Notch-mediated transitions between intercalated and principal-cell states, with disease-associated shifts toward principal-cell fate.
- Recap angle: Which conclusions became durable field assumptions, which depended on early-generation single-cell technology, and how would spatial and multi-omic tools now test the same hypotheses?

