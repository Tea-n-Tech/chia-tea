import asyncio
import os
from typing import AsyncGenerator, Awaitable, Callable, Coroutine, Optional, TextIO, Union

from ..utils.logger import get_logger


async def watch_lines_infinitely(
    filepath: str,
    on_file_missing: Optional[Coroutine] = None,
    on_ready: Optional[Coroutine] = None,
    on_line: Optional[Callable[[str], Awaitable[None]]] = None,
):
    """Start watching the specified file

    Parameters
    ----------
    filepath : str
        filepath to the file to be watched
    on_file_missing: Optional[Coroutine]
        function to be called when the specified logfile
        does not exist
    on_ready : Optional[Coroutine]
        function to be called when the initial startup
        has been completed (all current lines read)
    on_line : Optional[Callable[[str], Awaitable[None]]]
        function to be triggered if a new line has
        been found in the file
    """

    if not filepath:
        if on_file_missing is not None:
            await on_file_missing()
        return

    logger = get_logger(__name__)
    logger.debug("Searching logfile: %s", filepath)

    # try to watch file
    file_missing_was_run = False
    line_generator: Union[None, AsyncGenerator[str, None]] = None
    while line_generator is None:
        try:
            line_generator = watch_logfile_generator(
                filepath=filepath,
                on_ready=on_ready,
            )

            logger.debug("Logfile '%s' found. Starting to watch it.", filepath)

            # process lines
            async for line in line_generator:
                if on_line is not None:
                    await on_line(line)

        except FileNotFoundError:
            # in case there is no log file (yet) simply
            # wait gently for one to appear
            logger.info("Logfile %s not found, waiting for one to appear.", filepath)
            await asyncio.sleep(3)
            if on_file_missing is not None and not file_missing_was_run:
                await on_file_missing()
                file_missing_was_run = True


async def watch_logfile_generator(
    filepath: str, on_ready: Optional[Coroutine] = None, interval_seconds: float = 1
) -> AsyncGenerator[str, None]:
    """Watch a logfile for changes

    Parameters
    ----------
    filepath : str
        path to the logfile to watch
    on_ready: Optional[Coroutine] = None,
        function to be called if initial lines were loaded
    interval_seconds : str
        timing interval in which to check the file for new content

    Yields
    ------
    line : str
        a newly added line to the file
    """
    logger = get_logger(__name__)

    if filepath.startswith("~"):
        filepath = os.path.expanduser(filepath)

    # loop for reopening the log file
    # chia uses a rotating logging scheme
    # moving the log file when it's full
    # and making a new one in-place.
    # To keep track we need to reopen the new file
    while True:
        logger.debug("(Re)opening logfile: %s", filepath)
        with open(filepath, "r", encoding="utf8") as fp:
            while True:

                # yield as many lines as there are
                new_line = fp.readline()
                while new_line:

                    # must be placed here so when we yielded
                    # the last line we caught up
                    if _end_of_file(fp):
                        await on_ready()

                    terminate = yield new_line
                    if terminate:
                        raise StopAsyncIteration()
                    new_line = fp.readline()

                # sleep to give it a rest
                await asyncio.sleep(interval_seconds)

                # check if file was replaced, then rewind
                if _file_was_replaced_or_cleared(fp, filepath):
                    break

        if terminate:
            break


def _end_of_file(fp: TextIO) -> bool:
    return fp.tell() == os.stat(fp.fileno()).st_size


def _file_was_replaced_or_cleared(fp: TextIO, filepath: str) -> bool:
    return fp.tell() > os.stat(filepath).st_size
