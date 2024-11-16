# modules/client_config.py

def create_client_config(private_key, address, dns_servers, server_public_key, preshared_key, endpoint):
    """
    Создает конфигурацию клиента WireGuard.

    Args:
        private_key (bytes): Приватный ключ клиента.
        address (str): IP-адрес клиента.
        dns_servers (str): Список DNS-серверов для клиента.
        server_public_key (str): Публичный ключ сервера WireGuard.
        preshared_key (bytes): Pre-shared ключ для соединения.
        endpoint (str): Адрес сервера (IP и порт).

    Returns:
        str: Конфигурация клиента в формате WireGuard.
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
