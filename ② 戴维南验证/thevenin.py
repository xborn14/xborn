# -*- coding: utf-8 -*-
# ② 验证戴维南定理：10V + R1=4kΩ 串 + R2=6kΩ；端口 A-B
# 手算 V_oc=6V, I_sc=2.5mA, R_th=2.4kΩ
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
from matplotlib import font_manager
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

# ---- 1) 开路电压 V_oc ----
v_oc = vA(build_original())

# ---- 2) 短路电流 I_sc（0V 电源当电流表，分支名 vamp）----
cs = Circuit('short')
cs.V('s', 'vcc', cs.gnd, VS@u_V)
cs.R('1', 'vcc', 'A', R1@u_Ohm)
cs.R('2', 'A', cs.gnd, R2@u_Ohm)
cs.V('amp', 'A', cs.gnd, 0@u_V)
o = cs.simulator().operating_point()
i_sc = abs(float(np.asarray(o.branches['vamp']).flat[0]))
r_th = v_oc/i_sc

print('='*66)
print('② 戴维南定理验证   10 V + R1 = 4 kΩ + R2 = 6 kΩ，端口 A-B')
print('='*66)
print(f'{"量":<14}{"手算(理论)":<20}{"仿真":<20}{"相对误差"}')
print('-'*66)
print(f'{"开路电压 V_oc":<14}{V_OC_TH:<20.4f}{v_oc:<20.4f}{abs(v_oc-V_OC_TH)/V_OC_TH*100:.4f} %')
print(f'{"短路电流 I_sc":<14}{I_SC_TH*1e3:<20.4f}{i_sc*1e3:<20.4f}{abs(i_sc-I_SC_TH)/I_SC_TH*100:.4f} %')
print(f'{"(单位)":<14}{"V / mA":<20}{"V / mA"}')
print('-'*66)
print(f'等效电阻 R_th = V_oc/I_sc = {r_th:.2f} Ω   (理论 R1∥R2 = {R_TH_TH:.2f} Ω, 误差 {abs(r_th-R_TH_TH)/R_TH_TH*100:.4f} %)')
print('='*66)

# ---- 3) 等效替换后的负载验证 ----
RLS = [1000.0, 2000.0, 3000.0, 6000.0]
rows = []
print()
print(f'{"RL":<10}{"原电路 V_L":<14}{"等效 V_L":<14}{"V差异":<10}{"原电路 I_L":<14}{"等效 I_L":<14}{"I差异"}')
print('-'*80)
for rl in RLS:
    v1 = vA(build_original(rl)); i1 = v1/rl
    v2 = vA(build_thevenin(v_oc, r_th, rl)); i2 = v2/rl
    rows.append((rl, v1, i1, v2, i2))
    print(f'{rl/1000:<10.1f}{v1:<14.4f}{v2:<14.4f}{abs(v1-v2)/v1*100:<10.4f}{i1*1e3:<14.4f}{i2*1e3:<14.4f}{abs(i1-i2)/i1*100:.4f}')
print('-'*80)
print('单位：RL=Ω，V_L=V，I_L=mA；差异为相对误差 %')

# ---- 4) 图：V_L 随 RL 变化，两条曲线重合 ----
sweep = np.logspace(2, 4.3, 25)
vo = np.array([vA(build_original(rl)) for rl in sweep])
vt = np.array([vA(build_thevenin(v_oc, r_th, rl)) for rl in sweep])
print(f'\n两条 V_L(RL) 曲线最大差异 = {np.max(np.abs(vo-vt)):.3e} V')

plt.figure(figsize=(7.4, 4.6))
plt.semilogx(sweep, vo, 'o-', ms=4, color='tab:blue', label='原电路 original')
plt.semilogx(sweep, vt, 'x--', ms=6, color='tab:red', label='戴维南等效 Thevenin')
plt.axhline(v_oc, color='gray', ls=':', lw=1, label=f'V_oc = {v_oc:.2f} V (RL→∞)')
plt.axvline(r_th, color='green', ls=':', lw=1, label=f'R_th = {r_th:.0f} Ω')
plt.xlabel('负载 RL / Ω'); plt.ylabel('负载电压 V_L / V')
plt.title('② 戴维南定理验证：原电路与等效电路完全重合')
plt.legend(); plt.grid(True, which='both', alpha=.3)
plt.tight_layout(); plt.savefig('thevenin_compare.png', dpi=150); plt.close()

# ---- 5) 报告 ----
rows_md = '\n'.join(
    f'| {rl/1000:.1f} kΩ | {v1:.4f} V | {v2:.4f} V | {abs(v1-v2)/v1*100:.4f} % | {i1*1e3:.4f} mA | {i2*1e3:.4f} mA | {abs(i1-i2)/i1*100:.4f} % |'
    for rl, v1, i1, v2, i2 in rows)

rep = f"""# ② 戴维南定理验证 —— 实验报告

## 1. 含源二端网络与端口
- 电路：直流电源 10 V 与 R1 = 4 kΩ 串联，R2 = 6 kΩ 并在端口 A-B 之间
- 端口：A 为输出正端，B 为输出负端（接地）

手绘用接线图（照着画，标出端口 A、B，拍照存为 `含源二端网络_手绘.jpg`）：

```
             R1 = 4 kΩ
   ┌────────[====]────────┬───── A (端口 +)
   │                      │
 (10 V)                R2 = 6 kΩ
   │                      │
   └──────────────────────┴───── B (端口 −)
```

戴维南等效电路（同图，拍照存为 `等效电路_手绘.jpg`）：

```
            R_th = 2.4 kΩ
   ┌────────[====]────────┬───── A (端口 +)
   │                      │
 (V_th = 6 V)           RL = 3 kΩ
   │                      │
   └──────────────────────┴───── B (端口 −)
```

## 2. 手算过程
- 开路电压（端口不接负载，R1、R2 分压）：
  V_oc = V_S × R2/(R1+R2) = 10 × 6/10 = **6 V**
- 短路电流（端口短接，R2 被短路）：
  I_sc = V_S/R1 = 10/4000 = **2.5 mA**
- 等效内阻：R_th = V_oc/I_sc = 6/0.0025 = **2400 Ω**
  （也可由 R_th = R1∥R2 = 4×6/10 = 2.4 kΩ 验证）
- 带载 RL = 3 kΩ 时：
  V_L = V_oc × RL/(R_th+RL) = 6 × 3/5.4 = **3.3333 V**，
  I_L = V_L/RL = **1.1111 mA**

## 3. 表一：V_oc、I_sc 两次仿真的「手算 vs 仿真」
| 量 | 手算（理论） | 仿真 | 相对误差 |
|---|---|---|---|
| 开路电压 V_oc | {V_OC_TH:.4f} V | {v_oc:.4f} V | {abs(v_oc-V_OC_TH)/V_OC_TH*100:.4f} % |
| 短路电流 I_sc | {I_SC_TH*1e3:.4f} mA | {i_sc*1e3:.4f} mA | {abs(i_sc-I_SC_TH)/I_SC_TH*100:.4f} % |
| 等效电阻 R_th = V_oc/I_sc | {R_TH_TH:.1f} Ω | {r_th:.1f} Ω | {abs(r_th-R_TH_TH)/R_TH_TH*100:.4f} % |

## 4. 表二：等效电路替换后接负载的电压/电流验证
| 负载 RL | 原电路 V_L | 等效电路 V_L | V 相对差异 | 原电路 I_L | 等效电路 I_L | I 相对差异 |
|---|---|---|---|---|---|---|
{rows_md}

两条 V_L(RL) 曲线最大差异 = {np.max(np.abs(vo-vt)):.3e} V（可视为 0）。

## 5. 波形与图形
- 原电路与等效电路带载曲线对比：`thevenin_compare.png`
- 含源二端网络图（手绘）：`含源二端网络_手绘.jpg`
- 等效电路图（手绘）：`等效电路_手绘.jpg`

## 6. 结论
1. 仿真测得 V_oc = {v_oc:.4f} V、I_sc = {i_sc*1e3:.4f} mA，与手算完全一致（误差 < 0.01%）。
2. 由两者算出的 R_th = {r_th:.1f} Ω 与 R1∥R2 = {R_TH_TH:.1f} Ω 一致。
3. 把含源二端网络换成「V_th 串联 R_th」后接同一负载，端口电压、电流与原电路完全相同（差异 < 0.001%），**戴维南定理得到验证**。
"""
open('戴维南验证_报告.md', 'w', encoding='utf-8').write(rep)
print('已生成: thevenin_compare.png / 戴维南验证_报告.md')
