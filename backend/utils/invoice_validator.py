import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class InvoiceValidator:
    def __init__(self):
        self.erp_data = self._load_erp_data()
        self.fraud_keywords = [
            'urgent', 'immediate payment', 'act now', 'limited time',
            'wire transfer only', 'cash only', 'bitcoin', 'cryptocurrency'
        ]
        self.suspicious_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'
        ]
    
    def _load_erp_data(self) -> Dict:
        """Load mock ERP data from JSON file"""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, '..', '..', 'data', 'erp_mock.json')
            data_path = os.path.normpath(data_path)
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: ERP mock data not found, using empty dataset")
            return {"purchase_orders": [], "approved_vendors": [], "blacklisted_vendors": []}
    
    def validate_invoice(self, invoice_data: Dict) -> Tuple[str, List[str], Dict]:
        """
        Comprehensive invoice validation pipeline
        Returns: (status, issues_list, validation_details)
        """
        issues = []
        validation_details = {
            "basic_validation": {},
            "erp_validation": {},
            "contextual_validation": {},
            "fraud_detection": {},
            "overall_score": 0
        }
        
        # Stage 1: Basic Field Validation
        basic_issues = self._basic_validation(invoice_data)
        issues.extend(basic_issues)
        validation_details["basic_validation"] = {
            "passed": len(basic_issues) == 0,
            "issues": basic_issues,
            "score": 25 if len(basic_issues) == 0 else 0
        }
        
        # Stage 2: ERP Cross-checks
        erp_issues, erp_details = self._erp_validation(invoice_data)
        issues.extend(erp_issues)
        validation_details["erp_validation"] = {
            "passed": len(erp_issues) == 0,
            "issues": erp_issues,
            "details": erp_details,
            "score": 30 if len(erp_issues) == 0 else 10 if len(erp_issues) < 3 else 0
        }
        
        # Stage 3: Contextual Logic Validation
        contextual_issues = self._contextual_validation(invoice_data)
        issues.extend(contextual_issues)
        validation_details["contextual_validation"] = {
            "passed": len(contextual_issues) == 0,
            "issues": contextual_issues,
            "score": 25 if len(contextual_issues) == 0 else 10 if len(contextual_issues) < 2 else 0
        }
        
        # Stage 4: Fraud Detection
        fraud_issues, fraud_score = self._fraud_detection(invoice_data)
        issues.extend(fraud_issues)
        validation_details["fraud_detection"] = {
            "passed": len(fraud_issues) == 0,
            "issues": fraud_issues,
            "risk_score": fraud_score,
            "score": 20 if fraud_score < 3 else 10 if fraud_score < 6 else 0
        }
        
        # Calculate overall score
        total_score = sum([
            validation_details["basic_validation"]["score"],
            validation_details["erp_validation"]["score"],
            validation_details["contextual_validation"]["score"],
            validation_details["fraud_detection"]["score"]
        ])
        validation_details["overall_score"] = total_score
        
        # Determine final status
        if total_score >= 80 and len(issues) == 0:
            status = "approved"
        elif total_score >= 60 and len([i for i in issues if "critical" in i.lower()]) == 0:
            status = "approved_with_conditions"
        else:
            status = "rejected"
        
        return status, issues, validation_details
    
    def _basic_validation(self, invoice_data: Dict) -> List[str]:
        """Stage 1: Basic field validation"""
        issues = []
        
        # Required fields check
        required_fields = ['invoice_id', 'vendor_name', 'tax_id', 'amount', 'date']
        for field in required_fields:
            if not invoice_data.get(field):
                issues.append(f"Missing required field: {field}")
        
        # Data type validation
        try:
            amount = float(invoice_data.get('amount', 0))
            if amount <= 0:
                issues.append("Invoice amount must be positive")
            elif amount > 100000:
                issues.append("CRITICAL: Invoice amount exceeds $100,000 threshold")
        except (ValueError, TypeError):
            issues.append("Invalid amount format")
        
        # Invoice ID format validation
        invoice_id = invoice_data.get('invoice_id', '')
        if not re.match(r'^[A-Z0-9\-]{3,20}$', invoice_id):
            issues.append("Invalid invoice ID format")
        
        # Tax ID format validation
        tax_id = invoice_data.get('tax_id', '')
        if not re.match(r'^\d{2}-\d{7}$', tax_id):
            issues.append("Invalid tax ID format (expected XX-XXXXXXX)")
        
        # Date validation
        try:
            invoice_date = datetime.strptime(invoice_data.get('date', ''), '%Y-%m-%d')
            if invoice_date > datetime.now():
                issues.append("Invoice date cannot be in the future")
            elif invoice_date < datetime.now() - timedelta(days=365):
                issues.append("Invoice date is more than 1 year old")
        except ValueError:
            issues.append("Invalid date format (expected YYYY-MM-DD)")
        
        return issues
    
    def _erp_validation(self, invoice_data: Dict) -> Tuple[List[str], Dict]:
        """Stage 2: ERP system cross-validation"""
        issues = []
        details = {}
        
        vendor_name = invoice_data.get('vendor_name', '')
        tax_id = invoice_data.get('tax_id', '')
        amount = float(invoice_data.get('amount', 0))
        
        # Check if vendor is blacklisted
        blacklisted = any(
            vendor['vendor_name'].lower() == vendor_name.lower() or 
            vendor['tax_id'] == tax_id
            for vendor in self.erp_data['blacklisted_vendors']
        )
        
        if blacklisted:
            issues.append("CRITICAL: Vendor is blacklisted in ERP system")
            details['blacklisted'] = True
            return issues, details
        
        details['blacklisted'] = False
        
        # Find matching vendor in approved list
        approved_vendor = None
        for vendor in self.erp_data['approved_vendors']:
            if (vendor['vendor_name'].lower() == vendor_name.lower() and 
                vendor['tax_id'] == tax_id):
                approved_vendor = vendor
                break
        
        if not approved_vendor:
            issues.append("Vendor not found in approved vendor list")
            details['vendor_approved'] = False
        else:
            details['vendor_approved'] = True
            details['vendor_risk_level'] = approved_vendor['risk_level']
            
            # Check credit limit
            if amount > approved_vendor['credit_limit']:
                issues.append(f"Invoice amount exceeds vendor credit limit of ${approved_vendor['credit_limit']:,.2f}")
            
            # Risk level warnings
            if approved_vendor['risk_level'] == 'high':
                issues.append("WARNING: High-risk vendor requires additional approval")
            elif approved_vendor['status'] != 'approved':
                issues.append(f"Vendor status is '{approved_vendor['status']}', not fully approved")
        
        # Find matching purchase order
        matching_po = None
        for po in self.erp_data['purchase_orders']:
            if (po['vendor_name'].lower() == vendor_name.lower() and 
                po['status'] == 'open' and 
                abs(po['total_amount'] - amount) < 0.01):
                matching_po = po
                break
        
        if not matching_po:
            issues.append("No matching open purchase order found")
            details['po_matched'] = False
        else:
            details['po_matched'] = True
            details['po_number'] = matching_po['po_number']
            
            # Check PO date validity
            po_date = datetime.strptime(matching_po['created_date'], '%Y-%m-%d')
            invoice_date = datetime.strptime(invoice_data.get('date', ''), '%Y-%m-%d')
            
            if invoice_date < po_date:
                issues.append("Invoice date is before purchase order date")
        
        return issues, details
    
    def _contextual_validation(self, invoice_data: Dict) -> List[str]:
        """Stage 3: Contextual business logic validation"""
        issues = []
        
        try:
            amount = float(invoice_data.get('amount', 0))
            vendor_name = invoice_data.get('vendor_name', '')
            invoice_date = datetime.strptime(invoice_data.get('date', ''), '%Y-%m-%d')
            
            # Business day validation
            if invoice_date.weekday() >= 5:  # Saturday or Sunday
                issues.append("WARNING: Invoice dated on weekend")
            
            # Duplicate invoice check (simplified)
            invoice_id = invoice_data.get('invoice_id', '')
            if len(invoice_id) < 5:
                issues.append("Invoice ID too short for proper tracking")
            
            # Amount reasonableness
            if amount > 50000:
                issues.append("High-value invoice requires CFO approval")
            
            # Vendor name analysis
            if len(vendor_name.split()) < 2:
                issues.append("WARNING: Vendor name seems incomplete")
            
            # Seasonal/timing analysis
            current_month = datetime.now().month
            if current_month == 12 and amount > 10000:
                issues.append("Year-end high-value invoice - verify budget availability")
            
        except (ValueError, TypeError) as e:
            issues.append(f"Contextual validation failed: {str(e)}")
        
        return issues
    
    def _fraud_detection(self, invoice_data: Dict) -> Tuple[List[str], int]:
        """Stage 4: Fraud detection heuristics"""
        issues = []
        fraud_score = 0
        
        vendor_name = invoice_data.get('vendor_name', '').lower()
        amount = float(invoice_data.get('amount', 0))
        
        # Check for suspicious keywords in vendor name
        for keyword in self.fraud_keywords:
            if keyword in vendor_name:
                issues.append(f"FRAUD ALERT: Suspicious keyword '{keyword}' in vendor name")
                fraud_score += 3
        
        # Amount pattern analysis
        if amount % 1000 == 0:  # Round thousands
            fraud_score += 1
        
        if amount > 25000:
            fraud_score += 2
            issues.append("High-value transaction flagged for review")
        
        # Vendor name patterns
        if re.search(r'\d{3,}', vendor_name):  # Multiple digits in name
            fraud_score += 1
            issues.append("WARNING: Vendor name contains suspicious digit pattern")
        
        # Check for similar existing vendor names (simplified)
        similar_vendors = [v for v in self.erp_data['approved_vendors'] 
                          if any(word in v['vendor_name'].lower() for word in vendor_name.split())]
        
        if len(similar_vendors) > 1:
            fraud_score += 1
            issues.append("WARNING: Similar vendor names exist - verify authenticity")
        
        # Geographic/timing anomalies (simplified)
        invoice_date = datetime.strptime(invoice_data.get('date', ''), '%Y-%m-%d')
        if invoice_date.hour == 0 and invoice_date.minute == 0:  # Exactly midnight
            fraud_score += 1
        
        return issues, fraud_score
