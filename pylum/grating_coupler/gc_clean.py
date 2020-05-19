if __name__ == "__main__":
    import lumapi

    s = lumapi.FDTD()
    s.load("grating_coupler_2D.fsp")
    s.switchtolayout()
    s.save()
