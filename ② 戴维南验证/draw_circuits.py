# -*- coding: utf-8 -*-
# ② 手绘风格电路图：含源二端网络（端口 A-B）+ 戴维南等效电路
import sys, warnings
try:
    sys.stdout.reconfigure(errors='replace')
except Exception:
    pass

# 捕获所有告警（用于检查字体缺字）
_warns = []
_orig_show = warnings.showwarning
def _hook(message, category, filename, lineno, file=None, line=None):
    _warns.append(str(message))
warnings.showwarning = _hook
warnings.simplefilter('always')

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
_avail = {f.name for f in font_manager.fontManager.ttflist}
print('手写/中文字体可用:', [n for n in ('KaiTi', 'STKaiti', 'Microsoft YaHei', 'SimHei') if n in _avail])
print('实际使用的字体:', plt.rcParams['font.sans-serif'][0])

def wire(ax, pts, lw=2.2):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=INK, lw=lw, solid_capstyle='round', solid_joinstyle='round')

def res_h(ax, x0, y, w=1.8, h=0.52, label=''):
    ax.add_patch(Rectangle((x0, y-h/2), w, h, fill=False, ec=INK, lw=2.0))
    if label:
        ax.text(x0+w/2, y+h/2+0.20, label, ha='center', va='bottom', fontsize=14, color=INK)

def res_v(ax, x, y0, w=0.52, h=1.7, label=''):
    ax.add_patch(Rectangle((x-w/2, y0), w, h, fill=False, ec=INK, lw=2.0))
    if label:
        ax.text(x+w/2+0.26, y0+h/2, label, ha='left', va='center', fontsize=14, color=INK)

def source(ax, x, y, label, r=0.62):
    ax.add_patch(Circle((x, y), r, fill=False, ec=INK, lw=2.0))
    ax.text(x, y+0.30, '+', ha='center', va='center', fontsize=14, color=INK)
    ax.text(x, y-0.33, '－', ha='center', va='center', fontsize=16, color=INK)
    ax.text(x-r-0.28, y, label, ha='right', va='center', fontsize=15, color=INK)

def ground(ax, x, y, lw=2.0):
    for i, w in enumerate((0.95, 0.62, 0.32)):
        ax.plot([x-w/2, x+w/2], [y-i*0.17, y-i*0.17], color=INK, lw=lw, solid_capstyle='round')

def port(ax, x, y, label):
    ax.add_patch(Circle((x, y), 0.13, fill=True, fc=PAPER, ec=INK, lw=1.8))
    ax.text(x+0.30, y, label, ha='left', va='center', fontsize=15, color=INK)

def dot(ax, x, y):
    ax.plot([x], [y], marker='o', ms=6, color=INK)

def check(fig, ax, name, xlim, ylim):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    items = [(t.get_text(), t.get_window_extent(renderer=r)) for t in ax.texts]
    bad = []
    for i in range(len(items)):
        for j in range(i+1, len(items)):
            if items[i][1].overlaps(items[j][1]):
                bad.append((items[i][0], items[j][0]))
    # 检查是否有元素超出画布范围（被裁掉）
    inv = ax.transData.inverted()
    out = []
    for t in ax.texts:
        bb = t.get_window_extent(renderer=r)
        (x0, y0), (x1, y1) = inv.transform([[bb.x0, bb.y0], [bb.x1, bb.y1]])
        if x0 < xlim[0] or x1 > xlim[1] or y0 < ylim[0] or y1 > ylim[1]:
            out.append(t.get_text())
    print(f'[{name}] 标签 {len(items)} 个 | 重叠: {bad if bad else "无"} | 超出边界: {out if out else "无"}')

def canvas(figsize=(10.4, 6.2)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(PAPER); ax.set_facecolor(PAPER)
    xlim, ylim = (-2.5, 12.9), (0.4, 6.7)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_aspect('equal'); ax.axis('off')
    return fig, ax, xlim, ylim

def save(fig, fname):
    fig.savefig(fname, dpi=200, facecolor=PAPER, bbox_inches='tight', pad_inches=0.22,
                pil_kwargs={'quality': 95})

# ============ 图 1：含源二端网络（端口 A-B） ============
fig, ax, xl, yl = canvas()
source(ax, 1.8, 3.4, '10 V')
wire(ax, [(1.8, 4.02), (1.8, 4.85), (3.4, 4.85)])
res_h(ax, 3.4, 4.85, label='R1 = 4 kΩ')
wire(ax, [(5.2, 4.85), (7.2, 4.85), (9.55, 4.85)])
dot(ax, 7.2, 4.85)
port(ax, 9.7, 4.85, 'A （+）')
res_v(ax, 7.2, 2.15, label='R2 = 6 kΩ')
wire(ax, [(7.2, 4.85), (7.2, 3.85)])
wire(ax, [(7.2, 2.15), (7.2, 1.55)])
wire(ax, [(1.8, 2.78), (1.8, 1.55), (9.55, 1.55)])
port(ax, 9.7, 1.55, 'B （－）')
ground(ax, 4.4, 1.55)
ax.set_title('含源二端网络（端口 A、B）', fontsize=18, color=INK, pad=14)
check(fig, ax, '含源二端网络', xl, yl)
save(fig, '含源二端网络_手绘.jpg'); plt.close(fig)

# ============ 图 2：戴维南等效电路 ============
fig, ax, xl, yl = canvas()
source(ax, 1.8, 3.4, 'V_th = 6 V')
wire(ax, [(1.8, 4.02), (1.8, 4.85), (3.4, 4.85)])
res_h(ax, 3.4, 4.85, label='R_th = 2.4 kΩ')
wire(ax, [(5.2, 4.85), (7.2, 4.85), (9.55, 4.85)])
dot(ax, 7.2, 4.85)
port(ax, 9.7, 4.85, 'A （+）')
res_v(ax, 7.2, 2.15, label='R_L = 3 kΩ')
wire(ax, [(7.2, 4.85), (7.2, 3.85)])
wire(ax, [(7.2, 2.15), (7.2, 1.55)])
wire(ax, [(1.8, 2.78), (1.8, 1.55), (9.55, 1.55)])
port(ax, 9.7, 1.55, 'B （－）')
ground(ax, 4.4, 1.55)
ax.set_title('戴维南等效电路（端口 A、B 接负载 R_L）', fontsize=18, color=INK, pad=14)
check(fig, ax, '戴维南等效电路', xl, yl)
save(fig, '等效电路_手绘.jpg'); plt.close(fig)

print('已生成: 含源二端网络_手绘.jpg / 等效电路_手绘.jpg')
g = sorted({m for m in _warns if 'missing from font' in m.lower() or 'Glyph' in m})
print('缺字告警:', g if g else '无（中文渲染正常）')
