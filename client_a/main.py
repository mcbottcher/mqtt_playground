import time

from mqtt_client import MQTTClient


def main() -> None:
    with MQTTClient("client_a") as client:
        client.loop_start()  # spawns a background thread to drive the network loop
        counter = 0
        while True:
            client.publish("playground/messages", payload=str(counter), qos=0)
            counter += 1
            time.sleep(1.0)


if __name__ == "__main__":
    main()
