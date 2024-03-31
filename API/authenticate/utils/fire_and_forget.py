import asyncio


def fire_and_forget(f):
    """run it and forget it"""

    def wrapped(*args, **kwargs):
        loop = asyncio.new_event_loop()
        loop.run_in_executor(
            None, f, *args, *kwargs)
        loop.close()

    return wrapped
