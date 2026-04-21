#!/bin/bash
# MQTT Playground Launcher
# Sets up a tmux session with three panes: broker on left, subscriber (top right), publisher (bottom right)

# Get the absolute path to this script's directory so we can find the config files
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Kill any existing "mqtt" session to ensure a clean slate
tmux kill-session -t mqtt 2>/dev/null
# Kill any orphaned mosquitto processes from previous runs
pkill mosquitto 2>/dev/null

# Create a new detached tmux session named "mqtt" with 200 columns x 50 rows
tmux new-session -d -s mqtt -x 200 -y 50

# Set a hook so that when the tmux session closes, automatically kill any remaining mosquitto processes
tmux set-hook -t mqtt session-closed 'run-shell "pkill mosquitto"'

# Pane 0 (left side): Start the MQTT broker with its config file
tmux send-keys -t mqtt "cd '$REPO_ROOT' && mosquitto -c broker/mosquitto.conf" Enter

# Give the broker time to start before launching clients
sleep 1.5

# Split the session horizontally: create a right pane with 100 columns width
tmux split-window -t mqtt -h -l 100

# Split the right pane vertically: create two panes (top and bottom) with 25 rows height for the bottom pane
tmux split-window -t mqtt:1.2 -v -l 25

# Pane 1 (top right): Start client_b (broker has already had time to start)
tmux send-keys -t mqtt:1.2 "cd '$REPO_ROOT/client_b' && uv run main.py" Enter

# Pane 2 (bottom right): Start client_a (broker has already had time to start)
tmux send-keys -t mqtt:1.3 "cd '$REPO_ROOT/client_a' && uv run main.py" Enter

# Create a new window for the packet sniffer
tmux new-window -t mqtt -n sniffer
tmux send-keys -t mqtt:sniffer "cd '$REPO_ROOT/sniffer' && sudo /home/mcb/.local/bin/uv run python main.py" Enter

# Attach to the mqtt session and display it in the terminal
tmux attach-session -t mqtt
