"""
General Ledger Agent - Module 1
Handles Debit/Credit entries and ledger posting
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional
from ..models.accounting import Account, VoucherEntry


class GeneralLedgerAgent:
    """Manages General Ledger entries"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.accounts: Dict[str, Account] = {}
        self.vouchers: List[VoucherEntry] = []
        self.next_entry_id = 1
        self._initialize_default_accounts()
    
    def _initialize_default_accounts(self):
        """Create default chart of accounts"""
        default_accounts = [
            Account("1000", "Cash", "Asset"),
            Account("1100", "Accounts Receivable", "Asset"),
            Account("1200", "Inventory", "Asset"),
            Account("1500", "Fixed Assets", "Asset"),
            Account("2000", "Accounts Payable", "Liability"),
            Account("2100", "Tax Payable", "Liability"),
            Account("3000", "Owner Equity", "Equity"),
            Account("4000", "Sales Revenue", "Revenue"),
            Account("4100", "Service Revenue", "Revenue"),
            Account("5000", "Cost of Goods Sold", "Expense"),
            Account("5100", "Operating Expenses", "Expense"),
            Account("5200", "Depreciation Expense", "Expense"),
        ]
        for account in default_accounts:
            self.accounts[account.account_code] = account
    
    def add_entry(self, voucher_no: str, account_code: str, 
                 debit: Decimal = Decimal('0.00'), 
                 credit: Decimal = Decimal('0.00'),
                 description: str = "") -> VoucherEntry:
        """Add a new ledger entry"""
        if account_code not in self.accounts:
            raise ValueError(f"Account {account_code} not found")
        
        account = self.accounts[account_code]
        entry = VoucherEntry(
            entry_id=f"E{self.next_entry_id}",
            voucher_no=voucher_no,
            date=datetime.now(),
            account=account,
            description=description,
            debit=debit,
            credit=credit
        )
        self.next_entry_id += 1
        self.vouchers.append(entry)
        return entry
    
    def post_voucher(self, voucher_no: str) -> bool:
        """Post a complete voucher to ledger"""
        voucher_entries = [v for v in self.vouchers if v.voucher_no == voucher_no]
        
        # Check if balanced
        total_debit = sum(v.debit for v in voucher_entries)
        total_credit = sum(v.credit for v in voucher_entries)
        
        if total_debit != total_credit:
            return False
        
        # Update account balances
        for entry in voucher_entries:
            if entry.debit > 0:
                entry.account.balance += entry.debit
            else:
                entry.account.balance -= entry.credit
            entry.status = "Posted"
        
        return True
    
    def get_trial_balance(self) -> Dict[str, Decimal]:
        """Generate trial balance"""
        balance = {}
        for code, account in self.accounts.items():
            if account.balance != 0:
                balance[code] = account.balance
        return balance
    
    def get_account_balance(self, account_code: str) -> Decimal:
        """Get specific account balance"""
        if account_code in self.accounts:
            return self.accounts[account_code].balance
        return Decimal('0.00')
    
    def add_account(self, account_code: str, account_name: str, 
                   account_type: str) -> Account:
        """Add new account to chart of accounts"""
        if account_code in self.accounts:
            raise ValueError(f"Account {account_code} already exists")
        
        account = Account(account_code, account_name, account_type)
        self.accounts[account_code] = account
        return account
    
    def get_all_accounts(self) -> List[Account]:
        """Get all accounts"""
        return list(self.accounts.values())
    
    def get_voucher_entries(self, voucher_no: str) -> List[VoucherEntry]:
        """Get entries for specific voucher"""
        return [v for v in self.vouchers if v.voucher_no == voucher_no]
