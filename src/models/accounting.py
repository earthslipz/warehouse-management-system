"""
Accounting models for Thai Accounting System
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class InvoiceStatus(Enum):
    DRAFT = "Draft"
    POSTED = "Posted"
    PAID = "Paid"
    CANCELLED = "Cancelled"


class VATType(Enum):
    INCLUDED = "Include VAT"
    EXCLUDED = "Exclude VAT"
    EXEMPT = "Exempt"


class PaymentMethod(Enum):
    CASH = "Cash"
    CHEQUE = "Cheque"
    BANK_TRANSFER = "Bank Transfer"
    CREDIT_CARD = "Credit Card"


@dataclass
class Account:
    """General Ledger Account"""
    account_code: str
    account_name: str
    account_type: str  # Asset, Liability, Equity, Revenue, Expense
    balance: Decimal = Decimal('0.00')
    
    def __hash__(self):
        return hash(self.account_code)


@dataclass
class VoucherEntry:
    """Ledger Entry"""
    entry_id: str
    voucher_no: str
    date: datetime
    account: Account
    description: str
    debit: Decimal = Decimal('0.00')
    credit: Decimal = Decimal('0.00')
    status: str = "Draft"
    
    def __post_init__(self):
        if self.debit > 0 and self.credit > 0:
            raise ValueError("Cannot have both debit and credit")


@dataclass
class InvoiceItem:
    """Invoice Line Item"""
    item_id: str
    item_name: str
    quantity: Decimal
    unit_price: Decimal
    discount: Decimal = Decimal('0.00')
    vat_rate: Decimal = Decimal('7.00')
    
    def get_amount(self) -> Decimal:
        """Calculate line amount before VAT"""
        subtotal = self.quantity * self.unit_price
        discount_amount = subtotal * (self.discount / 100)
        return subtotal - discount_amount
    
    def get_vat_amount(self) -> Decimal:
        """Calculate VAT amount"""
        amount = self.get_amount()
        return amount * (self.vat_rate / 100)
    
    def get_total(self) -> Decimal:
        """Calculate total including VAT"""
        return self.get_amount() + self.get_vat_amount()


@dataclass
class SalesInvoice:
    """Sales Invoice / Tax Invoice"""
    invoice_no: str
    customer_id: str
    customer_name: str
    invoice_date: datetime
    due_date: datetime
    items: List[InvoiceItem] = field(default_factory=list)
    vat_type: VATType = VATType.INCLUDED
    status: InvoiceStatus = InvoiceStatus.DRAFT
    total_amount: Decimal = Decimal('0.00')
    total_vat: Decimal = Decimal('0.00')
    notes: str = ""
    
    def calculate_totals(self):
        """Calculate invoice totals"""
        total = Decimal('0.00')
        vat = Decimal('0.00')
        for item in self.items:
            total += item.get_amount()
            vat += item.get_vat_amount()
        self.total_amount = total
        self.total_vat = vat


@dataclass
class PurchaseOrder:
    """Purchase Order"""
    po_no: str
    supplier_id: str
    supplier_name: str
    order_date: datetime
    expected_delivery: datetime
    items: List[InvoiceItem] = field(default_factory=list)
    status: str = "Draft"  # Draft, Ordered, Received, Cancelled
    total_amount: Decimal = Decimal('0.00')
    
    def calculate_total(self):
        """Calculate PO total"""
        total = Decimal('0.00')
        for item in self.items:
            total += item.get_total()
        self.total_amount = total


@dataclass
class PurchaseInvoice:
    """Purchase Invoice"""
    invoice_no: str
    supplier_id: str
    supplier_name: str
    invoice_date: datetime
    due_date: datetime
    items: List[InvoiceItem] = field(default_factory=list)
    status: InvoiceStatus = InvoiceStatus.DRAFT
    total_amount: Decimal = Decimal('0.00')
    total_vat: Decimal = Decimal('0.00')
    
    def calculate_totals(self):
        """Calculate invoice totals"""
        total = Decimal('0.00')
        vat = Decimal('0.00')
        for item in self.items:
            total += item.get_amount()
            vat += item.get_vat_amount()
        self.total_amount = total
        self.total_vat = vat


@dataclass
class Customer:
    """Customer Master"""
    customer_id: str
    customer_name: str
    address: str
    phone: str
    tax_id: str = ""
    credit_limit: Decimal = Decimal('0.00')
    outstanding_balance: Decimal = Decimal('0.00')


@dataclass
class Supplier:
    """Supplier Master"""
    supplier_id: str
    supplier_name: str
    address: str
    phone: str
    tax_id: str = ""
    credit_limit: Decimal = Decimal('0.00')
    outstanding_balance: Decimal = Decimal('0.00')


@dataclass
class Payment:
    """Payment Record (A/R or A/P)"""
    payment_id: str
    invoice_no: str
    payment_date: datetime
    amount: Decimal
    method: PaymentMethod
    cheque_no: Optional[str] = None
    bank_name: Optional[str] = None
    reference: str = ""


@dataclass
class Cheque:
    """Cheque Record"""
    cheque_no: str
    issue_date: datetime
    amount: Decimal
    payee: str
    bank_name: str
    status: str = "In Hand"  # In Hand, Deposited, Cleared, Returned
    clearing_date: Optional[datetime] = None


@dataclass
class FixedAsset:
    """Fixed Asset Register"""
    asset_id: str
    asset_name: str
    purchase_date: datetime
    cost: Decimal
    depreciation_method: str  # Straight Line, Diminishing Value
    useful_life_years: int
    accumulated_depreciation: Decimal = Decimal('0.00')
    department: str = ""
    
    def get_book_value(self) -> Decimal:
        """Calculate book value"""
        return self.cost - self.accumulated_depreciation
    
    def calculate_annual_depreciation(self) -> Decimal:
        """Calculate annual depreciation"""
        if self.depreciation_method == "Straight Line":
            return self.cost / self.useful_life_years
        return Decimal('0.00')


@dataclass
class BudgetAllocation:
    """Budget Control"""
    budget_id: str
    fiscal_year: int
    account_code: str
    department: str
    monthly_budget: List[Decimal] = field(default_factory=lambda: [Decimal('0.00')] * 12)
    actual_spending: List[Decimal] = field(default_factory=lambda: [Decimal('0.00')] * 12)
    
    def get_variance(self, month: int) -> Decimal:
        """Calculate variance for month (0-11)"""
        return self.monthly_budget[month] - self.actual_spending[month]


@dataclass
class TaxReport:
    """VAT/Tax Report"""
    report_no: str
    report_month: int  # 1-12
    report_year: int
    total_sales_invoice: Decimal = Decimal('0.00')
    total_sales_vat: Decimal = Decimal('0.00')
    total_purchase_invoice: Decimal = Decimal('0.00')
    total_purchase_vat: Decimal = Decimal('0.00')
    net_vat: Decimal = Decimal('0.00')
    status: str = "Draft"  # Draft, Submitted
