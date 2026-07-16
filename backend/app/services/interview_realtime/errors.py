"""Domain errors translated to stable HTTP responses by the route layer."""


class RealtimeInterviewError(Exception):
    """Base class for expected Phase 8 service failures."""


class RealtimeInterviewNotFound(RealtimeInterviewError):
    pass


class RealtimeInterviewValidationError(RealtimeInterviewError):
    pass


class RealtimeInterviewConflict(RealtimeInterviewError):
    pass


class RealtimeInterviewUnavailable(RealtimeInterviewError):
    pass


class RealtimeInterviewProviderUnavailable(RealtimeInterviewUnavailable):
    pass
