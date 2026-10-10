# thevenin.py —— 原电路: 10V + R1=4k + R2=6k；理论 V_th=6V, R_th=2.4k
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import numpy as np

def op(circuit, names):
    o = circuit.simulator().operating_point()
    return {n: float(np.asarray(o[n]).flat[0]) for n in names}

# 1) 开路电压
c1 = Circuit('open circuit')
c1.V('s', 'vcc', c1.gnd, 10@u_V)
c1.R('1', 'vcc', 'A', 4000@u_Ohm)
c1.R('2', 'A', c1.gnd, 6000@u_Ohm)
v_oc = op(c1, ['A'])['A']
print('1) 开路电压 V_th = %.4f V   (理论 6.0000)' % v_oc)

# 2) 短路电流：串一个 0V 电源当电流表（分支名是 'v'+元件名）
c2 = Circuit('short circuit')
c2.V('s', 'vcc', c2.gnd, 10@u_V)
c2.R('1', 'vcc', 'A', 4000@u_Ohm)
c2.R('2', 'A', c2.gnd, 6000@u_Ohm)
c2.V('amp', 'A', c2.gnd, 0@u_V)
o2 = c2.simulator().operating_point()
i_sc = abs(float(np.asarray(o2.branches['vamp']).flat[0]))
print('2) 短路电流 I_sc = %.4f mA  ->  R_th = %.1f ohm   (理论 2400)' % (i_sc*1000, v_oc/i_sc))

# 3) 原电路带载 RL=3k
c3 = Circuit('original + load')
c3.V('s', 'vcc', c3.gnd, 10@u_V)
c3.R('1', 'vcc', 'A', 4000@u_Ohm)
c3.R('2', 'A', c3.gnd, 6000@u_Ohm)
c3.R('L', 'A', c3.gnd, 3000@u_Ohm)
v_orig = op(c3, ['A'])['A']
print('3) 原电路带载 V_L = %.4f V   (理论 3.3333)' % v_orig)

# 4) 戴维南等效电路带载
c4 = Circuit('thevenin + load')
c4.V('th', 'x', c4.gnd, v_oc@u_V)
c4.R('th', 'x', 'A', 2400@u_Ohm)
c4.R('L', 'A', c4.gnd, 3000@u_Ohm)
v_th = op(c4, ['A'])['A']
print('4) 等效电路带载 V_L = %.4f V   两者一致? %s' % (v_th, abs(v_orig-v_th) < 1e-9))