import requests
import os
from typing import Dict, Any, Optional
import time
from sqlalchemy.orm import Session
from app.db.models import TenantSettings

class MarketDataService:
    """
    Fetches real-time job market data from external APIs (Adzuna)
    Supports dynamic API keys from database.
    """
    
    def __init__(self):
        self.default_app_id = os.getenv("ADZUNA_APP_ID")
        self.default_app_key = os.getenv("ADZUNA_APP_KEY")
        self._cache = {}
        self._cache_duration = 3600
        
    def get_sector_demand(
        self, 
        sector: str,
        tenant_id: str = "default",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Get job demand metrics for a specific sector.
        """
        # 1. Check Cache
        if sector in self._cache:
            timestamp, data = self._cache[sector]
            if time.time() - timestamp < self._cache_duration:
                return data

        # 2. Resolve Keys
        app_id = self.default_app_id
        app_key = self.default_app_key
        
        if db and tenant_id:
            settings = db.query(TenantSettings).filter(TenantSettings.tenant_id == tenant_id).first()
            if settings:
                if settings.adzuna_app_id: app_id = settings.adzuna_app_id
                if settings.adzuna_app_key: app_key = settings.adzuna_app_key

        if not app_id or not app_key:
            return self._get_fallback_data(sector)

        # 3. Call External API (Adzuna)
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/in/search/1"
            params = {
                "app_id": app_id,
                "app_key": app_key,
                "what": sector,
                "results_per_page": 1,
                "content-type": "application/json"
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                demand_score = min(count / 50000.0, 1.0)
                
                result = {
                    "live_data": True,
                    "field_job_demand_score": round(demand_score, 2),
                    "sector_hiring_growth": 0.05,
                    "job_count": count
                }
                self._cache[sector] = (time.time(), result)
                return result
        except:
            pass
            
        return self._get_fallback_data(sector)

    def _get_fallback_data(self, sector: str) -> Dict[str, Any]:
        defaults = {
            "IT": {"field_job_demand_score": 0.85, "sector_hiring_growth": 0.12},
            "Engineering": {"field_job_demand_score": 0.75, "sector_hiring_growth": 0.08},
            "MBA": {"field_job_demand_score": 0.70, "sector_hiring_growth": 0.05},
            "Medical": {"field_job_demand_score": 0.90, "sector_hiring_growth": 0.15},
            "Commerce": {"field_job_demand_score": 0.65, "sector_hiring_growth": 0.04},
            "Arts": {"field_job_demand_score": 0.40, "sector_hiring_growth": -0.02}
        }
        data = defaults.get(sector, {"field_job_demand_score": 0.50, "sector_hiring_growth": 0.02})
        data["live_data"] = False
        return data
