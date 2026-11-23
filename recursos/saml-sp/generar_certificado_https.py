# -*- coding: utf-8 -*-
"""Crea el certificado HTTPS autofirmado de https://localhost:5001 (carpeta certs).

Genera: certs/localhost.pem (certificado), certs/localhost-key.pem (clave privada)
        y certs/localhost.cer (para importarlo como raíz de confianza en Windows).
"""
import datetime as dt
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

CARPETA = Path(__file__).resolve().parent / "certs"
CARPETA.mkdir(exist_ok=True)

clave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
nombre = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
ahora = dt.datetime.now(dt.timezone.utc)
cert = (x509.CertificateBuilder()
        .subject_name(nombre).issuer_name(nombre)
        .public_key(clave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(ahora - dt.timedelta(minutes=5))
        .not_valid_after(ahora + dt.timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .sign(clave, hashes.SHA256()))

(CARPETA / "localhost-key.pem").write_bytes(clave.private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()))
(CARPETA / "localhost.pem").write_bytes(cert.public_bytes(serialization.Encoding.PEM))
(CARPETA / "localhost.cer").write_bytes(cert.public_bytes(serialization.Encoding.DER))
print("Certificado creado en", CARPETA)
print("Huella:", cert.fingerprint(hashes.SHA1()).hex().upper())
