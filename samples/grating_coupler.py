import pylut
from pylut.grating_coupler import sweep

scripts = sweep(
    sweep_variable="thick_Si", sweep_start=205e-9, sweep_stop=240e-9, sweep_points=3,
)
pylut.write_scripts(scripts)
print(scripts["dirpath"])

# pylut.run_fdtd(scripts, dirpath)
