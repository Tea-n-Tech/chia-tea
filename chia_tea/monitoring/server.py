
import asyncio

import grpc

from ..protobuf.generated.monitoring_service_pb2_grpc import \
    add_MonitoringServicer_to_server
from ..protobuf.generated.config_pb2 import ChiaTeaConfig
from ..utils.cli import parse_args
from ..utils.config import read_config
from ..utils.logger import get_logger
from .common import get_credentials_cert, get_credentials_key
from .MonitoringDatabase import MonitoringDatabase
from .MonitoringServer import MonitoringServer


def __get_port(config: ChiaTeaConfig) -> int:
    """ Get the port for the server

    Returns
    -------
    port : int
        port of the server from the config
    """
    port = config.monitoring.server.port

    if not isinstance(port, int):
        msg = "Monitoring server port '{0}' must be a positive number"
        raise ValueError(msg.format(port))

    if not port > 0:
        msg = "Monitoring server port '{0}' must be a positive number"
        raise ValueError(msg.format(port))

    return port


def __get_database_filepath(config: ChiaTeaConfig) -> str:
    """ Get the database filepath from the config

    Parameters
    ---------
    config : ChiaTeaConfig
        config to read filepath for cert and key

    Returns
    -------
    db_filepath : str
        path where the database is or will be stored
    """
    filepath = config.monitoring.server.db_filepath

    if not filepath:
        raise ValueError(
            "Config entry 'monitoring.server.db_filepath' may not be empty.")

    return filepath


def create_server(
        ip_address: str,
        cert: bytes,
        key: bytes,
        db: MonitoringDatabase) -> grpc.aio.Server:
    """ Creates a grpc server from the config
    """
    logger = get_logger(__name__)

    server = grpc.aio.server()

    if cert and key:
        logger.info("Using encryption")
        server_credentials = grpc.ssl_server_credentials(
            [(key, cert)],
        )
        server.add_secure_port(ip_address, server_credentials)
    else:
        logger.warning("Encryption disabled")
        server.add_insecure_port(ip_address)

    add_MonitoringServicer_to_server(
        MonitoringServer(
            db=db
        ),
        server
    )

    return server


async def build_server(config: ChiaTeaConfig, db: MonitoringDatabase):
    """ Builds the monitoring server

    Parmeters
    ---------
    config : ChiaTeaConfig
        Config used by the server
    db : MonitoringDatabase
        database to store monitoring data in

    Returns
    -------
    server : grpc.aio.Server
        Monitoring server instance
    """

    # server address
    port = __get_port(config)
    ip_address = "[::]:"+str(port)

    # testing disables certificate security
    is_testing = config.development.testing

    # get certificates for security
    cert = get_credentials_cert(is_testing, config)
    key = get_credentials_key(is_testing, config)

    # build server
    server = create_server(
        ip_address,
        cert,
        key,
        db)

    return server


async def start_server(config: ChiaTeaConfig):
    """ Builds and starts the server

    Parmeters
    ---------
    config : ChiaTeaConfig
        config used by the server
    """
    logger = get_logger(__name__)

    logger.debug("Initializing database")
    db_filepath = __get_database_filepath(config)
    with MonitoringDatabase(db_filepath) as db:

        logger.debug("Building server")
        server = await build_server(config, db)

        logger.info("Starting Server")
        await server.start()
        await server.wait_for_termination()


def main():
    """ Main function starting the monitoring server
    """

    try:
        args = parse_args(
            name="Chia Tea Monitoring Server",
            description=("Start a server collecting data from" +
                         "from monitoring clients.")
        )

        # load config
        config = read_config(args.config)

        # setup logger
        logger = get_logger(__name__)

        # start the server
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server(config))

    except KeyboardInterrupt:
        logger.info("Stopped server.")


if __name__ == "__main__":
    main()
