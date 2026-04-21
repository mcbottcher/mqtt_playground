from pathlib import Path

from mqtt_client import TLSMQTTClient


def main() -> None:
    client = TLSMQTTClient(
        "client_b",
        ca_certs=Path("../certs/ca.crt"),
        certfile=Path("../certs/client_b.crt"),
        keyfile=Path("../certs/client_b.key"),
    )

    with client as c:
        c.subscribe("playground/messages", qos=0)
        print("Subscribed to playground/messages on TLS")

        c.loop_start()

        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            c.loop_stop()


if __name__ == "__main__":
    main()
