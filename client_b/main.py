from mqtt_client import MQTTClient


def main() -> None:
    with MQTTClient("client_b") as client:
        client.subscribe("playground/#", qos=0)
        print("Subscribed to playground/#")
        client.loop_forever()  # blocks this thread to drive the network loop


if __name__ == "__main__":
    main()
