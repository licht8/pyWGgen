import configparser

def load_params(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config['server']
