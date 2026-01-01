# ADR-0030 Semantic Versioning for Tool Pins

![status: accepted](https://img.shields.io/badge/status-accepted-green)

Datum: 2026-01-01  
Status: Accepted  
Owner: tooling-team

## Kontext

Tool pin scripts (`yq-pin.sh`, `just-pin.sh`, etc.) verwendeten strikte Versions-Gleichheit (`==`), was zu unnötigen Failures führte wenn Systeme neuere kompatible Versionen hatten (z.B. yq 4.50.1 vs. erwartetes 4.49.2). Dies verursachte Reibung in CI/CD und lokaler Entwicklung.

Zudem war die Versions-Vergleichslogik über 7 Scripts dupliziert, was Drift-Risiko und Wartungsaufwand erhöhte.

## Entscheidung

1. **Zentrale Semver-Library**: `scripts/lib/semver.sh` implementiert semantische Versionierung
2. **0.x-Sonderbehandlung**: Bei Major 0 muss Minor exakt matchen (Breaking Changes per SemVer-Spec möglich)
3. **0.0.x-Strictness**: Bei 0.0.x wird exakte Version verlangt (alles potentiell breaking)
4. **Opt-in Strict Mode**: Via `STRICT_VERSION_PIN=1` kann exakte Version erzwungen werden
5. **Alle Pin-Scripts nutzen Library**: Code-Duplikation eliminiert

### Versionsregeln

| Scenario | Have | Want | Result | Reason |
|----------|------|------|--------|--------|
| Exact | 4.49.2 | 4.49.2 | ✅ OK | Exact match |
| Newer Patch | 4.49.3 | 4.49.2 | ✅ OK | Compatible upgrade |
| Newer Minor | 4.50.0 | 4.49.2 | ✅ OK | Compatible upgrade |
| Different Major | 5.0.0 | 4.49.2 | ❌ FAIL | Breaking change |
| 0.x Newer Minor | 0.5.0 | 0.4.20 | ❌ FAIL | Potentially breaking |
| 0.x Newer Patch | 0.4.21 | 0.4.20 | ✅ OK | Patch upgrade safe |
| 0.0.x Newer | 0.0.2 | 0.0.1 | ❌ FAIL | Everything breaking |

## Konsequenzen

### Positiv
- Weniger false negatives bei kompatiblen neueren Versionen
- Keine Code-Duplikation (DRY-Prinzip)
- Korrekte 0.x-Behandlung per SemVer-Spec
- Opt-in Strict Mode für reproduzierbare Builds
- Zentrale Testabdeckung

### Negativ
- Determinismus wird zugunsten Praktikabilität aufgeweicht (gemildert durch Strict Mode)
- Verschiedene Runner können unterschiedliche Toolversionen nutzen (innerhalb Kompatibilitätsregeln)

### Mitigation
- `STRICT_VERSION_PIN=1` für absolute Reproduzierbarkeit
- Tools in `tools/bin/` bleiben deterministisch (kontrollierter Download)
- Nur PATH-Fallback ist tolerant

## Alternativen

1. **Status Quo beibehalten**: Führt weiter zu unnötigen Failures
2. **Alle Versionen erlauben**: Zu permissiv, Breaking Changes möglich
3. **Nur exakte 0.x erlauben**: Zu strikt, auch Patch-Updates würden fehlschlagen

## Links

- `scripts/lib/semver.sh` - Zentrale Library
- `scripts/lib/test_semver.sh` - Test Suite
- ADR-003 CI-Reusables & Pinning-Policy
- `toolchain.versions.yml` - Version Pins
