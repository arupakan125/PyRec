import sys


class PMTHeader:
    def __init__(self):
        self.table_id = None
        self.section_length = None
        self.version_number = None

    def parse_pmt_header(self, data):
        self.table_id = data[0]
        self.section_length = ((data[1] & 0x0F) << 8) | data[2]
        self.version_number = (data[5] & 0x3E) >> 1

    def is_valid_pmt(self):
        return self.table_id == 0x02  # Table ID for PMT


def detect_pmt_version_changes(ts_stream, max_packets=100000):
    previous_version = None
    pmt_data = bytearray()
    collecting = False
    version_changed = False
    packet_count = 0

    buffered_packets = []

    for packet in ts_stream:
        if packet[0] != 0x47:  # Sync byte
            continue

        packet_count += 1

        if version_changed:
            sys.stdout.buffer.write(packet)
            continue

        buffered_packets.append(packet)

        pusi = (packet[1] & 0x40) >> 6  # Payload Unit Start Indicator
        if pusi:
            if collecting and pmt_data:
                pmt_header = PMTHeader()
                pmt_header.parse_pmt_header(pmt_data[:12])
                if pmt_header.is_valid_pmt():
                    if (
                        previous_version is not None
                        and previous_version != pmt_header.version_number
                    ):
                        print(
                            f"PMT version changed from {previous_version} to {pmt_header.version_number}",
                            file=sys.stderr,
                        )
                        version_changed = True
                        buffered_packets = []
                        sys.stdout.buffer.write(packet)
                    previous_version = pmt_header.version_number
            collecting = True
            pmt_data = bytearray()

            pointer_field = packet[4]
            pmt_packet = packet[pointer_field + 5 :]
            pmt_data.extend(pmt_packet)
        elif collecting:
            pmt_data.extend(packet[4:])

            # Check if we have collected enough data for the PMT
            if len(pmt_data) >= 12:
                pmt_header = PMTHeader()
                pmt_header.parse_pmt_header(pmt_data[:12])
                section_length = pmt_header.section_length
                if (
                    len(pmt_data) >= section_length + 3
                ):  # 3 bytes for table_id and section_length fields
                    collecting = False
                    if pmt_header.is_valid_pmt():
                        if (
                            previous_version is not None
                            and previous_version != pmt_header.version_number
                        ):
                            print(
                                f"PMT version changed from {previous_version} to {pmt_header.version_number}",
                                file=sys.stderr,
                            )
                            version_changed = True
                            buffered_packets = []
                            sys.stdout.buffer.write(packet)
                        previous_version = pmt_header.version_number

        if packet_count >= max_packets:
            break

    # If no version change was detected within the first max_packets, output all buffered packets
    if not version_changed:
        for buffered_packet in buffered_packets:
            sys.stdout.buffer.write(buffered_packet)

    # Continue to output the remaining packets
    for packet in ts_stream:
        if packet[0] == 0x47:  # Sync byte check
            sys.stdout.buffer.write(packet)


if __name__ == "__main__":
    ts_stream = iter(lambda: sys.stdin.buffer.read(188), b"")
    detect_pmt_version_changes(ts_stream)
