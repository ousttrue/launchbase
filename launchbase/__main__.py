import asyncio

import prompt_toolkit


async def main():
    app = prompt_toolkit.Application(full_screen=True)
    return await app.run_async()


if __name__ == "__main__":
    asyncio.run(main())
