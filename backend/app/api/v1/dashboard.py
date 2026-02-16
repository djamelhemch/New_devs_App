from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user
from decimal import Decimal
from ...database import supabase
import logging
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get revenue summary for a specific property
    
    Security: Verifies property belongs to user's tenant before returning data
    """
    
    # Extract tenant_id
    tenant_id = getattr(current_user, "tenant_id", None)
    
    if not tenant_id or tenant_id == "default_tenant":
        logger.error(f"Invalid tenant_id for user: {tenant_id}")
        raise HTTPException(
            status_code=403,
            detail="No valid tenant context"
        )
    
    # ✅ BUG FIX #1: Verify property belongs to user's tenant
    try:
        property_check = supabase.table('properties')\
            .select('id, name, timezone')\
            .eq('id', property_id)\
            .eq('tenant_id', tenant_id)\
            .maybe_single()\
            .execute()
        
        if not property_check.data:
            logger.warning(
                f"Property {property_id} not found or access denied for tenant {tenant_id}"
            )
            raise HTTPException(
                status_code=404, 
                detail="Property not found"
            )
        
        property_data = property_check.data
        logger.info(f"Access granted: {property_id} for tenant {tenant_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying property ownership: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error verifying property access"
        )
    
    # Get revenue data with tenant_id
    try:
        revenue_data = await get_revenue_summary(property_id, tenant_id)
    except Exception as e:
        logger.error(f"Error fetching revenue: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error fetching revenue data"
        )
    
    # ✅ BUG FIX #2: Proper decimal handling
    total_revenue = revenue_data.get('total', 0)
    
    # Handle Decimal type properly
    if isinstance(total_revenue, Decimal):
        # Round to 2 decimal places, then convert to float
        total_revenue_float = float(round(total_revenue, 2))
    else:
        total_revenue_float = float(total_revenue)
    
    return {
        "property_id": revenue_data.get('property_id', property_id),
        "total_revenue": total_revenue_float,
        "currency": revenue_data.get('currency', 'USD'),
        "reservations_count": revenue_data.get('count', 0)
    }