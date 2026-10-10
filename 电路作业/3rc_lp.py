# nmos_cs.py —— VDD=5V, Rg1=60k, Rg2=40k, Rd=2k, K=0.8mA/V², Vth=1V, λ=0.02/V, Vi=10mV/1kHz
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import numpy as np

VDD, RG1, RG2, RD = 5.0, 60000.0, 40000.0, 2000.0
K, VTH, LAM = 0.8e-3, 1.0, 0.02

c = Circuit('NMOS common-source amplifier')
c.V('dd', 'vdd', c.gnd, VDD@u_V)
c.R('g1', 'vdd', 'g', RG1@u_Ohm)          # 栅极分压上臂
c.R('g2', 'g', c.gnd, RG2@u_Ohm)          # 栅极分压下臂
c.R('d', 'vdd', 'drain', RD@u_Ohm)        # 漏极负载
c.C('b1', 'vin', 'g', 10@u_uF)            # 输入耦合电容
c.SinusoidalVoltageSource('in', 'vin', c.gnd, amplitude=10@u_mV, frequency=1@u_kHz)
c.M('1', 'drain', 'g', c.gnd, c.gnd, model='nmos1', w=1e-6, l=1e-6)
c.model('nmos1', 'nmos', level=1, kp=K, vto=VTH, lambda_=LAM)
sim = c.simulator()

# ---- 直流工作点：对比手算 I_D、V_DS ----
op = sim.operating_point()
Vg = float(np.asarray(op['g']).flat[0])
Vd = float(np.asarray(op['drain']).flat[0])
Id = (VDD - Vd)/RD
print('V_GS = %.4f V   (手算 2.0000)' % Vg)
print('V_DS = %.4f V   (手算 4.1339)' % Vd)
print('I_D  = %.4f mA  (手算 0.4331)' % (Id*1e3))
print('饱和区? V_DS > V_GS-Vth :', Vd > Vg - VTH)
print('gm   = %.4f mS  (手算 0.866)' % (2*Id/(Vg-VTH)*1e3))

# ---- 瞬态：看输出波形 + 实测增益 ----
tr = sim.transient(step_time=10@u_us, end_time=4@u_ms)
t  = np.asarray(tr.time).real*1000
vg = np.asarray(tr['g']).real
vd = np.asarray(tr['drain']).real
tail = slice(len(t)//2, len(t))            # 取后半段（稳态）
vin_pp  = vg[tail].max() - vg[tail].min()
vout_pp = vd[tail].max() - vd[tail].min()
print('输入峰峰值 = %.2f mV' % (vin_pp*1000))
print('输出峰峰值 = %.2f mV' % (vout_pp*1000))
print('实测增益 |Av| = %.3f   (手算 1.70)' % (vout_pp/vin_pp))

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True)
ax[0].plot(t, vg*1000, color='b'); ax[0].set_ylabel('Vin / mV')
ax[0].set_title('input at gate'); ax[0].grid(True)
ax[1].plot(t, vd, color='r'); ax[1].set_xlabel('t / ms'); ax[1].set_ylabel('Vout / V')
ax[1].set_title('output at drain'); ax[1].grid(True)
plt.tight_layout(); plt.savefig('nmos_cs.png', dpi=150)
print('OK -> nmos_cs.png')