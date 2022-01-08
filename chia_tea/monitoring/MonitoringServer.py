import asyncio
import datetime
import traceback
from typing import List, Union

import grpc
from google.protobuf.json_format import MessageToDict

from ..protobuf.generated.machine_info_pb2 import MachineInfo
from ..protobuf.generated.monitoring_service_pb2 import DataUpdateRequest
from ..protobuf.generated.monitoring_service_pb2_grpc import MonitoringServicer
from ..utils.logger import get_logger
from .MonitoringDatabase import MonitoringDatabase


class MonitoringServer(MonitoringServicer):
    """This class contains the server receiving and storing
    monitoring data from monitoring clients.
    """

    db: MonitoringDatabase

    def __init__(self, db: MonitoringDatabase):
        """Constructor

        Parameters
        ----------
        db : MonitoringDatabase
            database to operate on
        """
        super().__init__()
        self.db = db

    # pylint: disable=invalid-overridden-method
    async def GetMachineState(self, request, context):
        """Stub to get the latest state of a machine"""
        logger = get_logger(__name__)

        msg = "Received message from {address}: {message}".format(
            address=context.peer(),
            message=MessageToDict(request),
        )
        logger.info(msg)

        return self.db.get_machine_state(request.machine_id)

    # pylint: disable=invalid-overridden-method
    async def SendMonitoringUpdate(self, request_iterator, context):
        """Stub to receive monitoring updates from clients"""
        logger = get_logger(__name__)
        logger.info("Connected to %s", context.peer())

        last_machine_info: Union[MachineInfo, None] = None

        # we endlessly process updates
        from rich import inspect

        inspect(context, all=True)
        while True:
            try:

                # TODO add a timeout of read!!!!

                # check for a response
                data_update_request: Union[DataUpdateRequest, grpc.aio.EOF] = await context.read()

                # last stream ended (batch of messages)
                if data_update_request == grpc.aio.EOF:
                    continue

                logger.info("Received update from %s", context.peer())

                if not data_update_request.timestamp:
                    raise ValueError("DataUpdateRequest requires a timestamp.")

                if not data_update_request.machine_id:
                    raise ValueError("DataUpdateRequest requires a machine id.")

                last_machine_info = MachineInfo(
                    machine_id=data_update_request.machine_id,
                    name=data_update_request.machine_name,
                    ip_address=context.peer(),
                    time_last_msg=data_update_request.timestamp,
                )

                # store in database
                self.db.store_data_update_request(
                    data_update_request=data_update_request, ip_address=context.peer()
                )

            except Exception:
                trace = traceback.format_exc()
                logger.error(trace)

                self.db.set_machine_as_disconnected(last_machine_info)

                await context.abort(
                    code=grpc.StatusCode.INTERNAL,
                    details=trace,
                )
                break
