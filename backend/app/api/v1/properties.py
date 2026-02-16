from fastapi import APIRouter, Depends
from typing import Dict, Any
from ...core.auth import authenticate_request
from ...models.auth import AuthenticatedUser
from ...database import supabase
import logging

router = APIRouter(prefix="/properties", tags=["properties"])
logger = logging.getLogger(__name__)

@router.get("")
async def get_properties(
    current_user: AuthenticatedUser = Depends(authenticate_request)
) -> Dict[str, Any]:
    """Get properties for current user's tenant"""
    
    logger.info(f"🔍 GET /properties called by: {current_user.email}")
    
    tenant_id = current_user.tenant_id
    logger.info(f"🔍 Tenant ID: {tenant_id}")
    
    if not tenant_id:
        logger.warning(f"⚠️ No tenant_id for user {current_user.email}")
        return {"data": [], "total": 0}
    
    try:
        result = supabase.table('properties')\
            .select('id, name, timezone')\
            .eq('tenant_id', tenant_id)\
            .order('name')\
            .execute()
        
        properties = result.data or []
        logger.info(f"✅ Found {len(properties)} properties for tenant {tenant_id}")
        
        return {
            "data": properties,
            "total": len(properties)
        }
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return {"data": [], "total": 0}
