"""
Revenue Service - Business logic for revenue/payment tracking
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.revenue import Revenue
from app.models.license import License
from app.models.user import User


class RevenueService:
    """Service for revenue operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        license_id: int,
        amount: Decimal,
        currency: str = "EUR",
        payment_type: str = "extension",
        notes: Optional[str] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        created_by_id: Optional[int] = None
    ) -> Revenue:
        """Create a new revenue entry"""
        # Get user_id from license
        result = await self.db.execute(
            select(License).where(License.id == license_id)
        )
        license = result.scalar_one_or_none()
        user_id = license.user_id if license else None
        
        revenue = Revenue(
            license_id=license_id,
            user_id=user_id,
            amount=amount,
            currency=currency,
            payment_type=payment_type,
            notes=notes,
            period_start=period_start,
            period_end=period_end,
            created_by_id=created_by_id
        )
        
        self.db.add(revenue)
        await self.db.commit()
        await self.db.refresh(revenue)
        
        return revenue
    
    async def get_by_id(self, revenue_id: int) -> Optional[Revenue]:
        """Get revenue entry by ID"""
        result = await self.db.execute(
            select(Revenue).where(Revenue.id == revenue_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        license_id: Optional[int] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List[Revenue], int, Decimal]:
        """Get all revenue entries with filters"""
        query = select(Revenue)
        count_query = select(func.count(Revenue.id))
        sum_query = select(func.coalesce(func.sum(Revenue.amount), 0))
        
        # Apply filters
        if license_id:
            query = query.where(Revenue.license_id == license_id)
            count_query = count_query.where(Revenue.license_id == license_id)
            sum_query = sum_query.where(Revenue.license_id == license_id)
        
        if user_id:
            query = query.where(Revenue.user_id == user_id)
            count_query = count_query.where(Revenue.user_id == user_id)
            sum_query = sum_query.where(Revenue.user_id == user_id)
        
        if start_date:
            query = query.where(Revenue.created_at >= start_date)
            count_query = count_query.where(Revenue.created_at >= start_date)
            sum_query = sum_query.where(Revenue.created_at >= start_date)
        
        if end_date:
            query = query.where(Revenue.created_at <= end_date)
            count_query = count_query.where(Revenue.created_at <= end_date)
            sum_query = sum_query.where(Revenue.created_at <= end_date)
        
        # Execute queries
        result = await self.db.execute(
            query.order_by(Revenue.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        revenues = result.scalars().all()
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        sum_result = await self.db.execute(sum_query)
        total_amount = sum_result.scalar() or Decimal("0")
        
        return revenues, total, total_amount
    
    async def get_for_license(self, license_id: int) -> List[Revenue]:
        """Get all revenue entries for a specific license"""
        result = await self.db.execute(
            select(Revenue)
            .where(Revenue.license_id == license_id)
            .order_by(Revenue.created_at.desc())
        )
        return result.scalars().all()
    
    async def delete(self, revenue_id: int) -> bool:
        """Delete a revenue entry"""
        revenue = await self.get_by_id(revenue_id)
        if not revenue:
            return False
        
        await self.db.delete(revenue)
        await self.db.commit()
        return True
    
    async def get_summary(self) -> dict:
        """Get revenue summary/statistics"""
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Total revenue
        total_result = await self.db.execute(
            select(func.coalesce(func.sum(Revenue.amount), 0))
        )
        total_revenue = total_result.scalar() or Decimal("0")
        
        # Revenue this month
        month_result = await self.db.execute(
            select(func.coalesce(func.sum(Revenue.amount), 0))
            .where(Revenue.created_at >= start_of_month)
        )
        revenue_this_month = month_result.scalar() or Decimal("0")
        
        # Revenue this year
        year_result = await self.db.execute(
            select(func.coalesce(func.sum(Revenue.amount), 0))
            .where(Revenue.created_at >= start_of_year)
        )
        revenue_this_year = year_result.scalar() or Decimal("0")
        
        # Total transactions
        count_result = await self.db.execute(
            select(func.count(Revenue.id))
        )
        total_transactions = count_result.scalar() or 0
        
        # Transactions this month
        month_count_result = await self.db.execute(
            select(func.count(Revenue.id))
            .where(Revenue.created_at >= start_of_month)
        )
        transactions_this_month = month_count_result.scalar() or 0
        
        # Average transaction
        avg_transaction = total_revenue / total_transactions if total_transactions > 0 else Decimal("0")
        
        # By currency
        currency_result = await self.db.execute(
            select(Revenue.currency, func.sum(Revenue.amount))
            .group_by(Revenue.currency)
        )
        by_currency = {row[0]: float(row[1]) for row in currency_result.fetchall()}
        
        # By payment type
        type_result = await self.db.execute(
            select(Revenue.payment_type, func.sum(Revenue.amount))
            .group_by(Revenue.payment_type)
        )
        by_payment_type = {row[0]: float(row[1]) for row in type_result.fetchall()}
        
        # Monthly breakdown (last 12 months)
        monthly_breakdown = []
        for i in range(11, -1, -1):
            month_start = (now.replace(day=1) - timedelta(days=i*30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1)
            
            month_result = await self.db.execute(
                select(func.coalesce(func.sum(Revenue.amount), 0))
                .where(Revenue.created_at >= month_start)
                .where(Revenue.created_at < month_end)
            )
            month_amount = month_result.scalar() or Decimal("0")
            
            monthly_breakdown.append({
                "month": month_start.strftime("%Y-%m"),
                "amount": float(month_amount)
            })
        
        return {
            "total_revenue": total_revenue,
            "revenue_this_month": revenue_this_month,
            "revenue_this_year": revenue_this_year,
            "total_transactions": total_transactions,
            "transactions_this_month": transactions_this_month,
            "average_transaction": avg_transaction,
            "by_currency": by_currency,
            "by_payment_type": by_payment_type,
            "monthly_breakdown": monthly_breakdown
        }
    
    async def enrich_revenue(self, revenue: Revenue) -> dict:
        """Enrich revenue with license and user info"""
        # Get license info
        license_result = await self.db.execute(
            select(License).where(License.id == revenue.license_id)
        )
        license = license_result.scalar_one_or_none()
        
        # Get user info
        user_result = await self.db.execute(
            select(User).where(User.id == revenue.user_id)
        ) if revenue.user_id else None
        user = user_result.scalar_one_or_none() if user_result else None
        
        return {
            "id": revenue.id,
            "license_id": revenue.license_id,
            "user_id": revenue.user_id,
            "amount": revenue.amount,
            "currency": revenue.currency,
            "payment_type": revenue.payment_type,
            "notes": revenue.notes,
            "period_start": revenue.period_start,
            "period_end": revenue.period_end,
            "created_at": revenue.created_at,
            "created_by_id": revenue.created_by_id,
            "license_name": license.name if license else None,
            "license_key": license.key if license else None,
            "user_email": user.email if user else None,
        }
