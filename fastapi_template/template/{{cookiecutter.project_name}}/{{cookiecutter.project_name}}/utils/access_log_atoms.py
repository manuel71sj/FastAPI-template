import os
import time
from http import HTTPStatus

from starlette.requests import Request


class AccessLogAtoms(dict):  # type: ignore
    def __init__(
        self,
        request: Request,
        response: dict[str, list[tuple[bytes, bytes]] | int],
        request_time: float,
    ) -> None:
        for name, value in request["headers"]:
            self[f"{{{name.decode('latin1').lower()}}}i"] = value.decode("latin1")
        for name, value in os.environ.items():
            self[f"{{{name.lower()}}}e"] = value
        protocol = request.get("http_version", "ws")
        client = request.get("client")
        if client is None:
            remote_addr = None
        elif len(client) == 2:
            remote_addr = f"{client[0]}:{client[1]}"
        elif len(client) == 1:
            remote_addr = client[0]
        else:  # make sure not to throw UnboundLocalError
            remote_addr = f"<???{client}???>"
        if request["type"] == "http":
            method = request["method"]
        else:
            method = "GET"
        query_string = request["query_string"].decode()
        path_with_qs = request["path"] + ("?" + query_string if query_string else "")

        status_code = "-"
        status_phrase = "-"
        if response is not None:
            for name, value in response.get("headers", []):  # type: ignore
                self[f"{{{name.decode('latin1').lower()}}}o"] = value.decode("latin1")  # type: ignore # noqa: E501
            status_code = str(response["status"])
            try:
                status_phrase = HTTPStatus(response["status"]).phrase  # type: ignore
            except ValueError:
                status_phrase = f"<???{status_code}???>"
        self.update(
            {
                "h": remote_addr,
                "l": "-",
                "t": time.strftime("[%d/%b/%Y:%H:%M:%S %z]"),
                "r": f"{method} {request['path']} {protocol}",
                "R": f"{method} {path_with_qs} {protocol}",
                "s": status_code,
                "st": status_phrase,
                "S": request["scheme"],
                "m": method,
                "U": request["path"],
                "Uq": path_with_qs,
                "q": query_string,
                "H": protocol,
                "b": self["{Content-Length}o"],
                "B": self["{Content-Length}o"],
                "f": self["{Referer}i"],
                "a": self["{User-Agent}i"],
                "T": int(request_time),
                "D": int(request_time * 1_000_000),
                "L": f"{request_time:.6f}",
                "p": f"<{os.getpid()}>",
            }
        )

    def __getitem__(self, key: str) -> str:
        try:
            if key.startswith("{"):
                return super().__getitem__(key.lower())
            return super().__getitem__(key)
        except KeyError:
            return "-"
