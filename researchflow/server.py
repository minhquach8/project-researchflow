from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def serve_directory(
    directory: Path,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    """
    Serve the given directory over HTTP using Python's built-in server.

    This function blocks the current process until interrupted (Ctrl+C).
    """
    resolved_dir = directory.resolve()

    if not resolved_dir.is_dir():
        raise ValueError(f"Directory does not exist or is not a folder: {resolved_dir}")

    handler_class = partial(
        SimpleHTTPRequestHandler,
        directory=str(resolved_dir),
    )

    httpd = ThreadingHTTPServer((host, port), handler_class)

    print(f"Serving {resolved_dir} at http://{host}:{port}/")
    print("Press Ctrl+C to stop.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        httpd.server_close()
