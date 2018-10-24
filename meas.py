class pnp:
    def __init__(self, smu):
        self.smu = smu
        self.E=0
        self.C=4
        self.B=2
        self.channels=['x', 'B', 'x', 'C']
        
    def hfe(self, Ic=1e-3, Vce=-3, minhfe=10, Ic_max=0.15):
        B=self.B
        C=self.C
        smu = self.smu
        smu.connect([B,C])
        smu.search(B, start=-0.01, stop=-1, rate=20, i_lim=-Ic/minhfe) #ASV B, 0, 1, rate=200, i_compl=1e-4
        smu.sense_i(C, v=Vce, i_target=-Ic, i_lim=12*Ic) #AVI C, Vc=1, Ic_target=1e-3, ic_comp=1.2e-3
        smu.search_timing(hold=10e-3, delay=10e-3)
        smu.search_cfg(op='FBpos', meas="searchIsenseVI") #ASM 1,4,5e-4
        smu.write("MM6")
        smu.xe()
        smu.disconnect()
        r=smu.readresult()
        d=smu.parseresult(r, self.channels)
        return d['I_C'][0]/d['I_B'][0]
        
