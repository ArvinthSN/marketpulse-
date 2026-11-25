from app.market_data.streaming.stream_manager import LiveEventProcessor


def test_event_processor_starts_with_metrics():
    class Cache:
        pass
    class PubSub:
        pass
    class Connections:
        pass
    processor = LiveEventProcessor(Cache(), PubSub(), Connections())
    assert processor.metrics['received'] == 0
