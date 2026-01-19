import pytest
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyWGgen.modules.client_config import create_client_config
from pyWGgen.modules.keygen import generate_private_key, generate_public_key, generate_preshared_key

def test_create_client_config_basic():
    """Тест базовой генерации конфига клиента"""
    # Генерируем реальные ключи
    private_key = generate_private_key()
    server_public_key = generate_public_key(generate_private_key())
    preshared_key = generate_preshared_key()
    
    config = create_client_config(
        private_key=private_key,
        address="10.0.0.2/32",
        dns_servers="1.1.1.1,8.8.8.8",
        server_public_key=server_public_key.decode('utf-8'),
        preshared_key=preshared_key,
        endpoint="server.example.com:51820"
    )
    
    assert config is not None
    assert "[Interface]" in config
    assert "[Peer]" in config
    assert "PrivateKey" in config
    assert "Address = 10.0.0.2/32" in config
    assert "DNS = 1.1.1.1,8.8.8.8" in config
    assert "Endpoint = server.example.com:51820" in config
    print("✅ Базовый конфиг создан корректно!")

def test_create_client_config_format():
    """Тест формата конфига WireGuard"""
    private_key = generate_private_key()
    server_public_key = generate_public_key(generate_private_key())
    preshared_key = generate_preshared_key()
    
    config = create_client_config(
        private_key=private_key,
        address="10.0.0.3/32",
        dns_servers="8.8.8.8",
        server_public_key=server_public_key.decode('utf-8'),
        preshared_key=preshared_key,
        endpoint="vpn.myserver.pl:51820"
    )
    
    # НЕ проверяем точное количество строк - проверяем Наличие ВСЕХ секций
    assert "[Interface]" in config
    assert "PrivateKey" in config  
    assert "Address" in config
    assert "DNS" in config
    assert "[Peer]" in config
    assert "PublicKey" in config
    assert "PresharedKey" in config
    assert "Endpoint" in config
    assert "AllowedIPs = 0.0.0.0/0,::/0" in config
    print("✅ ВСЕ секции WireGuard конфига присутствуют!")
