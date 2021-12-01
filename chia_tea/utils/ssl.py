import os
from datetime import datetime, timedelta

from chia.util.ssl_check import DEFAULT_PERMISSIONS_CERT_FILE, DEFAULT_PERMISSIONS_KEY_FILE
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from ..utils.logger import get_logger


def write_ssl_cert_and_key(
    key_path: str, key_data: bytes, cert_path: str, cert_data: bytes, overwrite: bool
):
    """Writes the ssl certificate and key to the specified filepath

    Parameters
    ----------
    key_path : str
        path to save the key
    key_data : bytes
        key data
    cert_path : str
        path to save the certificate
    cert_data : bytes
        certificate data
    overwrite : bool
        overwrite existing files

    Notes
    -----
        This code is an adaption from the chia-blockchain codebase.
    """
    logger = get_logger(__file__)

    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY

    for filepath, data, mode in [
        (cert_path, cert_data, DEFAULT_PERMISSIONS_CERT_FILE),
        (key_path, key_data, DEFAULT_PERMISSIONS_KEY_FILE),
    ]:
        if os.path.exists(filepath):
            if not overwrite:
                logger.warning("⚠️  Certificate %s already exists, skipping", filepath)
                continue
            os.unlink(filepath)

        with open(os.open(filepath, flags, mode), "wb") as fp:
            fp.write(data)

        logger.info("Created certificate: %s", filepath)


def create_certificate_pair(
    key_path: str, cert_path: str, common_name: str = "localhost", overwrite: bool = False
) -> None:
    """Creates a certificate pair

    Parameters
    ----------
    key_path : str
        path to save the key
    cert_path : str
        path to save the certificate
    common_name : str
        common name for the certificate such as the hostname
    overwrite : bool
        overwrite existing files

    Notes
    -----
        This code is an adaption from the chia-blockchain codebase.
        The certificate is valid for 10 years.
    """

    root_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Chia-Tea"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Tea Brewing Division"),
        ]
    )
    root_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(root_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(root_key, hashes.SHA256(), default_backend())
    )

    cert_pem = root_cert.public_bytes(encoding=serialization.Encoding.PEM)
    key_pem = root_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    write_ssl_cert_and_key(cert_path, cert_pem, key_path, key_pem, overwrite=overwrite)
