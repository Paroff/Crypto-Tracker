# Crypto-Tracker

A widget that tracks cryptocurrency indexes.

---

## ₿ Crypto Ticker - Installation Guide

### Prerequisites

Python 3.8+ installed with the **"Add Python to PATH"** option checked → [Python Downloads](https://www.python.org/downloads/)

---

### Quick Installation

1. Place both files in the same folder:  
   - `crypto_ticker.pyw`  
   - `start.bat`

2. Double-click `start.bat`  

This will:  
- Automatically install the `requests` library  
- Add the ticker to Windows startup  
- Offer to launch it immediately  

---

### Usage

| Action                     | Description                       |
|-----------------------------|-----------------------------------|
| Move the window             | Left-click + drag                 |
| Quit                        | Right-click on the window         |
| Remove from startup         | Re-run `installer_demarrage.bat`  |

---

### How It Works

- Selected cryptocurrency price updates every 60 seconds (free CoinGecko API)  
- Green chart if the crypto is up over 24h  
- Red chart if the crypto is down over 24h  
- Borderless window, always on top  
- Minimum size ≈ Windows taskbar clock  
- Memory usage < 30 MB, near-zero CPU between updates  

---

### Resource Usage

The app "sleeps" 60 seconds between updates.  

**Typical usage:**  
- RAM: ~15–25 MB  
- CPU: < 0.1% while idle
