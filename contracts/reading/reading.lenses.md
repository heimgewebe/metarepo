# Reading Lenses: Canonical Taxonomy

## Purpose
Reading Lenses are a mechanism to guide attention within a repository, specifically when creating context for LLMs or human reviewers. They function as a **focus overlay**, boosting the visibility of relevant files based on the type of inquiry (e.g., "Where does the data enter?" vs. "Where is the business logic?").

## Core Principles
1.  **Focus, not Exclusion:** Lenses prioritize content (e.g., via sorting or "recommended subsets") but **never exclude** files from the merge. All context remains available.
2.  **Question-Oriented:** The choice of lens depends on the question being asked, not on the repository itself.
3.  **Canonical Categories:** To ensure consistent communication across the organism (wgx, leitstand, agents), we use a fixed set of lens IDs.

## Lens Taxonomy

The 7 canonical lenses are:

1.  **entrypoints**: Where execution begins or external interaction happens (CLI commands, API handlers, main scripts).
    *   *Question:* "Where do I start?"
2.  **core**: The central logic, decision-making algorithms, and business rules.
    *   *Question:* "How does it think/decide?"
3.  **interfaces**: Boundaries between modules, repositories, or external systems (APIs, adapters).
    *   *Question:* "How does it talk to others?"
4.  **data_models**: Static structures, schemas, contracts, and types.
    *   *Question:* "What is true? What structures exist?"
5.  **pipelines**: Flows, sequences, and orchestrations over time.
    *   *Question:* "What happens in what order?"
6.  **ui**: User interaction layers, frontends, and visualizations.
    *   *Question:* "What does the user see?"
7.  **guards**: Validation, security, safety checks, and policies.
    *   *Question:* "What is forbidden? How is it protected?"

## Usage
Tools (like `repolens`) apply these lenses to tag files and generate a "Recommended Subset". This subset is highlighted in the output, but the full file list and content are always included to prevent context loss.
