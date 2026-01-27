#!/usr/bin/env python3
"""
Testy jednostkowe generowania kluczy kryptograficznych WireGuard.

Moduł testuje funkcje generowania kluczy:
- Kluczy prywatnych (generate_private_key)
- Kluczy publicznych z prywatnych (generate_public_key) 
- Kluczy preshared (generate_preshared_key)

Sprawdzane aspekty:
- Poprawność generowania (nie None)
- Typ bajtowy (bytes)
- Długość base64 (~44 znaki WireGuard)
"""

import pytest
import sys
import os

# Dodajemy ścieżkę do projektu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyWGgen.modules.keygen import (
    generate_private_key, 
    generate_public_key, 
    generate_preshared_key
)

def test_generate_private_key():
    """Test generowania klucza prywatnego."""
    private_key = generate_private_key()
    
    assert private_key is not None
    assert isinstance(private_key, bytes)
    assert len(private_key) > 40  # WireGuard klucze ~44 symbole base64

def test_generate_public_key():
    """Test generowania klucza publicznego z prywatnego."""
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    
    assert public_key is not None
    assert isinstance(public_key, bytes)
    assert len(public_key) > 40

def test_generate_preshared_key():
    """Test generowania klucza preshared."""
    preshared_key = generate_preshared_key()
    
    assert preshared_key is not None
    assert isinstance(preshared_key, bytes)
    assert len(preshared_key) > 40
