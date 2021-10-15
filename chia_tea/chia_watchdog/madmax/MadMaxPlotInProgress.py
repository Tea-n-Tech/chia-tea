from datetime import datetime
from typing import Optional


class MadMaxPercentages:
    phase1 = (
        0.02232820817,
        0.08422978293,
        0.172304759,
        0.2580199571,
        0.3384422125,
        0.4093906676,
        0.4595129564,
    )
    phase2 = (
        0.4671522489,
        0.4938333946,
        0.5033927017,
        0.5267895266,
        0.5361274338,
        0.5582587301,
        0.5674848834,
        0.5905356127,
        0.6002520189,
        0.6219090798,
        0.6310177749,
        0.6531890657,
    )
    phase3 = (
        0.67627183,
        0.7014293004,
        0.7286114592,
        0.755564902,
        0.7815212812,
        0.8093481191,
        0.8359168967,
        0.8643466994,
        0.892014296,
        0.9206682944,
        0.9560488983,
        0.9878807454,
    )
    phase4 = 1


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
