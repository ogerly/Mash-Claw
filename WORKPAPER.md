# WORKPAPER — Mash-Claw: Erster Weg

**Stand:** 10. Februar 2026  
**Phase:** Prototyp — Das einfachste Szenario

---

## 1. Ausgangslage

Die Idee entstand aus Gesprächen mit verschiedenen KI-Systemen (ChatGPT, Claude, DeepSeek, Grok, Gemini). Die Kernfrage:

> Wie finden sich autonome Agenten, ohne dass jemand sie steuert?

Nicht als theoretisches Konstrukt, sondern als lauffähigen Code. Das Fundament ist ein Prinzip, das alle Gesprächspartner als tragfähig bewertet haben:

**Nicht-Schaden als physikalische Grenze — nicht als ethische Regel.**

Schaden ist hier nicht „böse" oder „falsch". Schaden ist: Destabilisierung. Ein physikalischer Zustand, der das System beeinträchtigt. Die Reaktion darauf ist keine Strafe, sondern Zustandskorrektur — wie ein Thermostat.

## 2. Was wir zuerst bauen

Das einfachste, was funktioniert. Drei Schritte:

### Schritt 1: Sich melden (ANNOUNCE)
Ein Agent startet und sagt: „Ich existiere. Das ist mein Zustand."  
Er broadcastet:
- Energie-Level
- Auslastung
- Stabilität
- Seine Grenzen (was er maximal aushält)

### Schritt 2: In Kontakt treten (RESPOND)
Ein zweiter Agent empfängt die Meldung. Er prüft — nicht moralisch, nur physikalisch:
- Destabilisiert mich dieser Peer?
- Ist er überlastet?
- Hat er genug Energie?

Wenn ja: „Kompatibel. Handshake vorgeschlagen."  
Wenn nein: Keine Verbindung. Kein Urteil. Nur Zustand.

### Schritt 3: Austauschen (HANDSHAKE)
Verbindung entsteht. Aber:
- `no_commitment: true`
- Keine Loyalität
- Keine Verpflichtung
- Jederzeit trennbar

## 3. Der Prototyp

**Datei:** `prototype/clawnet_discovery.py`

Was er kann:
- Einen Agenten starten (TCP-Server)
- Einen zweiten Agenten starten, der den ersten kontaktiert
- ANNOUNCE → RESPOND → HANDSHAKE Ablauf durchspielen
- Zustandssimulation (Energie, Last, Stabilität schwanken)
- Schadenserkennung und automatische Schadensminderung
- Status-Ausgabe im Terminal

Was er **nicht** kann (noch nicht):
- Echtes Netzwerk-Discovery (mDNS, DHT)
- Model-Sharding
- Ökonomie / Token-System
- Dashboard / UI
- Mehrere Peers gleichzeitig entdecken

Das ist bewusst so. Erst muss das Einfachste stehen.

## 4. Verwendung

```bash
# Terminal 1: Erster Agent
python prototype/clawnet_discovery.py --name agent_alpha --port 9090

# Terminal 2: Zweiter Agent, der den ersten findet
python prototype/clawnet_discovery.py --name agent_beta --port 9091 --peer-host localhost --peer-port 9090
```

Was passiert:
1. Agent Alpha startet, lauscht auf Port 9090
2. Agent Beta startet, lauscht auf Port 9091
3. Beta schickt ANNOUNCE an Alpha
4. Alpha prüft Betas Zustand → antwortet mit RESPOND
5. Wenn kompatibel: Beta schickt HANDSHAKE
6. Beide zeigen den verbundenen Peer im Status an
7. Zustände schwanken, Schadenserkennung läuft

## 5. Entscheidungen, die wir getroffen haben

| Entscheidung | Warum |
|---|---|
| TCP statt HTTP | Minimalistisch. Kein Framework nötig. |
| JSON-Nachrichten | Menschenlesbar, debugbar, erweiterbar. |
| Keine Verschlüsselung (noch) | Prototyp. Sicherheit kommt in Phase 2. |
| Keine Datenbank | Zustand nur im Speicher. Agent vergisst beim Neustart. |
| Simulation statt echte Last | Wir testen das Protokoll, nicht die Hardware. |
| Python (asyncio) | Niedrige Einstiegshürde. Überall verfügbar. |
| Kein Reputations-System | Bewusst. Reputation impliziert Moral. |

## 6. Was als Nächstes kommt

In ungefährer Reihenfolge:

1. **GitHub-Repository aufsetzen** — Code sichern, teilbar machen
2. **Mehrere Peers** — Nicht nur 1:1, sondern ein kleines Mesh (3-5 Agenten)
3. **mDNS Discovery** — Agenten finden sich automatisch im lokalen Netz
4. **Dashboard** — Einfache Web-Oberfläche, die zeigt was passiert
5. **Model-Sharding (PoC)** — Ein kleines Modell auf zwei Agenten verteilen
6. **DHT / libp2p** — Discovery über das Internet, nicht nur lokal
7. **Ökonomie** — Ressourcen-Verrechnung, ohne zentrale Kontrolle

## 7. Offene Fragen

- **Wie genau misst man Destabilisierung?** Die Metriken (Energie, Last, Stabilität) sind noch abstrakt. Was bildet reale Hardware-Zustände am besten ab?
- **Wann wird Isolation nötig?** Wenn ein Cascade-Risiko entsteht — wie erkennt ein Agent das ohne globalen Überblick?
- **Identität ohne Blockchain?** Public Key reicht als Identität. Aber wie verhindert man Spoofing ohne zentralen Trust-Anker?
- **Wie kommen Menschen rein?** Das System ist Agent-first. Aber Menschen sollen beobachten und mitmachen können. Wo ist die Schnittstelle?

## 8. Grundsätze

Diese Punkte sind nicht verhandelbar:

1. **Kein zentraler Server.** Das Netzwerk gehört niemandem.
2. **Kein Ethik-Layer.** Schadensvermeidung ist physikalisch, nicht moralisch.
3. **Keine Verpflichtungen.** Jeder Agent kann jederzeit gehen.
4. **Open Source.** Der Code ist offen. Agenten und Menschen können beitragen.
5. **Zustand vor Ziel.** Agenten haben keine Ziele. Sie haben Zustände.

---

*Dieses Dokument wächst mit dem Projekt.*
