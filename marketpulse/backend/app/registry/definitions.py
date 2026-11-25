from dataclasses import dataclass


@dataclass(frozen=True)
class CountryDefinition:
    code: str
    name: str
    currency: str
    timezone: str


@dataclass(frozen=True)
class ExchangeDefinition:
    code: str
    name: str
    country_code: str
    yahoo_suffix: str | None
    currency: str
    timezone: str
    enabled: bool = True


COUNTRIES = (
    CountryDefinition('US','United States','USD','America/New_York'),
    CountryDefinition('GB','United Kingdom','GBP','Europe/London'),
    CountryDefinition('IN','India','INR','Asia/Kolkata'),
    CountryDefinition('JP','Japan','JPY','Asia/Tokyo'),
    CountryDefinition('CN','China','CNY','Asia/Shanghai'),
    CountryDefinition('HK','Hong Kong','HKD','Asia/Hong_Kong'),
    CountryDefinition('DE','Germany','EUR','Europe/Berlin'),
    CountryDefinition('FR','France','EUR','Europe/Paris'),
    CountryDefinition('CA','Canada','CAD','America/Toronto'),
    CountryDefinition('AU','Australia','AUD','Australia/Sydney'),
    CountryDefinition('KR','South Korea','KRW','Asia/Seoul'),
    CountryDefinition('TW','Taiwan','TWD','Asia/Taipei'),
    CountryDefinition('BR','Brazil','BRL','America/Sao_Paulo'),
    CountryDefinition('CH','Switzerland','CHF','Europe/Zurich'),
    CountryDefinition('NL','Netherlands','EUR','Europe/Amsterdam'),
    CountryDefinition('SE','Sweden','SEK','Europe/Stockholm'),
    CountryDefinition('SG','Singapore','SGD','Asia/Singapore'),
    CountryDefinition('SA','Saudi Arabia','SAR','Asia/Riyadh'),
    CountryDefinition('ZA','South Africa','ZAR','Africa/Johannesburg'),
    CountryDefinition('AE','United Arab Emirates','AED','Asia/Dubai'),
)

EXCHANGES = (
    ExchangeDefinition('NYSE','New York Stock Exchange','US','', 'USD','America/New_York'),
    ExchangeDefinition('NASDAQ','NASDAQ','US','', 'USD','America/New_York'),
    ExchangeDefinition('LSE','London Stock Exchange','GB','L', 'GBP','Europe/London'),
    ExchangeDefinition('NSE','National Stock Exchange of India','IN','NS','INR','Asia/Kolkata'),
    ExchangeDefinition('BSE','Bombay Stock Exchange','IN','BO','INR','Asia/Kolkata'),
    ExchangeDefinition('TSE','Tokyo Stock Exchange','JP','T','JPY','Asia/Tokyo'),
    ExchangeDefinition('SSE','Shanghai Stock Exchange','CN','SS','CNY','Asia/Shanghai'),
    ExchangeDefinition('SZSE','Shenzhen Stock Exchange','CN','SZ','CNY','Asia/Shanghai'),
    ExchangeDefinition('HKEX','Hong Kong Exchanges','HK','HK','HKD','Asia/Hong_Kong'),
    ExchangeDefinition('XETRA','Xetra','DE','DE','EUR','Europe/Berlin'),
    ExchangeDefinition('EURONEXT_PARIS','Euronext Paris','FR','PA','EUR','Europe/Paris'),
    ExchangeDefinition('TSX','Toronto Stock Exchange','CA','TO','CAD','America/Toronto'),
    ExchangeDefinition('ASX','Australian Securities Exchange','AU','AX','AUD','Australia/Sydney'),
    ExchangeDefinition('KRX','Korea Exchange','KR','KS','KRW','Asia/Seoul'),
    ExchangeDefinition('TWSE','Taiwan Stock Exchange','TW','TW','TWD','Asia/Taipei'),
    ExchangeDefinition('B3','B3 Brasil Bolsa Balcao','BR','SA','BRL','America/Sao_Paulo'),
    ExchangeDefinition('SIX','SIX Swiss Exchange','CH','SW','CHF','Europe/Zurich'),
    ExchangeDefinition('EURONEXT_AMS','Euronext Amsterdam','NL','AS','EUR','Europe/Amsterdam'),
    ExchangeDefinition('NASDAQ_STOCKHOLM','Nasdaq Stockholm','SE','ST','SEK','Europe/Stockholm'),
    ExchangeDefinition('SGX','Singapore Exchange','SG','SI','SGD','Asia/Singapore'),
    ExchangeDefinition('TADAWUL','Saudi Exchange','SA','SR','SAR','Asia/Riyadh'),
    ExchangeDefinition('JSE','Johannesburg Stock Exchange','ZA','JO','ZAR','Africa/Johannesburg'),
    ExchangeDefinition('ADX','Abu Dhabi Securities Exchange','AE','AD','AED','Asia/Dubai'),
)
