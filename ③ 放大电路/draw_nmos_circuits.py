# -*- coding: utf-8 -*-
# ③ 手绘风格：直流通路 + 小信号等效模型
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
print('字体:', [n for n in ('KaiTi', 'STKaiti') if n in {f.name for f in font_manager.fontManager.ttflist}])

def wire(ax, pts, lw=2.2):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=INK, lw=lw, solid_capstyle='round', solid_joinstyle='round')

def rect(ax, x, y0, w, h, lw=2.0):
    ax.add_patch(Rectangle((x-w/2, y0), w, h, fill=False, ec=INK, lw=lw))

def res_v(ax, x, y0, h, label='', side='right', dy=0.0):
    rect(ax, x, y0, 0.5, h)
    if label:
        dx = 0.42 if side == 'right' else -0.42
        ax.text(x+dx, y0+h/2+dy, label, ha='left' if side == 'right' else 'right',
                va='center', fontsize=13, color=INK)

def res_h(ax, x0, y, w, label='', below=False):
    rect(ax, x0+w/2, y-0.26, w, 0.52)
    if label:
        ax.text(x0+w/2, y-0.42 if below else y+0.42, label, ha='center',
                va='top' if below else 'bottom', fontsize=13, color=INK)

def ground(ax, x, y, lw=2.0):
    for i, w in enumerate((0.95, 0.62, 0.32)):
        ax.plot([x-w/2, x+w/2], [y-i*0.17, y-i*0.17], color=INK, lw=lw, solid_capstyle='round')

def port(ax, x, y, label, ha='left'):
    ax.add_patch(Circle((x, y), 0.13, fill=True, fc=PAPER, ec=INK, lw=1.8))
    ax.text(x+(0.30 if ha == 'left' else -0.30), y, label,
            ha=ha, va='center', fontsize=14, color=INK)

def dot(ax, x, y):
    ax.plot([x], [y], marker='o', ms=6, color=INK)

def source_ac(ax, x, y, label, r=0.60):
    ax.add_patch(Circle((x, y), r, fill=False, ec=INK, lw=2.0))
    xs = np.linspace(-0.33, 0.33, 60)
    ax.plot(x+xs, y+0.15*np.sin(xs/0.33*np.pi), color=INK, lw=1.6)
    ax.text(x, y-r-0.30, label, ha='center', va='top', fontsize=14, color=INK)

def arrow(ax, x0, y0, x1, y1, lw=1.8):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='-|>', color=INK, lw=lw, shrinkA=0, shrinkB=0))

def nmos(ax, gx, cx, ybot, ytop, gate_y):
    """gx=栅极板 x, cx=沟道 x"""
    ax.plot([gx, gx], [ybot, ytop], color=INK, lw=2.6, solid_capstyle='round')   # 栅极板
    ax.plot([cx, cx], [ybot, ytop], color=INK, lw=2.6, solid_capstyle='round')   # 沟道
    ax.plot([gx-1.4, gx], [gate_y, gate_y], color=INK, lw=2.2)                    # 栅极引线
    ax.plot([cx, cx+1.6], [ytop, ytop], color=INK, lw=2.2)                        # 漏极引线
    ax.plot([cx, cx+1.6], [ybot, ybot], color=INK, lw=2.2)                        # 源极引线

def check(fig, ax, name, xlim, ylim):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    items = [(t.get_text(), t.get_window_extent(renderer=r)) for t in ax.texts]
    bad = [(items[i][0], items[j][0]) for i in range(len(items)) for j in range(i+1, len(items))
           if items[i][1].overlaps(items[j][1])]
    inv = ax.transData.inverted(); out = []
    for t in ax.texts:
        bb = t.get_window_extent(renderer=r)
        (x0, y0), (x1, y1) = inv.transform([[bb.x0, bb.y0], [bb.x1, bb.y1]])
        if x0 < xlim[0] or x1 > xlim[1] or y0 < ylim[0] or y1 > ylim[1]:
            out.append(t.get_text())
    print(f'[{name}] 标签 {len(items)} 个 | 重叠: {bad if bad else "无"} | 越界: {out if out else "无"}')

# ================= 图 A：直流通路 =================
fig, ax = plt.subplots(figsize=(10.6, 6.0))
fig.patch.set_facecolor(PAPER); ax.set_facecolor(PAPER)
XL, YL = (-1.6, 12.6), (0.6, 7.4)
ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_aspect('equal'); ax.axis('off')

RAIL, GNDY = 6.6, 2.4
wire(ax, [(2.2, RAIL), (8.2, RAIL)])
port(ax, 8.5, RAIL, 'VDD (5 V)')
res_v(ax, 2.2, 4.9, 1.0, 'Rg1 = 60 kΩ', 'left')          # Rg1
wire(ax, [(2.2, RAIL), (2.2, 5.9)]); wire(ax, [(2.2, 4.9), (2.2, 4.0)])
res_v(ax, 7.0, 4.9, 1.0, 'Rd = 2 kΩ', 'right')           # Rd
wire(ax, [(7.0, RAIL), (7.0, 5.9)]); wire(ax, [(7.0, 4.9), (7.0, 4.6)])
dot(ax, 2.2, 4.0); dot(ax, 7.0, 4.6)
nmos(ax, 4.3, 4.7, 3.4, 4.6, 4.0)                         # 晶体管
wire(ax, [(2.2, 4.0), (4.3, 4.0)])                        # 栅极引线接到分压点
wire(ax, [(6.3, 4.6), (7.0, 4.6)])                        # 漏极接到 Rd
wire(ax, [(6.3, 3.4), (7.0, 3.4), (7.0, GNDY)])           # 源极到地
wire(ax, [(4.7, 4.0), (5.6, 4.0), (5.6, 3.4)])            # 衬底接源极
dot(ax, 5.6, 3.4)
ax.text(5.6, 3.22, 'B', ha='center', va='top', fontsize=13, color=INK)
res_v(ax, 2.2, 2.4, 1.0, 'Rg2 = 40 kΩ', 'left')          # Rg2
wire(ax, [(2.2, 4.0), (2.2, 3.4)]); wire(ax, [(2.2, 2.4), (2.2, GNDY)])
wire(ax, [(2.2, GNDY), (7.0, GNDY)])
ground(ax, 5.4, GNDY)
arrow(ax, 6.2, 4.35, 6.2, 3.75)
ax.text(6.05, 4.05, 'I_D', ha='right', va='center', fontsize=13, color=INK)
ax.set_title('直流通路（耦合电容开路、交流源置零）', fontsize=17, color=INK, pad=14)
fig.text(0.5, 0.035, 'V_GS = 2 V，I_D = 0.433 mA，V_DS = 4.13 V（饱和区）',
         ha='center', fontsize=11, color='#555555')
plt.subplots_adjust(top=0.86, bottom=0.13, left=0.03, right=0.97)
check(fig, ax, '直流通路', XL, YL)
fig.savefig('直流通路_手绘.jpg', dpi=200, facecolor=PAPER, bbox_inches='tight',
            pad_inches=0.22, pil_kwargs={'quality': 95})
plt.close(fig)

# ================= 图 B：小信号等效模型 =================
fig, ax = plt.subplots(figsize=(11.0, 6.0))
fig.patch.set_facecolor(PAPER); ax.set_facecolor(PAPER)
XL, YL = (-1.6, 13.2), (0.6, 7.4)
ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_aspect('equal'); ax.axis('off')

GNDY, GBUS, DBUS = 1.8, 5.4, 4.3
source_ac(ax, 1.4, 3.6, 'vi')
wire(ax, [(1.4, 4.2), (1.4, GBUS), (2.6, GBUS)])
wire(ax, [(1.4, 3.0), (1.4, GNDY)])
res_h(ax, 2.6, GBUS, 1.8, 'Ri = 24 kΩ', below=True)       # Ri
wire(ax, [(4.4, GBUS), (5.6, GBUS)])
dot(ax, 5.6, GBUS)
ax.text(5.6, GBUS+0.22, 'g', ha='center', va='bottom', fontsize=14, color=INK)
ax.plot([5.6, 5.6], [GBUS, GNDY], color='#777777', lw=1.4, ls='--')
ax.text(5.78, 3.5, 'vgs', ha='left', va='center', fontsize=14, color='#444444')
# 漏极母线
wire(ax, [(6.6, DBUS), (9.8, DBUS)])
dot(ax, 6.6, DBUS)
ax.text(6.6, DBUS+0.22, 'd', ha='center', va='bottom', fontsize=14, color=INK)
port(ax, 9.8, DBUS, 'vo')
wire(ax, [(11.0, DBUS), (11.0, DBUS)]) if False else None
wire(ax, [(9.8, DBUS), (11.0, DBUS)])
wire(ax, [(6.6, DBUS), (6.6, 3.45)])
wire(ax, [(6.6, 2.55), (6.6, GNDY)])
ax.add_patch(Circle((6.6, 3.0), 0.45, fill=True, fc=PAPER, ec=INK, lw=2.0))
arrow(ax, 6.6, 3.30, 6.6, 2.72)
ax.text(6.6, 2.25, 'gm*vgs', ha='center', va='top', fontsize=13, color=INK)
rect(ax, 8.0, 2.5, 0.5, 1.4)                              # ro
wire(ax, [(8.0, DBUS), (8.0, 3.9)]); wire(ax, [(8.0, 2.5), (8.0, GNDY)])
ax.text(8.0, 2.25, 'ro', ha='center', va='top', fontsize=13, color=INK)
rect(ax, 9.4, 2.5, 0.5, 1.4)                              # Rd
wire(ax, [(9.4, DBUS), (9.4, 3.9)]); wire(ax, [(9.4, 2.5), (9.4, GNDY)])
ax.text(9.4, 2.25, 'Rd', ha='center', va='top', fontsize=13, color=INK)
wire(ax, [(1.4, GNDY), (9.4, GNDY)])
ground(ax, 4.0, GNDY)
ax.set_title('小信号等效模型（直流源置零、电容短路）', fontsize=17, color=INK, pad=14)
fig.text(0.5, 0.035, 'gm = 0.866 mS，ro = 115 kΩ，Rd = 2 kΩ   →   Av = -gm(Rd//ro) = -1.70',
         ha='center', fontsize=11, color='#555555')
plt.subplots_adjust(top=0.86, bottom=0.13, left=0.03, right=0.97)
check(fig, ax, '小信号等效模型', XL, YL)
fig.savefig('小信号等效模型_手绘.jpg', dpi=200, facecolor=PAPER, bbox_inches='tight',
            pad_inches=0.22, pil_kwargs={'quality': 95})
plt.close(fig)

g = sorted({m for m in _warns if 'missing from font' in m.lower() or 'Glyph' in m})
print('缺字告警:', g if g else '无（中文渲染正常）')
print('已生成: 直流通路_手绘.jpg / 小信号等效模型_手绘.jpg')
