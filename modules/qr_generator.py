import pyqrcode # type: ignore

def generate_qr_code(data, qr_path):
    qr = pyqrcode.create(data)
    qr.png(qr_path, scale=6)
