import re


class SubscriptionService:
    @staticmethod
    def validate(symbols: list[str]) -> list[str]:
        validated = []
        for symbol in symbols:
            cleaned = str(symbol).strip().upper()
            if not cleaned or len(cleaned) > 50 or not re.fullmatch(r'[A-Z0-9.&/^_-]+', cleaned):
                raise ValueError(f'Invalid symbol: {symbol}')
            validated.append(cleaned)
        return list(dict.fromkeys(validated))
