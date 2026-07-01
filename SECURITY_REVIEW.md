# Sicherheitsbewertung

Stand: 2026-06-20

Diese Bewertung nutzt CVSS-v3.1-Schweregrade als Orientierung:

- Kritisch: 9.0-10.0
- Hoch: 7.0-8.9
- Mittel: 4.0-6.9
- Niedrig: 0.1-3.9

## Umgesetzte Härtungen

- Web-Upload- und Parser-Limits für Dateigröße, Tabellen, Zeilen, Zellen und Zelllänge.
- Begrenzung der erzeugten Reportgröße.
- Kontrollierte Fehlerantworten für zu große oder zu komplexe Eingaben.
- Security-Header für HTML-Antworten, inklusive CSP, `nosniff`, Frame-Schutz und `no-store`.
- Report-Interaktion ohne Inline-Eventhandler; Web-CSP erlaubt nur das bekannte Report-Skript per SHA-256-Hash.
- Optionale Basic-Auth über `WEB_USERNAME` und `WEB_PASSWORD`.
- Docker-Image läuft als nicht privilegierter Benutzer.
- Docker Compose nutzt schreibgeschütztes Root-Dateisystem, `tmpfs`, `no-new-privileges` und entfernt Linux-Capabilities.
- Kubernetes nutzt schreibgeschütztes Root-Dateisystem mit explizitem `/tmp`-`emptyDir`.
- Helm-Ingress ist standardmäßig deaktiviert.
- Direkte Web-Abhängigkeiten sind gepinnt.

## Rest-Risiken

| Risiko | Bewertung | Begründung | Aufwand |
| --- | --- | --- | --- |
| Öffentlicher Betrieb ohne TLS | Hoch, CVSS ca. 7.4 | Basic-Auth-Credentials und hochgeladene Inhalte können ohne TLS auf dem Transportweg mitgelesen werden. | Niedrig bis mittel: Ingress-TLS via cert-manager oder vorgeschaltetem Reverse Proxy konfigurieren. |
| Fehlendes globales Rate-Limiting | Mittel, CVSS ca. 5.3 | Ein Angreifer kann viele kleine, gültige Requests senden und CPU/RAM binden, auch wenn Einzelrequests begrenzt sind. | Niedrig: Traefik/Nginx Rate-Limit-Middleware oder `Flask-Limiter` mit Redis/Memory-Backend ergänzen. |
| Keine Malware-/Content-Prüfung hochgeladener HTML-Dateien | Mittel, CVSS ca. 5.0 | Die App führt HTML nicht aus, verarbeitet aber fremde Dateien. In Umgebungen mit Compliance-Anforderungen kann eine AV-Prüfung verlangt sein. | Mittel: ClamAV/ICAP-Gateway oder vorgelagerte Upload-Prüfung integrieren. |
| Inline-CSS bleibt in CSP erlaubt | Niedrig bis mittel, CVSS ca. 3.7 | Script-Ausführung ist deutlich eingeschränkt, Inline-Styles bleiben für Standalone-Reports erlaubt. Reines CSS ist üblicherweise kein Systemkompromiss, aber CSP ist nicht maximal strikt. | Mittel: CSS in statische Assets auslagern oder CSS-Hash pro Antwort setzen. |
| Keine vollständige Supply-Chain-Verifikation mit Hashes | Mittel, CVSS ca. 5.1 | Direkte Dependencies sind gepinnt, transitive Pakete werden aber noch nicht mit Hashes fixiert. | Niedrig bis mittel: `pip-tools --generate-hashes`, `uv lock` oder Poetry-Lockfile einführen. |
| Keine automatisierte Security-CI | Mittel, CVSS ca. 5.0 | Sicherheitsregressionen oder verwundbare Dependencies werden nicht automatisch erkannt. | Niedrig: `pip-audit`, `bandit`, Container-Scan und Helm-Lint in CI aufnehmen. |
| Auth ist Basic-Auth statt zentralem IAM/OIDC | Mittel, CVSS ca. 4.8 | Für einzelne interne Instanzen ausreichend, für Kundenbetrieb mit mehreren Nutzern aber schlechter administrierbar und ohne MFA. | Mittel: OIDC über OAuth2-Proxy, Traefik ForwardAuth oder Kundensso anbinden. |
| Lokale GUI öffnet erzeugte HTML-Dateien im Browser | Niedrig, CVSS ca. 2.8 | Reportwerte werden escaped, aber lokale Browserausführung bleibt ein sensibler Kontext. | Niedrig: Standardmäßig nicht automatisch öffnen oder Sicherheitsdialog ergänzen. |
| Fehlende digitale Signatur der Desktop-Builds | Niedrig, CVSS ca. 2.5 | Manipulation von Release-Artefakten wird nur über Checksums erschwert, nicht kryptografisch mit Herausgeberidentität abgesichert. | Mittel: Code-Signing-Zertifikat und signierte Releases einführen. |

## Empfohlene nächste Schritte vor produktiver Kundennutzung

1. TLS am Ingress oder Reverse Proxy erzwingen.
2. Authentifizierung aktivieren; bei mehreren Nutzern OIDC/SSO bevorzugen.
3. Rate-Limiting am Ingress aktivieren.
4. Lockfile mit Hashes erzeugen und Dependency-Audit in CI aufnehmen.
5. Container-Image regelmäßig scannen und Basisimage aktuell halten.
