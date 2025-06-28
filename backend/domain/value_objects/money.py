"""
Money Value Object

This module defines the Money value object which represents monetary values
with currency in the Sophia AI system.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Union


class Currency(Enum):
    """Enumeration of supported currencies."""

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CNY = "CNY"


@dataclass(frozen=True)
class Money:
    """
    Value object representing a monetary amount with currency.

    This is an immutable value object that ensures monetary calculations
    are performed correctly with proper precision.
    """

    amount: Decimal
    currency: Currency

    def __post_init__(self):
        """Validate money on creation."""
        # Ensure amount is a Decimal
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))

        # Validate amount is not negative for most business cases
        # (can be overridden for specific use cases like refunds)
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

        # Validate currency
        if not isinstance(self.currency, Currency):
            raise ValueError(f"Invalid currency: {self.currency}")

    @classmethod
    def from_string(cls, amount_str: str, currency: Union[str, Currency]) -> "Money":
        """
        Create Money from string representation.

        Args:
            amount_str: String representation of amount
            currency: Currency code or Currency enum

        Returns:
            Money: New Money instance
        """
        # Parse amount
        amount = Decimal(amount_str.replace(",", "").replace("$", "").strip())

        # Parse currency
        if isinstance(currency, str):
            currency = Currency(currency.upper())

        return cls(amount=amount, currency=currency)

    @classmethod
    def zero(cls, currency: Currency) -> "Money":
        """
        Create zero money for a given currency.

        Args:
            currency: The currency for zero amount

        Returns:
            Money: Zero money instance
        """
        return cls(amount=Decimal("0"), currency=currency)

    def __str__(self) -> str:
        """String representation of money."""
        # Format based on currency
        if self.currency == Currency.USD:
            return f"${self.amount:,.2f}"
        elif self.currency == Currency.EUR:
            return f"€{self.amount:,.2f}"
        elif self.currency == Currency.GBP:
            return f"£{self.amount:,.2f}"
        elif self.currency == Currency.JPY:
            return f"¥{self.amount:,.0f}"
        else:
            return f"{self.currency.value} {self.amount:,.2f}"

    def __repr__(self) -> str:
        """Developer representation of money."""
        return f"Money(amount={self.amount}, currency={self.currency.value})"

    def __eq__(self, other: object) -> bool:
        """Check equality of money values."""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: "Money") -> bool:
        """Compare money values."""
        self._ensure_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        """Compare money values."""
        self._ensure_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        """Compare money values."""
        self._ensure_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        """Compare money values."""
        self._ensure_same_currency(other)
        return self.amount >= other.amount

    def __add__(self, other: "Money") -> "Money":
        """Add money values."""
        self._ensure_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: "Money") -> "Money":
        """Subtract money values."""
        self._ensure_same_currency(other)
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Subtraction would result in negative money")
        return Money(amount=result, currency=self.currency)

    def __mul__(self, scalar: Union[int, float, Decimal]) -> "Money":
        """Multiply money by a scalar."""
        if isinstance(scalar, (int, float)):
            scalar = Decimal(str(scalar))
        return Money(amount=self.amount * scalar, currency=self.currency)

    def __truediv__(self, scalar: Union[int, float, Decimal]) -> "Money":
        """Divide money by a scalar."""
        if isinstance(scalar, (int, float)):
            scalar = Decimal(str(scalar))
        if scalar == 0:
            raise ValueError("Cannot divide by zero")
        return Money(amount=self.amount / scalar, currency=self.currency)

    def _ensure_same_currency(self, other: "Money") -> None:
        """
        Ensure two money values have the same currency.

        Args:
            other: Other money value to compare

        Raises:
            ValueError: If currencies don't match
        """
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot perform operation on different currencies: "
                f"{self.currency.value} and {other.currency.value}"
            )

    def round(self, decimal_places: int = 2) -> "Money":
        """
        Round money to specified decimal places.

        Args:
            decimal_places: Number of decimal places

        Returns:
            Money: Rounded money value
        """
        quantizer = Decimal(f"0.{'0' * decimal_places}")
        rounded_amount = self.amount.quantize(quantizer)
        return Money(amount=rounded_amount, currency=self.currency)

    def to_cents(self) -> int:
        """
        Convert money to cents (or smallest unit).

        Returns:
            int: Amount in cents
        """
        if self.currency == Currency.JPY:
            # JPY doesn't have decimal places
            return int(self.amount)
        else:
            return int(self.amount * 100)

    @classmethod
    def from_cents(cls, cents: int, currency: Currency) -> "Money":
        """
        Create money from cents (or smallest unit).

        Args:
            cents: Amount in cents
            currency: Currency

        Returns:
            Money: Money instance
        """
        if currency == Currency.JPY:
            # JPY doesn't have decimal places
            amount = Decimal(str(cents))
        else:
            amount = Decimal(str(cents)) / 100

        return cls(amount=amount, currency=currency)

    def format(self, include_currency_code: bool = False) -> str:
        """
        Format money for display.

        Args:
            include_currency_code: Whether to include currency code

        Returns:
            str: Formatted money string
        """
        formatted = str(self)
        if include_currency_code:
            formatted = f"{formatted} {self.currency.value}"
        return formatted
