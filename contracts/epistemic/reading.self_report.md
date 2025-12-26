# Reading Self-Report: Epistemic Traceability

## Purpose
The Reading Self-Report is a mechanism to document the "epistemic footprint" of a context generation or reading process. It answers the question: **"What did the system actually see?"**

In large repositories, LLMs and agents often operate on truncated data or metadata-only views. This creates a risk of hallucination where the system *claims* knowledge about a file it has never actually read. The Self-Report makes this gap visible.

## Core Principles
1.  **Traceability, Not Gatekeeping:** A "High Risk" report is not a failure; it is a signal. It allows downstream systems (and humans) to weigh the confidence of the generated output.
2.  **Evidence Types:**
    *   `full`: The complete file content was included.
    *   `snippet`: Only a part of the file (e.g., first 50 lines) was included.
    *   `meta`: Only the file path and metadata (size, last modified) were included.
3.  **Negation Trail:** By explicitly listing `claims_without_contact`, the system can flag areas where it inferred logic without seeing the source code.

## Usage
Tools generating merge contexts (like `repolens`) should emit this self-report as a JSON sidecar or a structured Markdown section. This allows the consumer (agent or human) to assess whether the context is sufficient for the task at hand.
