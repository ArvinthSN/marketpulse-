from app.utils.retry import retry_with_backoff


def test_retry_eventually_succeeds():
    calls = []
    def operation():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError('temporary')
        return 'ok'

    result = retry_with_backoff(operation, max_attempts=3, base_delay=0, jitter_ratio=0,
                                retryable_exceptions=(RuntimeError,), sleep=lambda _: None)
    assert result == 'ok'
    assert len(calls) == 3


def test_retry_rejects_zero_attempts():
    import pytest
    with pytest.raises(ValueError):
        retry_with_backoff(lambda: None, max_attempts=0)
