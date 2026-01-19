import pytest
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyWGgen.modules.keygen import (
    generate_private_key, 
    generate_public_key, 
    generate_preshared_key
)

def test_generate_private_key():
    """Тестит генерацию приватного ключа"""
    private_key = generate_private_key()
    
    assert private_key is not None
    assert isinstance(private_key, bytes)
    assert len(private_key) > 40  # WireGuard ключи ~44 символа base64
    print(f"✅ Приватный ключ: {private_key[:20]}...")

def test_generate_public_key():
    """Тестит генерацию публичного ключа из приватного"""
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    
    assert public_key is not None
    assert isinstance(public_key, bytes)
    assert len(public_key) > 40
    print(f"✅ Публичный ключ: {public_key[:20]}...")

def test_generate_preshared_key():
    """Тестит генерацию preshared ключа"""
    preshared_key = generate_preshared_key()
    
    assert preshared_key is not None
    assert isinstance(preshared_key, bytes)
    assert len(preshared_key) > 40
    print(f"✅ Preshared ключ: {preshared_key[:20]}...")
