"""
Flask Web Application for Thai Accounting System
Run: python -m src.web_app
Access: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from decimal import Decimal
import json
import os
import sys

# Handle imports
try:
    from .event_bus import EventBus
    from .agents.general_ledger import GeneralLedgerAgent
    from .agents.sales_manager import SalesManager
    from .agents.purchase_manager import PurchaseManager
    from .agents.accounting_managers import (
        TaxManager, BankingManager, AssetManager, BudgetManager
    )
    from .models.accounting import VATType
except ImportError:
    from src.event_bus import EventBus
    from src.agents.general_ledger import GeneralLedgerAgent
    from src.agents.sales_manager import SalesManager
    from src.agents.purchase_manager import PurchaseManager
    from src.agents.accounting_managers import (
        TaxManager, BankingManager, AssetManager, BudgetManager
    )
    from src.models.accounting import VATType

# Initialize Flask app
app = Flask(__name__, 
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
)
CORS(app)

# Initialize accounting managers
event_bus = EventBus()
general_ledger = GeneralLedgerAgent(event_bus)
sales_manager = SalesManager(event_bus)
purchase_manager = PurchaseManager(event_bus)
tax_manager = TaxManager(event_bus)
banking_manager = BankingManager(event_bus)
asset_manager = AssetManager(event_bus)
budget_manager = BudgetManager(event_bus)


# ===== WEB ROUTES =====

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')


@app.route('/stats')
def stats():
    """Get dashboard statistics"""
    try:
        sales_invoices = sales_manager.get_all_invoices()
        purchase_invoices = list(purchase_manager.invoices.values())
        
        total_sales = sum(inv.total_amount + inv.total_vat for inv in sales_invoices)
        total_purchases = sum(inv.total_amount + inv.total_vat for inv in purchase_invoices)
        outstanding_ar = sum(inv.total_amount + inv.total_vat for inv in sales_invoices 
                            if inv.status.value != "Paid")
        outstanding_ap = sum(inv.total_amount + inv.total_vat for inv in purchase_invoices 
                            if inv.status.value != "Paid")
        
        return jsonify({
            'total_sales': str(total_sales),
            'total_purchases': str(total_purchases),
            'outstanding_ar': str(outstanding_ar),
            'outstanding_ap': str(outstanding_ap),
            'cash_balance': str(banking_manager.cash_balance)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ===== MODULE 1: GENERAL LEDGER =====

@app.route('/api/ledger/entries', methods=['POST'])
def add_ledger_entry():
    """Add general ledger entry"""
    try:
        data = request.json
        voucher_no = data.get('voucher_no')
        account_code = data.get('account_code')
        debit = Decimal(data.get('debit', 0))
        credit = Decimal(data.get('credit', 0))
        description = data.get('description', '')
        
        entry = general_ledger.add_entry(voucher_no, account_code, debit, credit, description)
        return jsonify({'message': 'Entry added', 'entry_id': entry.entry_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/ledger/post', methods=['POST'])
def post_ledger():
    """Post voucher to ledger"""
    try:
        data = request.json
        voucher_no = data.get('voucher_no')
        
        if general_ledger.post_voucher(voucher_no):
            return jsonify({'message': 'Voucher posted successfully'})
        else:
            return jsonify({'error': 'Voucher not balanced'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/ledger/trial-balance')
def get_trial_balance():
    """Get trial balance"""
    try:
        tb = general_ledger.get_trial_balance()
        return jsonify(tb)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ===== MODULE 4: SALES INVOICES =====

@app.route('/api/sales/invoices', methods=['GET'])
def get_sales_invoices():
    """Get all sales invoices"""
    try:
        invoices = sales_manager.get_all_invoices()
        data = []
        for inv in invoices:
            data.append({
                'invoice_no': inv.invoice_no,
                'customer_id': inv.customer_id,
                'customer_name': inv.customer_name,
                'invoice_date': inv.invoice_date.strftime('%Y-%m-%d'),
                'total_amount': str(inv.total_amount),
                'total_vat': str(inv.total_vat),
                'total': str(inv.total_amount + inv.total_vat),
                'status': inv.status.value
            })
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/sales/invoices', methods=['POST'])
def create_sales_invoice():
    """Create sales invoice"""
    try:
        data = request.json
        customer_id = data.get('customer_id')
        customer_name = data.get('customer_name')
        
        # Create customer if needed
        customer = sales_manager.create_customer(customer_id, customer_name, "", "")
        
        # Create invoice
        invoice = sales_manager.create_invoice(
            customer_id,
            datetime.now(),
            datetime.now() + timedelta(days=30),
            VATType.INCLUDED
        )
        
        # Add items
        items = data.get('items', [])
        for item in items:
            sales_manager.add_item_to_invoice(
                invoice.invoice_no,
                item['item_id'],
                item['item_name'],
                Decimal(item['quantity']),
                Decimal(item['unit_price']),
                Decimal(item.get('discount', 0)),
                Decimal(item.get('vat_rate', 7))
            )
        
        return jsonify({
            'invoice_no': invoice.invoice_no,
            'total': str(invoice.total_amount + invoice.total_vat)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ===== MODULE 6: PURCHASE ORDERS =====

@app.route('/api/purchase-orders', methods=['GET'])
def get_purchase_orders():
    """Get all purchase orders"""
    try:
        pos = purchase_manager.purchase_orders
        data = []
        for po in pos.values():
            data.append({
                'po_no': po.po_no,
                'supplier_id': po.supplier_id,
                'supplier_name': po.supplier_name,
                'order_date': po.order_date.strftime('%Y-%m-%d'),
                'total_amount': str(po.total_amount),
                'status': po.status
            })
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/purchase-orders', methods=['POST'])
def create_purchase_order():
    """Create purchase order"""
    try:
        data = request.json
        supplier_id = data.get('supplier_id')
        supplier_name = data.get('supplier_name')
        
        # Create supplier if needed
        supplier = purchase_manager.create_supplier(supplier_id, supplier_name, "", "")
        
        # Create PO
        po = purchase_manager.create_purchase_order(
            supplier_id,
            datetime.now(),
            datetime.now() + timedelta(days=30)
        )
        
        # Add items
        items = data.get('items', [])
        for item in items:
            purchase_manager.add_item_to_po(
                po.po_no,
                item['item_id'],
                item['item_name'],
                Decimal(item['quantity']),
                Decimal(item['unit_price'])
            )
        
        return jsonify({
            'po_no': po.po_no,
            'total': str(po.total_amount)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ===== MODULE 9: VAT/TAX =====

@app.route('/api/tax/report', methods=['GET'])
def get_tax_report():
    """Get tax report"""
    try:
        from_date = request.args.get('from_date', 
                                     (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        to_date = request.args.get('to_date', datetime.now().strftime('%Y-%m-%d'))
        
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')
        
        total_sales_vat = Decimal('0')
        total_purchase_vat = Decimal('0')
        
        for invoice in sales_manager.get_all_invoices():
            if from_date <= invoice.invoice_date <= to_date:
                total_sales_vat += invoice.total_vat
        
        for invoice in purchase_manager.invoices.values():
            if from_date <= invoice.invoice_date <= to_date:
                total_purchase_vat += invoice.total_vat
        
        net_vat = total_sales_vat - total_purchase_vat
        
        return jsonify({
            'sales_vat': str(total_sales_vat),
            'purchase_vat': str(total_purchase_vat),
            'net_vat': str(net_vat),
            'vat_payable': str(net_vat) if net_vat > 0 else '0'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ===== MODULE 10: ACCOUNTS RECEIVABLE =====

@app.route('/api/ar/outstanding', methods=['GET'])
def get_outstanding_ar():
    """Get outstanding customer invoices"""
    try:
        customer_id = request.args.get('customer_id')
        invoices = sales_manager.get_outstanding_invoices(customer_id) if customer_id else []
        
        data = []
        for inv in invoices:
            days_overdue = (datetime.now() - inv.due_date).days
            data.append({
                'invoice_no': inv.invoice_no,
                'customer_name': inv.customer_name,
                'amount': str(inv.total_amount + inv.total_vat),
                'due_date': inv.due_date.strftime('%Y-%m-%d'),
                'days_overdue': max(0, days_overdue)
            })
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/ar/payment', methods=['POST'])
def record_ar_payment():
    """Record customer payment"""
    try:
        data = request.json
        customer_id = data.get('customer_id')
        amount = Decimal(data.get('amount'))
        
        invoices = sales_manager.get_outstanding_invoices(customer_id)
        if not invoices:
            return jsonify({'error': 'No outstanding invoices'}), 400
        
        if sales_manager.record_payment(invoices[0].invoice_no, amount):
            return jsonify({'message': 'Payment recorded successfully'})
        else:
            return jsonify({'error': 'Payment amount insufficient'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ===== MODULE 12: BANKING =====

@app.route('/api/banking/balance', methods=['GET'])
def get_cash_balance():
    """Get cash balance"""
    return jsonify({'balance': str(banking_manager.cash_balance)})


@app.route('/api/banking/deposit', methods=['POST'])
def deposit_cash():
    """Deposit cash"""
    try:
        data = request.json
        amount = Decimal(data.get('amount'))
        balance = banking_manager.deposit_cash(amount)
        return jsonify({'message': 'Deposited', 'balance': str(balance)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/banking/withdraw', methods=['POST'])
def withdraw_cash():
    """Withdraw cash"""
    try:
        data = request.json
        amount = Decimal(data.get('amount'))
        
        if banking_manager.withdraw_cash(amount):
            return jsonify({'message': 'Withdrawn', 'balance': str(banking_manager.cash_balance)})
        else:
            return jsonify({'error': 'Insufficient balance'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ===== MODULE 15: ASSET DEPRECIATION =====

@app.route('/api/assets', methods=['GET'])
def get_assets():
    """Get all fixed assets"""
    try:
        assets = asset_manager.get_all_assets()
        data = []
        for asset in assets:
            data.append({
                'asset_id': asset.asset_id,
                'asset_name': asset.asset_name,
                'cost': str(asset.cost),
                'accumulated_depreciation': str(asset.accumulated_depreciation),
                'book_value': str(asset.get_book_value())
            })
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/assets', methods=['POST'])
def register_asset():
    """Register fixed asset"""
    try:
        data = request.json
        asset = asset_manager.register_asset(
            data.get('asset_name'),
            datetime.now(),
            Decimal(data.get('cost')),
            'Straight Line',
            int(data.get('useful_life', 5))
        )
        return jsonify({'asset_id': asset.asset_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🌐 Thai Accounting System - Web Version")
    print("=" * 60)
    print("\n📱 Starting web server...")
    print("🔗 Access: http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
