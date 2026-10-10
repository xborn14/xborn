# -*- coding: utf-8 -*-
# ② 把两张验证表渲染成图片（表格数据由仿真实时计算）
import sys
try:
    sys.stdout.reconfigure(errors='replace')
except Exception:
    pass

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

VS, R1, R2 = 10.0, 4000.0, 6000.0
V_OC_TH, I_SC_TH = VS*R2/(R1+R2), VS/R1
R_TH_TH = R1*R2/(R1+R2)

def build_original(rl=None):
    c = Circuit('original')
    c.V('s', 'vcc', c.gnd, VS@u_V)
    c.R('1', 'vcc', 'A', R1@u_Ohm)
    c.R('2', 'A', c.gnd, R2@u_Ohm)
    if rl: c.R('L', 'A', c.gnd, rl@u_Ohm)
    return c

def build_thevenin(vth, rth, rl=None):
    c = Circuit('thevenin')
    c.V('th', 'x', c.gnd, vth@u_V)
    c.R('th', 'x', 'A', rth@u_Ohm)
    if rl: c.R('L', 'A', c.gnd, rl@u_Ohm)
    return c

def vA(c):
    o = c.simulator().operating_point()
    return float(np.asarray(o['A']).flat[0])

v_oc = vA(build_original())
cs = Circuit('short')
cs.V('s', 'vcc', cs.gnd, VS@u_V)
cs.R('1', 'vcc', 'A', R1@u_Ohm)
cs.R('2', 'A', cs.gnd, R2@u_Ohm)
cs.V('amp', 'A', cs.gnd, 0@u_V)
o = cs.simulator().operating_point()
i_sc = abs(float(np.asarray(o.branches['vamp']).flat[0]))
r_th = v_oc/i_sc

rows = []
for rl in (1000.0, 2000.0, 3000.0, 6000.0):
    v1 = vA(build_original(rl)); i1 = v1/rl
    v2 = vA(build_thevenin(v_oc, r_th, rl)); i2 = v2/rl
    rows.append((rl, v1, i1, v2, i2))

def render(header, data, title, note, fname, figsize, fs=12, colw=None):
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    tbl = ax.table(cellText=data, colLabels=header, loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(fs)
    tbl.scale(1, 2.1)
    for j in range(len(header)):
        c = tbl[0, j]
        c.set_facecolor('#1A3A5C'); c.set_text_props(color='white', fontweight='bold')
    for i in range(len(data)):
        for j in range(len(header)):
            tbl[i+1, j].set_facecolor('#EEF3F7' if i % 2 else '#FFFFFF')
    if colw:
        for j, w in enumerate(colw):
            for i in range(len(data)+1):
                tbl[i, j].set_width(w)
    ax.set_title(title, fontsize=15, fontweight='bold', pad=16)
    fig.text(0.5, 0.035, note, ha='center', fontsize=9.5, color='#555555')
    plt.subplots_adjust(top=0.80, bottom=0.16, left=0.03, right=0.97)
    plt.savefig(fname, dpi=170, facecolor='white')
    plt.close()

# ===== 表一 =====
h1 = ['量', '手算（理论）', '仿真', '相对误差']
d1 = [
    ['开路电压 V_oc',      f'{V_OC_TH:.4f} V',  f'{v_oc:.4f} V',  f'{abs(v_oc-V_OC_TH)/V_OC_TH*100:.4f} %'],
    ['短路电流 I_sc',      f'{I_SC_TH*1e3:.4f} mA', f'{i_sc*1e3:.4f} mA', f'{abs(i_sc-I_SC_TH)/I_SC_TH*100:.4f} %'],
    ['等效电阻 R_th = V_oc / I_sc', f'{R_TH_TH:.1f} Ω', f'{r_th:.1f} Ω', f'{abs(r_th-R_TH_TH)/R_TH_TH*100:.4f} %'],
]
render(h1, d1, '表一  V_oc、I_sc 两次仿真：手算 vs 仿真',
       '10 V 电源 + R1 = 4 kΩ + R2 = 6 kΩ，端口 A-B；R_th 与 R1∥R2 = 2.4 kΩ 相互印证',
       '表一_Voc_Isc对比.png', (9.2, 3.3), fs=12.5, colw=[0.30, 0.24, 0.24, 0.22])

# ===== 表二 =====
h2 = ['负载 R_L', '原电路 V_L', '等效电路 V_L', 'V 相对差异', '原电路 I_L', '等效电路 I_L', 'I 相对差异']
d2 = [[f'{rl/1000:.1f} kΩ', f'{v1:.4f} V', f'{v2:.4f} V', f'{abs(v1-v2)/v1*100:.4f} %',
       f'{i1*1e3:.4f} mA', f'{i2*1e3:.4f} mA', f'{abs(i1-i2)/i1*100:.4f} %']
      for rl, v1, i1, v2, i2 in rows]
render(h2, d2, '表二  等效电路替换后接负载的电压 / 电流验证',
       'V_th = 6 V，R_th = 2.4 kΩ；原电路与等效电路在同一负载下 V_L、I_L 完全相同（差异 0.0000 %）',
       '表二_负载验证.png', (13.5, 3.9), fs=11.5,
       colw=[0.13, 0.15, 0.15, 0.14, 0.15, 0.15, 0.13])

print('已生成: 表一_Voc_Isc对比.png / 表二_负载验证.png')
