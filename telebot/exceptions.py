class TelegramAPIError(Exception):
    def __init__(self, description: str, error_code: int | None = None):
        super().__init__(f"{error_code or ''} {description}".strip())
        self.error_code = error_code
        self.description = description

    @classmethod
    def from_payload(cls, payload: dict) -> "TelegramAPIError":
        code = payload.get("error_code")
        desc = payload.get("description", "Unknown error!")

        if code == 429:
            return TelegramRetryAfter(
                desc,
                retry_after=payload.get("parameters", {}).get("retry_after", 0)
            )

        exc_cls = ERROR_MAP.get(code, cls)
        return exc_cls(desc, code)


class TelegramBadRequest(TelegramAPIError):
    pass

class TelegramUnauthorized(TelegramAPIError):
    pass

class TelegramForbidden(TelegramAPIError):
    pass

class TelegramRetryAfter(TelegramAPIError):
    def __init__(self, description:str, retry_after: int):
        super().__init__(description, 429)
        self.retry_after = retry_after

ERROR_MAP = {
    400: TelegramBadRequest,
    401: TelegramUnauthorized,
    403: TelegramForbidden,
    429: TelegramRetryAfter
}
