import requests
import os
from typing import Dict, Any, Optional
import time
from functools import lru_cache

class MarketDataService:
    """
    Fetches real-time job market data from external APIs (Adzuna)
    """
    
    def __init__(self):
        self.app_id = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")
        self.base_url = "https://api.adzuna.com/v1/api/jobs/in/top_billboard"
        self._cache = {}
        self._cache_duration = 3600  # 1 hour cache
        
    def get_sector_demand(self, sector: str) -> Dict[str, Any]:
        """
        Get job demand metrics for a specific sector.
        Returns a dictionary with demand_score and growth_trend.
        """
        # 1. Check Cache
        if sector in self._cache:
            timestamp, data = self._cache[sector]
            if time.time() - timestamp < self._cache_duration:
                return data

        # 2. Return Mock Data if API keys are missing (Fallback)
        if not self.app_id or not self.app_key:
            return self._get_fallback_data(sector)

        # 3. Call External API (Adzuna)
        try:
            # Note: Adzuna top_billboard is free and gives high-level stats
            # For a more specific search, we'd use /jobs/in/search
            # Here we simulate high-level demand for the sector
            url = f"https://api.adzuna.com/v1/api/jobs/in/search/1"
            params = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "what": sector,
                "results_per_page": 1,
                "content-type": "application/json"
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                
                # Normalize count to a 0-1 demand score (heuristic)
                # Assume 50,000+ jobs in India for a sector is "Very High" (1.0)
                demand_score = min(count / 50000.0, 1.0)
                
                result = {
                    "live_data": True,
                    "field_job_demand_score": round(demand_score, 2),
                    "sector_hiring_growth": 0.05, # Adzuna search doesn't give growth directly
                    "job_count": count
                }
                
                self._cache[sector] = (time.time(), result)
                return result
                
        except Exception as e:
            print(f"Warning: Market data fetch failed: {e}")
            
        return self._get_fallback_data(sector)

    def _get_fallback_data(self, sector: str) -> Dict[str, Any]:
        """Static data mapping for various sectors when API is unavailable"""
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
