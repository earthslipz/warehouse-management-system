# Thai Accounting System - Deployment Guide

## ถ้าเอาขึ้นเว็บ ทำไง?

ได้! ✅ มี Flask web version แล้ว!

---

## ⚡ Quick Start (เฉพาะ Web Version)

```bash
# 1. ติดตั้ง Flask
pip install flask flask-cors

# 2. รัน web server
python -m src.web_app

# 3. เปิด browser เข้า
# http://localhost:5000
```

**Done!** ✨

---

## 🌐 ตัวเลือกในการ Deploy (Deployment Options)

### **Option 1: PyInstaller - Desktop Executable (ง่ายที่สุด for Desktop)**
แพ็คเจจ app เป็น .exe หรือ binary ที่สามารถเรียกใช้ได้เลยโดยไม่ต้อง Python

```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Create executable
cd /workspaces/warehouse-management-system
pyinstaller --onefile --windowed --name "ThaiAccountingSystem" src/app.py

# 3. Executable จะอยู่ใน: dist/ThaiAccountingSystem.exe (Windows)
```

**ข้อดี:**
- ✅ ผู้ใช้ไม่ต้องติดตั้ง Python
- ✅ ใช้งานง่าย - ดับเบิลคลิก exe ก็ได้
- ✅ 16 modules แบบสมบูรณ์

**ข้อเสีย:**
- ❌ Desktop เท่านั้น
- ❌ Multiple users ไม่ได้

---

### **Option 2: Flask Web Version (แนะนำ!) 🌐**
เปิด browser ใช้ได้ที่ไหนก็ได้

```bash
# 1. Install Flask
pip install flask flask-cors

# 2. Run web server
python -m src.web_app

# 3. Access
# http://localhost:5000
```

**ข้อดี:**
- ✅ ใช้ผ่าน browser ทั่วไป
- ✅ Modern web interface
- ✅ Multiple users รองรับ
- ✅ Deploy ได้ที่ไหนก็ได้ (local/cloud)
- ✅ Realt-time updates

**ข้อเสีย:**
- ❌ ต้องมี web server/Python
- ❌ Modules บางส่วนอยู่ระหว่างสร้าง

---

### **Option 3: Docker (ตัวเลือกดี)**
ใช้ Docker container สำหรับไม่ต้องกังวล environment

```bash
# 1. Build image
docker build -t thai-accounting:latest .

# 2. Run container
docker run -p 5000:5000 thai-accounting:latest

# 3. Access
# http://localhost:5000
```

**ข้อดี:**
- ✅ ทำงานเหมือนกันทุก platform
- ✅ Sandbox environment
- ✅ Easy deployment

**ข้อเสีย:**
- ❌ ต้องติดตั้ง Docker

---

### **Option 4: Docker Compose (พัฒนา)**
สำหรับการพัฒนา local ง่ายๆ

```bash
# 1. Run with Docker Compose
docker-compose up

# 2. Access
# http://localhost:5000
```

---

### **Option 5: Cloud Deployment (Global Access) ☁️**

#### **A. Heroku (Free tier พอ)**
```bash
# 1. Install Heroku CLI
# 2. Create Procfile and requirements.txt (รวมแล้ว!)
# 3. Deploy
heroku create thai-accounting-system
git push heroku main
# Access: https://thai-accounting-system.herokuapp.com
```

#### **B. PythonAnywhere (Easy)**
1. Sign up: https://www.pythonanywhere.com
2. Upload code
3. Configure web app
4. Access: `yourusername.pythonanywhere.com` (Free!)

#### **C. AWS / Google Cloud / DigitalOcean**
```bash
# 1. Create server (EC2/VM)
# 2. Install Python, Flask
# 3. Run: python -m src.web_app
# 4. Use Nginx/Apache as reverse proxy
```

#### **D. Render.com (Recommended)**
```bash
# Connect GitHub repo
# Auto-deploys on push
# Free tier available
```

---

## 💾 Local Web Deployment

### Start Web Server:
```bash
cd /workspaces/warehouse-management-system
python -m src.web_app
```

Open: **http://localhost:5000** in browser ✅

---

## 🚀 Global Web Deployment (ให้คนอื่นใช้ได้ทั่วโลก)

### **ตัวเลือกที่ดีที่สุด:**

1. **Render.com** (Recommended)
   - Easy GitHub integration
   - Free tier
   - Auto-deploys
   
2. **PythonAnywhere**
   - Simplest setup
   - Free tier available
   - No CLI needed

3. **Heroku**
   - Popular
   - Good documentation
   - (Paid plans only now)

---

## 📋 Web API Endpoints (สำหรับ Integration)

```
Dashboard:
- GET /                           # Main dashboard
- GET /stats                      # Statistics

General Ledger:
- POST /api/ledger/entries        # Add entry
- POST /api/ledger/post           # Post voucher
- GET /api/ledger/trial-balance   # Trial balance

Sales:
- GET /api/sales/invoices         # List invoices
- POST /api/sales/invoices        # Create invoice

Purchases:
- GET /api/purchase-orders        # List POs
- POST /api/purchase-orders       # Create PO

Tax:
- GET /api/tax/report             # Tax report

Banking:
- GET /api/banking/balance        # Cash balance
- POST /api/banking/deposit       # Deposit
- POST /api/banking/withdraw      # Withdraw

Receivables:
- GET /api/ar/outstanding        # Outstanding AR
- POST /api/ar/payment           # Record payment

Assets:
- GET /api/assets                # List assets
- POST /api/assets               # Register asset
```

---

## 📊 Feature Comparison

| Feature | Desktop | Web (Local) | Web (Cloud) |
|---------|---------|------------|-----------|
| 16 Modules | ✅ | ⏳ | ⏳ |
| Offline | ✅ | ❌ | ❌ |
| Browser | ❌ | ✅ | ✅ |
| Multiple Users | ❌ | ✅ | ✅ |
| Global Access | ❌ | ❌ | ✅ |
| Setup Time | 5 min | 2 min | 10 min |
| Cost | Free | Free | Free-$$ |

---

## 🎯 Recommendations

**สำหรับเล็ก / ออฟฟิศเดียว:**
→ Use **Desktop Version** (Option 1)

**สำหรับ Team 1-5 คน / Office:**
→ Use **Web Version Local** (Option 2)

**สำหรับ Global / Multiple Offices:**
→ Use **Cloud Deployment** (Option 5A/5B)

**สำหรับ Development:**
→ Use **Docker Compose** (Option 4)

---

## ✅ บันทึก (Notes)

- ✅ Flask web version พร้อมใช้แล้ว!
- ✅ API endpoints สำหรับ Modules 1, 4, 6, 9, 10, 12, 15
- ✅ Modern responsive UI
- ✅ Database persistence coming soon
- ⏳ Modules 2, 3, 5, 7, 8, 11, 13, 16 API in progress

---

**Ready to deploy?** Pick an option above! 🚀
