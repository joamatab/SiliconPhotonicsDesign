import lumapi

s = lumapi.FDTD()
s.load("grating_coupler_2D.fsp")
s.switchtolayout()
s.save()
