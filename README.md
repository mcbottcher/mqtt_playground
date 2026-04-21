# mqtt_playground
A template project for testing out different MQTT concepts. Run two clients and a broker locally. Simply alter code in *client_a* and *client_b* to test different things.

## Branches

Each branch demonstrates a different MQTT concept. You can checkout a branch to explore a specific feature, or use `main` as a clean base to experiment on your own.

| Branch | Description |
|--------|-------------|
| `acl` | Access control lists (ACL) with client authentication using username and password |

## Setup

1. Install Mosquitto, clients, and tmux:
   ```bash
   sudo apt install mosquitto mosquitto-clients tmux
   ```

   **Important:** Disable the Mosquitto systemd service to avoid conflicts with the broker started by `launch.sh`:
   ```bash
   sudo systemctl disable mosquitto
   sudo systemctl stop mosquitto
   ```

2. Install uv (if not already installed).

3. Generate TLS certificates (required for encrypted connections):
   ```bash
   ./generate_certs.sh
   ```

4. Install client dependencies:
   ```bash
   cd mqtt_client && uv sync && cd ..
   cd client_a && uv sync && cd ..
   cd client_b && uv sync && cd ..
   cd sniffer && uv sync && cd ..
   ```

## Running

```bash
./launch.sh
```

This launches a tmux session with four panes:
- Window 0: Broker (left), Client_b subscriber (top right), Client_a publisher (bottom right)
- Window 1: Packet sniffer

Both clients communicate via port 1883 (plaintext) and port 8883 (TLS) simultaneously.

**Switching tmux windows:**
- `Ctrl+B` then `n` — next window
- `Ctrl+B` then `p` — previous window
- `Ctrl+B` then `0` — window 0 (clients and broker)
- `Ctrl+B` then `1` — window 1 (sniffer)

The sniffer shows the difference between encrypted and plaintext traffic:
- **Port 1883**: Plaintext MQTT packets with decoded payload
- **Port 8883**: Encrypted TLS packets (payload hidden)

To stop everything:
```bash
tmux kill-session -t mqtt
```

or simply exit each pane in the tmux window.
