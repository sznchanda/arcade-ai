from decimal import Decimal
from typing import Any, Sequence, TypeVar

import msgspec

from starlette.responses import JSONResponse


class MsgSpecJSONResponse(JSONResponse):
    """
    JSON response using the high-performance msgspec library to serialize data to JSON.
    """

    def render(self, content: Any) -> bytes:
        return msgspec.json.encode(content)
