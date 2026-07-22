"""Domain errors translated to stable HTTP responses by the route layer."""


class RealtimeInterviewError(Exception):
    """Base class for expected Phase 8 service failures."""


class RealtimeInterviewNotFound(RealtimeInterviewError):
    pass


class RealtimeInterviewValidationError(RealtimeInterviewError):
    pass


class RealtimeInterviewConflict(RealtimeInterviewError):
    pass


class RealtimeInterviewThrottled(RealtimeInterviewConflict):
    """A retryable conflict with a bounded server-owned retry delay."""

    def __init__(self, message: str, *, retry_after_seconds: int) -> None:
        super().__init__(message)
        self.retry_after_seconds = max(1, retry_after_seconds)


class RealtimeInterviewUnavailable(RealtimeInterviewError):
    pass


class RealtimeInterviewProviderUnavailable(RealtimeInterviewUnavailable):
    pass
