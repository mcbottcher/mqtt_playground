import ssl
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from types import TracebackType
from typing import Any

from paho.mqtt.client import Client, CallbackAPIVersion, MQTTMessage
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode


def on_connect(
    _client: Client,
    _userdata: Any,
    _connect_flags: Any,
    reason_code: ReasonCode,
    _properties: Properties,
) -> None:
    if reason_code.is_failure:
        print(f"Failed to connect, return code {reason_code}")
        return
    print("Connected to broker")


def on_disconnect(
    _client: Client,
    _userdata: Any,
    _disconnect_flags: Any,
    reason_code: ReasonCode,
    _properties: Properties,
) -> None:
    print(f"Disconnected with reason code {reason_code}")


def on_publish(
    _client: Client,
    _userdata: Any,
    mid: int,
    _reason_code: ReasonCode,
    _properties: Properties,
) -> None:
    print(f"Message {mid} published successfully")


def on_message(_client: Client, _userdata: Any, msg: MQTTMessage) -> None:
    payload = msg.payload.decode("utf-8")
    print(f"Topic: {msg.topic} | Payload: {payload}")


class MQTTClientBase(ABC):
    """Abstract base class for MQTT client connection.

    Note: paho-mqtt's network loop must be driven by the caller — either
    manually via loop(), blocking via loop_forever(), or by calling
    loop_start() which spawns a background thread.
    """

    def __init__(
        self, client_id: str, callbacks: dict[str, Callable] | None = None
    ) -> None:
        self.client = Client(CallbackAPIVersion.VERSION2, client_id=client_id)
        self._setup_callbacks(callbacks)

    def _setup_callbacks(self, callbacks: dict[str, Callable] | None = None) -> None:
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_publish = on_publish
        self.client.on_message = on_message

        if callbacks:
            for event, callback in callbacks.items():
                setattr(self.client, event, callback)

    @abstractmethod
    def _configure_connection(self) -> tuple[str, int]:
        """Configure client for connection. Return (host, port)."""
        pass

    def __enter__(self) -> Client:
        host, port = self._configure_connection()
        print(f"Connecting to broker at {host}:{port}...")
        self.client.connect(host, port, keepalive=60)
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


class PlainMQTTClient(MQTTClientBase):
    """Plain text MQTT client (no TLS)."""

    def _configure_connection(self) -> tuple[str, int]:
        return "localhost", 1883


class TLSMQTTClient(MQTTClientBase):
    """TLS-encrypted MQTT client."""

    def __init__(
        self,
        client_id: str,
        ca_certs: Path = Path("certs/ca.crt"),
        certfile: Path = Path("certs/client.crt"),
        keyfile: Path = Path("certs/client.key"),
        callbacks: dict[str, Callable] | None = None,
    ) -> None:
        self.ca_certs = ca_certs
        self.certfile = certfile
        self.keyfile = keyfile
        self._validate_certs()
        super().__init__(client_id, callbacks)

    def _validate_certs(self) -> None:
        for cert_path in [self.ca_certs, self.certfile, self.keyfile]:
            if not cert_path.exists():
                raise FileNotFoundError(f"Certificate file not found: {cert_path}")

    def _configure_connection(self) -> tuple[str, int]:
        self.client.tls_set(
            ca_certs=str(self.ca_certs),
            certfile=str(self.certfile),
            keyfile=str(self.keyfile),
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS_CLIENT,
            ciphers=None,
        )
        self.client.tls_insecure = False
        return "localhost", 8883


# Backward compatibility alias
MQTTClient = PlainMQTTClient
