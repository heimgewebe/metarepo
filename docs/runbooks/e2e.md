# Historischer E2E-Pfad: aussensensor → chronik → heimlern

> **Status:** archiviert und bedingungslos stillgelegt.

Der frühere direkte Push von Außen-Events zu Heimlern ist kein aktiver Betriebsweg mehr.
Heimlern ist eine archivierte Referenz ohne Ingest-, Runtime-, Queue-, Routing- oder
Produktionsautorität. Die Dateien `scripts/e2e/run_aussen_to_heimlern.sh` und
`scripts/e2e/report.sh` bleiben als eindeutige Kompatibilitäts-Tombstones erhalten und
brechen immer mit Exit-Code 64 ab. Umgebungsvariablen können diesen Zustand nicht umgehen.

Normative Vertragskopien und vorhandene historische Reports bleiben als Belege erhalten.
Aktive Datenflüsse werden aus aktuellen Verträgen, Systemkatalog und Runtime-Readbacks abgeleitet.
