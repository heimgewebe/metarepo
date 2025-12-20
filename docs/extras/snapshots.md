# Snapshots & Extras

Dieses Dokument erklärt den Wahrheitspfad für Metadaten und Snapshots im Heimgewebe.

## Wahrheitspfad

1. **metarepo-sync**
   - **Aufgabe:** Verteilt Dateien (Templates, Workflows, Docs) vom Metarepo an die Fleet-Repositories.
   - **Rolle:** Distribution.

2. **sources_refresh**
   - **Aufgabe:** Baut Snapshots basierend auf den verteilten Daten.
   - **Rolle:** Aggregation.

3. **diagnostics_rebuild**
   - **Aufgabe:** Berechnet Extras ausschließlich aus Snapshots.
   - **Rolle:** Analyse & Diagnose.
