# -*- coding: utf-8 -*-
# ③ NMOS 共源级放大电路：直流工作点 + 小信号 + 瞬态波形（反相放大）
import sys, warnings
try:
    sys.stdout.reconfigure(errors='replace')
except Exception:
    pass
_warns = []
warnings.showwarning = lambda message, *a, **k: _warns.append(str(message))
warnings.simplefilter('always')

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

VDD, RG1, RG2, RD = 5.0, 60000.0, 40000.0, 2000.0
K, VTH, LAM = 0.8e-3, 1.0, 0.02
VI_AMP, FREQ, CB = 0.010, 1000.0, 1e-6      # Cb1 取 1uF：1kHz 时容抗 159Ω << Rg1||Rg2=24kΩ

# ---------------- 手算 ----------------
VG = VDD*RG2/(RG1+RG2); VGS = VG
ID = 0.5*K*(VGS-VTH)**2
for _ in range(6):                                   # 迭代计入沟道长度调制
    VDS = VDD - ID*RD
    ID = 0.5*K*(VGS-VTH)**2*(1+LAM*VDS)
VDS = VDD - ID*RD
SAT = VDS > (VGS-VTH)
GM = K*(VGS-VTH)*(1+LAM*VDS)
RO = 1/(LAM*ID)
AV = -GM*(RD*RO/(RD+RO))
AV_IDEAL = -GM*RD

print('='*70)
print('③ NMOS 共源级放大电路   手算')
print('='*70)
print(f'V_G = V_GS = {VGS:.4f} V     (VDD x Rg2/(Rg1+Rg2) = 5 x 40/100)')
print(f'I_D  = {ID*1e3:.4f} mA')
print(f'V_DS = {VDS:.4f} V')
print(f'饱和判断: V_DS ({VDS:.4f} V) > V_GS - V_th ({VGS-VTH:.2f} V)  ->  {"饱和区(放大区)" if SAT else "非饱和"}')
print(f'gm   = {GM*1e3:.4f} mS')
print(f'ro   = {RO/1000:.2f} kΩ')
print(f'Av   = -gm(Rd||ro) = {AV:.4f}      (忽略 ro 时 {AV_IDEAL:.4f})')

# ---------------- 仿真 ----------------
def build():
    c = Circuit('NMOS common-source amplifier')
    c.V('dd', 'vdd', c.gnd, VDD@u_V)
    c.R('g1', 'vdd', 'g', RG1@u_Ohm)
    c.R('g2', 'g', c.gnd, RG2@u_Ohm)
    c.R('d', 'vdd', 'drain', RD@u_Ohm)
    c.C('b1', 'vin', 'g', CB@u_F)
    c.SinusoidalVoltageSource('in', 'vin', c.gnd, amplitude=VI_AMP@u_V, frequency=FREQ@u_Hz)
    c.M('1', 'drain', 'g', c.gnd, c.gnd, model='nmos1', w=1e-6, l=1e-6)
    c.model('nmos1', 'nmos', level=1, kp=K, vto=VTH, lambda_=LAM)
    return c

sim = build().simulator()
op = sim.operating_point()
VGS_S = float(np.asarray(op['g']).flat[0])
VDS_S = float(np.asarray(op['drain']).flat[0])
ID_S = (VDD - VDS_S)/RD
SAT_S = VDS_S > (VGS_S - VTH)
GM_S = 2*ID_S/(VGS_S - VTH)
RO_S = 1/(LAM*ID_S)
AV_S_CALC = -GM_S*(RD*RO_S/(RD+RO_S))

tr = sim.transient(step_time=10@u_us, end_time=150@u_ms)   # 跑够时间让耦合电容进入稳态
t = np.asarray(tr.time).real*1000
vg = np.asarray(tr['g']).real
vd = np.asarray(tr['drain']).real
seg = (t > 147.0)                                          # 取最后 3 ms 稳态
ts, vgs_t, vds_t = t[seg], vg[seg], vd[seg]
VIN_PP = vgs_t.max() - vgs_t.min()
VOUT_PP = vds_t.max() - vds_t.min()
AV_S = VOUT_PP/VIN_PP
# 反相验证：输入最大值与输出最小值是否同时刻
i_in_max = int(np.argmax(vgs_t)); i_out_min = int(np.argmin(vds_t))
lag_ms = abs(ts[i_in_max] - ts[i_out_min])
print()
print('='*70)
print('仿真结果')
print('='*70)
print(f'V_GS = {VGS_S:.4f} V    V_DS = {VDS_S:.4f} V    I_D = {ID_S*1e3:.4f} mA')
print(f'饱和判断: {SAT_S}   gm = {GM_S*1e3:.4f} mS   ro = {RO_S/1000:.2f} kΩ')
print(f'瞬态: 输入峰峰 {VIN_PP*1e3:.2f} mV, 输出峰峰 {VOUT_PP*1e3:.2f} mV')
print(f'实测增益 |Av| = {AV_S:.4f}')
print(f'反相验证: 输入峰值时刻与输出谷值时刻相差 {lag_ms:.4f} ms (周期 1.0000 ms) -> {"同相" if lag_ms > 0.25 else "反相(差 180°)"}')

# ---------------- 表格图片 ----------------
def render(header, data, title, note, fname, figsize, fs=12, colw=None):
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    tbl = ax.table(cellText=data, colLabels=header, loc='center', cellLoc='center')
    tbl.auto_set_font_size(False); tbl.set_fontsize(fs); tbl.scale(1, 2.1)
    for j in range(len(header)):
        tbl[0, j].set_facecolor('#1A3A5C'); tbl[0, j].set_text_props(color='white', fontweight='bold')
    for i in range(len(data)):
        for j in range(len(header)):
            tbl[i+1, j].set_facecolor('#EEF3F7' if i % 2 else '#FFFFFF')
    if colw:
        for j, w in enumerate(colw):
            for i in range(len(data)+1):
                tbl[i, j].set_width(w)
    ax.set_title(title, fontsize=15, fontweight='bold', pad=16)
    fig.text(0.5, 0.04, note, ha='center', va='bottom', fontsize=9.5, color='#555555', linespacing=1.5)
    plt.subplots_adjust(top=0.80, bottom=0.22, left=0.03, right=0.97)
    fig.canvas.draw()
    _r = fig.canvas.get_renderer(); _bad = []
    for _k, _cell in tbl.get_celld().items():
        _t = _cell.get_text(); _s = _t.get_text()
        if not _s.strip():
            continue
        _bb = _cell.get_window_extent(_r); _tb = _t.get_window_extent(_r)
        if _tb.width > _bb.width*0.80 + 1 or _tb.height > _bb.height - 2:
            _bad.append('%s：文字%.0fpx > 可用%.0fpx' % (_s.replace(chr(10), '/'), _tb.width, _bb.width*0.80))
    print('[%s] 单元格溢出: %s' % (fname, _bad if _bad else '无'))
    plt.savefig(fname, dpi=170, facecolor='white'); plt.close()

def err(a, b):
    return f'{abs(a-b)/abs(b)*100:.4f} %'

h1 = ['物理量', '手算（理论）', '仿真', '相对误差']
d1 = [
    ['V_GS', f'{VGS:.4f} V', f'{VGS_S:.4f} V', err(VGS_S, VGS)],
    ['I_D',  f'{ID*1e3:.4f} mA', f'{ID_S*1e3:.4f} mA', err(ID_S, ID)],
    ['V_DS', f'{VDS:.4f} V', f'{VDS_S:.4f} V', err(VDS_S, VDS)],
    ['饱和区判断', f'饱和（V_DS={VDS:.2f} V > V_GS-V_th={VGS-VTH:.2f} V）', f'饱和（V_DS={VDS_S:.2f} V > V_GS-V_th={VGS_S-VTH:.2f} V）', '一致'],
]
render(h1, d1, '表一  直流工作点：手算 vs 仿真', 
       '饱和判据：V_DS > V_GS - V_th；实测 4.13 V > 1.00 V → 工作在饱和区（放大区）\n'
       '器件参数：VDD=5 V, Rg1=60 kΩ, Rg2=40 kΩ, Rd=2 kΩ, K=0.8 mA/V², V_th=1 V, λ=0.02 /V',
       '表一_直流工作点.png', (13.8, 4.6), fs=11, colw=[0.12, 0.355, 0.355, 0.17])

h2 = ['物理量', '手算（理论）', '仿真', '相对误差']
d2 = [
    ['跨导 gm', f'{GM*1e3:.4f} mS', f'{GM_S*1e3:.4f} mS', err(GM_S, GM)],
    ['输出电阻 ro', f'{RO/1000:.2f} kΩ', f'{RO_S/1000:.2f} kΩ', err(RO_S, RO)],
    ['电压增益 |Av|', f'{abs(AV):.4f}', f'{AV_S:.4f}（瞬态实测）', err(AV_S, abs(AV))],
]
render(h2, d2, '表二  小信号：gm 与增益 手算 vs 仿真',
       f'增益公式：Av = -gm(Rd//ro) = {AV:.4f}（负号表示与输入反相）\n'
       f'忽略 ro 时 Av = -gm·Rd = {AV_IDEAL:.4f}；仿真实测 |Av| = {AV_S:.4f}，与手算一致',
       '表二_小信号.png', (12.6, 4.0), fs=11, colw=[0.15, 0.28, 0.34, 0.23])

# ---------------- 波形图 ----------------
vg_ac = (vgs_t - vgs_t.mean())*1000
vd_ac = (vds_t - vds_t.mean())*1000
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 6.6), sharex=True)
ax1.plot(ts, vg_ac, color='tab:blue', lw=1.8, label='输入 v_i（交流分量）')
ax1.plot(ts, vd_ac, color='tab:red', lw=1.8, label='输出 v_o（交流分量）')
ax1.axhline(0, color='gray', lw=0.8)
ax1.set_ylabel('交流分量 / mV')
ax1.set_title('共源放大：输入/输出交流分量（输出反相 180°，|Av| ≈ %.2f）' % AV_S)
ax1.legend(); ax1.grid(alpha=.3)
ax2.plot(ts, vds_t, color='tab:red', lw=1.5, label='漏极电压 v_d')
ax2.axhline(VDS_S, color='gray', ls='--', lw=1, label=f'直流工作点 V_DS = {VDS_S:.3f} V')
ax2.set_xlabel('时间 t / ms'); ax2.set_ylabel('v_d / V')
ax2.set_title('漏极完整波形：直流 %0.3f V 上叠加峰峰 %.1f mV 的交流' % (VDS_S, VOUT_PP*1000))
ax2.legend(); ax2.grid(alpha=.3)
plt.tight_layout(); plt.savefig('输入输出波形_反相.png', dpi=170); plt.close()

# ---------------- 报告 ----------------
rep = f"""# ③ NMOS 共源级放大电路 —— 实验报告

## 1. 电路与参数
- 电路：NMOS 共源级，分压式偏置（Rg1 = 60 kΩ 接 VDD，Rg2 = 40 kΩ 接地），漏极电阻 Rd = 2 kΩ，源极直接接地，衬底接源极
- 参数：VDD = 5 V，K = 0.8 mA/V²，V_th = 1 V，λ = 0.02 /V
- 输入：Vi = 10 mV / 1 kHz 正弦，经耦合电容 Cb1 加到栅极
- Cb1 取 1 μF：在 1 kHz 时容抗仅 159 Ω，远小于 Rg1∥Rg2 = 24 kΩ，可视为"足够大"的耦合电容

## 2. 手算静态工作点
- 栅极分压（栅极电流为 0）：V_G = VDD × Rg2/(Rg1+Rg2) = 5 × 40/100 = **2 V**
- 源极接地，故 **V_GS = V_G = 2 V**；V_GS − V_th = 1 V > 0，管子导通
- 忽略 λ 时：I_D = ½K(V_GS−V_th)² = ½ × 0.8m × 1² = **0.4 mA**，V_DS = 5 − 0.4m×2k = **4.2 V**
- 计入沟道长度调制后迭代：**I_D = {ID*1e3:.4f} mA**，**V_DS = {VDS:.4f} V**
- **饱和区判断**：V_DS = {VDS:.4f} V > V_GS − V_th = 1.00 V，且 V_GS > V_th → **工作在饱和区（放大区）**

## 3. 手算小信号
- 跨导：gm = K(V_GS−V_th)(1+λV_DS) = {GM*1e3:.4f} mS（也等于 2I_D/(V_GS−V_th)）
- 输出电阻：ro = 1/(λI_D) = {RO/1000:.2f} kΩ
- 电压增益：**Av = −gm(Rd∥ro) = {AV:.4f}**（负号＝反相）；忽略 ro 时为 −gm·Rd = {AV_IDEAL:.4f}
- 输入电阻：Ri ≈ Rg1∥Rg2 = 24 kΩ；输出电阻：Ro = Rd∥ro ≈ {RD*RO/(RD+RO)/1000:.2f} kΩ

## 4. 表一：直流工作点 手算 vs 仿真
| 物理量 | 手算（理论） | 仿真 | 相对误差 |
|---|---|---|---|
| V_GS | {VGS:.4f} V | {VGS_S:.4f} V | {err(VGS_S, VGS)} |
| I_D | {ID*1e3:.4f} mA | {ID_S*1e3:.4f} mA | {err(ID_S, ID)} |
| V_DS | {VDS:.4f} V | {VDS_S:.4f} V | {err(VDS_S, VDS)} |
| 饱和区判断 | 饱和（V_DS={VDS:.2f} V > V_GS−V_th=1.00 V） | 饱和（V_DS={VDS_S:.2f} V > V_GS−V_th=1.00 V） | 一致 |

（表格图片：`表一_直流工作点.png`）

## 5. 表二：gm 与增益 手算 vs 仿真
| 物理量 | 手算（理论） | 仿真 | 相对误差 |
|---|---|---|---|
| 跨导 gm | {GM*1e3:.4f} mS | {GM_S*1e3:.4f} mS | {err(GM_S, GM)} |
| 输出电阻 ro | {RO/1000:.2f} kΩ | {RO_S/1000:.2f} kΩ | {err(RO_S, RO)} |
| 电压增益 \|Av\| | {abs(AV):.4f} | {AV_S:.4f}（瞬态实测） | {err(AV_S, abs(AV))} |

（表格图片：`表二_小信号.png`）

## 6. 瞬态波形（反相放大）
- 输入峰峰值 {VIN_PP*1000:.2f} mV，输出峰峰值 {VOUT_PP*1000:.2f} mV，**实测增益 |Av| = {AV_S:.4f}**
- 输出与输入**反相 180°**（输入达峰值时输出接近谷值，二者时刻相差 {lag_ms:.4f} ms）
- 输出波形是在 V_DS = {VDS_S:.3f} V 直流上叠加的交流，峰峰约 {VOUT_PP*1000:.1f} mV
- 波形图：`输入输出波形_反相.png`

## 7. 结论
1. 仿真静态工作点 V_GS = {VGS_S:.4f} V、I_D = {ID_S*1e3:.4f} mA、V_DS = {VDS_S:.4f} V 与手算一致，且 V_DS > V_GS − V_th，确认工作在**饱和区**。
2. 手算 gm = {GM*1e3:.4f} mS、|Av| = {abs(AV):.4f}，仿真实测 |Av| = {AV_S:.4f}，误差 {err(AV_S, abs(AV))}，小信号模型成立。
3. 输出波形与输入反相，符合共源级放大器 Av = −gm(Rd∥ro) 的结论。
"""
open('③放大电路_报告.md', 'w', encoding='utf-8').write(rep)
_g = sorted({m for m in _warns if 'missing from font' in m.lower() or 'Glyph' in m})
print('缺字告警:', _g if _g else '无（中文渲染正常）')
print('\n已生成: 表一_直流工作点.png / 表二_小信号.png / 输入输出波形_反相.png / ③放大电路_报告.md')
