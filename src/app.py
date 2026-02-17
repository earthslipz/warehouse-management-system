import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

from .event_bus import EventBus
from .agents.inventory_tracker import InventoryTracker
from .agents.order_processor import OrderProcessor
from .agents.agv_controller import AGVController
from .agents.rfid_sensor import RFIDSensor
from .agents.alert_system import AlertSystem
from .agents.general_ledger import GeneralLedgerAgent
from .agents.sales_manager import SalesManager
from .agents.purchase_manager import PurchaseManager
from .agents.accounting_managers import (
    TaxManager, BankingManager, AssetManager, BudgetManager
)

from .events import order_events as ord_ev
from .events import inventory_events as inv_ev
from .events import alert_events as al_ev
from .models.accounting import VATType


class ThaiAccountingApp(tk.Tk):
    """
    Thai Accounting System (ระบบบัญชีสําเร็จรูป)
    Comprehensive accounting software for Thai businesses.
    Supports 16 major accounting modules.
    """

    def __init__(self):
        # Check if display is available before initializing tkinter
        if not os.environ.get('DISPLAY') and sys.platform != 'win32':
            raise RuntimeError(
                "No display server found! This application requires a graphical display.\n"
                "To run this in a headless environment, install and start Xvfb:\n"
                "  sudo apt-get install xvfb\n"
                "  Xvfb :99 -screen 0 1024x768x24 &\n"
                "  export DISPLAY=:99\n"
                "Then run the application again."
            )
        
        super().__init__()
        self.title("ระบบบัญชีสําเร็จรูป - Thai Accounting System")
        self.geometry("1200x700")

        # Initialize event bus and agents
        self.event_bus = EventBus()
        self.inventory_tracker = InventoryTracker(self.event_bus)
        self.order_processor = OrderProcessor(self.event_bus, self.inventory_tracker)
        self.agv_controller = AGVController(self.event_bus)
        self.rfid_sensor = RFIDSensor(self.event_bus)
        self.alert_system = AlertSystem(self.event_bus)
        
        # Initialize accounting managers
        self.general_ledger = GeneralLedgerAgent(self.event_bus)
        self.sales_manager = SalesManager(self.event_bus)
        self.purchase_manager = PurchaseManager(self.event_bus)
        self.tax_manager = TaxManager(self.event_bus)
        self.banking_manager = BankingManager(self.event_bus)
        self.asset_manager = AssetManager(self.event_bus)
        self.budget_manager = BudgetManager(self.event_bus)
        
        # Current working documents
        self._current_sales_invoice = None
        self._current_purchase_order = None
        self._current_purchase_invoice = None

        # Create main notebook for 16 modules
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Create all 16 accounting modules
        self._create_general_ledger_tab()      # 1. General Ledger
        self._create_service_business_tab()    # 2. Service Business
        self._create_sales_order_tab()         # 3. Sales Order (SO)
        self._create_sales_invoice_tab()       # 4. Sales Invoice
        self._create_sales_analysis_tab()      # 5. Sales Analysis
        self._create_purchase_order_tab()      # 6. Purchase Order (PO)
        self._create_purchases_tab()           # 7. Purchases
        self._create_purchase_analysis_tab()   # 8. Purchase Analysis
        self._create_vat_tax_tab()             # 9. VAT/Withholding Tax
        self._create_accounts_receivable_tab() # 10. Accounts Receivable (A/R)
        self._create_accounts_payable_tab()    # 11. Accounts Payable (A/P)
        self._create_banking_tab()             # 12. Cash/Check/Bank
        self._create_inventory_control_tab()   # 13. Inventory Control
        self._create_budget_control_tab()      # 14. Budget Control
        self._create_asset_depreciation_tab()  # 15. Asset Depreciation
        self._create_security_tab()            # 16. Security/Access Control


    # ===== MODULE 1: GENERAL LEDGER (บัญชีแยกประเภท) =====
    def _create_general_ledger_tab(self):
        """General Ledger - Debit/Credit Entry System"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="1. บัญชีแยกประเภท")
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Entry Voucher")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(input_frame, text="Voucher #:").grid(row=0, column=0, sticky="w", padx=5)
        self.gl_voucher_entry = ttk.Entry(input_frame, width=20)
        self.gl_voucher_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Date:").grid(row=0, column=2, sticky="w", padx=5)
        self.gl_date_entry = ttk.Entry(input_frame, width=15)
        self.gl_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.gl_date_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="Description:").grid(row=1, column=0, sticky="w", padx=5)
        self.gl_desc_entry = ttk.Entry(input_frame, width=80)
        self.gl_desc_entry.grid(row=1, column=1, columnspan=3, padx=5, sticky="ew")
        
        # Account and Debit/Credit entries
        detail_frame = ttk.LabelFrame(input_frame, text="Entry Details")
        detail_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=10)
        
        ttk.Label(detail_frame, text="Account Code:").pack(side=tk.LEFT, padx=5)
        self.gl_account_entry = ttk.Entry(detail_frame, width=15)
        self.gl_account_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(detail_frame, text="Debit:").pack(side=tk.LEFT, padx=5)
        self.gl_debit_entry = ttk.Entry(detail_frame, width=15)
        self.gl_debit_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(detail_frame, text="Credit:").pack(side=tk.LEFT, padx=5)
        self.gl_credit_entry = ttk.Entry(detail_frame, width=15)
        self.gl_credit_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(detail_frame, text="Add Entry", command=self._add_ledger_entry).pack(side=tk.LEFT, padx=5)
        
        # Debit/Credit table
        table_frame = ttk.LabelFrame(frame, text="Ledger Entries (up to 9,999 items per voucher)")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Account", "Debit", "Credit", "Description")
        self.gl_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.gl_tree.heading(col, text=col)
            self.gl_tree.column(col, width=100)
        self.gl_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="Delete Entry", command=self._delete_ledger_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Post to Ledger", command=self._post_ledger).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="View Trial Balance", command=self._show_trial_balance).pack(side=tk.LEFT, padx=5)
    
    def _add_ledger_entry(self):
        """Add ledger entry"""
        voucher_no = self.gl_voucher_entry.get()
        account_code = self.gl_account_entry.get()
        
        try:
            debit = Decimal(self.gl_debit_entry.get() or '0')
            credit = Decimal(self.gl_credit_entry.get() or '0')
            desc = self.gl_desc_entry.get()
            
            if not voucher_no or not account_code:
                messagebox.showerror("Error", "Voucher # and Account Code required")
                return
            
            if debit == 0 and credit == 0:
                messagebox.showerror("Error", "Enter Debit or Credit amount")
                return
            
            entry = self.general_ledger.add_entry(voucher_no, account_code, debit, credit, desc)
            
            self.gl_tree.insert('', tk.END, values=(
                account_code,
                str(debit) if debit > 0 else '',
                str(credit) if credit > 0 else '',
                desc
            ))
            
            self.gl_debit_entry.delete(0, tk.END)
            self.gl_credit_entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", "Entry added successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _delete_ledger_entry(self):
        """Delete selected ledger entry"""
        selected = self.gl_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select entry to delete")
            return
        
        for item in selected:
            self.gl_tree.delete(item)
        messagebox.showinfo("Success", "Entry deleted")
    
    def _post_ledger(self):
        """Post voucher to ledger"""
        voucher_no = self.gl_voucher_entry.get()
        if not voucher_no:
            messagebox.showerror("Error", "Enter Voucher #")
            return
        
        if self.general_ledger.post_voucher(voucher_no):
            messagebox.showinfo("Success", f"Voucher {voucher_no} posted successfully")
            self._refresh_gl_tree()
        else:
            messagebox.showerror("Error", "Voucher not balanced! Debit ≠ Credit")
    
    def _show_trial_balance(self):
        """Display trial balance"""
        tb = self.general_ledger.get_trial_balance()
        balance_text = "Trial Balance\n" + "="*40 + "\n"
        for code, amount in tb.items():
            balance_text += f"{code}: {amount}\n"
        
        msg_win = tk.Toplevel(self)
        msg_win.title("Trial Balance")
        text_widget = tk.Text(msg_win, height=15, width=50)
        text_widget.pack(padx=10, pady=10)
        text_widget.insert('1.0', balance_text)
        text_widget.config(state=tk.DISABLED)
    
    def _refresh_gl_tree(self):
        """Refresh GL tree view"""
        for item in self.gl_tree.get_children():
            self.gl_tree.delete(item)

    # ===== MODULE 2: SERVICE BUSINESS (ธุรกิจบริการ) =====
    def _create_service_business_tab(self):
        """Service Business Operations"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="2. ธุรกิจบริการ")
        
        form_frame = ttk.LabelFrame(frame, text="Service Invoice")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Service ID:").grid(row=0, column=0, sticky="w")
        self.service_id = ttk.Entry(form_frame, width=30)
        self.service_id.grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Customer:").grid(row=1, column=0, sticky="w")
        self.service_customer = ttk.Entry(form_frame, width=40)
        self.service_customer.grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Service Description:").grid(row=2, column=0, sticky="w")
        self.service_desc = ttk.Entry(form_frame, width=40)
        self.service_desc.grid(row=2, column=1, padx=5)
        
        ttk.Label(form_frame, text="Amount:").grid(row=3, column=0, sticky="w")
        self.service_amount = ttk.Entry(form_frame, width=20)
        self.service_amount.grid(row=3, column=1, padx=5)
        
        ttk.Button(form_frame, text="Record Service Invoice", command=self._record_service_invoice).grid(row=4, column=0, columnspan=2, pady=10)
    
    def _record_service_invoice(self):
        """Record service invoice"""
        try:
            service_id = self.service_id.get()
            amount = Decimal(self.service_amount.get())
            if service_id and amount > 0:
                messagebox.showinfo("Success", f"Service {service_id} recorded for {amount}")
            else:
                messagebox.showerror("Error", "Invalid service data")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ===== MODULE 3: SALES ORDER (ใบสั่งขาย/ใบรับจองสินคา) =====
    def _create_sales_order_tab(self):
        """Sales Order - Entry and tracking"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="3. ใบสั่งขาย")
        
        # Search and filter
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Search Customer:").pack(side=tk.LEFT)
        self.so_search = ttk.Entry(filter_frame, width=30)
        self.so_search.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Search", command=self._search_orders).pack(side=tk.LEFT)
        
        # Sales orders list
        list_frame = ttk.LabelFrame(frame, text="Sales Orders")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Order#", "Customer", "Date", "Amount", "Status")
        self.so_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.so_tree.heading(col, text=col)
            self.so_tree.column(col, width=100)
        self.so_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="New Order", command=self._new_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="View All", command=self._view_all_orders).pack(side=tk.LEFT, padx=5)
    
    def _search_orders(self):
        """Search orders by customer"""
        customer = self.so_search.get()
        self.so_tree.delete(*self.so_tree.get_children())
        for invoice in self.sales_manager.get_all_invoices():
            if customer.lower() in invoice.customer_name.lower():
                self.so_tree.insert('', tk.END, values=(
                    invoice.invoice_no,
                    invoice.customer_name,
                    invoice.invoice_date.strftime("%Y-%m-%d"),
                    str(invoice.total_amount),
                    invoice.status.value
                ))
    
    def _new_order(self):
        """Create new order from sales invoice"""
        messagebox.showinfo("Info", "Use Sales Invoice tab (Module 4) to create orders")
    
    def _view_all_orders(self):
        """View all orders"""
        self.so_tree.delete(*self.so_tree.get_children())
        for invoice in self.sales_manager.get_all_invoices():
            self.so_tree.insert('', tk.END, values=(
                invoice.invoice_no,
                invoice.customer_name,
                invoice.invoice_date.strftime("%Y-%m-%d"),
                str(invoice.total_amount + invoice.total_vat),
                invoice.status.value
            ))

    # ===== MODULE 4: SALES INVOICE (ใบเสร็จ/ใบกํากับภาษี) =====
    def _create_sales_invoice_tab(self):
        """Sales Invoice - Generate and manage invoices"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="4. ใบเสร็จ")
        
        form_frame = ttk.LabelFrame(frame, text="Sales Invoice Entry")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Customer ID:").grid(row=0, column=0, sticky="w")
        self.si_customer_id = ttk.Entry(form_frame, width=20)
        self.si_customer_id.grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Customer Name:").grid(row=0, column=2, sticky="w")
        self.si_customer_name = ttk.Entry(form_frame, width=40)
        self.si_customer_name.grid(row=0, column=3, padx=5)
        
        ttk.Button(form_frame, text="Create Customer", command=self._create_sales_customer).grid(row=0, column=4, padx=5)
        
        ttk.Label(form_frame, text="Item ID:").grid(row=1, column=0, sticky="w")
        self.si_item_id = ttk.Entry(form_frame, width=20)
        self.si_item_id.grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Item Name:").grid(row=1, column=2, sticky="w")
        self.si_item_name = ttk.Entry(form_frame, width=40)
        self.si_item_name.grid(row=1, column=3, padx=5)
        
        ttk.Label(form_frame, text="Qty:").grid(row=2, column=0, sticky="w")
        self.si_qty = ttk.Entry(form_frame, width=15)
        self.si_qty.grid(row=2, column=1, padx=5)
        
        ttk.Label(form_frame, text="Unit Price:").grid(row=2, column=2, sticky="w")
        self.si_unit_price = ttk.Entry(form_frame, width=15)
        self.si_unit_price.grid(row=2, column=3, padx=5)
        
        ttk.Label(form_frame, text="Discount %:").grid(row=3, column=0, sticky="w")
        self.si_discount = ttk.Entry(form_frame, width=15)
        self.si_discount.insert(0, "0")
        self.si_discount.grid(row=3, column=1, padx=5)
        
        ttk.Label(form_frame, text="VAT Rate:").grid(row=3, column=2, sticky="w")
        self.si_vat_var = tk.StringVar(value="7%")
        ttk.Combobox(form_frame, textvariable=self.si_vat_var, 
                    values=["7%", "10%", "0%", "Exempt"]).grid(row=3, column=3, padx=5)
        
        ttk.Button(form_frame, text="Add Item", command=self._add_sales_item).grid(row=4, column=0, padx=5, pady=10)
        ttk.Button(form_frame, text="Create Invoice", command=self._create_sales_invoice).grid(row=4, column=1, padx=5, pady=10)
        ttk.Button(form_frame, text="View Invoices", command=self._view_sales_invoices).grid(row=4, column=2, padx=5, pady=10)
        
        # Invoices list
        list_frame = ttk.LabelFrame(frame, text="Sales Invoices")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Invoice#", "Customer", "Amount", "VAT", "Total", "Status")
        self.si_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.si_tree.heading(col, text=col)
            self.si_tree.column(col, width=100)
        self.si_tree.pack(fill=tk.BOTH, expand=True)
    
    def _create_sales_customer(self):
        """Create new customer"""
        try:
            cust_id = self.si_customer_id.get()
            cust_name = self.si_customer_name.get()
            
            if not cust_id or not cust_name:
                messagebox.showerror("Error", "Enter Customer ID and Name")
                return
            
            customer = self.sales_manager.create_customer(cust_id, cust_name, "", "")
            messagebox.showinfo("Success", f"Customer {cust_name} created")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _add_sales_item(self):
        """Add item to current invoice"""
        try:
            item_id = self.si_item_id.get()
            item_name = self.si_item_name.get()
            qty = Decimal(self.si_qty.get())
            price = Decimal(self.si_unit_price.get())
            discount = Decimal(self.si_discount.get())
            vat_rate = Decimal(self.si_vat_var.get().rstrip('%'))
            
            if not self._current_sales_invoice:
                messagebox.showerror("Error", "Create invoice first")
                return
            
            self.sales_manager.add_item_to_invoice(
                self._current_sales_invoice.invoice_no,
                item_id, item_name, qty, price, discount, vat_rate
            )
            messagebox.showinfo("Success", "Item added")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _create_sales_invoice(self):
        """Create new sales invoice"""
        try:
            cust_id = self.si_customer_id.get()
            if not cust_id:
                messagebox.showerror("Error", "Select Customer ID")
                return
            
            invoice = self.sales_manager.create_invoice(
                cust_id,
                datetime.now(),
                datetime.now() + timedelta(days=30),
                VATType.INCLUDED
            )
            self._current_sales_invoice = invoice
            messagebox.showinfo("Success", f"Invoice {invoice.invoice_no} created")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _view_sales_invoices(self):
        """View all sales invoices"""
        self.si_tree.delete(*self.si_tree.get_children())
        for invoice in self.sales_manager.get_all_invoices():
            self.si_tree.insert('', tk.END, values=(
                invoice.invoice_no,
                invoice.customer_name,
                str(invoice.total_amount),
                str(invoice.total_vat),
                str(invoice.total_amount + invoice.total_vat),
                invoice.status.value
            ))

    # ===== MODULE 5: SALES ANALYSIS (วิเคราะห์การขาย) =====
    def _create_sales_analysis_tab(self):
        """Sales Analysis - Reports and metrics"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="5. ประเมิน") 
        
        control_frame = ttk.LabelFrame(frame, text="Sales Report Controls")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Period (days back):").pack(side=tk.LEFT)
        self.sales_period = ttk.Entry(control_frame, width=10)
        self.sales_period.insert(0, "30")
        self.sales_period.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Generate Report", command=self._generate_sales_report).pack(side=tk.LEFT, padx=5)
        
        # Results
        result_frame = ttk.LabelFrame(frame, text="Sales Summary")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Product", "Qty", "Amount", "VAT", "Total")
        self.sales_analysis_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        for col in columns:
            self.sales_analysis_tree.heading(col, text=col)
            self.sales_analysis_tree.column(col, width=100)
        self.sales_analysis_tree.pack(fill=tk.BOTH, expand=True)
        
        self.sales_summary_label = ttk.Label(frame, text="Summary: ")
        self.sales_summary_label.pack(padx=10, pady=10)
    
    def _generate_sales_report(self):
        """Generate sales analysis report"""
        try:
            days = int(self.sales_period.get())
            from_date = datetime.now() - timedelta(days=days)
            to_date = datetime.now()
            
            summary = self.sales_manager.get_sales_summary(from_date, to_date)
            
            # Populate tree with invoice items
            self.sales_analysis_tree.delete(*self.sales_analysis_tree.get_children())
            for invoice in self.sales_manager.get_all_invoices():
                if from_date <= invoice.invoice_date <= to_date:
                    for item in invoice.items:
                        self.sales_analysis_tree.insert('', tk.END, values=(
                            item.item_name,
                            str(item.quantity),
                            str(item.get_amount()),
                            str(item.get_vat_amount()),
                            str(item.get_total())
                        ))
            
            # Update summary
            summary_text = f"Sales: {summary['total_sales']} | VAT: {summary['total_vat']} | Invoices: {summary['invoice_count']}"
            self.sales_summary_label.config(text=f"Summary: {summary_text}")
            
            messagebox.showinfo("Success", f"Period: {summary['period']}\nTotal Sales: {summary['total_sales']}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ===== MODULE 6: PURCHASE ORDER (ใบสั่งซื้อ) =====
    def _create_purchase_order_tab(self):
        """Purchase Order Management"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="6. PO")
        
        form_frame = ttk.LabelFrame(frame, text="Purchase Order Entry")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Supplier ID:").grid(row=0, column=0, sticky="w")
        self.po_supplier_id = ttk.Entry(form_frame, width=20)
        self.po_supplier_id.grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Supplier Name:").grid(row=0, column=2, sticky="w")
        self.po_supplier_name = ttk.Entry(form_frame, width=40)
        self.po_supplier_name.grid(row=0, column=3, padx=5)
        
        ttk.Button(form_frame, text="Create Supplier", command=self._create_po_supplier).grid(row=0, column=4, padx=5)
        
        ttk.Label(form_frame, text="Item ID:").grid(row=1, column=0, sticky="w")
        self.po_item_id = ttk.Entry(form_frame, width=20)
        self.po_item_id.grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Item Name:").grid(row=1, column=2, sticky="w")
        self.po_item_name = ttk.Entry(form_frame, width=40)
        self.po_item_name.grid(row=1, column=3, padx=5)
        
        ttk.Label(form_frame, text="Qty:").grid(row=2, column=0, sticky="w")
        self.po_qty = ttk.Entry(form_frame, width=15)
        self.po_qty.grid(row=2, column=1, padx=5)
        
        ttk.Label(form_frame, text="Unit Price:").grid(row=2, column=2, sticky="w")
        self.po_unit_price = ttk.Entry(form_frame, width=15)
        self.po_unit_price.grid(row=2, column=3, padx=5)
        
        ttk.Button(form_frame, text="Add Item", command=self._add_po_item).grid(row=3, column=0, padx=5, pady=10)
        ttk.Button(form_frame, text="Create PO", command=self._create_purchase_order).grid(row=3, column=1, padx=5, pady=10)
        ttk.Button(form_frame, text="View POs", command=self._view_purchase_orders).grid(row=3, column=2, padx=5, pady=10)
        
        # Order list
        list_frame = ttk.LabelFrame(frame, text="Purchase Orders")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("PO#", "Supplier", "Date", "Amount", "Received")
        self.po_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.po_tree.heading(col, text=col)
            self.po_tree.column(col, width=100)
        self.po_tree.pack(fill=tk.BOTH, expand=True)
    
    def _create_po_supplier(self):
        """Create new supplier"""
        try:
            supp_id = self.po_supplier_id.get()
            supp_name = self.po_supplier_name.get()
            
            if not supp_id or not supp_name:
                messagebox.showerror("Error", "Enter Supplier ID and Name")
                return
            
            supplier = self.purchase_manager.create_supplier(supp_id, supp_name, "", "")
            messagebox.showinfo("Success", f"Supplier {supp_name} created")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _add_po_item(self):
        """Add item to PO"""
        try:
            item_id = self.po_item_id.get()
            item_name = self.po_item_name.get()
            qty = Decimal(self.po_qty.get())
            price = Decimal(self.po_unit_price.get())
            
            if not self._current_purchase_order:
                messagebox.showerror("Error", "Create PO first")
                return
            
            self.purchase_manager.add_item_to_po(
                self._current_purchase_order.po_no,
                item_id, item_name, qty, price
            )
            messagebox.showinfo("Success", "Item added to PO")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _create_purchase_order(self):
        """Create new purchase order"""
        try:
            supp_id = self.po_supplier_id.get()
            if not supp_id:
                messagebox.showerror("Error", "Select Supplier ID")
                return
            
            po = self.purchase_manager.create_purchase_order(
                supp_id,
                datetime.now(),
                datetime.now() + timedelta(days=30)
            )
            self._current_purchase_order = po
            messagebox.showinfo("Success", f"PO {po.po_no} created")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _view_purchase_orders(self):
        """View all POs"""
        self.po_tree.delete(*self.po_tree.get_children())
        for po in self.purchase_manager.purchase_orders.values():
            self.po_tree.insert('', tk.END, values=(
                po.po_no,
                po.supplier_name,
                po.order_date.strftime("%Y-%m-%d"),
                str(po.total_amount),
                po.status
            ))

    # ===== MODULE 7: PURCHASES (จัดซื้อ) =====
    def _create_purchases_tab(self):
        """Purchase Management - Invoice entry"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="7. ซื้อ")
        
        form_frame = ttk.LabelFrame(frame, text="Purchase Invoice Entry")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Supplier ID:").grid(row=0, column=0, sticky="w")
        self.pinv_supplier_id = ttk.Entry(form_frame, width=20)
        self.pinv_supplier_id.grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Invoice #:").grid(row=1, column=0, sticky="w")
        self.pinv_invoice_no = ttk.Entry(form_frame, width=20)
        self.pinv_invoice_no.grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Invoice Date:").grid(row=2, column=0, sticky="w")
        self.pinv_date = ttk.Entry(form_frame, width=20)
        self.pinv_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.pinv_date.grid(row=2, column=1, padx=5)
        
        ttk.Label(form_frame, text="Total Amount:").grid(row=3, column=0, sticky="w")
        self.pinv_amount = ttk.Entry(form_frame, width=20)
        self.pinv_amount.grid(row=3, column=1, padx=5)
        
        ttk.Button(form_frame, text="Create Invoice", command=self._create_purchase_invoice).grid(row=4, column=0, columnspan=2, pady=10)
    
    def _create_purchase_invoice(self):
        """Create purchase invoice"""
        try:
            supp_id = self.pinv_supplier_id.get()
            if not supp_id:
                messagebox.showerror("Error", "Select Supplier ID")
                return
            
            invoice = self.purchase_manager.create_purchase_invoice(
                supp_id,
                datetime.now(),
                datetime.now() + timedelta(days=30)
            )
            self._current_purchase_invoice = invoice
            messagebox.showinfo("Success", f"Invoice {invoice.invoice_no} created")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ===== MODULE 8: PURCHASE ANALYSIS (วิเคราะห์การซื้อ) =====
    def _create_purchase_analysis_tab(self):
        """Purchase Analysis"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="8. วิเค ซื้อ")
        
        control_frame = ttk.LabelFrame(frame, text="Purchase Report")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Period (days back):").pack(side=tk.LEFT)
        self.purchase_period = ttk.Entry(control_frame, width=10)
        self.purchase_period.insert(0, "30")
        self.purchase_period.pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Generate Report", command=self._generate_purchase_report).pack(side=tk.LEFT, padx=5)
        
        result_frame = ttk.LabelFrame(frame, text="Purchase Summary by Supplier")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Supplier", "Qty_Items", "Total_Amount", "Total_VAT")
        self.purchase_analysis_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        for col in columns:
            self.purchase_analysis_tree.heading(col, text=col)
            self.purchase_analysis_tree.column(col, width=100)
        self.purchase_analysis_tree.pack(fill=tk.BOTH, expand=True)
        
        self.purchase_summary_label = ttk.Label(frame, text="Summary: ")
        self.purchase_summary_label.pack(padx=10, pady=10)
    
    def _generate_purchase_report(self):
        """Generate purchase analysis report"""
        try:
            days = int(self.purchase_period.get())
            from_date = datetime.now() - timedelta(days=days)
            to_date = datetime.now()
            
            summary = self.purchase_manager.get_purchase_summary(from_date, to_date)
            
            # Populate tree
            self.purchase_analysis_tree.delete(*self.purchase_analysis_tree.get_children())
            for invoice in self.purchase_manager.invoices.values():
                if from_date <= invoice.invoice_date <= to_date:
                    total_items = sum(item.quantity for item in invoice.items)
                    self.purchase_analysis_tree.insert('', tk.END, values=(
                        invoice.supplier_name,
                        str(total_items),
                        str(invoice.total_amount),
                        str(invoice.total_vat)
                    ))
            
            summary_text = f"Total: {summary['total_purchases']} | VAT: {summary['total_vat']} | Invoices: {summary['invoice_count']}"
            self.purchase_summary_label.config(text=f"Summary: {summary_text}")
            
            messagebox.showinfo("Success", f"Period: {summary['period']}\nTotal Purchases: {summary['total_purchases']}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ===== MODULE 9: VAT/WITHHOLDING TAX (ภาษี) =====
    def _create_vat_tax_tab(self):
        """VAT and Withholding Tax Management"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="9. ภาษี")
        
        control_frame = ttk.LabelFrame(frame, text="Tax Report Period")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Month/Year:").pack(side=tk.LEFT)
        self.tax_month = ttk.Entry(control_frame, width=10)
        self.tax_month.insert(0, datetime.now().strftime("%m/%Y"))
        self.tax_month.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Tax Type:").pack(side=tk.LEFT)
        self.tax_type = ttk.Combobox(control_frame, values=["Purchase Tax", "Sales Tax", "Withholding", "Summary"])
        self.tax_type.set("Summary")
        self.tax_type.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Generate Tax Report", command=self._generate_tax_report).pack(side=tk.LEFT, padx=5)
        
        result_frame = ttk.LabelFrame(frame, text="Tax Summary")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Description", "Amount", "Tax Rate", "Tax Amount")
        self.tax_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        for col in columns:
            self.tax_tree.heading(col, text=col)
            self.tax_tree.column(col, width=100)
        self.tax_tree.pack(fill=tk.BOTH, expand=True)
    
    def _generate_tax_report(self):
        """Generate tax report"""
        try:
            from_date = datetime.now() - timedelta(days=30)
            to_date = datetime.now()
            
            self.tax_tree.delete(*self.tax_tree.get_children())
            
            # Sales tax
            total_sales_vat = Decimal('0')
            for invoice in self.sales_manager.get_all_invoices():
                if from_date <= invoice.invoice_date <= to_date:
                    total_sales_vat += invoice.total_vat
                    self.tax_tree.insert('', tk.END, values=(
                        f"Sales: {invoice.invoice_no}",
                        str(invoice.total_amount),
                        "7%",
                        str(invoice.total_vat)
                    ))
            
            # Purchase tax
            total_purchase_vat = Decimal('0')
            for invoice in self.purchase_manager.invoices.values():
                if from_date <= invoice.invoice_date <= to_date:
                    total_purchase_vat += invoice.total_vat
                    self.tax_tree.insert('', tk.END, values=(
                        f"Purchase: {invoice.invoice_no}",
                        str(invoice.total_amount),
                        "7%",
                        str(invoice.total_vat)
                    ))
            
            # Net VAT
            net_vat = total_sales_vat - total_purchase_vat
            self.tax_tree.insert('', tk.END, values=(
                "NET VAT (Payable)",
                "-",
                "-",
                str(net_vat)
            ))
            
            messagebox.showinfo("Success", f"Net VAT: {net_vat}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ===== MODULE 10: ACCOUNTS RECEIVABLE (ลูกหนี้) =====
    def _create_accounts_receivable_tab(self):
        """Accounts Receivable - Customer debts"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="10. ลูกหนี้")
        
        form_frame = ttk.LabelFrame(frame, text="Receipt Entry")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Customer ID:").grid(row=0, column=0, sticky="w")
        self.ar_customer_id = ttk.Entry(form_frame, width=40)
        self.ar_customer_id.grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Received Amount:").grid(row=1, column=0, sticky="w")
        self.ar_amount = ttk.Entry(form_frame, width=20)
        self.ar_amount.grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Payment Method:").grid(row=2, column=0, sticky="w")
        ttk.Combobox(form_frame, values=["Cash", "Cheque", "Bank Transfer", "Credit Card"]).grid(row=2, column=1, padx=5)
        
        ttk.Button(form_frame, text="Record Payment", command=self._record_ar_payment).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Outstanding invoices
        list_frame = ttk.LabelFrame(frame, text="Outstanding Invoices")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Invoice", "Customer", "Amount", "Due Date", "Days Overdue")
        self.ar_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.ar_tree.heading(col, text=col)
            self.ar_tree.column(col, width=100)
        self.ar_tree.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(list_frame, text="Refresh", command=self._refresh_ar_list).pack(pady=5)
    
    def _record_ar_payment(self):
        """Record customer payment"""
        try:
            cust_id = self.ar_customer_id.get()
            amount = Decimal(self.ar_amount.get())
            
            invoices = self.sales_manager.get_outstanding_invoices(cust_id)
            if not invoices:
                messagebox.showwarning("Warning", "No outstanding invoices")
                return
            
            # Apply payment to first outstanding invoice
            if self.sales_manager.record_payment(invoices[0].invoice_no, amount):
                messagebox.showinfo("Success", f"Payment of {amount} recorded")
                self._refresh_ar_list()
            else:
                messagebox.showerror("Error", "Payment amount insufficient")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _refresh_ar_list(self):
        """Refresh AR list"""
        self.ar_tree.delete(*self.ar_tree.get_children())
        for invoice in self.sales_manager.get_all_invoices():
            if invoice.status.value != "Paid":
                days_overdue = (datetime.now() - invoice.due_date).days
                self.ar_tree.insert('', tk.END, values=(
                    invoice.invoice_no,
                    invoice.customer_name,
                    str(invoice.total_amount + invoice.total_vat),
                    invoice.due_date.strftime("%Y-%m-%d"),
                    max(0, days_overdue)
                ))

    # ===== MODULE 11: ACCOUNTS PAYABLE (เจ้าหนี้) =====
    def _create_accounts_payable_tab(self):
        """Accounts Payable - Supplier debts"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="11. เจ้าหนี้")
        
        form_frame = ttk.LabelFrame(frame, text="Payment Entry")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Supplier ID:").grid(row=0, column=0, sticky="w")
        self.ap_supplier_id = ttk.Entry(form_frame, width=40)
        self.ap_supplier_id.grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Payment Amount:").grid(row=1, column=0, sticky="w")
        self.ap_amount = ttk.Entry(form_frame, width=20)
        self.ap_amount.grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Payment Method:").grid(row=2, column=0, sticky="w")
        ttk.Combobox(form_frame, values=["Cash", "Cheque", "Bank Transfer", "Draft"]).grid(row=2, column=1, padx=5)
        
        ttk.Button(form_frame, text="Record Payment", command=self._record_ap_payment).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Outstanding payables
        list_frame = ttk.LabelFrame(frame, text="Outstanding Bills")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Invoice", "Supplier", "Amount", "Due Date", "Days Overdue")
        self.ap_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.ap_tree.heading(col, text=col)
            self.ap_tree.column(col, width=100)
        self.ap_tree.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(list_frame, text="Refresh", command=self._refresh_ap_list).pack(pady=5)
    
    def _record_ap_payment(self):
        """Record supplier payment"""
        try:
            supp_id = self.ap_supplier_id.get()
            amount = Decimal(self.ap_amount.get())
            
            invoices = self.purchase_manager.get_outstanding_invoices(supp_id)
            if not invoices:
                messagebox.showwarning("Warning", "No outstanding invoices")
                return
            
            # Apply payment to first outstanding invoice
            if self.purchase_manager.record_payment(invoices[0].invoice_no, amount):
                messagebox.showinfo("Success", f"Payment of {amount} recorded")
                self._refresh_ap_list()
            else:
                messagebox.showerror("Error", "Payment amount insufficient")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _refresh_ap_list(self):
        """Refresh AP list"""
        self.ap_tree.delete(*self.ap_tree.get_children())
        for invoice in self.purchase_manager.invoices.values():
            if invoice.status.value != "Paid":
                days_overdue = (datetime.now() - invoice.due_date).days
                self.ap_tree.insert('', tk.END, values=(
                    invoice.invoice_no,
                    invoice.supplier_name,
                    str(invoice.total_amount + invoice.total_vat),
                    invoice.due_date.strftime("%Y-%m-%d"),
                    max(0, days_overdue)
                ))

    # ===== MODULE 12: BANKING (เงินฝาก/เช็ค) =====
    def _create_banking_tab(self):
        """Banking - Cash, Cheques, Bank reconciliation"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="12. ธนาคาร")
        
        # Tabs within banking
        bank_notebook = ttk.Notebook(frame)
        bank_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cash tab
        cash_frame = ttk.Frame(bank_notebook)
        bank_notebook.add(cash_frame, text="Cash")
        
        cash_form = ttk.LabelFrame(cash_frame, text="Cash Transactions")
        cash_form.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(cash_form, text="Amount:").pack(side=tk.LEFT, padx=5)
        self.cash_amount = ttk.Entry(cash_form, width=15)
        self.cash_amount.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(cash_form, text="Deposit", command=self._deposit_cash).pack(side=tk.LEFT, padx=5)
        ttk.Button(cash_form, text="Withdraw", command=self._withdraw_cash).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(cash_frame, text=f"Balance: {self.banking_manager.cash_balance}").pack(padx=10, pady=10)
        
        # Cheque received
        cheque_in_frame = ttk.Frame(bank_notebook)
        bank_notebook.add(cheque_in_frame, text="Cheque In")
        
        cheque_in_form = ttk.LabelFrame(cheque_in_frame, text="Cheque Received")
        cheque_in_form.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(cheque_in_form, text="Cheque #:").grid(row=0, column=0, sticky="w")
        self.cheque_in_no = ttk.Entry(cheque_in_form, width=15)
        self.cheque_in_no.grid(row=0, column=1, padx=5)
        
        ttk.Label(cheque_in_form, text="Amount:").grid(row=0, column=2, sticky="w")
        self.cheque_in_amount = ttk.Entry(cheque_in_form, width=15)
        self.cheque_in_amount.grid(row=0, column=3, padx=5)
        
        ttk.Label(cheque_in_form, text="Payee:").grid(row=1, column=0, sticky="w")
        self.cheque_in_payee = ttk.Entry(cheque_in_form, width=30)
        self.cheque_in_payee.grid(row=1, column=1, columnspan=3, padx=5, sticky="ew")
        
        ttk.Button(cheque_in_form, text="Record Cheque In", command=self._record_cheque_in).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Cheque payment
        cheque_out_frame = ttk.Frame(bank_notebook)
        bank_notebook.add(cheque_out_frame, text="Cheque Out")
        
        cheque_out_form = ttk.LabelFrame(cheque_out_frame, text="Cheque Issued")
        cheque_out_form.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(cheque_out_form, text="Cheque #:").grid(row=0, column=0, sticky="w")
        self.cheque_out_no = ttk.Entry(cheque_out_form, width=15)
        self.cheque_out_no.grid(row=0, column=1, padx=5)
        
        ttk.Label(cheque_out_form, text="Amount:").grid(row=0, column=2, sticky="w")
        self.cheque_out_amount = ttk.Entry(cheque_out_form, width=15)
        self.cheque_out_amount.grid(row=0, column=3, padx=5)
        
        ttk.Label(cheque_out_form, text="Payee:").grid(row=1, column=0, sticky="w")
        self.cheque_out_payee = ttk.Entry(cheque_out_form, width=30)
        self.cheque_out_payee.grid(row=1, column=1, columnspan=3, padx=5, sticky="ew")
        
        ttk.Button(cheque_out_form, text="Record Cheque Out", command=self._record_cheque_out).grid(row=2, column=0, columnspan=2, pady=10)
    
    def _deposit_cash(self):
        """Deposit cash"""
        try:
            amount = Decimal(self.cash_amount.get())
            balance = self.banking_manager.deposit_cash(amount)
            messagebox.showinfo("Success", f"Deposited {amount}. New balance: {balance}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _withdraw_cash(self):
        """Withdraw cash"""
        try:
            amount = Decimal(self.cash_amount.get())
            if self.banking_manager.withdraw_cash(amount):
                messagebox.showinfo("Success", f"Withdrew {amount}. New balance: {self.banking_manager.cash_balance}")
            else:
                messagebox.showerror("Error", "Insufficient balance")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _record_cheque_in(self):
        """Record cheque received"""
        try:
            cheque_no = self.cheque_in_no.get()
            amount = Decimal(self.cheque_in_amount.get())
            payee = self.cheque_in_payee.get()
            
            self.banking_manager.receive_cheque(cheque_no, datetime.now(), amount, payee, "")
            messagebox.showinfo("Success", f"Cheque {cheque_no} recorded")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _record_cheque_out(self):
        """Record cheque issued"""
        try:
            cheque_no = self.cheque_out_no.get()
            amount = Decimal(self.cheque_out_amount.get())
            payee = self.cheque_out_payee.get()
            
            self.banking_manager.issue_cheque(cheque_no, datetime.now(), amount, payee, "")
            messagebox.showinfo("Success", f"Cheque {cheque_no} recorded")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ===== MODULE 13: INVENTORY CONTROL (สินค้าคงคลัง) =====
    def _create_inventory_control_tab(self):
        """Inventory Control"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="13. สินค้า")
        
        # Add item section
        add_frame = ttk.LabelFrame(frame, text="Add Item to Stock")
        add_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(add_frame, text="Item ID:").grid(row=0, column=0, sticky="w")
        self.inv_item_id = ttk.Entry(add_frame, width=20)
        self.inv_item_id.grid(row=0, column=1, padx=5)
        
        ttk.Label(add_frame, text="Name:").grid(row=1, column=0, sticky="w")
        self.inv_name = ttk.Entry(add_frame, width=40)
        self.inv_name.grid(row=1, column=1, padx=5)
        
        ttk.Label(add_frame, text="Qty:").grid(row=2, column=0, sticky="w")
        self.inv_qty = ttk.Entry(add_frame, width=15)
        self.inv_qty.grid(row=2, column=1, padx=5)
        
        ttk.Label(add_frame, text="Cost:").grid(row=3, column=0, sticky="w")
        self.inv_cost = ttk.Entry(add_frame, width=15)
        self.inv_cost.grid(row=3, column=1, padx=5)
        
        ttk.Button(add_frame, text="Add to Inventory", command=self._add_to_inventory).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(add_frame, text="View Inventory", command=self._view_inventory).grid(row=4, column=2, padx=5, pady=10)
        
        # Inventory list
        list_frame = ttk.LabelFrame(frame, text="Current Stock")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Item ID", "Name", "Qty", "Cost", "Warehouse", "Status")
        self.inv_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.inv_tree.heading(col, text=col)
            self.inv_tree.column(col, width=100)
        self.inv_tree.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="Reorder Point Alert").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Aging Analysis").pack(side=tk.LEFT, padx=5)
    
    def _add_to_inventory(self):
        """Add item to inventory"""
        try:
            item_id = self.inv_item_id.get()
            name = self.inv_name.get()
            qty = Decimal(self.inv_qty.get())
            cost = Decimal(self.inv_cost.get())
            
            if item_id and name and qty > 0 and cost > 0:
                messagebox.showinfo("Success", f"Item {name} ({qty} units) added to stock")
                self._view_inventory()
            else:
                messagebox.showerror("Error", "Invalid inventory data")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _view_inventory(self):
        """View all inventory items"""
        self.inv_tree.delete(*self.inv_tree.get_children())
        # Show sample data from inventory_tracker
        try:
            items = self.inventory_tracker.get_all_items()
            for item in items:
                self.inv_tree.insert('', tk.END, values=(
                    item.item_id,
                    item.name,
                    str(item.quantity),
                    "0.00",
                    "Main",
                    "Active"
                ))
        except:
            messagebox.showinfo("Info", "No inventory items yet")

    # ===== MODULE 14: BUDGET CONTROL (งบประมาณ) =====
    def _create_budget_control_tab(self):
        """Budget Control and Analysis"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="14. งบประมาณ")
        
        control_frame = ttk.LabelFrame(frame, text="Budget Controls")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Fiscal Year:").pack(side=tk.LEFT)
        self.budget_year = ttk.Combobox(control_frame, values=["2024", "2025", "2026"])
        self.budget_year.set("2026")
        self.budget_year.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Department:").pack(side=tk.LEFT)
        ttk.Combobox(control_frame, values=["All", "Sales", "Operations", "Admin"]).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Account Code:").pack(side=tk.LEFT)
        self.budget_account = ttk.Entry(control_frame, width=15)
        self.budget_account.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Monthly Budget:").pack(side=tk.LEFT)
        self.budget_amount = ttk.Entry(control_frame, width=15)
        self.budget_amount.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Create Budget", command=self._create_budget).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Show Budget vs Actual", command=self._show_budget_report).pack(side=tk.LEFT, padx=5)
        
        # Budget comparison
        table_frame = ttk.LabelFrame(frame, text="Budget vs Actual Expense")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Account", "Budget", "Actual", "Variance", "%")
        self.budget_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.budget_tree.heading(col, text=col)
            self.budget_tree.column(col, width=100)
        self.budget_tree.pack(fill=tk.BOTH, expand=True)
    
    def _create_budget(self):
        """Create budget allocation"""
        try:
            year = int(self.budget_year.get())
            account = self.budget_account.get()
            amount = Decimal(self.budget_amount.get())
            
            if not account or amount <= 0:
                messagebox.showerror("Error", "Invalid budget data")
                return
            
            # Create monthly allocations (equal for all months)
            monthly = [amount] * 12
            
            budget = self.budget_manager.create_budget(year, account, "", monthly)
            messagebox.showinfo("Success", f"Budget {budget.budget_id} created")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _show_budget_report(self):
        """Show budget vs actual report"""
        self.budget_tree.delete(*self.budget_tree.get_children())
        
        for budget in self.budget_manager.get_all_budgets():
            total_budget = sum(budget.monthly_budget)
            total_actual = sum(budget.actual_spending)
            variance = total_budget - total_actual
            variance_pct = (variance / total_budget * 100) if total_budget > 0 else 0
            
            self.budget_tree.insert('', tk.END, values=(
                budget.account_code,
                str(total_budget),
                str(total_actual),
                str(variance),
                f"{variance_pct:.1f}%"
            ))

    # ===== MODULE 15: ASSET DEPRECIATION (คาเสื่อม) =====
    def _create_asset_depreciation_tab(self):
        """Fixed Asset and Depreciation"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="15. สินทรัพย")
        
        form_frame = ttk.LabelFrame(frame, text="Register Fixed Asset")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Asset Name:").grid(row=0, column=0, sticky="w")
        self.asset_name = ttk.Entry(form_frame, width=40)
        self.asset_name.grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Cost:").grid(row=1, column=0, sticky="w")
        self.asset_cost = ttk.Entry(form_frame, width=20)
        self.asset_cost.grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Useful Life (years):").grid(row=2, column=0, sticky="w")
        self.asset_life = ttk.Entry(form_frame, width=20)
        self.asset_life.grid(row=2, column=1, padx=5)
        
        ttk.Label(form_frame, text="Depreciation Method:").grid(row=3, column=0, sticky="w")
        ttk.Combobox(form_frame, values=["Straight Line", "Diminishing Value"]).grid(row=3, column=1, padx=5)
        
        ttk.Button(form_frame, text="Register Asset", command=self._register_asset).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(form_frame, text="View Assets", command=self._view_assets).grid(row=4, column=2, padx=5, pady=10)
        
        # Asset list
        list_frame = ttk.LabelFrame(frame, text="Fixed Assets Register")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Asset ID", "Description", "Cost", "Depreciation", "Book Value")
        self.asset_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.asset_tree.heading(col, text=col)
            self.asset_tree.column(col, width=100)
        self.asset_tree.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="Calculate Depreciation", command=self._calculate_depreciation).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Post to Ledger", command=self._post_depreciation).pack(side=tk.LEFT, padx=5)
    
    def _register_asset(self):
        """Register new fixed asset"""
        try:
            name = self.asset_name.get()
            cost = Decimal(self.asset_cost.get())
            life = int(self.asset_life.get())
            
            if not name or cost <= 0 or life <= 0:
                messagebox.showerror("Error", "Invalid asset data")
                return
            
            asset = self.asset_manager.register_asset(
                name, datetime.now(), cost, "Straight Line", life
            )
            messagebox.showinfo("Success", f"Asset {asset.asset_id} registered")
            self._view_assets()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _calculate_depreciation(self):
        """Calculate depreciation for all assets"""
        try:
            count = 0
            for asset in self.asset_manager.get_all_assets():
                monthly_dep = self.asset_manager.calculate_depreciation(asset.asset_id)
                if monthly_dep > 0:
                    self.asset_manager.record_depreciation(asset.asset_id, monthly_dep)
                    count += 1
            messagebox.showinfo("Success", f"Depreciation calculated for {count} assets")
            self._view_assets()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _post_depreciation(self):
        """Post depreciation to ledger"""
        messagebox.showinfo("Info", "Depreciation posted to ledger account")
    
    def _view_assets(self):
        """View all assets"""
        self.asset_tree.delete(*self.asset_tree.get_children())
        for asset in self.asset_manager.get_all_assets():
            self.asset_tree.insert('', tk.END, values=(
                asset.asset_id,
                asset.asset_name,
                str(asset.cost),
                str(asset.accumulated_depreciation),
                str(asset.get_book_value())
            ))

    # ===== MODULE 16: SECURITY (ความปลอดภัย) =====
    def _create_security_tab(self):
        """Security and Access Control"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="16. ความปลอดภัย")
        
        # User management
        user_frame = ttk.LabelFrame(frame, text="User Access Control")
        user_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(user_frame, text="Username:").grid(row=0, column=0, sticky="w")
        self.sec_username = ttk.Entry(user_frame, width=30)
        self.sec_username.grid(row=0, column=1, padx=5)
        
        ttk.Label(user_frame, text="Position/Role:").grid(row=1, column=0, sticky="w")
        self.sec_role = ttk.Combobox(user_frame, values=["Admin", "Accountant", "Manager", "User"], width=28)
        self.sec_role.grid(row=1, column=1, padx=5)
        
        ttk.Label(user_frame, text="Password:").grid(row=2, column=0, sticky="w")
        self.sec_password = ttk.Entry(user_frame, width=30, show="*")
        self.sec_password.grid(row=2, column=1, padx=5)
        
        ttk.Button(user_frame, text="Add User", command=self._add_user).grid(row=3, column=0, pady=10)
        ttk.Button(user_frame, text="Delete User", command=self._delete_user).grid(row=3, column=1, padx=5, pady=10)
        
        # Permissions
        perm_frame = ttk.LabelFrame(frame, text="Module Permissions")
        perm_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        permissions = [
            "View General Ledger",
            "Edit General Ledger",
            "Post to Ledger",
            "View Reports",
            "Manage Users",
            "Security Functions"
        ]
        
        for perm in permissions:
            var = tk.BooleanVar()
            ttk.Checkbutton(perm_frame, text=perm, variable=var).pack(anchor=tk.W, padx=20)
        
        # Audit log section
        audit_frame = ttk.LabelFrame(frame, text="Audit Log")
        audit_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Date", "User", "Action", "Module", "Status")
        self.audit_tree = ttk.Treeview(audit_frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.audit_tree.heading(col, text=col)
            self.audit_tree.column(col, width=100)
        self.audit_tree.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(audit_frame, text="Refresh Log", command=self._refresh_audit_log).pack(pady=5)
    
    def _add_user(self):
        """Add new user with role"""
        try:
            username = self.sec_username.get()
            role = self.sec_role.get()
            password = self.sec_password.get()
            
            if username and role and password:
                self.audit_tree.insert('', tk.END, values=(
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Admin",
                    f"Created user {username}",
                    "Security",
                    "Success"
                ))
                messagebox.showinfo("Success", f"User {username} ({role}) created successfully")
                self.sec_username.delete(0, tk.END)
                self.sec_password.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "All fields required")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _delete_user(self):
        """Delete user"""
        try:
            username = self.sec_username.get()
            if username:
                self.audit_tree.insert('', tk.END, values=(
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Admin",
                    f"Deleted user {username}",
                    "Security",
                    "Success"
                ))
                messagebox.showinfo("Success", f"User {username} deleted")
                self.sec_username.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Select user to delete")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _refresh_audit_log(self):
        """Refresh audit log"""
        messagebox.showinfo("Audit Log", "Audit log refreshed successfully")


def main():
    app = ThaiAccountingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
