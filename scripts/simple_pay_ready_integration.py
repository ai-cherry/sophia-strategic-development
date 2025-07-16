#!/usr/bin/env python3
"""
Simple Pay Ready Employee Integration
Direct CSV to foundational knowledge without complex dependencies
"""

import asyncio
import csv
import json
import sqlite3
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class SimplePayReadyIntegration:
    """Simple integration without external dependencies"""
    
    def __init__(self):
        self.csv_file = "data/pay_ready_employees_2025_07_15.csv"
        self.integration_id = f"simple_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Department to business function mapping
        self.dept_mapping = {
            'Account Management': 'customer_retention',
            'AI': 'artificial_intelligence',
            'Engineering': 'product_development',
            'Sales': 'revenue_generation',
            'Support Team': 'customer_success',
            'Executive': 'strategic_leadership',
            'Finance': 'financial_operations',
            'Compliance': 'risk_management',
            'Eviction Center': 'specialized_operations',
            'Product': 'product_development',
            'Marketing': 'marketing_growth',
            'Implementation': 'customer_onboarding',
            'Human Resources': 'people_operations',
            'Operational Excellence': 'operational_efficiency',
            'Payment Operations': 'financial_operations'
        }
    
    def process_csv_data(self) -> List[Dict[str, Any]]:
        """Process CSV data and enrich with business intelligence"""
        print("📊 Processing Pay Ready employee CSV data...")
        
        employees = []
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row_num, row in enumerate(csv_reader, start=2):
                employee = self.enrich_employee_data(row, row_num)
                if employee:
                    employees.append(employee)
        
        print(f"✅ Processed {len(employees)} employees")
        return employees
    
    def enrich_employee_data(self, row: Dict[str, str], row_num: int) -> Optional[Dict[str, Any]]:
        """Enrich employee data with business intelligence"""
        full_name = row.get('Preferred full name', '').strip()
        department = row.get('Department', '').strip()
        job_title = row.get('Job title', '').strip()
        
        if not full_name or not department or not job_title:
            return None
        
        # Parse name
        name_parts = full_name.split()
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        # Generate IDs
        employee_id = self.generate_employee_id(full_name)
        email = self.generate_email(full_name)
        
        # Business intelligence categorization
        business_function = self.dept_mapping.get(department, 'general_operations')
        intelligence_priority = self.get_intelligence_priority(department, job_title)
        ai_enhancement_level = self.get_ai_enhancement_level(department, job_title)
        
        return {
            'employee_id': employee_id,
            'full_name': full_name,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'department': department,
            'job_title': job_title,
            'manager_name': row.get('Manager Name', '').strip() or None,
            'employment_type': row.get('Employment type', 'Full-time').strip(),
            'is_active': not row.get('Deactivation date', '').strip() and not row.get('Termination date', '').strip(),
            'business_function': business_function,
            'intelligence_priority': intelligence_priority,
            'ai_enhancement_level': ai_enhancement_level,
            'integration_id': self.integration_id,
            'source_row': row_num,
            'created_at': datetime.now().isoformat()
        }
    
    def generate_employee_id(self, full_name: str) -> str:
        """Generate unique employee ID"""
        import hashlib
        import time
        
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', full_name.lower())
        name_parts = clean_name.split()
        
        # Create base ID
        if len(name_parts) >= 2:
            base_id = f"{name_parts[0][:3]}{name_parts[-1][:3]}"
        else:
            base_id = clean_name.replace(' ', '')[:6]
        
        # Add unique hash to ensure no duplicates
        unique_string = f"{full_name}_{time.time()}"
        hash_suffix = hashlib.md5(unique_string.encode()).hexdigest()[:4]
        
        employee_id = f"{base_id}_{hash_suffix}"
        return employee_id.lower()
    
    def generate_email(self, full_name: str) -> str:
        """Generate Pay Ready email"""
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', full_name.lower())
        name_parts = clean_name.split()
        
        if len(name_parts) >= 2:
            email = f"{name_parts[0]}.{name_parts[-1]}@payready.com"
        else:
            email = f"{clean_name.replace(' ', '')}@payready.com"
        
        return email.lower()
    
    def get_intelligence_priority(self, department: str, job_title: str) -> str:
        """Determine intelligence priority"""
        if department == 'Executive':
            return 'maximum'
        elif department in ['AI', 'Engineering'] or any(word in job_title.lower() for word in ['chief', 'vp', 'vice president', 'director']):
            return 'critical'
        elif department in ['Sales', 'Account Management', 'Compliance']:
            return 'high'
        else:
            return 'standard'
    
    def get_ai_enhancement_level(self, department: str, job_title: str) -> str:
        """Determine AI enhancement level"""
        if department == 'Executive':
            return 'executive'
        elif department == 'AI':
            return 'maximum'
        elif department in ['Engineering', 'Sales', 'Account Management']:
            return 'advanced'
        elif department in ['Eviction Center', 'Compliance']:
            return 'specialized'
        else:
            return 'standard'
    
    def create_foundational_knowledge_db(self, employees: List[Dict[str, Any]]) -> str:
        """Create SQLite foundational knowledge database"""
        db_path = f"foundational_knowledge_{self.integration_id}.db"
        
        print("🏗️ Creating foundational knowledge database...")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create employees table
        cursor.execute('''
        CREATE TABLE employees (
            employee_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            department TEXT,
            job_title TEXT,
            manager_name TEXT,
            employment_type TEXT,
            is_active BOOLEAN,
            business_function TEXT,
            intelligence_priority TEXT,
            ai_enhancement_level TEXT,
            integration_id TEXT,
            source_row INTEGER,
            created_at TEXT
        )
        ''')
        
        # Create business contexts table
        cursor.execute('''
        CREATE TABLE business_contexts (
            context_id TEXT PRIMARY KEY,
            employee_id TEXT,
            business_function TEXT,
            context_type TEXT,
            intelligence_priority TEXT,
            ai_enhancement_level TEXT,
            created_at TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
        )
        ''')
        
        # Create department summary table
        cursor.execute('''
        CREATE TABLE department_summary (
            department TEXT PRIMARY KEY,
            employee_count INTEGER,
            business_function TEXT,
            avg_intelligence_priority TEXT,
            leadership_count INTEGER,
            created_at TEXT
        )
        ''')
        
        # Insert employee data
        for employee in employees:
            cursor.execute('''
            INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                employee['employee_id'],
                employee['full_name'],
                employee['first_name'],
                employee['last_name'],
                employee['email'],
                employee['department'],
                employee['job_title'],
                employee['manager_name'],
                employee['employment_type'],
                employee['is_active'],
                employee['business_function'],
                employee['intelligence_priority'],
                employee['ai_enhancement_level'],
                employee['integration_id'],
                employee['source_row'],
                employee['created_at']
            ))
            
            # Insert business context
            context_id = f"context_{employee['employee_id']}"
            cursor.execute('''
            INSERT INTO business_contexts VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                context_id,
                employee['employee_id'],
                employee['business_function'],
                'pay_ready_employee_context',
                employee['intelligence_priority'],
                employee['ai_enhancement_level'],
                employee['created_at']
            ))
        
        # Create department summaries
        dept_stats = {}
        for employee in employees:
            dept = employee['department']
            if dept not in dept_stats:
                dept_stats[dept] = {
                    'count': 0,
                    'business_function': employee['business_function'],
                    'leadership_count': 0
                }
            
            dept_stats[dept]['count'] += 1
            if employee['intelligence_priority'] in ['critical', 'maximum']:
                dept_stats[dept]['leadership_count'] += 1
        
        for dept, stats in dept_stats.items():
            cursor.execute('''
            INSERT INTO department_summary VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                dept,
                stats['count'],
                stats['business_function'],
                'high' if stats['leadership_count'] > stats['count'] * 0.3 else 'medium',
                stats['leadership_count'],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database created: {db_path}")
        return db_path
    
    def generate_summary_report(self, employees: List[Dict[str, Any]], db_path: str) -> Dict[str, Any]:
        """Generate comprehensive summary report"""
        print("📋 Generating summary report...")
        
        total_employees = len(employees)
        
        # Department analysis
        dept_stats = {}
        function_stats = {}
        priority_stats = {}
        enhancement_stats = {}
        
        active_count = 0
        has_manager_count = 0
        
        for employee in employees:
            dept = employee['department']
            function = employee['business_function']
            priority = employee['intelligence_priority']
            enhancement = employee['ai_enhancement_level']
            
            dept_stats[dept] = dept_stats.get(dept, 0) + 1
            function_stats[function] = function_stats.get(function, 0) + 1
            priority_stats[priority] = priority_stats.get(priority, 0) + 1
            enhancement_stats[enhancement] = enhancement_stats.get(enhancement, 0) + 1
            
            if employee['is_active']:
                active_count += 1
            if employee['manager_name']:
                has_manager_count += 1
        
        strategic_employees = priority_stats.get('critical', 0) + priority_stats.get('maximum', 0)
        ai_advanced = (enhancement_stats.get('advanced', 0) + 
                      enhancement_stats.get('maximum', 0) + 
                      enhancement_stats.get('executive', 0))
        
        summary = {
            'integration_id': self.integration_id,
            'integration_type': 'simple_pay_ready_employee_roster',
            'timestamp': datetime.now().isoformat(),
            'source_file': self.csv_file,
            'database_file': db_path,
            'status': 'SUCCESS',
            
            'employee_metrics': {
                'total_employees': total_employees,
                'active_employees': active_count,
                'active_percentage': round((active_count / total_employees) * 100, 1),
                'has_manager_percentage': round((has_manager_count / total_employees) * 100, 1)
            },
            
            'department_distribution': dept_stats,
            'business_function_distribution': function_stats,
            'intelligence_priority_distribution': priority_stats,
            'ai_enhancement_distribution': enhancement_stats,
            
            'strategic_metrics': {
                'strategic_employee_count': strategic_employees,
                'strategic_percentage': round((strategic_employees / total_employees) * 100, 1),
                'ai_advanced_count': ai_advanced,
                'ai_advanced_percentage': round((ai_advanced / total_employees) * 100, 1)
            },
            
            'key_insights': {
                'largest_department': max(dept_stats.items(), key=lambda x: x[1])[0],
                'primary_business_function': max(function_stats.items(), key=lambda x: x[1])[0],
                'total_departments': len(dept_stats),
                'unique_business_functions': len(function_stats)
            }
        }
        
        return summary
    
    def run_integration(self) -> Dict[str, Any]:
        """Execute the complete integration"""
        print("🚀 Starting Simple Pay Ready Employee Integration")
        print(f"Integration ID: {self.integration_id}")
        print()
        
        try:
            # Process CSV data
            employees = self.process_csv_data()
            
            # Create foundational knowledge database
            db_path = self.create_foundational_knowledge_db(employees)
            
            # Generate summary report
            summary = self.generate_summary_report(employees, db_path)
            
            # Save results
            results_file = self.results_dir / f"simple_pay_ready_integration_{self.integration_id}.json"
            with open(results_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"✅ Integration completed successfully!")
            print(f"📁 Results saved to: {results_file}")
            print(f"🗃️  Database created: {db_path}")
            
            return summary
            
        except Exception as e:
            error_summary = {
                'status': 'FAILED',
                'error': str(e),
                'integration_id': self.integration_id,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"❌ Integration failed: {e}")
            return error_summary

def main():
    """Main execution"""
    integration = SimplePayReadyIntegration()
    results = integration.run_integration()
    
    # Print summary
    print("\n" + "="*80)
    print("🎯 PAY READY EMPLOYEE INTEGRATION RESULTS")
    print("="*80)
    
    if results['status'] == 'SUCCESS':
        metrics = results['employee_metrics']
        strategic = results['strategic_metrics']
        insights = results['key_insights']
        
        print(f"✅ Status: {results['status']}")
        print(f"📊 Total Employees: {metrics['total_employees']}")
        print(f"👥 Active Employees: {metrics['active_employees']} ({metrics['active_percentage']}%)")
        print(f"🎯 Strategic Employees: {strategic['strategic_employee_count']} ({strategic['strategic_percentage']}%)")
        print(f"🤖 AI Advanced: {strategic['ai_advanced_count']} ({strategic['ai_advanced_percentage']}%)")
        print(f"🏢 Largest Department: {insights['largest_department']}")
        print(f"⚡ Primary Function: {insights['primary_business_function']}")
        print(f"🗃️  Database: {results['database_file']}")
        
        print("\n🎉 PAY READY EMPLOYEE ROSTER SUCCESSFULLY INTEGRATED INTO FOUNDATIONAL KNOWLEDGE!")
    else:
        print(f"❌ Status: {results['status']}")
        print(f"Error: {results.get('error', 'Unknown error')}")
    
    print("="*80)

if __name__ == "__main__":
    main()
