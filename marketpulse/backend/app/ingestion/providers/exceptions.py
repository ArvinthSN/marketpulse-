class ProviderError(RuntimeError):
    pass


class ProviderTimeoutError(ProviderError):
    pass


class UnsupportedSymbolError(ProviderError):
    pass


class RateLimitError(ProviderError):
    pass
