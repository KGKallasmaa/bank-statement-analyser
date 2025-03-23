"""
Balance reconciliation module for bank statement analysis.

This module contains functions to calculate totals from transactions and
verify if the calculated balance matches the reported closing balance.
"""

from typing import List, Optional
from pydantic import BaseModel
from src.main.utils import sum_moneys
from src.main.models.balance_analysis import BalanceAnalysis, Money, Transaction


class TransactionTotals(BaseModel):
    """Pydantic model for transaction totals."""
    total_deposits: Money
    total_withdrawals: Money
    net_change: Money


class ReconciliationResult(BaseModel):
    """Pydantic model for reconciliation results."""
    opening_balance: Money
    closing_balance: Money
    total_deposits: Money
    total_withdrawals: Money
    net_change: Money
    expected_closing_balance: Money
    reconciles: bool
    discrepancy_reason: Optional[str] = None
    transactions_count: int

    def is_valid(self) -> bool:
        return self.reconciles


def calculate_transaction_totals(
        transactions: List[Transaction]) -> TransactionTotals:
    """
    Calculate totals from a list of transactions.

    Args:
        transactions: List of transaction objects

    Returns:
        TransactionTotals: Pydantic model containing total deposits, withdrawals, and net change
    """
    if len(transactions) == 0:
        return TransactionTotals(
            total_deposits=Money(amount=0, currency=""),
            total_withdrawals=Money(amount=0, currency=""),
            net_change=Money(amount=0, currency="")
        )
    deposits = [t for t in transactions if t.money.amount > 0]
    withdrawals = [t for t in transactions if t.money.amount < 0]

    deposits_sum = Money(amount=0, currency="")
    withdrawals_sum = Money(amount=0, currency="")

    all_deposits = sum_moneys([t.money for t in deposits])
    if len(all_deposits) > 1:
        raise ValueError("Multiple currencies found in deposits")
    elif len(all_deposits) == 1:
        deposits_sum = all_deposits[0]

    all_withdrawals = sum_moneys([t.money for t in withdrawals])
    if len(all_withdrawals) > 1:
        raise ValueError("Multiple currencies found in withdrawals")
    elif len(all_withdrawals) == 1:
        withdrawals_sum = all_withdrawals[0]

    if deposits_sum.currency != "" and withdrawals_sum.currency != "":
        if deposits_sum.currency != withdrawals_sum.currency:
            raise ValueError(
                "Deposits and withdrawals have different currencies")

    net_change = Money(
        amount=deposits_sum.amount + withdrawals_sum.amount,
        currency=deposits_sum.currency
    )
    print(f"Total deposits: {deposits_sum}")
    print(f"Total withdrawals: {withdrawals_sum}")
    print(f"Net change: {net_change}")

    return TransactionTotals(
        total_deposits=deposits_sum,
        total_withdrawals=withdrawals_sum,
        net_change=net_change
    )


def reconcile_balances(
    balance_info: BalanceAnalysis,
    transactions: List[Transaction]
) -> ReconciliationResult:
    """
    Reconcile the calculated balance with the reported closing balance.

    Args:
        balance_info: Balance information from the statement
        transactions: List of transactions

    Returns:
        ReconciliationResult: Pydantic model with reconciliation results
    """
    # Calculate totals
    totals = calculate_transaction_totals(transactions)
    net_change = totals.net_change

    # Calculate expected closing balance
    expected_closing = balance_info.opening_balance.amount + net_change.amount
    # Check if balances reconcile
    difference = round(abs(expected_closing -
                           balance_info.closing_balance.amount), 3)
    reconciles = difference < 0.01

    if not reconciles:
        # Create a more detailed discrepancy reason
        discrepancy_reason = (
            f"Discrepancy detected:"
            f"Opening balance: {balance_info.opening_balance}"
            f"Total deposits: {totals.total_deposits}"
            f"Total withdrawals: {totals.total_withdrawals}"
            f"Net change: {net_change}"
            f"Expected closing balance: {expected_closing}"
            f"Reported closing balance: {balance_info.closing_balance}"
            f"Difference (should be less than 0.01): {difference}"
            f"This may be due to missing transactions, fees not captured in the transaction list, "
            f"or calculation errors."
        )

        for tx in transactions:
            print(tx.money.amount)

        return ReconciliationResult(
            opening_balance=balance_info.opening_balance,
            closing_balance=balance_info.closing_balance,
            total_deposits=totals.total_deposits,
            total_withdrawals=totals.total_withdrawals,
            net_change=net_change,
            expected_closing_balance=Money(
                amount=expected_closing,
                currency=balance_info.closing_balance.currency),
            reconciles=False,
            discrepancy_reason=discrepancy_reason,
            transactions_count=len(transactions)
        )

    return ReconciliationResult(
        opening_balance=balance_info.opening_balance,
        closing_balance=balance_info.closing_balance,
        total_deposits=totals.total_deposits,
        total_withdrawals=totals.total_withdrawals,
        net_change=net_change,
        expected_closing_balance=Money(
            amount=expected_closing,
            currency=balance_info.closing_balance.currency),
        reconciles=True,
        transactions_count=len(transactions)
    )
