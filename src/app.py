import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime
from decimal import Decimal

from .event_bus import EventBus
from .agents.inventory_tracker import InventoryTracker
from .agents.order_processor import OrderProcessor
from .agents.agv_controller import AGVController
from .agents.rfid_sensor import RFIDSensor
from .agents.alert_system import AlertSystem

from .events import order_events as ord_ev
from .events import inventory_events as inv_ev
from .events import alert_events as al_ev


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
        ttk.Entry(input_frame, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Date:").grid(row=0, column=2, sticky="w", padx=5)
        ttk.Entry(input_frame, width=15).grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="Description:").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Entry(input_frame, width=80).grid(row=1, column=1, columnspan=3, padx=5, sticky="ew")
        
        # Debit/Credit table
        table_frame = ttk.LabelFrame(frame, text="Ledger Entries (up to 9,999 items per voucher)")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Account", "Debit", "Credit", "Description")
        self.gl_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.gl_tree.heading(col, text=col)
        self.gl_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="Add Entry").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Entry").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Post to Ledger").pack(side=tk.LEFT, padx=5)

    # ===== MODULE 2: SERVICE BUSINESS (ธุรกิจบริการ) =====
    def _create_service_business_tab(self):
        """Service Business Operations"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="2. ธุรกิจบริการ")
        
        info = ttk.Label(frame, text="Service Business Module\n"
                        "- Service Invoice Management\n"
                        "- Customer Service Billing\n"
                        "- Time and Material Tracking")
        info.pack(padx=10, pady=10)
        
        # Input form
        form_frame = ttk.LabelFrame(frame, text="Service Invoice")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Service ID:").grid(row=0, column=0, sticky="w")
        ttk.Entry(form_frame).grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Customer:").grid(row=1, column=0, sticky="w")
        ttk.Entry(form_frame).grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Service Description:").grid(row=2, column=0, sticky="w")
        ttk.Entry(form_frame, width=50).grid(row=2, column=1, padx=5, sticky="ew")

    # ===== MODULE 3: SALES ORDER (ใบสั่งขาย/ใบรับจองสินคา) =====
    def _create_sales_order_tab(self):
        """Sales Order - Entry and tracking"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="3. ใบสั่งขาย")
        
        # Search and filter
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Search Customer:").pack(side=tk.LEFT)
        ttk.Entry(filter_frame, width=30).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Search").pack(side=tk.LEFT)
        
        # Sales orders list
        list_frame = ttk.LabelFrame(frame, text="Sales Orders")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Order#", "Customer", "Date", "Amount", "Status")
        so_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            so_tree.heading(col, text=col)
        so_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="New Order").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Partial Delivery").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel Order").pack(side=tk.LEFT, padx=5)

    # ===== MODULE 4: SALES INVOICE (ใบเสร็จ/ใบกํากับภาษี) =====
    def _create_sales_invoice_tab(self):
        """Sales Invoice - Generate and manage invoices"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="4. ใบเสร็จ")
        
        form_frame = ttk.LabelFrame(frame, text="Sales Invoice Entry")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Invoice #:").grid(row=0, column=0, sticky="w")
        ttk.Entry(form_frame, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Customer:").grid(row=1, column=0, sticky="w")
        ttk.Entry(form_frame, width=40).grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Item:").grid(row=2, column=0, sticky="w")
        ttk.Entry(form_frame, width=40).grid(row=2, column=1, padx=5)
        
        ttk.Label(form_frame, text="Quantity/Unit Price/Discount:").grid(row=3, column=0, sticky="w")
        ttk.Entry(form_frame, width=40).grid(row=3, column=1, padx=5)
        
        ttk.Label(form_frame, text="VAT Rate:").grid(row=4, column=0, sticky="w")
        vat_var = tk.StringVar(value="7%")
        ttk.Combobox(form_frame, textvariable=vat_var, values=["7%", "10%", "0%", "Exempt"]).grid(row=4, column=1, padx=5)
        
        ttk.Button(form_frame, text="Generate Invoice").grid(row=5, column=0, columnspan=2, pady=10)

    # ===== MODULE 5: SALES ANALYSIS (วิเคราะห์การขาย) =====
    def _create_sales_analysis_tab(self):
        """Sales Analysis - Reports and metrics"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="5. ประเมิน") 
        
        control_frame = ttk.LabelFrame(frame, text="Sales Report Controls")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Report Type:").pack(side=tk.LEFT)
        report_type = tk.StringVar(value="Daily")
        ttk.Combobox(control_frame, textvariable=report_type, 
                    values=["Daily", "Weekly", "Monthly", "Annual"]).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Period:").pack(side=tk.LEFT)
        ttk.Entry(control_frame, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Generate Report").pack(side=tk.LEFT, padx=5)
        
        # Results
        result_frame = ttk.LabelFrame(frame, text="Sales Summary")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Product", "Qty", "Amount", "Profit", "Profit%")
        analysis_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        for col in columns:
            analysis_tree.heading(col, text=col)
        analysis_tree.pack(fill=tk.BOTH, expand=True)

    # ===== MODULE 6: PURCHASE ORDER (ใบสั่งซื้อ) =====
    def _create_purchase_order_tab(self):
        """Purchase Order Management"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="6. PO")
        
        form_frame = ttk.LabelFrame(frame, text="Purchase Order Entry")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="PO #:").grid(row=0, column=0, sticky="w")
        ttk.Entry(form_frame, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Supplier:").grid(row=1, column=0, sticky="w")
        ttk.Entry(form_frame, width=40).grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Item:").grid(row=2, column=0, sticky="w")
        ttk.Entry(form_frame, width=40).grid(row=2, column=1, padx=5)
        
        ttk.Label(form_frame, text="Qty/Unit Price:").grid(row=3, column=0, sticky="w")
        ttk.Entry(form_frame, width=40).grid(row=3, column=1, padx=5)
        
        # Order list
        list_frame = ttk.LabelFrame(frame, text="Purchase Orders")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("PO#", "Supplier", "Date", "Amount", "Received")
        po_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            po_tree.heading(col, text=col)
        po_tree.pack(fill=tk.BOTH, expand=True)

    # ===== MODULE 7: PURCHASES (จัดซื้อ) =====
    def _create_purchases_tab(self):
        """Purchase Management - Invoice entry"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="7. ซื้อ")
        
        form_frame = ttk.LabelFrame(frame, text="Purchase Invoice Entry")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Invoice #:").grid(row=0, column=0, sticky="w")
        ttk.Entry(form_frame, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Supplier:").grid(row=1, column=0, sticky="w")
        ttk.Entry(form_frame, width=40).grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Invoice Date:").grid(row=2, column=0, sticky="w")
        ttk.Entry(form_frame, width=20).grid(row=2, column=1, padx=5)
        
        ttk.Label(form_frame, text="Total Amount:").grid(row=3, column=0, sticky="w")
        ttk.Entry(form_frame, width=20).grid(row=3, column=1, padx=5)

    # ===== MODULE 8: PURCHASE ANALYSIS (วิเคราะห์การซื้อ) =====
    def _create_purchase_analysis_tab(self):
        """Purchase Analysis"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="8. วิเค ซื้อ")
        
        control_frame = ttk.LabelFrame(frame, text="Purchase Report")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Period:").pack(side=tk.LEFT)
        ttk.Entry(control_frame, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Generate Report").pack(side=tk.LEFT, padx=5)
        
        result_frame = ttk.LabelFrame(frame, text="Purchase Summary by Supplier")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Supplier", "Qty", "Amount", "12-Month Comp")
        analysis_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        for col in columns:
            analysis_tree.heading(col, text=col)
        analysis_tree.pack(fill=tk.BOTH, expand=True)

    # ===== MODULE 9: VAT/WITHHOLDING TAX (ภาษี) =====
    def _create_vat_tax_tab(self):
        """VAT and Withholding Tax Management"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="9. ภาษี")
        
        control_frame = ttk.LabelFrame(frame, text="Tax Report Period")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Month/Year:").pack(side=tk.LEFT)
        ttk.Entry(control_frame, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Tax Type:").pack(side=tk.LEFT)
        ttk.Combobox(control_frame, values=["Purchase Tax", "Sales Tax", "Withholding", "Summary"]).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Generate Tax Report").pack(side=tk.LEFT, padx=5)
        
        result_frame = ttk.LabelFrame(frame, text="Tax Summary")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Description", "Amount", "Tax Rate", "Tax Amount")
        tax_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        for col in columns:
            tax_tree.heading(col, text=col)
        tax_tree.pack(fill=tk.BOTH, expand=True)

    # ===== MODULE 10: ACCOUNTS RECEIVABLE (ลูกหนี้) =====
    def _create_accounts_receivable_tab(self):
        """Accounts Receivable - Customer debts"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="10. ลูกหนี้")
        
        form_frame = ttk.LabelFrame(frame, text="Receipt Entry")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Customer:").grid(row=0, column=0, sticky="w")
        ttk.Entry(form_frame, width=40).grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Received Amount:").grid(row=1, column=0, sticky="w")
        ttk.Entry(form_frame, width=20).grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Payment Method:").grid(row=2, column=0, sticky="w")
        ttk.Combobox(form_frame, values=["Cash", "Cheque", "Bank Transfer", "Credit Card"]).grid(row=2, column=1, padx=5)
        
        # Outstanding invoices
        list_frame = ttk.LabelFrame(frame, text="Outstanding Invoices")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Invoice", "Customer", "Amount", "Due Date", "Days Overdue")
        ar_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            ar_tree.heading(col, text=col)
        ar_tree.pack(fill=tk.BOTH, expand=True)

    # ===== MODULE 11: ACCOUNTS PAYABLE (เจ้าหนี้) =====
    def _create_accounts_payable_tab(self):
        """Accounts Payable - Supplier debts"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="11. เจ้าหนี้")
        
        form_frame = ttk.LabelFrame(frame, text="Payment Entry")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Supplier:").grid(row=0, column=0, sticky="w")
        ttk.Entry(form_frame, width=40).grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Payment Amount:").grid(row=1, column=0, sticky="w")
        ttk.Entry(form_frame, width=20).grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Payment Method:").grid(row=2, column=0, sticky="w")
        ttk.Combobox(form_frame, values=["Cash", "Cheque", "Bank Transfer", "Draft"]).grid(row=2, column=1, padx=5)
        
        # Outstanding payables
        list_frame = ttk.LabelFrame(frame, text="Outstanding Bills")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Invoice", "Supplier", "Amount", "Due Date", "Days Overdue")
        ap_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            ap_tree.heading(col, text=col)
        ap_tree.pack(fill=tk.BOTH, expand=True)

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
        ttk.Label(cash_frame, text="Cash transactions and deposits").pack(padx=10, pady=10)
        
        # Cheque received
        cheque_in_frame = ttk.Frame(bank_notebook)
        bank_notebook.add(cheque_in_frame, text="Cheque In")
        ttk.Label(cheque_in_frame, text="Cheques received from customers").pack(padx=10, pady=10)
        
        # Cheque payment
        cheque_out_frame = ttk.Frame(bank_notebook)
        bank_notebook.add(cheque_out_frame, text="Cheque Out")
        ttk.Label(cheque_out_frame, text="Cheques issued to suppliers").pack(padx=10, pady=10)
        
        # Bank reconciliation
        reconcile_frame = ttk.Frame(bank_notebook)
        bank_notebook.add(reconcile_frame, text="Reconciliation")
        ttk.Label(reconcile_frame, text="Bank statement reconciliation").pack(padx=10, pady=10)

    # ===== MODULE 13: INVENTORY CONTROL (สินค้าคงคลัง) =====
    def _create_inventory_control_tab(self):
        """Inventory Control"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="13. สินค้า")
        
        # Add item section
        add_frame = ttk.LabelFrame(frame, text="Add Item to Stock")
        add_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(add_frame, text="Item ID:").grid(row=0, column=0, sticky="w")
        ttk.Entry(add_frame, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(add_frame, text="Name:").grid(row=1, column=0, sticky="w")
        ttk.Entry(add_frame, width=40).grid(row=1, column=1, padx=5)
        
        ttk.Label(add_frame, text="Qty / Cost / Selling Price:").grid(row=2, column=0, sticky="w")
        ttk.Entry(add_frame, width=40).grid(row=2, column=1, padx=5)
        
        ttk.Label(add_frame, text="Warehouse:").grid(row=3, column=0, sticky="w")
        ttk.Combobox(add_frame, values=["Warehouse 1", "Warehouse 2"]).grid(row=3, column=1, padx=5)
        
        # Inventory list
        list_frame = ttk.LabelFrame(frame, text="Current Stock")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Item ID", "Name", "Qty", "Cost", "Warehouse", "Status")
        inv_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            inv_tree.heading(col, text=col)
        inv_tree.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="Reorder Point Alert").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Aging Analysis").pack(side=tk.LEFT, padx=5)

    # ===== MODULE 14: BUDGET CONTROL (งบประมาณ) =====
    def _create_budget_control_tab(self):
        """Budget Control and Analysis"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="14. งบประมาณ")
        
        control_frame = ttk.LabelFrame(frame, text="Budget Controls")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Fiscal Year:").pack(side=tk.LEFT)
        ttk.Combobox(control_frame, values=["2024", "2025", "2026"]).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Department:").pack(side=tk.LEFT)
        ttk.Combobox(control_frame, values=["All", "Sales", "Operations", "Admin"]).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Show Budget vs Actual").pack(side=tk.LEFT, padx=5)
        
        # Budget comparison
        table_frame = ttk.LabelFrame(frame, text="Budget vs Actual Expense")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Account", "Budget", "Actual", "Variance", "%")
        budget_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            budget_tree.heading(col, text=col)
        budget_tree.pack(fill=tk.BOTH, expand=True)

    # ===== MODULE 15: ASSET DEPRECIATION (คาเสื่อม) =====
    def _create_asset_depreciation_tab(self):
        """Fixed Asset and Depreciation"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="15. สินทรัพย")
        
        form_frame = ttk.LabelFrame(frame, text="Register Fixed Asset")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Asset ID:").grid(row=0, column=0, sticky="w")
        ttk.Entry(form_frame, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, sticky="w")
        ttk.Entry(form_frame, width=50).grid(row=1, column=1, padx=5)
        
        ttk.Label(form_frame, text="Purchase Date:").grid(row=2, column=0, sticky="w")
        ttk.Entry(form_frame, width=20).grid(row=2, column=1, padx=5)
        
        ttk.Label(form_frame, text="Cost / Depreciation Method:").grid(row=3, column=0, sticky="w")
        ttk.Entry(form_frame, width=50).grid(row=3, column=1, padx=5)
        
        # Asset list
        list_frame = ttk.LabelFrame(frame, text="Fixed Assets Register")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Asset ID", "Description", "Cost", "Depreciation", "Book Value")
        asset_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            asset_tree.heading(col, text=col)
        asset_tree.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="Calculate Depreciation").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Post to Ledger").pack(side=tk.LEFT, padx=5)

    # ===== MODULE 16: SECURITY (ความปลอดภัย) =====
    def _create_security_tab(self):
        """Security and Access Control"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="16. ความปลอดภัย")
        
        # User management
        user_frame = ttk.LabelFrame(frame, text="User Access Control")
        user_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(user_frame, text="Username:").grid(row=0, column=0, sticky="w")
        ttk.Entry(user_frame, width=30).grid(row=0, column=1, padx=5)
        
        ttk.Label(user_frame, text="Position/Role:").grid(row=1, column=0, sticky="w")
        ttk.Combobox(user_frame, values=["Admin", "Accountant", "Manager", "User"]).grid(row=1, column=1, padx=5)
        
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


def main():
    app = ThaiAccountingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
