# rc_lp.py  —— RC 低通滤波：R=1kΩ, C=1µF, 理论 fc≈159Hz
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import numpy as np

R_OHM, C_F = 1000.0, 1e-6
fc = 1.0/(2*np.pi*R_OHM*C_F)
print('手算 fc = %.2f Hz' % fc)

c = Circuit('RC low-pass')
c.SinusoidalVoltageSource('in', 'vin', c.gnd, amplitude=1@u_V, frequency=1@u_kHz)
c.R('1', 'vin', 'vout', R_OHM@u_Ohm)
c.C('1', 'vout', c.gnd, C_F@u_F)
sim = c.simulator()

# AC 扫频：看幅频特性
ac = sim.ac(start_frequency=1@u_Hz, stop_frequency=100@u_kHz,
            number_of_points=50, variation='dec')
f = np.asarray(ac.frequency).real
g = np.abs(np.asarray(ac['vout']))
i = int(np.argmin(np.abs(f-fc)))
print('AC 在 fc 处增益 = %.4f  (理论 0.7071)' % g[i])

# 瞬态：1kHz 正弦输入，看被衰减多少
tr = sim.transient(step_time=5@u_us, end_time=5@u_ms)
vout = np.asarray(tr['vout']).real
print('瞬态稳态幅度 = %.4f V  (理论 %.4f)' % (
    np.max(np.abs(vout[-200:])), 1/np.sqrt(1+(1000/fc)**2)))

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
ax[0].semilogx(f, 20*np.log10(g)); ax[0].axvline(fc, color='r', ls='--', label='fc=%.0fHz' % fc)
ax[0].set_xlabel('f / Hz'); ax[0].set_ylabel('gain / dB'); ax[0].set_title('RC low-pass Bode')
ax[0].legend(); ax[0].grid(True, which='both')
ax[1].plot(np.asarray(tr.time).real*1000, vout)
ax[1].set_xlabel('t / ms'); ax[1].set_ylabel('Vout / V'); ax[1].set_title('transient @1kHz')
ax[1].grid(True)
plt.tight_layout(); plt.savefig('rc_filter.png', dpi=150)
print('OK -> rc_filter.png')