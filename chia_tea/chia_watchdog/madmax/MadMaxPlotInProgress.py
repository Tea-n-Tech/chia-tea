from datetime import datetime
from typing import Optional


class MadMaxPlotInProgress:
    def __init__(
        self,
        public_key: str,
        pool_public_key: str,
        farmer_public_key: str,
        start_time: datetime,
        end_time: Optional[datetime],
        progress: float,
        end_time_copy: Optional[datetime],
        plot_type: int,
        state: str,
    ) -> None:
        """
        Parameters
        ----------
        public_key : str
            public key of the plot
        pool_public_key : str
            public key of the pool
        farmer_public_key : str
            public key of the farmer
        start_time : datetime
            time plotting started
        end_time : datetime
            time plotting finished
        progress : float
            precentage of progress
        end_time_copy : datetime
            time copying finished
        plot_type : int
            plot type such as 32 for k32
        state : str
            the state of the plot
        """
        self.public_key = public_key
        self.pool_public_key = pool_public_key
        self.farmer_public_key = farmer_public_key
        self.start_time = start_time
        self.end_time = end_time
        self.progress = progress
        self.end_time_copy = end_time_copy
        self.plot_type = plot_type
        self.state = state

    def copy(self) -> "MadMaxPlotInProgress":
        """Get a copy of the instance

        Returns
        -------
        plot : MadMaxPlotInProgress
            copy of this instance
        """
        return MadMaxPlotInProgress(**self.__dict__)
