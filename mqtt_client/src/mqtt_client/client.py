from collections.abc import Callable
from types import TracebackType
from typing import Any

from paho.mqtt.client import Client, CallbackAPIVersion, MQTTMessage
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode


def on_connect(_client: Client, _userdata: Any, _connect_flags: Any, reason_code: ReasonCode, _properties: Properties) -> None:
    if reason_code.is_failure:
        print(f"Failed to connect, return code {reason_code}")
        return
    print("Connected to broker")


def on_disconnect(_client: Client, _userdata: Any, _disconnect_flags: Any, reason_code: ReasonCode, _properties: Properties) -> None:
    print(f"Disconnected with reason code {reason_code}")


def on_publish(_client: Client, _userdata: Any, mid: int, _reason_code: ReasonCode, _properties: Properties) -> None:
    print(f"Message {mid} published successfully")


def on_message(_client: Client, _userdata: Any, msg: MQTTMessage) -> None:
    payload = msg.payload.decode("utf-8")
    print(f"Topic: {msg.topic} | Payload: {payload}")


class MQTTClient:
    """Context manager for MQTT client connection.

    Note: paho-mqtt's network loop must be driven by the caller — either
    manually via loop(), blocking via loop_forever(), or by calling
    loop_start() which spawns a background thread.
    """

    def __init__(self, client_id: str, callbacks: dict[str, Callable] | None = None) -> None:
        self.client = Client(CallbackAPIVersion.VERSION2, client_id=client_id)

        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_publish = on_publish
        self.client.on_message = on_message

        if callbacks:
            for event, callback in callbacks.items():
                setattr(self.client, event, callback)

    def __enter__(self) -> Client:
        print("Connecting to broker at localhost:1883...")
        self.client.connect("localhost", 1883, keepalive=60)
        return self.client

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        print("\nShutting down client...")
        self.client.disconnect()
        return False
