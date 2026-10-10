# -*- coding: utf-8 -*-
# ① RC 低通滤波：方波瞬态 + 波特图 + 手算/仿真对比表
# 参数 R = 1 kOhm, C = 1 uF   ->   tau = 1 ms, fc ≈ 159.15 Hz
import sys
try:
    sys.stdout.reconfigure(errors='replace')   # 控制台编码不了的字用 ? 代替，不崩
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
_avail = {f.name for f in font_manager.fontManager.ttflist}
print('中文字体可用:', [n for n in ('Microsoft YaHei', 'SimHei') if n in _avail])

R_OHM, C_F = 1000.0, 1e-6
TAU = R_OHM * C_F
FC  = 1.0/(2*np.pi*TAU)
G1K_TH = 1/np.sqrt(1+(1000/FC)**2)
TR_TH  = 2.197*TAU

def make(src):
    c = Circuit('RC low-pass')
    src(c)
    c.R('1', 'vin', 'vout', R_OHM@u_Ohm)
    c.C('1', 'vout', c.gnd, C_F@u_F)
    return c

# ---------- 1) 交流分析 -> 波特图 ----------
def ac_src(c):
    c.SinusoidalVoltageSource('in', 'vin', c.gnd, amplitude=1@u_V, frequency=1@u_kHz)
ac = make(ac_src).simulator().ac(start_frequency=1@u_Hz, stop_frequency=100@u_kHz,
                                 number_of_points=200, variation='dec')
f = np.asarray(ac.frequency).real
h = np.asarray(ac['vout'])
mag, phase = np.abs(h), np.angle(h, deg=True)
target = 1/np.sqrt(2)
k = int(np.argmax(mag < target))
fc_meas = float(np.exp(np.log(f[k-1]) + (np.log(f[k])-np.log(f[k-1]))*(mag[k-1]-target)/(mag[k-1]-mag[k])))
ph_fc = float(np.interp(np.log(fc_meas), np.log(f), phase))
g1k = float(np.interp(1000.0, f, mag))

# ---------- 2) 方波瞬态 -> tau 与充放电 ----------
def pulse_src(c):
    c.PulseVoltageSource('in', 'vin', c.gnd, initial_value=0@u_V, pulsed_value=1@u_V,
                         pulse_width=10@u_ms, period=20@u_ms,
                         rise_time=1@u_ns, fall_time=1@u_ns)
tr = make(pulse_src).simulator().transient(step_time=1@u_us, end_time=25@u_ms)
t    = np.asarray(tr.time).real
vin  = np.asarray(tr['vin']).real
vout = np.asarray(tr['vout']).real
i0   = int(np.argmax(vin > 0.5))
t0   = t[i0]
v_ss = vout[int(np.argmin(np.abs(t-(t0+8e-3))))]
tau_meas = t[i0+int(np.argmax(vout[i0:] >= 0.632*v_ss))] - t0
i10 = i0+int(np.argmax(vout[i0:] >= 0.10*v_ss))
i90 = i0+int(np.argmax(vout[i0:] >= 0.90*v_ss))
tr_meas = t[i90]-t[i10]

# ---------- 3) 对比表 ----------
print()
print('='*64)
print('① RC 低通滤波    R = 1 kOhm,  C = 1 uF')
print('='*64)
print('%-22s %-16s %-16s %s' % ('物理量', '手算(理论)', '仿真', '相对误差'))
print('-'*64)
print('%-22s %-16s %-16s %.2f%%' % ('时间常数 tau (ms)',   '%.4f'%(TAU*1e3),    '%.4f'%(tau_meas*1e3), abs(tau_meas-TAU)/TAU*100))
print('%-22s %-16s %-16s %.2f%%' % ('截止频率 fc (Hz)',   '%.2f'%FC,          '%.2f'%fc_meas,        abs(fc_meas-FC)/FC*100))
print('%-22s %-16s %-16s %.2f%%' % ('上升时间 10-90% (ms)','%.3f'%(TR_TH*1e3), '%.3f'%(tr_meas*1e3),  abs(tr_meas-TR_TH)/TR_TH*100))
print('%-22s %-16s %-16s %.2f%%' % ('fc 处相位 (度)',     '-45.00',           '%.2f'%ph_fc,          abs(abs(ph_fc)-45)/45*100))
print('%-22s %-16s %-16s %.2f%%' % ('1 kHz 处增益',        '%.4f'%G1K_TH,      '%.4f'%g1k,            abs(g1k-G1K_TH)/G1K_TH*100))
print('='*64)
print('方波稳态值 V_ss = %.4f V' % v_ss)

# ---------- 4) 波特图 ----------
fig, ax = plt.subplots(2, 1, figsize=(7.2, 6.2), sharex=True)
ax[0].semilogx(f, 20*np.log10(mag), lw=1.6, color='tab:blue')
ax[0].axvline(fc_meas, color='r', ls='--', lw=1.1, label='fc = %.1f Hz' % fc_meas)
ax[0].axhline(-3, color='gray', ls=':', lw=1.1, label='-3 dB')
ax[0].plot([fc_meas], [20*np.log10(target)], 'ro')
ax[0].set_ylabel('幅值 |H| / dB'); ax[0].set_title('RC 低通滤波 波特图')
ax[0].legend(); ax[0].grid(True, which='both', alpha=.3)
ax[1].semilogx(f, phase, lw=1.6, color='tab:orange')
ax[1].axvline(fc_meas, color='r', ls='--', lw=1.1)
ax[1].axhline(-45, color='gray', ls=':', lw=1.1, label='-45 度')
ax[1].plot([fc_meas], [ph_fc], 'ro')
ax[1].set_xlabel('频率 f / Hz'); ax[1].set_ylabel('相位 / 度'); ax[1].legend()
ax[1].grid(True, which='both', alpha=.3)
plt.tight_layout(); plt.savefig('rc_bode.png', dpi=150); plt.close()

# ---------- 5) 方波输入/输出瞬态 ----------
plt.figure(figsize=(7.2, 4.2))
plt.plot(t*1e3, vin, '--', color='tab:blue', lw=1.2, label='Vin 方波')
plt.plot(t*1e3, vout, '-', color='tab:red', lw=1.8, label='Vout')
plt.axvline(t0*1e3, color='gray', ls=':', lw=1)
plt.axvline((t0+tau_meas)*1e3, color='green', ls=':', lw=1.2)
plt.axhline(0.632*v_ss, color='green', ls=':', lw=1)
plt.plot([(t0+tau_meas)*1e3], [0.632*v_ss], 'go')
plt.annotate('tau = %.3f ms' % (tau_meas*1e3), xy=((t0+tau_meas)*1e3, 0.632*v_ss),
             xytext=((t0+3.5e-3)*1e3, 0.35), arrowprops=dict(arrowstyle='->', color='green'))
plt.xlabel('时间 t / ms'); plt.ylabel('电压 / V')
plt.title('RC 低通滤波 方波响应（充电到 63.2% 用时 = tau）')
plt.legend(); plt.grid(alpha=.3)
plt.tight_layout(); plt.savefig('rc_square.png', dpi=150); plt.close()

# ---------- 6) 报告 ----------
rep = """# ① RC 低通滤波电路 —— 实验报告

## 1. 电路与参数
- 结构：电阻 R 串在信号路径，电容 C 并在输出与地之间（低通）
- 参数：R = 1 kOhm，C = 1 uF
- 激励：瞬态用方波 0→1 V（脉宽 10 ms、周期 20 ms）；交流分析用 1 V 正弦扫频

电路接线（照着画在纸上，拍照存为 `rc_circuit_手绘.jpg`）：

    方波/正弦源 ── R = 1 kOhm ──┬── Vout
                                │
                              C = 1 uF
                                │
                               GND

    源的另一端也接 GND（即：Vin 两端分别接到 R 的左端和 GND）。

## 2. 手算过程
- 时间常数：tau = RC = 1e3 x 1e-6 = **1 ms**
- 截止频率：fc = 1/(2*pi*RC) = 1/(2*pi*1e-3) ≈ **159.15 Hz**
- 1 kHz 处增益：|H| = 1/sqrt(1+(f/fc)^2) = 1/sqrt(1+(1000/159.15)^2) ≈ **0.157**
- 上升时间：tr ≈ 2.2 tau = **2.20 ms**（10%%→90%%）
- fc 处相位：**−45 度**
- 充电规律：u_C(t) = V(1 − e^(−t/tau))，t = tau 时达到 63.2%%，约 5 tau 基本稳定

## 3. 手算 vs 仿真对比表
| 物理量 | 手算（理论） | 仿真 | 相对误差 |
|---|---|---|---|
| 时间常数 tau | %.4f ms | %.4f ms | %.2f %% |
| 截止频率 fc | %.2f Hz | %.2f Hz | %.2f %% |
| 上升时间 10%%→90%% | %.3f ms | %.3f ms | %.2f %% |
| fc 处相位 | −45.00 度 | %.2f 度 | %.2f %% |
| 1 kHz 处增益 | %.4f | %.4f | %.2f %% |

仿真测得方波稳态值 V_ss = %.4f V。

## 4. 波形与曲线
- 方波输入/输出瞬态波形：`rc_square.png`
- 波特图（幅频 + 相频）：`rc_bode.png`
- 电路图（手绘拍照）：`rc_circuit_手绘.jpg`

## 5. 结论
1. 仿真测得的 tau 与 fc 和手算结果一致（误差 < 2%%），验证了 RC 低通滤波的频率特性。
2. 方波输入下输出按指数规律充放电：经 1 tau 达到稳态值的 63.2%%，约 5 tau 后基本稳定。
3. 幅频曲线在 fc 处下降 3 dB，之后以 −20 dB/十倍频滚降；相频曲线在 fc 处为 −45 度。
""" % (TAU*1e3, tau_meas*1e3, abs(tau_meas-TAU)/TAU*100,
       FC, fc_meas, abs(fc_meas-FC)/FC*100,
       TR_TH*1e3, tr_meas*1e3, abs(tr_meas-TR_TH)/TR_TH*100,
       ph_fc, abs(abs(ph_fc)-45)/45*100,
       G1K_TH, g1k, abs(g1k-G1K_TH)/G1K_TH*100, v_ss)
open('RC低通滤波_报告.md', 'w', encoding='utf-8').write(rep)
print('已生成: rc_bode.png / rc_square.png / RC低通滤波_报告.md')
