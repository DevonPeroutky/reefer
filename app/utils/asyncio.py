import asyncio
from typing import AsyncIterator


async def combine_generators(*generators: AsyncIterator) -> AsyncIterator:
    tasks = {asyncio.create_task(anext(gen, None)): gen for gen in generators}

    while tasks:
        # Wait for the first task to complete and yield the result
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            if (result := task.result()) is not None:
                yield result

            generator = tasks.pop(task)

            if result and generator:
                next_task = asyncio.create_task(anext(generator, None))
                print("Rescheduling next_task ", next_task)
                tasks[next_task] = generator
