from subprocess import Popen, CREATE_NEW_CONSOLE
import numpy as np

ELES = [0.2, 0.5, 1.0, 1.5]
ERES = np.array([10, 15, 20, 50])

i = 0
for l in ELES:
    for R in ERES:
        i += 1
        L = R*1.6119915*l
        ne = min(int(L//(1.5*l)), 80)
        print(ne, l, R)
        proc = Popen(
            f'c:/Users/david/Desktop/FEM/.venv/Scripts/python.exe nolocal_runner_plane_stress.py {L} {l} {ne}', creationflags=CREATE_NEW_CONSOLE)
        if not i % 4:
            Popen.communicate(proc)
