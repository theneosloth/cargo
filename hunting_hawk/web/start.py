import logging
import os

import uvicorn


def start() -> None:
    port = int(os.getenv("HUNTING_HAWK_PORT", "8080"))
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        "hunting_hawk.web.api:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    start()
