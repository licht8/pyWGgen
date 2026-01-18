# modules/client_config.py

def create_client_config(private_key, address, dns_servers, server_public_key, preshared_key, endpoint):
    """
    Tworzy konfigurację klienta WireGuard.

    Args:
        private_key (bytes): Klucz prywatny klienta.
        address (str): Adres IP klienta.
        dns_servers (str): Lista serwerów DNS dla klienta.
        server_public_key (str): Klucz publiczny serwera WireGuard.
        preshared_key (bytes): Klucz współdzielony dla połączenia.
        endpoint (str): Adres serwera (IP i port).

    Returns:
        str: Konfiguracja klienta w formacie WireGuard.
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
