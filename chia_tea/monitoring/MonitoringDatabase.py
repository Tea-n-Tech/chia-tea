
import sqlite3
from typing import Union

from google.protobuf.json_format import MessageToDict

from ..protobuf.generated.computer_info_pb2 import ComputerInfo
from ..protobuf.generated.monitoring_service_pb2 import DataUpdateRequest
from ..protobuf.to_sqlite.sql_cmds import (ALL_SQL_CREATE_TABLE_CMDS,
                                           get_computer_info_from_db,
                                           insert_update_event_in_db,
                                           update_state_tables_in_db)
from ..utils.logger import get_logger


class MonitoringDatabase:
    """ Used to store and retrieve data from the monitoring database
    """
    filepath: str
    connection: Union[sqlite3.Connection, None]
    cursor: Union[sqlite3.Cursor, None]

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.connection = None
        self.cursor = None

    def __check_if_initialized(self):
        if self.connection is None or self.cursor is None:
            err_msg = (
                "MonitoringDatabase needs to be initialized by"
                " a 'with' statement in python."
            )
            raise ValueError(err_msg)

    def __init_tables(self):
        logger = get_logger(__name__)

        logger.debug("Initializing database tables")
        self.__check_if_initialized()

        for cmd in ALL_SQL_CREATE_TABLE_CMDS:
            logger.debug(cmd)
            self.cursor.execute(cmd)

        logger.debug("Database Initialized")

    def __enter__(self):
        self.connection = sqlite3.connect(self.filepath)
        self.cursor = self.connection.cursor()

        self.__init_tables()

        self.connection.commit()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        # we don't handle the exception arguments since
        # this needs to be done further up. But they
        # need to exist to have a correct function
        # signature.
        #
        # See: https://docs.python.org/3/reference/datamodel.html#object.__exit__

        self.connection.commit()
        self.connection.close()

        self.cursor = None
        self.connection = None

    def get_machine_state(self, machine_id: str) -> ComputerInfo:
        """ Get the state of a machine

        Parameters
        ----------
        machine_id : str
            machine to get state of

        Returns
        -------
        computer_info : ComputerInfo
            latest information about the machine
        """

        computer_info = get_computer_info_from_db(
            self.cursor,
            machine_id,
        )

        return computer_info

    def store_data_update_request(
        self,
        data_update_request: DataUpdateRequest,
    ):
        """ Store the data in an update request in the database

        Parameters
        ----------
        data_update_request : DataUpdateRequest
            data update request to store update events
        """
        self.__check_if_initialized()

        logger = get_logger(__file__)

        for event in data_update_request.events:
            logger.debug(
                "Received event: %s",
                MessageToDict(event),
            )

            insert_update_event_in_db(
                sql_cursor=self.cursor,
                pb_message=event,
                meta_attributes=dict(
                    machine_id=data_update_request.machine_id,
                    timestamp=data_update_request.timestamp,
                    event_type=event.event_type,
                ),
            )

            update_state_tables_in_db(
                sql_cursor=self.cursor,
                pb_message=event,
                meta_attributes=dict(
                    machine_id=data_update_request.machine_id,
                ),
                event_type=event.event_type,
            )

        self.connection.commit()
