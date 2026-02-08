# This program was modified by Xia Wang / N01721277

import socket
import argparse
import struct

def run_server(port, output_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ('', port)
    print(f"[*] Server listening on port {port}")
    print(f"[*] Server will save received file as '{output_file}'")
    sock.bind(server_address)

    try:
        while True:
            f = None
            expected_seq_num = 0
            buffer = {}
            current_sender = None

            while True:
                data, addr = sock.recvfrom(4096 + 4)


                if not data:
                    if current_sender is None:
                        continue
                    if addr != current_sender:
                        continue

                    print(f"[*] EOF received from {addr}. Waiting briefly for late packets...")

                    sock.settimeout(0.5) 

                    while True:
                        try:
                            late_data, late_addr = sock.recvfrom(4096 + 4)
                        except socket.timeout:
                            break

                        if late_addr != current_sender:
                            continue

                        if not late_data:
                            continue

                        if len(late_data) < 4:
                            continue

                        late_seq = struct.unpack("!I", late_data[:4])[0]
                        late_payload = late_data[4:]

                        if late_seq == expected_seq_num:
                            f.write(late_payload)
                            expected_seq_num += 1
                            while expected_seq_num in buffer:
                                f.write(buffer.pop(expected_seq_num))
                                expected_seq_num += 1
                        elif late_seq > expected_seq_num:
                            if late_seq not in buffer:
                                buffer[late_seq] = late_payload
                        else:
                            pass 

                    sock.settimeout(None)

                    while expected_seq_num in buffer:
                        f.write(buffer.pop(expected_seq_num))
                        expected_seq_num += 1

                    print("[*] Closing file.")
                    break

                if f is None:
                    current_sender = addr
                    print("==== Start of reception ====")
                    f = open(output_file, 'wb')
                    print(f"[*] First packet received from {addr}. Writing to '{output_file}'.")

                if addr != current_sender:
                    continue

                if len(data) < 4:
                    continue

                seq_num = struct.unpack("!I", data[:4])[0]
                payload = data[4:]

                if seq_num == expected_seq_num:
                    f.write(payload)
                    expected_seq_num += 1

                    while expected_seq_num in buffer:
                        buffered_data = buffer.pop(expected_seq_num)
                        f.write(buffered_data)
                        expected_seq_num += 1

                elif seq_num > expected_seq_num:
                    buffer[seq_num] = payload

                else:
                    pass 

            if f:
                f.close()
            print("==== End of reception ====")

    except KeyboardInterrupt:
        print("\n[!] Server stopped manually.")
    finally:
        sock.close()
        print("[*] Server socket closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naive UDP File Receiver")
    parser.add_argument("--port", type=int, default=12001, help="Port to listen on")
    parser.add_argument("--output", type=str, default="received_file.jpg", help="File path to save data")
    args = parser.parse_args()

    run_server(args.port, args.output)

