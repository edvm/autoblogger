"""
Autoblogger - Generate content on demand using online data in real time.
Copyright (C) 2025  Emiliano Dalla Verde Marcozzi <edvm.inbox@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""Credits management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ..database import get_db, User, CreditTransaction
from ..auth import get_current_user

router = APIRouter()


# Pydantic models
class CreditTransactionResponse(BaseModel):
    """Credit transaction response model."""

    id: int
    amount: int
    transaction_type: str
    description: Optional[str]
    reference_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CreditBalance(BaseModel):
    """User credit balance model."""

    user_id: int
    credits: int
    email: str


class CreditPurchase(BaseModel):
    """Credit purchase request model."""

    amount: int
    payment_reference: Optional[str] = None


@router.get("/balance", response_model=CreditBalance)
async def get_credit_balance(current_user: User = Depends(get_current_user)):
    """Get current user's credit balance."""
    return CreditBalance(
        user_id=current_user.id, credits=current_user.credits, email=current_user.email
    )


@router.get("/transactions", response_model=List[CreditTransactionResponse])
async def get_credit_transactions(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's credit transaction history."""
    transactions = (
        db.query(CreditTransaction)
        .filter(CreditTransaction.user_id == current_user.id)
        .order_by(CreditTransaction.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return transactions


@router.post("/purchase", response_model=CreditTransactionResponse)
async def purchase_credits(
    purchase: CreditPurchase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Purchase credits (placeholder for future payment integration)."""

    if purchase.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credit amount must be positive",
        )

    if purchase.amount > 10000:  # Reasonable limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Credit amount too large"
        )

    # Create credit transaction
    transaction = CreditTransaction(
        user_id=current_user.id,
        amount=purchase.amount,
        transaction_type="purchase",
        description=f"Credit purchase: {purchase.amount} credits",
        reference_id=purchase.payment_reference,
    )

    # Update user credits
    current_user.credits += purchase.amount
    current_user.updated_at = datetime.utcnow()

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


def consume_credits(
    user: User,
    amount: int,
    description: str,
    reference_id: Optional[str] = None,
    db: Session = None,
) -> CreditTransaction:
    """
    Internal function to consume credits from a user account.
    This will be used by app endpoints when users consume apps.
    """
    if user.credits < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient credits"
        )

    # Create credit transaction
    transaction = CreditTransaction(
        user_id=user.id,
        amount=-amount,  # Negative for consumption
        transaction_type="usage",
        description=description,
        reference_id=reference_id,
    )

    # Update user credits
    user.credits -= amount
    user.updated_at = datetime.utcnow()

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction
