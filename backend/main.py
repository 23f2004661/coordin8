"""Coordin8 Backend CLI Entrypoint.

Starts the FastAPI server with uvicorn using configuration from app.core.config.
"""

import uvicorn
from app.core.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "development",
        log_level="info",
    )


if __name__ == "__main__":
    main()
