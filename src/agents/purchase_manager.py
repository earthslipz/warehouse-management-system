"""
Purchase Manager Agent - Modules 6, 7, 8
Handles Purchase Orders and Invoices
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Dict
from ..models.accounting import (
    PurchaseOrder, PurchaseInvoice, InvoiceItem, Supplier, InvoiceStatus
)


class PurchaseManager:
    """Manages purchase operations"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.purchase_orders: Dict[str, PurchaseOrder] = {}
        self.invoices: Dict[str, PurchaseInvoice] = {}
        self.suppliers: Dict[str, Supplier] = {}
        self.next_po_no = 1
        self.next_invoice_no = 1
    
    def create_supplier(self, supplier_id: str, name: str,
                       address: str, phone: str, tax_id: str = "",
                       credit_limit: Decimal = Decimal('100000')) -> Supplier:
        """Create new supplier"""
        supplier = Supplier(
            supplier_id=supplier_id,
            supplier_name=name,
            address=address,
            phone=phone,
            tax_id=tax_id,
            credit_limit=credit_limit
        )
        self.suppliers[supplier_id] = supplier
        return supplier
    
    def create_purchase_order(self, supplier_id: str, order_date: datetime,
                            expected_delivery: datetime) -> PurchaseOrder:
        """Create new purchase order"""
        if supplier_id not in self.suppliers:
            raise ValueError(f"Supplier {supplier_id} not found")
        
        supplier = self.suppliers[supplier_id]
        po_no = f"PO{self.next_po_no:06d}"
        self.next_po_no += 1
        
        po = PurchaseOrder(
            po_no=po_no,
            supplier_id=supplier_id,
            supplier_name=supplier.supplier_name,
            order_date=order_date,
            expected_delivery=expected_delivery
        )
        self.purchase_orders[po_no] = po
        return po
    
    def add_item_to_po(self, po_no: str, item_id: str,
                       item_name: str, quantity: Decimal,
                       unit_price: Decimal, discount: Decimal = Decimal('0'),
                       vat_rate: Decimal = Decimal('7')) -> InvoiceItem:
        """Add item to purchase order"""
        if po_no not in self.purchase_orders:
            raise ValueError(f"PO {po_no} not found")
        
        item = InvoiceItem(
            item_id=item_id,
            item_name=item_name,
            quantity=quantity,
            unit_price=unit_price,
            discount=discount,
            vat_rate=vat_rate
        )
        self.purchase_orders[po_no].items.append(item)
        return item
    
    def finalize_po(self, po_no: str) -> PurchaseOrder:
        """Finalize purchase order"""
        if po_no not in self.purchase_orders:
            raise ValueError(f"PO {po_no} not found")
        
        po = self.purchase_orders[po_no]
        po.calculate_total()
        po.status = "Ordered"
        return po
    
    def create_purchase_invoice(self, supplier_id: str, invoice_date: datetime,
                               due_date: datetime) -> PurchaseInvoice:
        """Create purchase invoice"""
        if supplier_id not in self.suppliers:
            raise ValueError(f"Supplier {supplier_id} not found")
        
        supplier = self.suppliers[supplier_id]
        invoice_no = f"PINV{self.next_invoice_no:06d}"
        self.next_invoice_no += 1
        
        invoice = PurchaseInvoice(
            invoice_no=invoice_no,
            supplier_id=supplier_id,
            supplier_name=supplier.supplier_name,
            invoice_date=invoice_date,
            due_date=due_date
        )
        self.invoices[invoice_no] = invoice
        return invoice
    
    def add_item_to_invoice(self, invoice_no: str, item_id: str,
                           item_name: str, quantity: Decimal,
                           unit_price: Decimal, discount: Decimal = Decimal('0'),
                           vat_rate: Decimal = Decimal('7')) -> InvoiceItem:
        """Add item to purchase invoice"""
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
    
    def finalize_invoice(self, invoice_no: str) -> PurchaseInvoice:
        """Finalize and calculate invoice totals"""
        if invoice_no not in self.invoices:
            raise ValueError(f"Invoice {invoice_no} not found")
        
        invoice = self.invoices[invoice_no]
        invoice.calculate_totals()
        invoice.status = InvoiceStatus.POSTED
        
        # Update supplier balance
        supplier = self.suppliers[invoice.supplier_id]
        supplier.outstanding_balance += invoice.total_amount + invoice.total_vat
        
        return invoice
    
    def record_payment(self, invoice_no: str, amount: Decimal) -> bool:
        """Record payment for invoice"""
        if invoice_no not in self.invoices:
            return False
        
        invoice = self.invoices[invoice_no]
        if amount >= (invoice.total_amount + invoice.total_vat):
            invoice.status = InvoiceStatus.PAID
            supplier = self.suppliers[invoice.supplier_id]
            supplier.outstanding_balance -= (invoice.total_amount + invoice.total_vat)
            return True
        return False
    
    def get_purchase_summary(self, from_date: datetime,
                            to_date: datetime) -> Dict:
        """Generate purchase analysis"""
        period_invoices = [inv for inv in self.invoices.values()
                          if from_date <= inv.invoice_date <= to_date]
        
        total_purchases = sum(inv.total_amount for inv in period_invoices)
        total_vat = sum(inv.total_vat for inv in period_invoices)
        invoice_count = len(period_invoices)
        
        return {
            'period': f"{from_date.date()} to {to_date.date()}",
            'total_purchases': total_purchases,
            'total_vat': total_vat,
            'invoice_count': invoice_count,
            'average_invoice': total_purchases / invoice_count if invoice_count > 0 else Decimal('0')
        }
    
    def get_outstanding_invoices(self, supplier_id: str) -> List[PurchaseInvoice]:
        """Get unpaid invoices for supplier"""
        return [inv for inv in self.invoices.values()
                if inv.supplier_id == supplier_id and inv.status != InvoiceStatus.PAID]
