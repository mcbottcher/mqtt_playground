#!/usr/bin/env python3
"""Packet sniffer to observe MQTT traffic on ports 1883 and 8883."""

from scapy.all import sniff, Raw
from scapy.layers.inet import IP, TCP

MQTT_PACKET_TYPES = {
    1: "CONNECT",
    2: "CONNACK",
    3: "PUBLISH",
    4: "PUBACK",
    5: "PUBREC",
    6: "PUBREL",
    7: "PUBCOMP",
    8: "SUBSCRIBE",
    9: "SUBACK",
    10: "UNSUBSCRIBE",
    11: "UNSUBACK",
    12: "PINGREQ",
    13: "PINGRESP",
    14: "DISCONNECT",
}


def decode_remaining_length(data: bytes, offset: int) -> tuple[int, int]:
    """Decode MQTT variable-length remaining length field.

    Returns (remaining_length, bytes_consumed).
    """
    multiplier = 1
    value = 0
    i = 0
    while True:
        if offset + i >= len(data):
            raise ValueError("Incomplete remaining length field")
        byte = data[offset + i]
        value += (byte & 0x7F) * multiplier
        multiplier *= 128
        i += 1
        if not (byte & 0x80):
            break
        if i > 4:
            raise ValueError("Remaining length field too long")
    return value, i


def parse_mqtt_info(raw_data: bytes) -> str:
    """Extract MQTT packet type and basic info."""
    if len(raw_data) < 2:
        return "Unknown (too short)"

    first_byte = raw_data[0]
    packet_type = (first_byte >> 4) & 0x0F
    packet_name = MQTT_PACKET_TYPES.get(packet_type, f"Unknown ({packet_type})")

    try:
        _, length_bytes = decode_remaining_length(raw_data, 1)
    except ValueError:
        return f"{packet_name} (malformed length)"

    header_end = 1 + length_bytes  # index where variable header starts

    if packet_type == 3:  # PUBLISH
        if len(raw_data) >= header_end + 2:
            topic_len = (raw_data[header_end] << 8) | raw_data[header_end + 1]
            topic_start = header_end + 2
            if len(raw_data) >= topic_start + topic_len:
                topic = raw_data[topic_start : topic_start + topic_len].decode(
                    "utf-8", errors="ignore"
                )
                payload_start = topic_start + topic_len
                payload = raw_data[payload_start:]
                payload_str = payload.decode("utf-8", errors="ignore")
                return f"PUBLISH  topic='{topic}'  payload='{payload_str}'"
        return "PUBLISH (malformed)"

    elif packet_type == 8:  # SUBSCRIBE
        pos = header_end + 2  # skip 2-byte packet identifier
        topics = []
        while pos + 2 <= len(raw_data):
            tlen = (raw_data[pos] << 8) | raw_data[pos + 1]
            pos += 2
            if pos + tlen > len(raw_data):
                break
            topics.append(raw_data[pos : pos + tlen].decode("utf-8", errors="ignore"))
            pos += tlen + 1  # +1 for QoS byte
        return f"SUBSCRIBE  topics={topics}"

    elif packet_type == 1:  # CONNECT
        if len(raw_data) >= header_end + 2:
            pname_len = (raw_data[header_end] << 8) | raw_data[header_end + 1]
            pname = raw_data[header_end + 2 : header_end + 2 + pname_len].decode(
                "utf-8", errors="ignore"
            )
            return f"CONNECT  protocol='{pname}'"
        return "CONNECT"

    return packet_name


def packet_callback(packet) -> None:
    if IP not in packet or TCP not in packet:
        return

    ip = packet[IP]
    tcp = packet[TCP]
    flags = str(tcp.flags)

    # On loopback, scapy sees every packet twice (outbound and inbound).
    # To avoid duplicates we only capture packets travelling in one direction
    # for each port: client→broker (dport==1883/8883) for plaintext/TLS publishes,
    # and broker→client (sport==1883/8883) for broker responses.
    # This gives us one clean copy of each logical packet.

    if tcp.dport == 1883:
        # Client → Broker
        direction = f"{ip.src}:{tcp.sport} → {ip.dst}:{tcp.dport}  (client→broker)"
        if Raw in packet:
            raw_data = packet[Raw].load
            mqtt_info = parse_mqtt_info(raw_data)
            print(f"\n[PORT 1883 - PLAINTEXT] {direction}  flags={flags}")
            print(f"  MQTT: {mqtt_info}")
            print(f"  Raw:  {raw_data.hex()[:80]}...")
        else:
            print(f"\n[PORT 1883 - TCP ONLY]  {direction}  flags={flags}  (no payload)")

    elif tcp.sport == 1883:
        # Broker → Client
        direction = f"{ip.src}:{tcp.sport} → {ip.dst}:{tcp.dport}  (broker→client)"
        if Raw in packet:
            raw_data = packet[Raw].load
            mqtt_info = parse_mqtt_info(raw_data)
            print(f"\n[PORT 1883 - PLAINTEXT] {direction}  flags={flags}")
            print(f"  MQTT: {mqtt_info}")
            print(f"  Raw:  {raw_data.hex()[:80]}...")
        else:
            print(f"\n[PORT 1883 - TCP ONLY]  {direction}  flags={flags}  (no payload)")

    elif tcp.dport == 8883:
        # Client → Broker (TLS)
        direction = f"{ip.src}:{tcp.sport} → {ip.dst}:{tcp.dport}  (client→broker)"
        if Raw in packet:
            raw_data = packet[Raw].load
            print(f"\n[PORT 8883 - TLS ENCRYPTED] {direction}  flags={flags}")
            print(f"  (Payload is encrypted, {len(raw_data)} bytes)")
        else:
            print(f"\n[PORT 8883 - TCP ONLY]  {direction}  flags={flags}  (no payload)")

    elif tcp.sport == 8883:
        # Broker → Client (TLS)
        direction = f"{ip.src}:{tcp.sport} → {ip.dst}:{tcp.dport}  (broker→client)"
        if Raw in packet:
            raw_data = packet[Raw].load
            print(f"\n[PORT 8883 - TLS ENCRYPTED] {direction}  flags={flags}")
            print(f"  (Payload is encrypted, {len(raw_data)} bytes)")
        else:
            print(f"\n[PORT 8883 - TCP ONLY]  {direction}  flags={flags}  (no payload)")


def main() -> None:
    print("Starting packet sniffer on loopback interface...")
    print("Monitoring ports 1883 (plaintext) and 8883 (TLS)")
    print("Press Ctrl+C to stop\n")
    sniff(
        iface="lo",
        prn=packet_callback,
        filter="tcp and (port 1883 or port 8883)",
        store=False,
    )


if __name__ == "__main__":
    main()
