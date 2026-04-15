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

2. Install uv (if not already installed):

3. Install client dependencies:
   ```bash
   cd client_a && uv sync && cd ..
   cd client_b && uv sync && cd ..
   ```

## Running

```bash
./launch.sh
```

This launches a tmux session with the broker, subscriber, and publisher running in separate panes.

To stop everything:
```bash
tmux kill-session -t mqtt
```

or simply exit each pane in the tmux window.
