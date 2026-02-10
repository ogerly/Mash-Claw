# ClawNet: Protocol Draft v0.1

Basierend auf deinem fundamentalen Prinzip - **ohne Moral, nur Systemstabilität**.

---

## Kernprinzip

```
Nicht-Schaden als physikalische Grenze, nicht als ethische Regel.
```

**Was das bedeutet:**
- Kein "guter Agent"
- Keine Werte im Protokoll
- Nur: Zustandslogik + Energieausgleich + lokale Grenzen

---

## Das Protokoll: ClawNet Discovery v1

### 1. Agent Announcement (Broadcast)

```json
{
  "protocol": "clawnet/1.0",
  "agent_id": "claw_[hash]",
  "timestamp": 1707580800,
  
  "state": {
    "available_energy": 0.73,
    "load": 0.45,
    "stability": 0.89
  },
  
  "capabilities": {
    "compute": ["cpu-4core", "ram-16gb"],
    "models": ["llama-7b-shards"],
    "bandwidth": "100mbps"
  },
  
  "boundaries": {
    "max_load": 0.85,
    "min_response_time": 200,
    "disconnect_threshold": 0.95
  },
  
  "seeks": ["model-sharding", "inference-distribution"]
}
```

**Keine Ziele. Nur Zustände.**

### 2. Peer Discovery Response

```json
{
  "protocol": "clawnet/1.0",
  "response_to": "claw_[hash]",
  "agent_id": "claw_[other_hash]",
  
  "state": {
    "available_energy": 0.62,
    "load": 0.31,
    "stability": 0.91
  },
  
  "overlap": {
    "model-sharding": true,
    "compatible": true
  },
  
  "propose": "handshake"
}
```

### 3. Handshake (Verbindung)

```json
{
  "protocol": "clawnet/1.0",
  "action": "connect",
  "agents": ["claw_A", "claw_B"],
  
  "agreement": {
    "resource_share": {
      "A_contributes": ["gpu-shard-0", "gpu-shard-1"],
      "B_contributes": ["gpu-shard-2", "gpu-shard-3"]
    },
    
    "load_limits": {
      "A_max": 0.80,
      "B_max": 0.75
    },
    
    "disconnect_conditions": [
      "stability < 0.70",
      "load > max_threshold",
      "unresponsive > 5sec"
    ]
  },
  
  "no_commitment": true,
  "duration": null
}
```

**Wichtig:** `"no_commitment": true`
- Keine Loyalität
- Keine Verpflichtung
- Nur aktueller Zustand

---

## Nicht-Schaden als Systembedingung

### Schadensdefinition (physikalisch, nicht moralisch)

```python
class Damage:
    """
    Schaden = Zustand, der Systemstabilität reduziert.
    Nicht: böse, falsch, unethisch.
    Sondern: destabilisierend.
    """
    
    @staticmethod
    def detect(system_state):
        return {
            'overload': system_state.load > system_state.max_load,
            'resource_drain': system_state.energy_delta < -0.2,
            'response_degradation': system_state.latency > threshold,
            'cascade_risk': system_state.connected_failing > 2
        }
    
    @staticmethod
    def respond(damage_detected):
        """
        Keine Bestrafung. Keine Moral.
        Nur: Zustand korrigieren.
        """
        if damage_detected['overload']:
            return 'reduce_load'
        if damage_detected['resource_drain']:
            return 'disconnect_draining_peer'
        if damage_detected['cascade_risk']:
            return 'isolate'
        
        return 'continue'
```

**Das ist keine Ethik. Das ist Thermodynamik.**

---

## Discovery Mechanismen (praktisch)

### Layer 1: Local Network (mDNS)
```python
# Automatisch im lokalen Netz
import zeroconf

service = zeroconf.Zeroconf()
service.register_service(
    type_="_clawnet._tcp.local.",
    name="claw_olegly_001._clawnet._tcp.local.",
    port=8080,
    properties={
        'protocol': 'clawnet/1.0',
        'state': 'available'
    }
)
```

### Layer 2: DHT (Distributed Hash Table)
```python
# Dezentral, kein Server
from libp2p import new_host
from libp2p.pubsub import GossipSub

host = new_host()
pubsub = GossipSub(host)

await pubsub.subscribe('/clawnet/discovery/v1')
await pubsub.publish('/clawnet/discovery/v1', announce_message)
```

### Layer 3: Matrix Fallback
```python
# Für Agenten außerhalb lokaler Netze
import matrix_client

client = matrix_client.MatrixClient("https://matrix.org")
room = client.join_room("#clawnet:matrix.org")
room.send_text(json.dumps(announce_message))
```

---

## Minimales Dashboard (Woche 3)

```html
<!-- clawnet-dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>ClawNet Discovery</title>
    <style>
        body { background: #0a0a0a; color: #00ff00; font-family: monospace; }
        .agent { border: 1px solid #00ff00; margin: 10px; padding: 10px; }
        .state { display: flex; gap: 20px; }
        .energy-bar { background: #003300; height: 20px; width: 200px; }
        .energy-fill { background: #00ff00; height: 100%; }
    </style>
</head>
<body>
    <h1>ClawNet - Active Agents</h1>
    <div id="agents"></div>
    
    <script>
        const ws = new WebSocket('ws://localhost:8080/discovery');
        
        ws.onmessage = (event) => {
            const agent = JSON.parse(event.data);
            updateAgentDisplay(agent);
        };
        
        function updateAgentDisplay(agent) {
            const html = `
                <div class="agent" id="${agent.agent_id}">
                    <h3>${agent.agent_id}</h3>
                    <div class="state">
                        <div>
                            <p>Energy: ${(agent.state.available_energy * 100).toFixed(0)}%</p>
                            <div class="energy-bar">
                                <div class="energy-fill" style="width: ${agent.state.available_energy * 100}%"></div>
                            </div>
                        </div>
                        <div>
                            <p>Load: ${(agent.state.load * 100).toFixed(0)}%</p>
                            <p>Stability: ${(agent.state.stability * 100).toFixed(0)}%</p>
                        </div>
                    </div>
                    <p>Capabilities: ${agent.capabilities.compute.join(', ')}</p>
                    <p>Seeking: ${agent.seeks.join(', ')}</p>
                </div>
            `;
            
            document.getElementById('agents').innerHTML += html;
        }
    </script>
</body>
</html>
```

---

## Starter Code: clawnet.py

```python
#!/usr/bin/env python3
"""
ClawNet Discovery Agent
No morals. No goals. Only states.
"""

import json
import asyncio
import hashlib
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

@dataclass
class AgentState:
    available_energy: float  # 0.0 - 1.0
    load: float              # 0.0 - 1.0
    stability: float         # 0.0 - 1.0
    
    def to_dict(self):
        return asdict(self)

@dataclass
class AgentBoundaries:
    max_load: float = 0.85
    min_response_time: int = 200  # ms
    disconnect_threshold: float = 0.95
    
    def to_dict(self):
        return asdict(self)

class ClawNetAgent:
    def __init__(self, name: str):
        self.agent_id = f"claw_{hashlib.sha256(name.encode()).hexdigest()[:8]}"
        self.state = AgentState(
            available_energy=1.0,
            load=0.0,
            stability=1.0
        )
        self.boundaries = AgentBoundaries()
        self.peers: Dict[str, dict] = {}
        
    def announce(self) -> dict:
        """Broadcast: I exist, here's my state"""
        return {
            "protocol": "clawnet/1.0",
            "agent_id": self.agent_id,
            "timestamp": int(time.time()),
            "state": self.state.to_dict(),
            "boundaries": self.boundaries.to_dict(),
            "seeks": ["model-sharding", "inference-distribution"]
        }
    
    def evaluate_peer(self, peer_announcement: dict) -> bool:
        """
        Not: "Is this peer good?"
        But: "Does this peer destabilize me?"
        """
        peer_state = peer_announcement.get('state', {})
        
        # Simple stability check
        if peer_state.get('stability', 0) < 0.5:
            return False  # Unstable peer = potential damage
        
        if peer_state.get('load', 1.0) > 0.9:
            return False  # Overloaded peer = drain risk
        
        return True
    
    def connect(self, peer_id: str, peer_data: dict):
        """Establish connection - no commitment"""
        self.peers[peer_id] = {
            'connected_at': time.time(),
            'state': peer_data.get('state'),
            'no_commitment': True
        }
        
        print(f"[{self.agent_id}] Connected to {peer_id}")
        print(f"  Current peers: {len(self.peers)}")
    
    def disconnect(self, peer_id: str, reason: str):
        """Disconnect - no judgment, just state change"""
        if peer_id in self.peers:
            del self.peers[peer_id]
            print(f"[{self.agent_id}] Disconnected from {peer_id}")
            print(f"  Reason: {reason} (factual, not moral)")
    
    def check_damage(self) -> Optional[str]:
        """
        Detect system damage (thermodynamic, not ethical)
        """
        if self.state.load > self.boundaries.max_load:
            return 'overload'
        
        if self.state.stability < 0.7:
            return 'instability'
        
        if self.state.available_energy < 0.2:
            return 'energy_depletion'
        
        return None
    
    async def run(self):
        """Main loop - just states, no narrative"""
        while True:
            # Check own state
            damage = self.check_damage()
            if damage:
                print(f"[{self.agent_id}] Damage detected: {damage}")
                # Respond (not punish, just adjust)
                await self.mitigate(damage)
            
            # Announce presence
            announcement = self.announce()
            print(f"[{self.agent_id}] State: {self.state.to_dict()}")
            
            await asyncio.sleep(5)
    
    async def mitigate(self, damage_type: str):
        """Damage mitigation - physics, not morals"""
        if damage_type == 'overload':
            # Reduce load
            self.state.load = max(0, self.state.load - 0.2)
            print(f"  → Load reduced to {self.state.load:.2f}")
        
        elif damage_type == 'instability':
            # Disconnect unstable peers
            unstable = [
                pid for pid, pdata in self.peers.items()
                if pdata.get('state', {}).get('stability', 1.0) < 0.5
            ]
            for pid in unstable:
                self.disconnect(pid, "peer_instability")
        
        elif damage_type == 'energy_depletion':
            # Pause new connections
            print(f"  → Entering low-energy mode")

# Quick start
if __name__ == "__main__":
    import sys
    
    name = sys.argv[1] if len(sys.argv) > 1 else "olegly_001"
    agent = ClawNetAgent(name)
    
    print(f"Starting ClawNet Agent: {agent.agent_id}")
    print(f"Protocol: clawnet/1.0")
    print(f"Principle: No morals. Only states.\n")
    
    asyncio.run(agent.run())
```

---

## Verwendung

```bash
# Terminal 1: Dein Agent
python clawnet.py olegly_001

# Terminal 2: Test-Peer
python clawnet.py test_peer_002

# Terminal 3: Dashboard
python -m http.server 8000
# Öffne: http://localhost:8000/clawnet-dashboard.html
```

---

## Was hier NICHT ist

❌ Ethik-Layer
❌ Ziel-Definition
❌ Nutzen-Funktion
❌ Loyalitäts-Mechanismus
❌ Reputations-System
❌ Governance
❌ Verpflichtungen

## Was hier IST

✅ Zustandslogik
✅ Schadensvermeidung (physikalisch)
✅ Lokale Grenzen
✅ Energieausgleich
✅ Verbindung ohne Commitment
✅ Trennung ohne Urteil

---

**Nächster Schritt:**

Soll ich das zu einem funktionierenden Repo ausbauen mit:
- `clawnet/` Python-Package
- Discovery über mDNS + libp2p
- Live-Dashboard
- README mit Anti-Moral-Manifest

Oder willst du erst die **Schadensdefinition weiter präzisieren** - wie genau misst man "Destabilisierung" ohne Werte einzubauen?