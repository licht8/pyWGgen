# modules/client_config.py

def create_client_config(private_key, address, dns_servers, server_public_key, preshared_key, endpoint):
    """
    Creates a WireGuard client configuration.

    Args:
        private_key (bytes): The client's private key.
        address (str): The client's IP address.
        dns_servers (str): List of DNS servers for the client.
        server_public_key (str): WireGuard server's public key.
        preshared_key (bytes): Pre-shared key for the connection.
        endpoint (str): Server address (IP and port).

    Returns:
        str: Client configuration in WireGuard format.
    """
    client_config = f"""[Interface]
PrivateKey = {private_key.decode('utf-8')}
Address = {address}
DNS = {dns_servers}

[Peer]
PublicKey = {server_public_key}
PresharedKey = {preshared_key.decode('utf-8')}
Endpoint = {endpoint}
AllowedIPs = 0.0.0.0/0,::/0"""
    return client_config
