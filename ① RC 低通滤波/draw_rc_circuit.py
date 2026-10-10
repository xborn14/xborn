# -*- coding: utf-8 -*-
# ① RC 低通滤波 —— 手绘风格电路图
import sys, warnings
try:
    sys.stdout.reconfigure(errors='replace')
except Exception:
    pass

_warns = []
warnings.showwarning = lambda message, *a, **k: _warns.append(str(message))
warnings.simplefilter('always')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib import font_manager

plt.xkcd(scale=1.1, length=110, randomness=2.2)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['KaiTi', 'STKaiti', 'Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

INK, PAPER = '#1b1b1b', '#FDFBF3'
print('字体可用:', [n for n in ('KaiTi', 'STKaiti', 'Microsoft YaHei', 'SimHei')
                if n in {f.name for f in font_manager.fontManager.ttflist}])
print('实际使用:', plt.rcParams['font.sans-serif'][0])

def wire(ax, pts, lw=2.2):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=INK, lw=lw, solid_capstyle='round', solid_joinstyle='round')

def res_h(ax, x0, y, w=1.8, h=0.52, label=''):
    ax.add_patch(Rectangle((x0, y-h/2), w, h, fill=False, ec=INK, lw=2.0))
    if label:
        ax.text(x0+w/2, y+h/2+0.20, label, ha='center', va='bottom', fontsize=14, color=INK)

def cap_v(ax, x, y_node, y_gnd, label=''):
    """竖直电容：上下两块极板 + 两条引线"""
    y1 = y_node - 1.30
    y2 = y1 - 0.36
    ax.plot([x, x], [y_node, y1], color=INK, lw=2.2)
    ax.plot([x-0.46, x+0.46], [y1, y1], color=INK, lw=3.2, solid_capstyle='round')
    ax.plot([x-0.46, x+0.46], [y2, y2], color=INK, lw=3.2, solid_capstyle='round')
    ax.plot([x, x], [y2, y_gnd], color=INK, lw=2.2)
    if label:
        ax.text(x+0.66, (y1+y2)/2, label, ha='left', va='center', fontsize=14, color=INK)

def source_ac(ax, x, y, label, r=0.62):
    """信号源：圆圈里画一个正弦"""
    ax.add_patch(Circle((x, y), r, fill=False, ec=INK, lw=2.0))
    xs = np.linspace(-0.34, 0.34, 60)
    ax.plot(x+xs, y+0.15*np.sin(xs/0.34*np.pi), color=INK, lw=1.6)
    ax.text(x-r-0.28, y, label, ha='right', va='center', fontsize=15, color=INK)

def ground(ax, x, y, lw=2.0):
    for i, w in enumerate((0.95, 0.62, 0.32)):
        ax.plot([x-w/2, x+w/2], [y-i*0.17, y-i*0.17], color=INK, lw=lw, solid_capstyle='round')

def port(ax, x, y, label):
    ax.add_patch(Circle((x, y), 0.13, fill=True, fc=PAPER, ec=INK, lw=1.8))
    ax.text(x+0.30, y, label, ha='left', va='center', fontsize=15, color=INK)

def dot(ax, x, y):
    ax.plot([x], [y], marker='o', ms=6, color=INK)

fig, ax = plt.subplots(figsize=(10.4, 6.2))
fig.patch.set_facecolor(PAPER); ax.set_facecolor(PAPER)
xlim, ylim = (-2.5, 13.4), (0.4, 6.7)
ax.set_xlim(*xlim); ax.set_ylim(*ylim)
ax.set_aspect('equal'); ax.axis('off')

NODE, GNDY = 4.85, 1.55
source_ac(ax, 1.8, 3.4, 'Vin')
wire(ax, [(1.8, 4.02), (1.8, NODE), (3.4, NODE)])          # 源 -> R
res_h(ax, 3.4, NODE, label='R = 1 kΩ')
wire(ax, [(5.2, NODE), (7.2, NODE), (9.55, NODE)])          # R -> 节点 -> 输出端
dot(ax, 7.2, NODE)
cap_v(ax, 7.2, NODE, GNDY, label='C = 1 μF')
port(ax, 9.7, NODE, 'Vout （+）')
wire(ax, [(1.8, 2.78), (1.8, GNDY), (9.55, GNDY)])          # 源 -> 回线
port(ax, 9.7, GNDY, 'GND （－）')
ground(ax, 4.4, GNDY)
ax.set_title('RC 低通滤波电路（输出取自电容两端）', fontsize=18, color=INK, pad=14)

# ---- 自动检查：标签重叠 / 越界 / 缺字 ----
fig.canvas.draw()
r = fig.canvas.get_renderer()
items = [(t.get_text(), t.get_window_extent(renderer=r)) for t in ax.texts]
bad = [(items[i][0], items[j][0]) for i in range(len(items)) for j in range(i+1, len(items))
       if items[i][1].overlaps(items[j][1])]
inv = ax.transData.inverted()
out = []
for t in ax.texts:
    bb = t.get_window_extent(renderer=r)
    (x0, y0), (x1, y1) = inv.transform([[bb.x0, bb.y0], [bb.x1, bb.y1]])
    if x0 < xlim[0] or x1 > xlim[1] or y0 < ylim[0] or y1 > ylim[1]:
        out.append(t.get_text())
print(f'标签 {len(items)} 个 | 重叠: {bad if bad else "无"} | 超出边界: {out if out else "无"}')

fig.savefig('RC低通滤波_手绘.jpg', dpi=200, facecolor=PAPER, bbox_inches='tight',
            pad_inches=0.22, pil_kwargs={'quality': 95})
plt.close(fig)

g = sorted({m for m in _warns if 'missing from font' in m.lower() or 'Glyph' in m})
print('缺字告警:', g if g else '无（中文渲染正常）')
print('已生成: RC低通滤波_手绘.jpg')
