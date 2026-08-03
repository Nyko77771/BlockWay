import psutil
import socket


class NetworkScan:
    def scan_network(self):
        addresses = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        available_addresses = []

        for interface, addresses_list in addresses.items():
            if interface not in stats or not stats[interface].isup:
                continue
            for addr in addresses_list:
                if addr.family != socket.AF_INET:
                    continue
                if addr.address.startswith("169.254"):
                    continue
                if addr.address.startswith("127."):
                    continue

                available_addresses.append(addr.address)

        return available_addresses
