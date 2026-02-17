# Thai Accounting System - Web & Desktop Versions

## 🚀 การใช้งาน (How to Use)

### **Option 1: Desktop Version (Tkinter) - GUI ฟังก์ชันมากมาย**

```bash
# Method 1: Run as module
python -m src.app

# Method 2: Run directly
python src/app.py
```

**ข้อดี:**
- ✅ ครบถ้วนทั้ง 16 modules
- ✅ ตัวเลขและการคำนวณติดตั้งแบบ offline
- ✅ ไม่ต้องเว็บ server
- ✅ ด้านลึก UI สำหรับ desktop

**ข้อเสีย:**
- ❌ ต้องติดตั้ง Python
- ❌ ต้องมี display/monitor

---

### **Option 2: Web Version (Flask) - ใช้ผ่าน Browser ได้ที่ไหนก็ได้**

```bash
# Install Flask (if not already installed)
pip install flask flask-cors

# Run web server
python -m src.web_app
```

**เข้าถึง:** http://localhost:5000

**ข้อดี:**
- ✅ ใช้ผ่าน browser ทั่วไป
- ✅ Deploy ได้ที่ไหนก็ได้ (cloud, server)
- ✅ Multiple users ใช้พร้อมกันได้
- ✅ Modern web interface
- ✅ ไม่ต้องติดตั้งบนแต่ละ PC

**ข้อเสีย:**
- ❌ ต้องมี web server
- ❌ Modules บางส่วนยังอยู่ระหว่างสร้าง

---

### **Option 3: PyInstaller Executable - ส่งให้คนอื่นใช้ได้เลย**

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --name "ThaiAccountingSystem" src/app.py

# Executable จะอยู่ใน: dist/ThaiAccountingSystem.exe (บน Windows)
```

**ข้อดี:**
- ✅ ส่งให้คนอื่นใช้ได้เลย
- ✅ ไม่ต้อง Python บนเครื่องอื่น
- ✅ ดับเบิลคลิกเรียกใช้ได้เลย

---

### **Option 4: Deploy บน Cloud (Heroku, PythonAnywhere, Render)**

#### **Heroku:**
```bash
pip install gunicorn
echo "gunicorn --bind 0.0.0.0 src.web_app:app" > Procfile
echo "flask==3.1.2" > requirements.txt
heroku create thai-accounting-system
git push heroku main
```

#### **PythonAnywhere:**
1. Sign up: https://www.pythonanywhere.com
2. Upload code
3. Configure Web app
4. Done! Access: `your-username.pythonanywhere.com`

#### **Docker + Deployment:**
```bash
docker build -t thai-accounting .
docker run -p 5000:5000 thai-accounting
```

---

## 📋 API Endpoints (สำหรับ Web Version)

### **Dashboard**
- `GET /` - Dashboard หลัก
- `GET /stats` - Statistics (sales, purchases, balance)

### **General Ledger (Module 1)**
- `POST /api/ledger/entries` - Add ledger entry
- `POST /api/ledger/post` - Post voucher
- `GET /api/ledger/trial-balance` - Get trial balance

### **Sales Invoices (Module 4)**
- `GET /api/sales/invoices` - List all invoices
- `POST /api/sales/invoices` - Create invoice

### **Purchase Orders (Module 6)**
- `GET /api/purchase-orders` - List all POs
- `POST /api/purchase-orders` - Create PO

### **VAT/Tax (Module 9)**
- `GET /api/tax/report` - Get tax report

### **Accounts Receivable (Module 10)**
- `GET /api/ar/outstanding` - Outstanding AR
- `POST /api/ar/payment` - Record payment

### **Banking (Module 12)**
- `GET /api/banking/balance` - Cash balance
- `POST /api/banking/deposit` - Deposit cash
- `POST /api/banking/withdraw` - Withdraw cash

### **Fixed Assets (Module 15)**
- `GET /api/assets` - List assets
- `POST /api/assets` - Register asset

---

## 🔐 การเลือกเวอร์ชัน (Version Comparison)

| Feature | Desktop | Web | Executable |
|---------|---------|-----|------------|
| 16 Modules | ✅ | ⏳ | ✅ |
| Offline | ✅ | ❌ | ✅ |
| Share Easy | ❌ | ✅ | ✅ |
| Multiple Users | ❌ | ✅ | ❌ |
| Cloud Deploy | ❌ | ✅ | ❌ |
| Setup Required | Python + display | Python + Flask | None |

---

## 🎯 แนะนำการใช้

**สำหรับบ้าน/ออฟฟิศเล็ก:**
→ ใช้ Desktop version (Option 1)

**สำหรับ Multiple Users/Team:**
→ ใช้ Web version (Option 2) บน local server หรือ cloud

**สำหรับส่งให้คนอื่น:**
→ ใช้ Executable (Option 3)

**สำหรับ Deploy Global:**
→ ใช้ Web version บน Heroku/PythonAnywhere (Option 4)

---

## 🐛 Troubleshooting

### Web version ไม่เข้าได้
```bash
# ลอง simulate localhost:5000
python -m src.web_app
# แล้วเปิด http://localhost:5000 ในบราวเซอร์
```

### Import errors
```bash
# ลองรันแบบนี้
cd /workspaces/warehouse-management-system
python -m src.web_app
```

### Display errors (Desktop)
```bash
# ต้องมี DISPLAY variable
export DISPLAY=:99
python -m src.app
```

---

## 📝 Notes

- **Data Persistence:** ขณะนี้ data เก็บใน memory เท่านั้น
- **Database:** ต่อไปจะเพิ่ม SQLite/PostgreSQL
- **Thai Language:** ✅ Support แล้ว (UI + calculations)
- **Modules 13, 16:** Inventory & Security อยู่ระหว่างพัฒนา

---

**ต้องการขึ้น Web ได้ไหม?** ✅ **ได้เลย! ใช้ Option 2 หรือ 4** 🚀
