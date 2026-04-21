import time

from mqtt_client import PlainMQTTClient


def main() -> None:
    client = PlainMQTTClient("client_a")

    with client as c:
        c.loop_start()

        try:
            counter = 0
            while True:
                message = f"The count is at {counter}"
                c.publish("playground/messages", payload=message, qos=0)
                counter += 1
                time.sleep(5.0)
        finally:
            c.loop_stop()


if __name__ == "__main__":
    main()
