from datetime import datetime, time, timedelta


class MarketSessionService:
    @staticmethod
    def classify(timestamp: datetime, open_time: time, close_time: time) -> str:
        if timestamp.weekday() >= 5:
            return 'CLOSED'
        local_time = timestamp.time()
        if open_time <= local_time <= close_time:
            return 'OPEN'
        if local_time < open_time:
            return 'PRE_MARKET'
        return 'POST_MARKET'
