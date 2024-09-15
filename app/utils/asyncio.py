import asyncio
from typing import AsyncIterator


"""
Takes in a list of async generators and yields values from them as they become available (in any order) as if they were a single combined generator.
"""


async def combine_generators(*generators: AsyncIterator) -> AsyncIterator:
    tasks = {
        asyncio.create_task(coro=anext(gen, None), name=f"Task {idx}"): gen
        for idx, gen in enumerate(generators)
    }

    while tasks:
        # Wait for the first task to complete and yield the result
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            if (result := task.result()) is not None:
                print(f"TASK {task.get_name()} FINISHED ")
                yield result

            print("Evaluating task lifecyle...: ", tasks)
            generator = tasks.pop(task)

            if result and generator:
                next_task = asyncio.create_task(
                    coro=anext(generator, None), name=task.get_name()
                )
                print("Rescheduling next_task ", next_task)
                tasks[next_task] = generator
