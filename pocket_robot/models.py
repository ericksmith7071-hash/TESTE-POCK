"""
Modelos mínimos para o robô (placeholders).
Estes modelos são simplificados para evitar erros de import.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Asset:
    symbol: str
    name: Optional[str] = None

@dataclass
class Balance:
    amount: float
    currency: str = 'USD'

@dataclass
class Candle:
    time: datetime
    open: float
    close: float
    high: float
    low: float
    volume: int

@dataclass
class Order:
    id: str
    asset: str
    amount: float
    direction: str
    timestamp: datetime

@dataclass
class OrderResult:
    order: Order
    success: bool
    message: Optional[str] = None

@dataclass
class ConnectionStatus:
    connected: bool
    region: str
    uptime: float
