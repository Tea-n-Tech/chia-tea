
import asyncio
import traceback
from typing import Union

import grpc
from google.protobuf.json_format import MessageToDict

from ..protobuf.generated.machine_info_pb2 import MachineInfo
from ..protobuf.generated.monitoring_service_pb2 import DataUpdateRequest
from ..protobuf.generated.monitoring_service_pb2_grpc import MonitoringServicer
from ..protobuf.to_sqlite.sql_cmds import insert_machine_info_in_db
from ..utils.logger import get_logger
from .MonitoringDatabase import MonitoringDatabase

LOG_MSG_RCV = "Received message from {address}: {message}"


class MonitoringServer(MonitoringServicer):
    db: MonitoringDatabase

    def __init__(self, db: MonitoringDatabase):
        """
        """
        super().__init__()
        self.db = db

    async def GetMachineState(self, request, context):
        logger = get_logger(__name__)

        logger.info(LOG_MSG_RCV.format(
            address=context.peer(),
            message=MessageToDict(request),
        ))

        return self.db.get_machine_state(request.machine_id)

    async def SendMonitoringUpdate(self, request_iterator, context):
        logger = get_logger(__name__)
        logger.info(f"Connected to {context.peer()}")

        # we endlessly process updates
        while True:
            try:
                # check for a response
                data_update_request: Union[DataUpdateRequest, grpc.aio.EOF] \
                    = await context.read()

                # last stream ended (batch of messages)
                if data_update_request == grpc.aio.EOF:
                    continue

                logger.info("Received update from {address}".format(
                    address=context.peer(),
                ))

                if not data_update_request.timestamp:
                    raise ValueError("DataUpdateRequest requires a timestamp.")

                if not data_update_request.machine_id:
                    raise ValueError(
                        "DataUpdateRequest requires a machine id.")

                # store info that the db was updated
                insert_machine_info_in_db(
                    self.db.cursor,
                    MachineInfo(
                        machine_id=data_update_request.machine_id,
                        name=data_update_request.machine_name,
                        ip_address=context.peer(),
                        time_last_msg=data_update_request.timestamp,
                    ),
                    {},
                )

                # store in database
                self.db.store_data_update_request(data_update_request)

            except asyncio.TimeoutError:
                # try again
                pass
            except Exception:
                trace = traceback.format_exc()
                logger.error(trace)
                await asyncio.sleep(5)
