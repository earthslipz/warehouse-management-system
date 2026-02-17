"""
Accounting Managers for remaining accounting modules
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional
from ..models.accounting import (
    TaxReport, Cheque, FixedAsset, BudgetAllocation, Payment, PaymentMethod
)


class TaxManager:
    """Module 9 - VAT/Withholding Tax Management"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.tax_reports: Dict[str, TaxReport] = {}
        self.next_report_no = 1
    
    def create_tax_report(self, report_month: int, report_year: int) -> TaxReport:
        """Create monthly tax report"""
        report_no = f"TAX{report_year}{report_month:02d}"
        report = TaxReport(
            report_no=report_no,
            report_month=report_month,
            report_year=report_year
        )
        self.tax_reports[report_no] = report
        return report
    
    def calculate_net_vat(self, report_no: str) -> Decimal:
        """Calculate net VAT (sales VAT - purchase VAT)"""
        if report_no not in self.tax_reports:
            return Decimal('0')
        
        report = self.tax_reports[report_no]
        report.net_vat = report.total_sales_vat - report.total_purchase_vat
        return report.net_vat
    
    def get_tax_report(self, report_no: str) -> Optional[TaxReport]:
        """Retrieve tax report"""
        return self.tax_reports.get(report_no)
    
    def get_all_reports(self) -> List[TaxReport]:
        """Get all tax reports"""
        return list(self.tax_reports.values())


class BankingManager:
    """Module 12 - Banking/Cash/Cheque Management"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.cheques_received: Dict[str, Cheque] = {}
        self.cheques_issued: Dict[str, Cheque] = {}
        self.cash_balance = Decimal('0.00')
        self.bank_accounts: Dict[str, Decimal] = {}
    
    def receive_cheque(self, cheque_no: str, issue_date: datetime,
                      amount: Decimal, payee: str, bank_name: str) -> Cheque:
        """Record cheque received"""
        cheque = Cheque(
            cheque_no=cheque_no,
            issue_date=issue_date,
            amount=amount,
            payee=payee,
            bank_name=bank_name,
            status="In Hand"
        )
        self.cheques_received[cheque_no] = cheque
        return cheque
    
    def issue_cheque(self, cheque_no: str, issue_date: datetime,
                    amount: Decimal, payee: str, bank_name: str) -> Cheque:
        """Record cheque issued"""
        cheque = Cheque(
            cheque_no=cheque_no,
            issue_date=issue_date,
            amount=amount,
            payee=payee,
            bank_name=bank_name,
            status="In Hand"
        )
        self.cheques_issued[cheque_no] = cheque
        return cheque
    
    def deposit_cheque(self, cheque_no: str) -> bool:
        """Mark cheque as deposited"""
        if cheque_no in self.cheques_received:
            cheque = self.cheques_received[cheque_no]
            cheque.status = "Deposited"
            return True
        return False
    
    def clear_cheque(self, cheque_no: str, clearing_date: datetime) -> bool:
        """Mark cheque as cleared"""
        if cheque_no in self.cheques_received:
            cheque = self.cheques_received[cheque_no]
            cheque.status = "Cleared"
            cheque.clearing_date = clearing_date
            return True
        return False
    
    def get_outstanding_cheques(self) -> List[Cheque]:
        """Get all outstanding cheques"""
        return [c for c in self.cheques_issued.values() if c.status == "In Hand"]
    
    def deposit_cash(self, amount: Decimal) -> Decimal:
        """Add cash to balance"""
        self.cash_balance += amount
        return self.cash_balance
    
    def withdraw_cash(self, amount: Decimal) -> bool:
        """Withdraw cash if sufficient balance"""
        if amount <= self.cash_balance:
            self.cash_balance -= amount
            return True
        return False


class AssetManager:
    """Module 15 - Fixed Asset and Depreciation"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.assets: Dict[str, FixedAsset] = {}
        self.next_asset_id = 1
    
    def register_asset(self, asset_name: str, purchase_date: datetime,
                      cost: Decimal, depreciation_method: str,
                      useful_life_years: int, department: str = "") -> FixedAsset:
        """Register new fixed asset"""
        asset_id = f"FA{self.next_asset_id:06d}"
        self.next_asset_id += 1
        
        asset = FixedAsset(
            asset_id=asset_id,
            asset_name=asset_name,
            purchase_date=purchase_date,
            cost=cost,
            depreciation_method=depreciation_method,
            useful_life_years=useful_life_years,
            department=department
        )
        self.assets[asset_id] = asset
        return asset
    
    def calculate_depreciation(self, asset_id: str) -> Decimal:
        """Calculate depreciation for asset"""
        if asset_id not in self.assets:
            return Decimal('0')
        
        asset = self.assets[asset_id]
        annual_depreciation = asset.calculate_annual_depreciation()
        monthly_depreciation = annual_depreciation / 12
        return monthly_depreciation
    
    def record_depreciation(self, asset_id: str, amount: Decimal) -> bool:
        """Record depreciation"""
        if asset_id not in self.assets:
            return False
        
        asset = self.assets[asset_id]
        if asset.accumulated_depreciation + amount <= asset.cost:
            asset.accumulated_depreciation += amount
            return True
        return False
    
    def get_all_assets(self) -> List[FixedAsset]:
        """Get all assets"""
        return list(self.assets.values())
    
    def get_asset_register(self) -> List[Dict]:
        """Generate asset register"""
        register = []
        for asset in self.assets.values():
            register.append({
                'asset_id': asset.asset_id,
                'name': asset.asset_name,
                'cost': asset.cost,
                'accumulated_depreciation': asset.accumulated_depreciation,
                'book_value': asset.get_book_value()
            })
        return register


class BudgetManager:
    """Module 14 - Budget Control"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.budgets: Dict[str, BudgetAllocation] = {}
        self.next_budget_id = 1
    
    def create_budget(self, fiscal_year: int, account_code: str,
                     department: str, monthly_amounts: List[Decimal]) -> BudgetAllocation:
        """Create budget allocation"""
        budget_id = f"BDG{self.next_budget_id:06d}"
        self.next_budget_id += 1
        
        budget = BudgetAllocation(
            budget_id=budget_id,
            fiscal_year=fiscal_year,
            account_code=account_code,
            department=department,
            monthly_budget=monthly_amounts
        )
        self.budgets[budget_id] = budget
        return budget
    
    def record_actual_spending(self, budget_id: str, month: int, amount: Decimal) -> bool:
        """Record actual spending"""
        if budget_id not in self.budgets:
            return False
        
        budget = self.budgets[budget_id]
        if 0 <= month <= 11:
            budget.actual_spending[month] = amount
            return True
        return False
    
    def get_budget_variance_report(self, budget_id: str) -> Dict:
        """Generate budget variance report"""
        if budget_id not in self.budgets:
            return {}
        
        budget = self.budgets[budget_id]
        report = {
            'budget_id': budget_id,
            'fiscal_year': budget.fiscal_year,
            'account': budget.account_code,
            'department': budget.department,
            'monthly_variances': []
        }
        
        for month in range(12):
            variance = budget.get_variance(month)
            report['monthly_variances'].append({
                'month': month + 1,
                'budget': budget.monthly_budget[month],
                'actual': budget.actual_spending[month],
                'variance': variance
            })
        
        return report
    
    def get_all_budgets(self) -> List[BudgetAllocation]:
        """Get all budgets"""
        return list(self.budgets.values())
