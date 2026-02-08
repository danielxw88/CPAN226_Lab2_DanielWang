# This program was modified by Xia Wang / N01721277

import socket
import argparse
import time
import os
import struct 

def run_client(target_ip, target_port, input_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (target_ip, target_port)

    print(f"[*] Sending file '{input_file}' to {target_ip}:{target_port}")

    if not os.path.exists(input_file):
        print(f"[!] Error: File '{input_file}' not found.")
        return

    try:
        sequence_number = 0  

        with open(input_file, 'rb') as f:
            while True:
                chunk = f.read(4096) 

                if not chunk:
                    break

                header = struct.pack("!I", sequence_number) 
                packet = header + chunk

                sock.sendto(packet, server_address)
                sequence_number += 1

                time.sleep(0.001)

        sock.sendto(b'', server_address)
        print("[*] File transmission complete.")

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Naive UDP File Sender")
    parser.add_argument("--target_ip", type=str, default="127.0.0.1", help="Destination IP (Relay or Server)")
    parser.add_argument("--target_port", type=int, default=12000, help="Destination Port")
    parser.add_argument("--file", type=str, required=True, help="Path to file to send")
    args = parser.parse_args()

    run_client(args.target_ip, args.target_port, args.file)

