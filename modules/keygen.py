import subprocess

def generate_private_key():
    private_key = subprocess.check_output(['wg', 'genkey']).strip()
    return private_key

def generate_public_key(private_key):
    public_key = subprocess.check_output(['wg', 'pubkey'], input=private_key).strip()
    return public_key

def generate_preshared_key():
    preshared_key = subprocess.check_output(['wg', 'genpsk']).strip()
    return preshared_key
