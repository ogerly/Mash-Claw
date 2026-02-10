#!/usr/bin/env python3
"""
ClawNet Discovery Prototype
============================

Das einfachste Szenario:
- Agenten melden sich an (ANNOUNCE)
- Agenten antworten (RESPOND)  
- Agenten verbinden sich — oder nicht (HANDSHAKE)

Keine Moral. Keine Ziele. Nur Zustände.

Verwendung:
    python clawnet_discovery.py --name agent_alpha
    python clawnet_discovery.py --name agent_beta --port 9091

Protokoll: clawnet/1.0
"""

import argparse
import asyncio
import hashlib
import json
import random
import time
from dataclasses import dataclass, asdict, field
from typing import Optional


# ---------------------------------------------------------------------------
# Datenstrukturen
# ---------------------------------------------------------------------------

@dataclass
class AgentState:
    """Zustand eines Agenten — physikalisch, nicht moralisch."""
    available_energy: float = 1.0   # 0.0 – 1.0
    load: float = 0.0               # 0.0 – 1.0
    stability: float = 1.0          # 0.0 – 1.0

    def is_healthy(self) -> bool:
        return self.stability > 0.5 and self.load < 0.9 and self.available_energy > 0.2


@dataclass
class AgentBoundaries:
    """Lokale Grenzen — der Agent bestimmt sie selbst."""
    max_load: float = 0.85
    disconnect_threshold: float = 0.70
    min_energy: float = 0.15


@dataclass
class PeerInfo:
    """Was wir über einen Peer wissen."""
    agent_id: str
    state: AgentState
    connected_at: float = 0.0
    last_seen: float = 0.0


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class ClawNetAgent:
    """
    Ein ClawNet-Agent.
    
    Er kann:
    - sich ankündigen (ANNOUNCE)
    - auf Ankündigungen antworten (RESPOND)
    - Verbindungen eingehen (HANDSHAKE) — ohne Verpflichtung
    - Verbindungen trennen — ohne Urteil
    - Schaden erkennen — physikalisch, nicht ethisch
    """

    def __init__(self, name: str, port: int = 9090):
        self.name = name
        self.agent_id = f"claw_{hashlib.sha256(name.encode()).hexdigest()[:8]}"
        self.port = port
        self.state = AgentState()
        self.boundaries = AgentBoundaries()
        self.peers: dict[str, PeerInfo] = {}
        self._server: Optional[asyncio.Server] = None

    # --- Protokoll-Nachrichten ---

    def make_announce(self) -> dict:
        """ANNOUNCE: Ich existiere. Das ist mein Zustand."""
        return {
            "protocol": "clawnet/1.0",
            "type": "ANNOUNCE",
            "agent_id": self.agent_id,
            "name": self.name,
            "timestamp": time.time(),
            "state": asdict(self.state),
            "boundaries": asdict(self.boundaries),
        }

    def make_respond(self, to_agent_id: str, compatible: bool) -> dict:
        """RESPOND: Ich sehe dich. Kompatibel — oder nicht."""
        return {
            "protocol": "clawnet/1.0",
            "type": "RESPOND",
            "agent_id": self.agent_id,
            "response_to": to_agent_id,
            "timestamp": time.time(),
            "state": asdict(self.state),
            "compatible": compatible,
            "propose": "handshake" if compatible else None,
        }

    def make_handshake(self, peer_id: str) -> dict:
        """HANDSHAKE: Verbindung. Keine Verpflichtung."""
        return {
            "protocol": "clawnet/1.0",
            "type": "HANDSHAKE",
            "agent_id": self.agent_id,
            "peer_id": peer_id,
            "timestamp": time.time(),
            "no_commitment": True,
        }

    # --- Bewertung ---

    def evaluate_peer(self, peer_state: dict) -> bool:
        """
        Nicht: 'Ist der Peer gut?'
        Sondern: 'Destabilisiert mich der Peer?'
        """
        stability = peer_state.get("stability", 0)
        load = peer_state.get("load", 1.0)
        energy = peer_state.get("available_energy", 0)

        if stability < 0.5:
            return False  # Instabiler Peer = Risiko
        if load > 0.9:
            return False  # Überlasteter Peer = Drain
        if energy < 0.15:
            return False  # Erschöpfter Peer = keine Kapazität
        return True

    # --- Schadenserkennung ---

    def detect_damage(self) -> Optional[str]:
        """Schaden = Destabilisierung. Nicht: böse. Sondern: physikalisch."""
        if self.state.load > self.boundaries.max_load:
            return "overload"
        if self.state.stability < self.boundaries.disconnect_threshold:
            return "instability"
        if self.state.available_energy < self.boundaries.min_energy:
            return "energy_depletion"
        return None

    def mitigate(self, damage: str):
        """Schadensminderung — Physik, nicht Moral."""
        if damage == "overload":
            self.state.load = max(0.0, self.state.load - 0.2)
            self._log(f"Last reduziert → {self.state.load:.2f}")
        elif damage == "instability":
            # Instabilste Peers trennen
            unstable = [
                pid for pid, p in self.peers.items()
                if p.state.stability < 0.5
            ]
            for pid in unstable:
                self.disconnect_peer(pid, "peer_instability")
        elif damage == "energy_depletion":
            self._log("Energiesparmodus aktiv")

    # --- Verbindungsverwaltung ---

    def add_peer(self, agent_id: str, state_dict: dict):
        """Peer aufnehmen — keine Loyalität, nur aktueller Zustand."""
        peer_state = AgentState(**state_dict)
        self.peers[agent_id] = PeerInfo(
            agent_id=agent_id,
            state=peer_state,
            connected_at=time.time(),
            last_seen=time.time(),
        )
        self._log(f"Verbunden mit {agent_id} (Peers: {len(self.peers)})")

    def disconnect_peer(self, agent_id: str, reason: str):
        """Trennung — kein Urteil, nur Zustandsänderung."""
        if agent_id in self.peers:
            del self.peers[agent_id]
            self._log(f"Getrennt von {agent_id} — Grund: {reason} (faktisch, nicht moralisch)")

    # --- Netzwerk (TCP, minimalistisch) ---

    async def start_server(self):
        """Lauscht auf eingehende Nachrichten."""
        self._server = await asyncio.start_server(
            self._handle_connection, "0.0.0.0", self.port
        )
        self._log(f"Lauscht auf Port {self.port}")

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Eingehende Nachricht verarbeiten."""
        try:
            data = await asyncio.wait_for(reader.read(4096), timeout=5.0)
            if not data:
                return
            msg = json.loads(data.decode())
            await self._process_message(msg, writer)
        except (json.JSONDecodeError, asyncio.TimeoutError):
            pass
        finally:
            writer.close()
            await writer.wait_closed()

    async def _process_message(self, msg: dict, writer: asyncio.StreamWriter):
        """Nachricht nach Typ verarbeiten."""
        msg_type = msg.get("type")
        sender_id = msg.get("agent_id", "?")
        sender_state = msg.get("state", {})

        if msg_type == "ANNOUNCE":
            self._log(f"← ANNOUNCE von {sender_id}")
            compatible = self.evaluate_peer(sender_state)
            response = self.make_respond(sender_id, compatible)
            writer.write(json.dumps(response).encode())
            await writer.drain()

            if compatible:
                self._log(f"  Peer {sender_id} ist kompatibel → Handshake")
                self.add_peer(sender_id, sender_state)
            else:
                self._log(f"  Peer {sender_id} destabilisiert — kein Handshake")

        elif msg_type == "HANDSHAKE":
            self._log(f"← HANDSHAKE von {sender_id}")
            if sender_id in self.peers:
                self._log(f"  Verbindung bestätigt mit {sender_id}")

    async def discover_peer(self, host: str, port: int):
        """Aktiv einen Peer kontaktieren."""
        try:
            reader, writer = await asyncio.open_connection(host, port)

            # ANNOUNCE senden
            announce = self.make_announce()
            self._log(f"→ ANNOUNCE an {host}:{port}")
            writer.write(json.dumps(announce).encode())
            await writer.drain()

            # Antwort lesen
            data = await asyncio.wait_for(reader.read(4096), timeout=5.0)
            if data:
                response = json.loads(data.decode())
                self._log(f"← RESPOND: kompatibel={response.get('compatible')}")

                if response.get("compatible") and response.get("propose") == "handshake":
                    peer_id = response.get("agent_id")
                    self.add_peer(peer_id, response.get("state", {}))

                    # Handshake senden
                    handshake = self.make_handshake(peer_id)
                    reader2, writer2 = await asyncio.open_connection(host, port)
                    writer2.write(json.dumps(handshake).encode())
                    await writer2.drain()
                    writer2.close()
                    await writer2.wait_closed()
                    self._log(f"→ HANDSHAKE an {peer_id}")

            writer.close()
            await writer.wait_closed()

        except (ConnectionRefusedError, asyncio.TimeoutError, OSError) as e:
            self._log(f"Peer {host}:{port} nicht erreichbar ({type(e).__name__})")

    # --- Simulation ---

    def simulate_activity(self):
        """Simuliert leichte Zustandsveränderungen (für den Prototyp)."""
        self.state.load = min(1.0, max(0.0, self.state.load + random.uniform(-0.05, 0.08)))
        self.state.available_energy = min(1.0, max(0.0, self.state.available_energy + random.uniform(-0.03, 0.02)))
        self.state.stability = min(1.0, max(0.0, self.state.stability + random.uniform(-0.02, 0.03)))

    # --- Hauptschleife ---

    async def run(self, discover_host: Optional[str] = None, discover_port: Optional[int] = None):
        """Agent starten und laufen lassen."""
        await self.start_server()

        # Einmalig: Peer entdecken, falls angegeben
        if discover_host and discover_port:
            await asyncio.sleep(1)  # Server des Peers Zeit geben
            await self.discover_peer(discover_host, discover_port)

        # Hauptschleife
        tick = 0
        while True:
            tick += 1
            self.simulate_activity()

            # Schadenserkennung
            damage = self.detect_damage()
            if damage:
                self._log(f"⚠ Schaden erkannt: {damage}")
                self.mitigate(damage)

            # Status alle 3 Ticks ausgeben
            if tick % 3 == 0:
                self._print_status()

            await asyncio.sleep(2)

    def _print_status(self):
        """Aktuellen Zustand anzeigen."""
        s = self.state
        print(f"\n{'='*50}")
        print(f"  {self.name} ({self.agent_id})")
        print(f"  Energie: {s.available_energy:.0%}  "
              f"Last: {s.load:.0%}  "
              f"Stabilität: {s.stability:.0%}")
        print(f"  Peers: {len(self.peers)}  "
              f"Gesund: {'ja' if s.is_healthy() else 'NEIN'}")
        if self.peers:
            for pid, p in self.peers.items():
                print(f"    ↔ {pid} (stabil: {p.state.stability:.0%})")
        print(f"{'='*50}\n")

    def _log(self, message: str):
        ts = time.strftime("%H:%M:%S")
        print(f"[{ts}] [{self.name}] {message}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="ClawNet Discovery Prototype — Agenten finden sich.",
        epilog="Keine Moral. Keine Ziele. Nur Zustände.",
    )
    parser.add_argument("--name", default="agent_alpha", help="Name des Agenten")
    parser.add_argument("--port", type=int, default=9090, help="Port zum Lauschen")
    parser.add_argument("--peer-host", default=None, help="Host eines bekannten Peers")
    parser.add_argument("--peer-port", type=int, default=None, help="Port eines bekannten Peers")
    args = parser.parse_args()

    agent = ClawNetAgent(name=args.name, port=args.port)

    print(f"""
╔══════════════════════════════════════════════╗
║  ClawNet Discovery Prototype v0.1            ║
║  Agent:    {agent.name:<33s} ║
║  ID:       {agent.agent_id:<33s} ║
║  Port:     {agent.port:<33d} ║
║  Protokoll: clawnet/1.0                      ║
║                                              ║
║  Keine Moral. Nur Zustände.                  ║
╚══════════════════════════════════════════════╝
""")

    try:
        asyncio.run(agent.run(
            discover_host=args.peer_host,
            discover_port=args.peer_port,
        ))
    except KeyboardInterrupt:
        print(f"\n[{agent.name}] Beendet. Keine Verpflichtung. Keine Schuld.")


if __name__ == "__main__":
    main()
