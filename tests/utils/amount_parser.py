"""
EUR Amount Parser for COST Action CA19130 Budget Verification.

CRITICAL FIX: Handles space-separated thousands in European number format.

The systematic error identified in previous verification:
- FFR documents use space as thousands separator: "1 011.15"
- Incorrect parsing dropped the thousands portion: stored as "11.15"
- This affected 175 participant reimbursements across 65 participants

This module provides the corrected parser that handles:
- Space-separated thousands: "1 011.15" -> 1011.15
- Comma-separated thousands: "1,011.15" -> 1011.15
- Negative amounts: "-42.50" -> -42.50
- EUR/euro symbols: "EUR 1,000.00" -> 1000.00
"""

import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Union, Optional


def parse_eur_amount(text: Optional[str]) -> Decimal:
    """
    Parse EUR amount from FFR/WBP text, handling space-separated thousands.

    FIXES the known bug where "1 011.15" was parsed as "11.15".

    Args:
        text: String containing EUR amount, possibly with:
              - Space as thousands separator (European format)
              - Comma as thousands separator
              - EUR or euro symbol prefix
              - Negative sign

    Returns:
        Decimal value rounded to 2 decimal places

    Examples:
        >>> parse_eur_amount("1 011.15")
        Decimal('1011.15')
        >>> parse_eur_amount("148 194.99")
        Decimal('148194.99')
        >>> parse_eur_amount("EUR 10,300.30")
        Decimal('10300.30')
        >>> parse_eur_amount("-42.50")
        Decimal('-42.50')
        >>> parse_eur_amount("")
        Decimal('0.00')
    """
    if not text or str(text).strip() == '':
        return Decimal("0.00")

    # Convert to string and strip
    text = str(text).strip()

    # Remove EUR symbol and variations
    text = re.sub(r'EUR|euro|€', '', text, flags=re.IGNORECASE).strip()

    # CRITICAL: Remove space thousands separator (European format)
    # This is the fix for the "1 011.15" -> "11.15" bug
    text = text.replace(' ', '')

    # Remove comma thousands separator
    text = text.replace(',', '')

    # Handle empty result after cleanup
    if not text or text == '-':
        return Decimal("0.00")

    try:
        return Decimal(text).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        return Decimal("0.00")


def parse_eur_amount_float(text: Optional[str]) -> float:
    """
    Parse EUR amount as float (for backward compatibility).

    Args:
        text: String containing EUR amount

    Returns:
        Float value (use parse_eur_amount for precision-critical operations)
    """
    return float(parse_eur_amount(text))


def validate_amount_format(text: str) -> bool:
    """
    Validate that a string represents a valid EUR amount.

    Args:
        text: String to validate

    Returns:
        True if valid EUR amount format, False otherwise
    """
    if not text or str(text).strip() == '':
        return False

    # Pattern for valid EUR amounts with optional space/comma thousands separators
    pattern = r'^-?(?:EUR\s*|€\s*)?[\d\s,]+\.?\d*$'
    return bool(re.match(pattern, str(text).strip(), re.IGNORECASE))


def format_eur_amount(amount: Union[Decimal, float, int], include_symbol: bool = True) -> str:
    """
    Format amount as EUR string for display.

    Args:
        amount: Numeric value to format
        include_symbol: Whether to include EUR suffix

    Returns:
        Formatted string like "1,234.56 EUR"
    """
    decimal_amount = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    formatted = f"{decimal_amount:,.2f}"
    if include_symbol:
        return f"{formatted} EUR"
    return formatted
