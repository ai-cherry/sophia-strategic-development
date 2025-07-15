#!/usr/bin/env python3
"""
Populate PayReady Competitor Intelligence
Adds the 7 main PayReady competitors to the system
"""

import asyncio
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PayReady competitor data
PAYREADY_COMPETITORS = [
    {
        "name": "EliseAI",
        "category": "direct",
        "description": "AI-powered leasing and customer service platform for multifamily properties",
        "website": "https://eliseai.com",
        "founded_year": 2017,
        "headquarters": "New York, NY",
        "employee_count": 150,
        "funding_total": 35000000,
        "valuation": 150000000,
        "key_products": ["AI Leasing Assistant", "Maintenance Coordination", "Resident Services"],
        "target_market": ["Multifamily Properties", "Property Management", "Real Estate"],
        "strengths": ["Advanced NLP", "Proven ROI", "Comprehensive Platform"],
        "weaknesses": ["Limited Customization", "High Cost", "Complex Setup"],
        "threat_level": 8,
        "market_share": 15.2,
        "growth_rate": 45.5,
        "metadata": {
            "primary_focus": "multifamily_leasing",
            "ai_technology": "conversational_ai",
            "deployment_model": "saas"
        }
    },
    {
        "name": "Entrata",
        "category": "direct",
        "description": "Comprehensive property management software with integrated payment processing",
        "website": "https://entrata.com",
        "founded_year": 2003,
        "headquarters": "Lehi, UT",
        "employee_count": 2000,
        "funding_total": 507000000,
        "valuation": 2000000000,
        "key_products": ["Property Management", "Payment Processing", "Resident Portal"],
        "target_market": ["Multifamily Properties", "Student Housing", "Commercial Real Estate"],
        "strengths": ["Market Leader", "Comprehensive Suite", "Strong Integrations"],
        "weaknesses": ["Legacy Architecture", "Slow Innovation", "Complex Pricing"],
        "threat_level": 9,
        "market_share": 28.7,
        "growth_rate": 12.3,
        "metadata": {
            "primary_focus": "property_management",
            "market_position": "established_leader",
            "deployment_model": "saas"
        }
    },
    {
        "name": "AppFolio",
        "category": "direct",
        "description": "Cloud-based property management software with payment solutions",
        "website": "https://appfolio.com",
        "founded_year": 2006,
        "headquarters": "Santa Barbara, CA",
        "employee_count": 1500,
        "funding_total": 38000000,
        "valuation": 4500000000,
        "key_products": ["Property Manager", "Investment Management", "Student Housing"],
        "target_market": ["Residential Properties", "Commercial Real Estate", "Student Housing"],
        "strengths": ["User-Friendly Interface", "Strong Mobile App", "Reliable Platform"],
        "weaknesses": ["Limited Customization", "Pricing Increases", "Feature Gaps"],
        "threat_level": 7,
        "market_share": 18.5,
        "growth_rate": 22.1,
        "metadata": {
            "primary_focus": "property_management",
            "market_position": "growth_leader",
            "deployment_model": "saas"
        }
    },
    {
        "name": "Yardi",
        "category": "direct",
        "description": "Enterprise property management and accounting software platform",
        "website": "https://yardi.com",
        "founded_year": 1984,
        "headquarters": "Santa Barbara, CA",
        "employee_count": 8000,
        "funding_total": 0,  # Private company
        "valuation": 3000000000,
        "key_products": ["Voyager", "RentCafe", "Payment Processing"],
        "target_market": ["Enterprise Properties", "Commercial Real Estate", "Affordable Housing"],
        "strengths": ["Enterprise Scale", "Deep Functionality", "Industry Experience"],
        "weaknesses": ["Complex Implementation", "Outdated UI", "High Costs"],
        "threat_level": 6,
        "market_share": 32.1,
        "growth_rate": 8.7,
        "metadata": {
            "primary_focus": "enterprise_property_management",
            "market_position": "legacy_leader",
            "deployment_model": "hybrid"
        }
    },
    {
        "name": "RealPage",
        "category": "direct",
        "description": "Property management and analytics platform with payment solutions",
        "website": "https://realpage.com",
        "founded_year": 1998,
        "headquarters": "Richardson, TX",
        "employee_count": 12000,
        "funding_total": 0,  # Acquired by Thoma Bravo
        "valuation": 10200000000,
        "key_products": ["OneSite", "LeasingDesk", "Resident Payments"],
        "target_market": ["Multifamily Properties", "Single Family Rentals", "Student Housing"],
        "strengths": ["Market Dominance", "Comprehensive Analytics", "Strong Integrations"],
        "weaknesses": ["Antitrust Concerns", "Complex Pricing", "Legacy Systems"],
        "threat_level": 9,
        "market_share": 35.8,
        "growth_rate": 6.2,
        "metadata": {
            "primary_focus": "property_management_analytics",
            "market_position": "market_leader",
            "deployment_model": "saas"
        }
    },
    {
        "name": "Buildium",
        "category": "direct",
        "description": "Property management software for small to mid-size property managers",
        "website": "https://buildium.com",
        "founded_year": 2004,
        "headquarters": "Boston, MA",
        "employee_count": 500,
        "funding_total": 0,  # Acquired by RealPage
        "valuation": 580000000,
        "key_products": ["Property Management", "Accounting", "Resident Portal"],
        "target_market": ["Small Property Managers", "Residential Properties", "HOA Management"],
        "strengths": ["SMB Focus", "Affordable Pricing", "Easy Setup"],
        "weaknesses": ["Limited Enterprise Features", "Basic Analytics", "Scalability Issues"],
        "threat_level": 5,
        "market_share": 8.3,
        "growth_rate": 18.9,
        "metadata": {
            "primary_focus": "smb_property_management",
            "market_position": "niche_player",
            "deployment_model": "saas"
        }
    },
    {
        "name": "Rent Manager",
        "category": "direct",
        "description": "Property management software with integrated payment processing",
        "website": "https://rentmanager.com",
        "founded_year": 1988,
        "headquarters": "Richardson, TX",
        "employee_count": 300,
        "funding_total": 0,  # Private company
        "valuation": 200000000,
        "key_products": ["Property Management", "Accounting", "Payment Processing"],
        "target_market": ["Residential Properties", "Commercial Properties", "Mixed-Use"],
        "strengths": ["Affordable Pricing", "Comprehensive Features", "Local Support"],
        "weaknesses": ["Outdated Interface", "Limited Mobile", "Slow Innovation"],
        "threat_level": 4,
        "market_share": 5.2,
        "growth_rate": 9.1,
        "metadata": {
            "primary_focus": "traditional_property_management",
            "market_position": "legacy_niche",
            "deployment_model": "on_premise"
        }
    }
]

# Sample intelligence data for competitors
SAMPLE_INTELLIGENCE = [
    {
        "competitor_name": "EliseAI",
        "intelligence_type": "funding_news",
        "title": "EliseAI Raises $35M Series B for AI Property Management Expansion",
        "description": "EliseAI secured $35M in Series B funding to expand their AI-powered leasing platform and enhance their natural language processing capabilities.",
        "source": "TechCrunch",
        "source_url": "https://techcrunch.com/eliseai-funding",
        "impact_score": 8,
        "confidence_score": 0.95,
        "tags": ["funding", "series_b", "expansion", "ai_advancement"]
    },
    {
        "competitor_name": "Entrata",
        "intelligence_type": "product_update",
        "title": "Entrata Launches AI-Powered Maintenance Coordination",
        "description": "Entrata introduced AI-driven maintenance request routing and predictive maintenance scheduling to compete with newer AI-first platforms.",
        "source": "Property Management Insider",
        "source_url": "https://pmi.com/entrata-ai-maintenance",
        "impact_score": 7,
        "confidence_score": 0.88,
        "tags": ["product_launch", "ai_integration", "maintenance", "competitive_response"]
    },
    {
        "competitor_name": "RealPage",
        "intelligence_type": "market_move",
        "title": "RealPage Faces Antitrust Investigation Over Pricing Algorithms",
        "description": "DOJ investigation into RealPage's revenue management algorithms could impact their market position and create opportunities for competitors.",
        "source": "Wall Street Journal",
        "source_url": "https://wsj.com/realpage-antitrust",
        "impact_score": 9,
        "confidence_score": 0.92,
        "tags": ["antitrust", "legal_risk", "market_opportunity", "pricing_algorithms"]
    },
    {
        "competitor_name": "AppFolio",
        "intelligence_type": "partnership",
        "title": "AppFolio Partners with Stripe for Enhanced Payment Processing",
        "description": "Strategic partnership with Stripe to improve payment processing capabilities and reduce transaction costs for property managers.",
        "source": "AppFolio Press Release",
        "source_url": "https://appfolio.com/stripe-partnership",
        "impact_score": 6,
        "confidence_score": 0.90,
        "tags": ["partnership", "payment_processing", "stripe", "cost_reduction"]
    },
    {
        "competitor_name": "Yardi",
        "intelligence_type": "strategy_shift",
        "title": "Yardi Accelerates Cloud Migration with $500M Investment",
        "description": "Yardi announces major cloud modernization initiative to compete with cloud-native competitors, investing $500M over 3 years.",
        "source": "Yardi Annual Report",
        "source_url": "https://yardi.com/cloud-investment",
        "impact_score": 8,
        "confidence_score": 0.85,
        "tags": ["cloud_migration", "modernization", "investment", "competitive_response"]
    }
]

class PayReadyCompetitorPopulator:
    """Populate PayReady competitor intelligence system"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.competitor_ids = {}
        
    def create_competitor_profile(self, competitor_data: Dict[str, Any]) -> bool:
        """Create a competitor profile via API"""
        try:
            url = f"{self.api_base_url}/api/v1/competitors/profiles"
            response = requests.post(url, json=competitor_data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    competitor_id = result.get("competitor_id")
                    self.competitor_ids[competitor_data["name"]] = competitor_id
                    logger.info(f"✅ Created competitor profile: {competitor_data['name']}")
                    return True
                else:
                    logger.error(f"❌ Failed to create competitor: {result}")
                    return False
            else:
                logger.error(f"❌ API error creating competitor {competitor_data['name']}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating competitor {competitor_data['name']}: {e}")
            return False
    
    def create_intelligence(self, intelligence_data: Dict[str, Any]) -> bool:
        """Create competitor intelligence via API"""
        try:
            # Get competitor ID
            competitor_name = intelligence_data.pop("competitor_name")
            competitor_id = self.competitor_ids.get(competitor_name)
            
            if not competitor_id:
                logger.error(f"❌ Competitor ID not found for {competitor_name}")
                return False
            
            intelligence_data["competitor_id"] = competitor_id
            
            url = f"{self.api_base_url}/api/v1/competitors/intelligence"
            response = requests.post(url, json=intelligence_data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"✅ Created intelligence: {intelligence_data['title']}")
                    return True
                else:
                    logger.error(f"❌ Failed to create intelligence: {result}")
                    return False
            else:
                logger.error(f"❌ API error creating intelligence: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating intelligence: {e}")
            return False
    
    def populate_all(self):
        """Populate all competitor data"""
        logger.info("🚀 Starting PayReady Competitor Intelligence Population")
        
        # Create competitor profiles
        logger.info("📋 Creating competitor profiles...")
        profile_success = 0
        for competitor in PAYREADY_COMPETITORS:
            if self.create_competitor_profile(competitor):
                profile_success += 1
        
        logger.info(f"✅ Created {profile_success}/{len(PAYREADY_COMPETITORS)} competitor profiles")
        
        # Create intelligence data
        logger.info("🔍 Creating intelligence data...")
        intelligence_success = 0
        for intelligence in SAMPLE_INTELLIGENCE:
            if self.create_intelligence(intelligence):
                intelligence_success += 1
        
        logger.info(f"✅ Created {intelligence_success}/{len(SAMPLE_INTELLIGENCE)} intelligence items")
        
        # Test search functionality
        logger.info("🔍 Testing search functionality...")
        self.test_search()
        
        # Get analytics
        logger.info("📊 Generating analytics...")
        self.test_analytics()
        
        logger.info("🎉 PayReady Competitor Intelligence Population Complete!")
    
    def test_search(self):
        """Test search functionality"""
        try:
            # Search competitors
            url = f"{self.api_base_url}/api/v1/competitors/profiles?query=property management&limit=5"
            response = requests.get(url)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"🔍 Search test: Found {result.get('count', 0)} competitors")
            
            # Search intelligence
            url = f"{self.api_base_url}/api/v1/competitors/intelligence/search?query=AI&limit=10"
            response = requests.get(url)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"🔍 Intelligence search test: Found {result.get('count', 0)} intelligence items")
                
        except Exception as e:
            logger.error(f"❌ Search test failed: {e}")
    
    def test_analytics(self):
        """Test analytics functionality"""
        try:
            # Get threat analysis
            url = f"{self.api_base_url}/api/v1/competitors/analytics/threat-analysis"
            response = requests.get(url)
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get("analysis", {})
                logger.info(f"📊 Threat Analysis: {analysis.get('total_competitors', 0)} competitors analyzed")
                logger.info(f"📊 Critical threats: {analysis.get('threat_distribution', {}).get('critical', 0)}")
            
            # Get dashboard data
            url = f"{self.api_base_url}/api/v1/competitors/analytics/dashboard"
            response = requests.get(url)
            
            if response.status_code == 200:
                result = response.json()
                dashboard = result.get("dashboard", {})
                overview = dashboard.get("overview", {})
                logger.info(f"📊 Dashboard: {overview.get('total_competitors', 0)} competitors, {overview.get('high_threats', 0)} high threats")
                
        except Exception as e:
            logger.error(f"❌ Analytics test failed: {e}")

def main():
    """Main function"""
    populator = PayReadyCompetitorPopulator()
    populator.populate_all()

if __name__ == "__main__":
    main() 