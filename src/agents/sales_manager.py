"""
Sales Manager Agent - Modules 3, 4, 5
Handles Sales Orders, Invoices, and Analysis
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Dict
from ..models.accounting import (
    SalesInvoice, InvoiceItem, Customer, InvoiceStatus, VATType
)


class SalesManager:
    """Manages sales operations"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.invoices: Dict[str, SalesInvoice] = {}
        self.customers: Dict[str, Customer] = {}
        self.next_invoice_no = 1
    
    def create_customer(self, customer_id: str, name: str, 
                       address: str, phone: str, tax_id: str = "",
                       credit_limit: Decimal = Decimal('100000')) -> Customer:
        """Create new customer"""
        customer = Customer(
            customer_id=customer_id,
            customer_name=name,
            address=address,
            phone=phone,
            tax_id=tax_id,
            credit_limit=credit_limit
        )
        self.customers[customer_id] = customer
        return customer
    
    def create_invoice(self, customer_id: str, invoice_date: datetime,
                      due_date: datetime, vat_type: VATType = VATType.INCLUDED) -> SalesInvoice:
        """Create new sales invoice"""
        if customer_id not in self.customers:
            raise ValueError(f"Customer {customer_id} not found")
        
        customer = self.customers[customer_id]
        invoice_no = f"INV{self.next_invoice_no:06d}"
        self.next_invoice_no += 1
        
        invoice = SalesInvoice(
            invoice_no=invoice_no,
            customer_id=customer_id,
            customer_name=customer.customer_name,
            invoice_date=invoice_date,
            due_date=due_date,
            vat_type=vat_type
        )
        self.invoices[invoice_no] = invoice
        return invoice
    
    def add_item_to_invoice(self, invoice_no: str, item_id: str, 
                          item_name: str, quantity: Decimal,
                          unit_price: Decimal, discount: Decimal = Decimal('0'),
                          vat_rate: Decimal = Decimal('7')) -> InvoiceItem:
        """Add item to invoice"""
        if invoice_no not in self.invoices:
            raise ValueError(f"Invoice {invoice_no} not found")
        
        item = InvoiceItem(
            item_id=item_id,
            item_name=item_name,
            quantity=quantity,
            unit_price=unit_price,
            discount=discount,
            vat_rate=vat_rate
        )
        self.invoices[invoice_no].items.append(item)
        return item
    
    def finalize_invoice(self, invoice_no: str) -> SalesInvoice:
        """Finalize and calculate invoice totals"""
        if invoice_no not in self.invoices:
            raise ValueError(f"Invoice {invoice_no} not found")
        
        invoice = self.invoices[invoice_no]
        invoice.calculate_totals()
        invoice.status = InvoiceStatus.POSTED
        
        # Update customer balance
        customer = self.customers[invoice.customer_id]
        customer.outstanding_balance += invoice.total_amount + invoice.total_vat
        
        return invoice
    
    def get_invoice(self, invoice_no: str) -> SalesInvoice:
        """Retrieve invoice"""
        return self.invoices.get(invoice_no)
    
    def get_all_invoices(self) -> List[SalesInvoice]:
        """Get all invoices"""
        return list(self.invoices.values())
    
    def get_outstanding_invoices(self, customer_id: str) -> List[SalesInvoice]:
        """Get unpaid invoices for customer"""
        return [inv for inv in self.invoices.values()
                if inv.customer_id == customer_id and inv.status != InvoiceStatus.PAID]
    
    def record_payment(self, invoice_no: str, amount: Decimal) -> bool:
        """Record payment for invoice"""
        if invoice_no not in self.invoices:
            return False
        
        invoice = self.invoices[invoice_no]
        if amount >= (invoice.total_amount + invoice.total_vat):
            invoice.status = InvoiceStatus.PAID
            customer = self.customers[invoice.customer_id]
            customer.outstanding_balance -= (invoice.total_amount + invoice.total_vat)
            return True
        return False
    
    def get_sales_summary(self, from_date: datetime, 
                         to_date: datetime) -> Dict:
        """Generate sales analysis"""
        period_invoices = [inv for inv in self.invoices.values()
                          if from_date <= inv.invoice_date <= to_date]
        
        total_sales = sum(inv.total_amount for inv in period_invoices)
        total_vat = sum(inv.total_vat for inv in period_invoices)
        invoice_count = len(period_invoices)
        
        return {
            'period': f"{from_date.date()} to {to_date.date()}",
            'total_sales': total_sales,
            'total_vat': total_vat,
            'invoice_count': invoice_count,
            'average_invoice': total_sales / invoice_count if invoice_count > 0 else Decimal('0')
        }
