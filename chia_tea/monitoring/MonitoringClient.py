
import asyncio
import traceback
import uuid
from datetime import datetime
from typing import Dict, Tuple, Union

import grpc
from google.protobuf.json_format import MessageToDict

from ..chia_watchdog.ChiaWatchdog import ChiaWatchdog
from ..chia_watchdog.computer_info_comparison import get_update_events
from ..protobuf.generated.computer_info_pb2 import ComputerInfo, UpdateEvent
from ..protobuf.generated.config_pb2 import (
    _MONITORINGCONFIG_CLIENTCONFIG_SENDUPDATEEVERY, MonitoringConfig)
from ..protobuf.generated.monitoring_service_pb2 import (DataUpdateRequest,
                                                         GetStateRequest)
from ..protobuf.generated.monitoring_service_pb2_grpc import MonitoringStub
from ..protobuf.to_sqlite.custom import ProtoType, get_update_even_data
from ..utils.logger import get_logger
from ..utils.settings import get_settings_value
from ..utils.timing import wait_at_least

ClientConfig = MonitoringConfig.ClientConfig


def load_machine_id() -> str:
    """ Loads id of the machine

    Returns
    -------
    machine_id : str
        id of the machine

    Notes
    -----
        The machine id is stored in the home directory in
        `~/.chia_tea/settings.json`.
    """

    return get_settings_value(
        "machineId",
        default=uuid.getnode())


def get_collection_frequencies(config: ClientConfig) -> Dict[str, float]:
    """ Get the collection frequencies for updates to the server

    Parameters
    ----------
    config : ClientConfig
        config for the monitoring client

    Returns
    -------
    collection_frequencies : Dict[str, float]
        update event name and frequency pairs

    Raises
    ------
    ValueError
        In case an invalid name not matching the proto schema
        was given
    """

    collection_frequencies = config.send_update_every

    user_rate_limits = {}
    for field in _MONITORINGCONFIG_CLIENTCONFIG_SENDUPDATEEVERY.fields:
        field_value = getattr(collection_frequencies, field.name)
        user_rate_limits[field.name] = field_value

    update_event_var_names = tuple(
        field.name for field in UpdateEvent.DESCRIPTOR.fields
        if field.type == ProtoType.MESSAGE.value
    )

    for name, _ in user_rate_limits.items():
        if name not in update_event_var_names:
            err_msg = ("Config entry '{0}' is not valid." +
                       " Use one of {1}")
            raise ValueError(err_msg.format(
                name,
                ", ".join(update_event_var_names)
            ))

    return user_rate_limits


class MonitoringClient:
    """ Class for collecting and sending monitoring data to a server
    """
    config: ClientConfig
    credentials_cert: str
    machine_id: str
    machine_name: str

    # throttling
    collection_frequencies: Dict[str, float]
    last_time_sent: Dict[Union[str, Tuple[str, str]], datetime]

    # watching stuff
    chia_dog: ChiaWatchdog

    def __init__(self,
                 chia_dog: ChiaWatchdog,
                 config=MonitoringConfig.ClientConfig,
                 credentials_cert: str = "",
                 machine_name: str = "",
                 ):
        self.config = config
        self.credentials_cert = credentials_cert
        self.machine_id = load_machine_id()
        self.chia_dog = chia_dog
        self.collection_frequencies = get_collection_frequencies(
            config)
        self.last_time_sent = {}
        self.machine_name = machine_name

    def is_event_allowed_to_be_sent(self, pb_msg: UpdateEvent) -> bool:
        """ Checks if a an update event is allowed to be sent

        Parameters
        ----------
        pb_msg : UpdateEvent
            event to be sent to the user

        Returns
        -------
        is_allowed : bool
            whether the event is allowed to be sent according to the
            data throttling limits
        """

        # get the name of the submessage to be updated
        field_name, sub_msg = get_update_even_data(pb_msg)
        field_id = getattr(sub_msg, "id") \
            if hasattr(sub_msg, "id") \
            else None

        field_key = field_name if field_id is None \
            else (field_name, field_id)

        # no field name found, that is odd. Do a warning and
        # continue
        if not field_name:
            warn_msg = ("Could not identify which field" +
                        " was set in an update event: %s")
            get_logger(__file__).warning(
                warn_msg,
                MessageToDict(pb_msg)
            )
            self.last_time_sent[field_key] = datetime.now()
            return True

        allowed_every = self.collection_frequencies.get(field_name)
        # no throttling active
        if allowed_every is None:
            self.last_time_sent[field_key] = datetime.now()
            return True

        last_time = self.last_time_sent.get(field_key)
        # not sent yet
        if last_time is None:
            self.last_time_sent[field_key] = datetime.now()
            return True

        # check if enough time passed
        is_allowed = (datetime.now() -
                      last_time).total_seconds() > allowed_every

        # memorize if we are sending this one
        if is_allowed:
            self.last_time_sent[field_key] = datetime.now()

        return is_allowed

    async def __setup_channel(
        self,
        address: str,
    ) -> Tuple[grpc.aio.Channel, dict]:
        logger = get_logger(__name__)

        channel_args = {
            "target": address,
        }

        # add auth if specified
        if self.credentials_cert:
            logger.debug("Using authentication.")
            channel_args["credentials"] = grpc.ssl_channel_credentials(
                root_certificates=self.credentials_cert,
                # private_key=self.credentials_key,
            )
            channel_constructor = grpc.aio.secure_channel
        else:
            logger.debug("No authentication used.")
            channel_constructor = grpc.aio.insecure_channel

        return channel_constructor, channel_args

    async def send_infinite_update_requests(
        self,
        last_known_state: ComputerInfo,
        stub: MonitoringStub,
        address_for_logging: str,
    ):
        """ Sends DataUpdateRequest in an infinite loop

        Parameters
        ----------
        last_known_state : ComputerInfo
            last known state to the server
        stub : MonitoringStub
            grpc stub connected to server
        address_for_logging : str
            ip address used for logging
        """
        logger = get_logger(__file__)

        stream = stub.SendMonitoringUpdate()

        previous_state = last_known_state
        while True:
            start_time = datetime.now()

            event_list, current_state = await get_update_events(
                machine_id=self.machine_id,
                initial_state=previous_state,
                chia_dog=self.chia_dog,
            )

            filtered_event_list = [
                update_event for update_event in event_list
                if self.is_event_allowed_to_be_sent(update_event)
            ]
            if not filtered_event_list:
                await wait_at_least(
                    min_duration=self.config.collect_data_every,
                    start_time=start_time)
                continue

            data_update_request = DataUpdateRequest(
                machine_id=self.machine_id,
                timestamp=datetime.now().timestamp(),
                events=filtered_event_list,
                machine_name=self.machine_name,
            )

            logger.info(
                "Sending message to %s: %s",
                address_for_logging,
                MessageToDict(data_update_request)
            )

            await stream.write(data_update_request)

            previous_state = current_state

            await wait_at_least(
                min_duration=self.config.collect_data_every,
                start_time=start_time)

    async def start_sending_updates(self):
        """ Starts sending updates to the server
        """

        logger = get_logger(__name__)
        logger.info("Starting to monitor system.")

        address = "{ip}:{port}".format(
            ip=self.config.address,
            port=self.config.port
        )

        channel_constructor, channel_args = await self.__setup_channel(
            address=address,
        )

        # don't do this at home kidz
        while True:
            try:
                # Open a connection to the server
                logger.debug("Connecting to %s", address)
                async with channel_constructor(**channel_args) \
                        as channel:

                    stub = MonitoringStub(channel)

                    # get last known state from the database
                    # we will compare to this and send the
                    # appropriate changes which happened
                    # in the meantime
                    logger.debug("Requesting last known state from server.")
                    last_known_state = await stub.GetMachineState(
                        GetStateRequest(
                            machine_id=self.machine_id
                        )
                    )
                    logger.debug(
                        "Received message %s",
                        MessageToDict(last_known_state),
                    )

                    # we can only send data once the watchdog
                    # is ready with it's init. Otherwise we will
                    # send updates for e.g. deleted plots which
                    # were just not found yet
                    await self.chia_dog.ready()

                    # send continuous updates
                    await self.send_infinite_update_requests(
                        last_known_state=last_known_state,
                        stub=stub,
                        address_for_logging=address,
                    )

            # in case of trouble reconnect
            except grpc.aio.AioRpcError as err:
                err_msg = "Connection error with %s (%d): %s"
                logger.error(
                    err_msg,
                    address,
                    err.code(),
                    err.details(),
                )
                await asyncio.sleep(5)

            except Exception:
                trace = traceback.format_exc()
                logger.error(trace)
                await asyncio.sleep(5)
