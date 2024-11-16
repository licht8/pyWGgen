import subprocess
import tempfile

def sync_wireguard_config(server_wg_nic):
    try:
        stripped_config = subprocess.check_output(['wg-quick', 'strip', server_wg_nic])
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(stripped_config)
            temp_file.flush()
            subprocess.run(['wg', 'syncconf', server_wg_nic, temp_file.name], check=True)
        print(f"Конфигурация для {server_wg_nic} успешно синхронизирована.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при синхронизации конфигурации: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
