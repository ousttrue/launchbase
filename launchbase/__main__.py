import asyncio

import prompt_toolkit


async def launch():
    app = prompt_toolkit.Application(full_screen=True)
    return await app.run_async()


def main():
    asyncio.run(launch())


if __name__ == "__main__":
    main()
