
from ..protobuf.generated.config_pb2 import ChiaTeaConfig


def get_credentials_key(
        is_testing: bool,
        config: ChiaTeaConfig,
) -> bytes:
    """ Get the private key from the config

    Parameters
    ---------
    is_testing : bool
        whether testing is being performed
    config : ChiaTeaConfig
        config to read filepath for cert and key

    Returns
    -------
    key : str
        key file as string
    """

    if is_testing:
        return b""

    key_filepath = config.monitoring.auth.key_filepath

    with open(key_filepath, 'r', encoding="utf8") as fp:
        key = fp.read().encode('utf8')

    return key


def get_credentials_cert(
        is_testing: bool,
        config: ChiaTeaConfig) -> bytes:
    """ Get the certificates from the config

    Parameters
    ---------
    is_testing : bool
        whether testing is being performed
    config : ChiaTeaConfig
        config to read filepath for cert and key

    Returns
    -------
    cert : str
        cert file as string
    """

    if is_testing:
        return b""

    cert_filepath = config.monitoring.auth.cert_filepath

    with open(cert_filepath, 'r', encoding="utf8") as fp:
        cert = fp.read().encode('utf8')

    return cert
