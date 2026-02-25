"""
ETH/EUR Ticker — Ultra compact, pure black background, embedded graph
- Binance API (reliable, no key, no limit)
- Fallback to CoinGecko if Binance fails
- Updates every 30s via after() (no blocking sleep)
- Window ~220x40px, Windows clock size
"""

import tkinter as tk
import threading
import urllib.request
import urllib.parse
import json
from collections import deque

# ── Config ────────────────────────────────────────────────────────────────────
UPDATE_MS      = 30_000
HISTORY_POINTS = 60
GRAPH_W        = 90
GRAPH_H        = 38
WIN_H          = 42
BG             = "#000000"
FG_PRICE       = "#ffffff"
FG_LABEL       = "#000000"
COLOR_POS      = "#00e676"
COLOR_NEG      = "#d50000"
COLOR_NEUTRAL  = "#555555"

price_history  = deque(maxlen=HISTORY_POINTS)
lock           = threading.Lock()

# ── APIs ──────────────────────────────────────────────────────────────────────
def fetch_binance():
    url = "https://api.binance.com/api/v3/ticker/24hr?symbol=ETHEUR"
    with urllib.request.urlopen(url, timeout=6) as r:
        d = json.loads(r.read())
    return float(d["lastPrice"]), float(d["priceChangePercent"])

def fetch_coingecko():
    params = urllib.parse.urlencode({
        "ids": "ethereum",
        "vs_currencies": "eur",
        "include_24hr_change": "true",
    })
    url = f"https://api.coingecko.com/api/v3/simple/price?{params}"
    with urllib.request.urlopen(url, timeout=8) as r:
        d = json.loads(r.read())["ethereum"]
    return float(d["eur"]), float(d["eur_24h_change"])

def fetch_eth():
    try:
        return fetch_binance()
    except Exception:
        pass
    try:
        return fetch_coingecko()
    except Exception:
        pass
    return None, None

# ── App ───────────────────────────────────────────────────────────────────────
class ETHTicker(tk.Tk):
    def __init__(self):
        super().__init__()
        self._last_color = COLOR_NEUTRAL
        self._drag_x = self._drag_y = 0
        self._setup_window()
        self._build_ui()
        self._schedule_update(delay=200)

    # ── Window ───────────────────────────────────────────────────────────────
    def _setup_window(self):
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=BG)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"10x{WIN_H}+{sw - 260}+{sh - WIN_H - 48}")
        self.bind("<ButtonPress-1>", self._drag_start)
        self.bind("<B1-Motion>",     self._drag_motion)
        self.bind("<ButtonPress-3>", lambda e: self.destroy())

    def _drag_start(self, e):
        self._drag_x, self._drag_y = e.x, e.y

    def _drag_motion(self, e):
        x = self.winfo_x() + e.x - self._drag_x
        y = self.winfo_y() + e.y - self._drag_y
        self.geometry(f"+{x}+{y}")

    # ── UI ───────────────────────────────────────────────────────────────────
    def _build_ui(self):
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=5, pady=2)

        txt = tk.Frame(outer, bg=BG)
        txt.pack(side="left", fill="y")

        top_row = tk.Frame(txt, bg=BG)
        top_row.pack(anchor="w", fill="x")

        tk.Label(top_row, text="Ξ", font=("Consolas", 8, "bold"),
                 fg=FG_LABEL, bg=BG).pack(side="left")

        self.lbl_change = tk.Label(top_row, text=" ···",
                                   font=("Consolas", 8),
                                   fg=COLOR_NEUTRAL, bg=BG)
        self.lbl_change.pack(side="left")

        self.lbl_price = tk.Label(txt, text="··· €",
                                  font=("Consolas", 14, "bold"),
                                  fg=FG_PRICE, bg=BG, anchor="w")
        self.lbl_price.pack(anchor="w")

        tk.Frame(outer, bg="#1a1a1a", width=1).pack(side="left", fill="y", padx=3)

        self.canvas = tk.Canvas(outer, width=GRAPH_W, height=GRAPH_H,
                                bg=BG, highlightthickness=0, bd=0)
        self.canvas.pack(side="left", fill="y")

        self.update_idletasks()
        total_w = outer.winfo_reqwidth() + 12
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{total_w}x{WIN_H}+{sw - total_w - 10}+{sh - WIN_H - 48}")

    # ── Scheduling ────────────────────────────────────────────────────────────
    def _schedule_update(self, delay=None):
        ms = delay if delay is not None else UPDATE_MS
        self.after(ms, self._do_update)

    def _do_update(self):
        threading.Thread(target=self._fetch_and_refresh, daemon=True).start()

    def _fetch_and_refresh(self):
        price, change = fetch_eth()
        if price is not None:
            with lock:
                price_history.append(price)
            self.after(0, self._refresh_ui, price, change)
        self.after(0, self._schedule_update)

    # ── Refresh UI ────────────────────────────────────────────────────────────
    def _refresh_ui(self, price: float, change: float):
        if change > 0:
            color, arrow = COLOR_POS, "▲"
        elif change < 0:
            color, arrow = COLOR_NEG, "▼"
        else:
            color, arrow = COLOR_NEUTRAL, "━"

        self._last_color = color
        p_str = f"{price:,.2f} €".replace(",", "\u202f")
        c_str = f" {arrow}{abs(change):.2f}%"

        self.lbl_price.config(text=p_str)
        self.lbl_change.config(text=c_str, fg=color)
        self._draw_sparkline(color)

    # ── Sparkline ─────────────────────────────────────────────────────────────
    def _draw_sparkline(self, color: str):
        self.canvas.delete("all")
        with lock:
            pts = list(price_history)

        if not pts:
            return

        if len(pts) == 1:
            mid = GRAPH_H // 2
            self.canvas.create_line(2, mid, GRAPH_W - 2, mid,
                                    fill=color, width=1.5)
            return

        mn, mx = min(pts), max(pts)
        w, h   = GRAPH_W, GRAPH_H
        pad    = 3
        n      = len(pts)

        def xy(i, v):
            x = pad + (i / (n - 1)) * (w - pad * 2)
            y = (h / 2) if mx == mn else (
                h - pad - ((v - mn) / (mx - mn)) * (h - pad * 2))
            return x, y

        poly = []
        for i, v in enumerate(pts):
            poly.extend(xy(i, v))
        poly.extend([w - pad, h, pad, h])
        self.canvas.create_polygon(*poly, fill=color, outline="", stipple="gray25")

        line = []
        for i, v in enumerate(pts):
            line.extend(xy(i, v))
        self.canvas.create_line(*line, fill=color, width=1.5,
                                smooth=True, capstyle=tk.ROUND, joinstyle=tk.ROUND)

        lx, ly = xy(n - 1, pts[-1])
        r = 2.5
        self.canvas.create_oval(lx - r, ly - r, lx + r, ly + r,
                                fill=color, outline=BG, width=1)

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = ETHTicker()
    app.mainloop()
