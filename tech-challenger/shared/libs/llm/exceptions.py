class LLMInvokeError(Exception):
    """Raised when the SageMaker endpoint invocation fails."""


class LLMResponseParseError(Exception):
    """Raised when the SageMaker response cannot be parsed."""
