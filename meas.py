import logging

log = logging.getLogger(__name__)

class pnp:
    def __init__(self, smu, B=2, C=4):
        assert(B!=C)
        self.smu = smu
        self.C=C
        self.B=B
        self.channels=['slot1', 'slot2', 'slot3', 'slot4', 'slot5', 'slot6', 'slot7', 'slot8']
        self.channels[C]='C'
        self.channels[B]='B'

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

    def vce_sat(self):
        B=self.B
        c=self.C
        smu.connect([B,C])
        smu.sweep_i(C, start=-1e-6, stop=-100e-3, v_lim=30, mode='log')
        smu.sweep_i_follow(B, start=-1e-6, stop=-10e-3, v_lim=-2)
        #smu.current(B,i=1e-3,v_lim=2)
        smu.write("MM2,2,4\n")

        smu.xe()
        smu.zero()
        smu.disconnect()

        r=smu.readresult()

        d=smu.parseresult(r, self.channels)

        return d

    #Measure BE reverse voltage
    def vebo(self, Vebo_test=10, Iebo=1e-6, Vce=-1, Ic_max=-0.001):
        smu.connect([B,C])
        smu.voltage(C, Vce, -Ic_max)
        smu.current(B, Iebo, v_lim=Vebo_test)
        smu.write("MM1,2,4\n")
        smu.xe()
        #print(smu.opstat())
        smu.zero()
        smu.disconnect()
        print(smu.error())

        r=smu.readresult()
        #print(r)
        d=smu.parseresult(r, self.channels)
        print(d)
        return d['V_B'][0]

    def ce_curve(self, Ibe=-100e-6, Vc_max=-30, Ic_max=-0.15):
       B=self.B
       C=self.C
    
       smu.connect([B,C])
       smu.current(B, Ibe, v_lim=-4)
       #smu.sweep_timing(hold=0.05, delay=0.05)

       smu.sweep_v(C, start=-0.1, stop=Vc_max, i_lim=Ic_max, mode='log')
       smu.write("MM2,2,4\n")

       smu.xe()
       smu.zero()
       smu.disconnect()

       r=smu.readresult()
       #print(r)
       d=smu.parseresult(r, self.channels)

       return d
                                                   
    def hfe_curve(self, Vce=-5.0, Ic_max=-0.15):
       smu.connect([B,C])
       smu.voltage(C, Vce, i_lim=Ic_max)
       smu.sweep_timing(hold=0.05, delay=0.05)

       smu.sweep_i(B, start=-1e-6, stop=-0.9e-3, v_lim=4, mode='log')
       smu.write("MM2,2,4\n")

       smu.xe()
       smu.zero()
       smu.disconnect()

       r=smu.readresult()
       #print(r)
       d=smu.parseresult(r, self.channels)

       return d

class npn:
    def __init__(self, smu, B=2, C=4):
        assert(B!=C)
        self.smu = smu
        self.C=C
        self.B=B
        self.channels=['slot1', 'slot2', 'slot3', 'slot4', 'slot5', 'slot6', 'slot7', 'slot8']
        self.channels[C]='C'
        self.channels[B]='B'
        
        
    def hfe_curve(self, Vce=5.0, Ic_max=0.15):
        smu = self.smu
        B = self.B
        C = self.B
        smu.connect([B,C])
        smu.voltage(C, Vce, i_lim=Ic_max)
        smu.sweep_timing(hold=0.05, delay=0.05)

        smu.sweep_i(B, start=1e-6, stop=0.9e-3, v_lim=4, mode='log')
        smu.write("MM2,2,4\n")
                        
        smu.xe()
        smu.zero()
        smu.disconnect()

        r=smu.readresult()
        d=parseresult(r, self.channels)

        return d

    def hfe(self, Ic=1e-3, Vce=1, minhfe=10, Ic_max=0.15):
        smu = self.smu
        B = self.B
        C = self.B
        smu.connect([B,C])
        smu.search(B, start=0, stop=1, rate=200, i_lim=Ic/minhfe) #ASV B, 0, 1, rate=200, i_compl=1e-4
        smu.sense_i(C, v=Vce, i_target=Ic, i_lim=1.2*Ic) #AVI C, Vc=1, Ic_target=1e-3, ic_comp=1.2e-3
        smu.search_timing(hold=10e-3, delay=10e-3)
        smu.search_cfg(op='FBpos', meas="searchIsenseVI") #ASM 1,4,5e-4
        smu.write("MM6")
        smu.xe()
        smu.disconnect()
        r=smu.readresult()
        d=parseresult(r, self.channels)
        #print(r)
        return d['I_C'][0]/d['I_B'][0]

    def vebo(self, Vebo_test=10, Iebo=1e-6, Vce=1, Ic_max=0.001):
        smu = self.smu
        B = self.B
        C = self.B
        smu.connect([B,C])
        smu.voltage(C, Vce, Ic_max)
        smu.current(B, -Iebo, v_lim=-Vebo_test)
        smu.write("MM1,2,4\n")
        smu.xe()
        #print(smu.opstat())
        smu.zero()
        smu.disconnect()

        r=smu.readresult()
        #print(r)
        d=parseresult(r, self.channels)
        print(d)
        return d['V_B'][0]

    def vce_sat(self):
        smu = self.smu
        B = self.B
        C = self.B
        smu.connect([B,C])
        smu.sweep_i(C, start=1e-6, stop=100e-3, v_lim=30, mode='log')
        smu.sweep_i_follow(B, start=1e-6, stop=10e-3, v_lim=2)
        #smu.current(B,i=1e-3,v_lim=2)
        smu.write("MM2,2,4\n")

        smu.xe()
        smu.zero()
        smu.disconnect()

        r=smu.readresult()

        d=parseresult(r, self.channels)
        
        return d

class njfet:
    def __init__(self, smu, G=2, D=4):
        assert(D!=G)
        self.smu = smu
        self.G=G
        self.D=D
        self.channels=['slot1', 'slot2', 'slot3', 'slot4', 'slot5', 'slot6', 'slot7', 'slot8']
        self.channels[G]='G'
        self.channels[D]='D'    

    def meas_njfet(Vgs=0.0, Vds_max=10, Ids_max=0.1, Igs_max=1e-3):
        smu.connect([G,D])
        smu.voltage(G, Vgs, i_lim=Igs_max)

        smu.sweep_v(D, start=0.01, stop=Vds_max, i_lim=Ids_max, mode='log')
        smu.write("MM2,2,4\n")

        smu.xe()
        smu.zero()
        smu.disconnect()

        r=smu.readresult()
        #print("RESULT: %s" % str(r))
        d=parseresult(r, channels)

        return d

    def meas_vgs_ids(Vds=10, Vgs_min=-2, Vgs_max=0.5, Ids_max=10e-3):
        smu.connect([G,D])
        smu.voltage(D, Vds, i_lim=Ids_max)

        smu.sweep_v(G, start=Vgs_min, stop=Vgs_max, i_lim=1e-3)
        smu.write("MM2,2,4\n")

        smu.xe()
        smu.zero()
        smu.disconnect()

        r=smu.readresult()
        #print("RESULT: %s" % str(r))
        d=parseresult(r, channels)

        return d


    def meas_idss(Vds=10.0, Vgs=0.0, Ids_max=0.1):
        smu.connect([G,D])
        smu.voltage(G, Vgs, i_lim=1e-3)
        smu.voltage(D, Vds, i_lim=Ids_max)
        
        smu.write("MM1,2,4")
        smu.xe()
        smu.disconnect()
        r=smu.readresult()
        d=parseresult(r, channels)
        return d['I_D'][0]
    
    def meas_vgs_off(Ids=1e-6, Vds=1, Ids_max=0.15):
        smu.connect([D,G])
        smu.search(G, start=-2, stop=1, rate=10, i_lim=100e-6)
        smu.sense_i(D, v=Vds, i_target=Ids, i_lim=1.2*Ids)
        smu.search_timing(hold=10e-3, delay=10e-3)
        smu.search_cfg(op='FBpos', meas="searchVsenseVI") #ASM 1,4,5e-4
        #smu.search_cfg(op='ramp_gt', meas="searchVsenseVI", itime=1e-3) #ASM 1,4,5e-4
        
        smu.write("MM6")
        smu.xe()
        #time.sleep(2)
        #print(smu.opstat())
        smu.zero()
        smu.disconnect()
        r=smu.readresult()
        #print(r)
        d=parseresult(r, channels)
        return d['V_G'][0]

class nmosfet:
    def __init__(self, smu, G=2, D=4):
        assert(D!=G)
        self.smu = smu
        self.G=G
        self.D=D
        self.channels=['slot1', 'slot2', 'slot3', 'slot4', 'slot5', 'slot6', 'slot7', 'slot8']
        self.channels[G]='G'
        self.channels[D]='D'    
        
        def meas_nfet(Vgs=0.0, Vds_max=10, Ids_max=0.1, Igs_max=1e-3, P_max=1):
            smu.connect([G,D])
            smu.voltage(G, Vgs, i_lim=Igs_max)
    
            smu.sweep_v(D, start=0.01, stop=Vds_max, i_lim=Ids_max, mode='log', p_lim=P_max)
            smu.write("MM2,2,4\n")

            smu.xe()
            time.sleep(0.5)
            #print(smu.errors())
            
            smu.zero()
            #print(smu.opstat())
            
            time.sleep(0.5)
            smu.disconnect()
            
            r=smu.readresult()
            #print("RESULT: %s" % str(r))
            d=smu.parseresult(r, channels)
    
            return d

        def meas_vgs_ids(Vds=5, Vgs_min=0, Vgs_max=12, Ids_max=10e-3):
            smu.connect([G,D])
            smu.voltage(D, Vds, i_lim=Ids_max)
            
            smu.sweep_v(G, start=Vgs_min, stop=Vgs_max, i_lim=1e-3)
            smu.write("MM2,2,4\n")
            
            smu.xe()
            smu.zero()
            smu.disconnect()
            
            r=smu.readresult()
            #print("RESULT: %s" % str(r))
            d=smu.parseresult(r, channels)
            
            return d
        
        
        def meas_idss(Vds=10.0, Vgs=0.0, Ids_max=1e-4):
            smu.connect([G,D])
            smu.voltage(G, Vgs, i_lim=1e-3)
            smu.voltage(D, Vds, i_lim=Ids_max)
            
            smu.write("MM1,2,4")
            smu.xe()
            smu.disconnect()
            r=smu.readresult()
            d=smu.parseresult(r, channels)
            return d['I_D'][0]
        
        def meas_vgs_on(Ids=1e-3, Vds=10, Ids_max=0.15):
            smu.connect([D,G])
            smu.search(G, start=0, stop=10, rate=10, i_lim=100e-6)
            smu.sense_i(D, v=Vds, i_target=Ids, i_lim=1.2*Ids)
            smu.search_timing(hold=10e-3, delay=10e-3)
            smu.search_cfg(op='FBpos', meas="searchVsenseVI") #ASM 1,4,5e-4
            #smu.search_cfg(op='ramp_gt', meas="searchVsenseVI", itime=1e-3) #ASM 1,4,5e-4
            
            smu.write("MM6")
            smu.xe()
            #time.sleep(2)
            print(smu.opstat())
            smu.zero()
            smu.disconnect()
            r=smu.readresult()
            #print(r)
            d=smu.parseresult(r, channels)
            return d['V_G'][0]

class pmosfet:
    def __init__(self, smu, G=2, D=4):
        assert(D!=G)
        self.smu = smu
        self.G=G
        self.D=D
        self.channels=['slot1', 'slot2', 'slot3', 'slot4', 'slot5', 'slot6', 'slot7', 'slot8']
        self.channels[G]='G'
        self.channels[D]='D'

        def meas_pfet(Vgs=0.0, Vds_max=-10, Ids_max=0.1, Igs_max=-1e-3, P_max=1):
            smu.connect([G,D])
            smu.voltage(G, Vgs, i_lim=Igs_max)
            
            smu.sweep_v(D, start=-0.01, stop=Vds_max, i_lim=Ids_max, mode='log', p_lim=P_max)
            smu.write("MM2,2,4\n")
            
            smu.xe()
            #Wait for 5 seconds, larger FET needs a lot of autoscaling in measurements due to
            #curreny limits being hit all the time
            time.sleep(5)
            #print(smu.errors())
            
            smu.zero()
            #print(smu.opstat())
            
            time.sleep(0.5)
            smu.disconnect()
            
            r=smu.readresult()
            #print("RESULT: %s" % str(r))
            d=smu.parseresult(r, channels)
            
            return d
        
        def meas_vgs_ids(Vds=-5, Vgs_min=0, Vgs_max=-12, Ids_max=-10e-3):
            smu.connect([G,D])
            smu.voltage(D, Vds, i_lim=Ids_max)
            
            smu.sweep_v(G, start=Vgs_min, stop=Vgs_max, i_lim=1e-3)
            smu.write("MM2,2,4\n")
            
            smu.xe()
            smu.zero()
            smu.disconnect()
            
            r=smu.readresult()
            #print("RESULT: %s" % str(r))
            d=smu.parseresult(r, channels)
            
            return d
        
        
        def meas_idss(Vds=-10.0, Vgs=0.0, Ids_max=-1e-3):
            smu.connect([G,D])
            smu.voltage(G, Vgs, i_lim=1e-6)
            smu.voltage(D, Vds, i_lim=Ids_max)
            
            smu.write("MM1,2,4")
            smu.xe()
            smu.disconnect()
            r=smu.readresult()
            d=smu.parseresult(r, channels)
            return d['I_D'][0]
        
        def meas_vgs_on(Ids=10e-3, Vds=-10, Ids_max=0.15):
            smu.connect([D,G])
            smu.search(G, start=-0.01, stop=-10, rate=10, i_lim=1e-3)
            smu.sense_i(D, v=Vds, i_target=-Ids, i_lim=2*Ids)
            smu.search_timing(hold=10e-3, delay=10e-3)
            smu.search_cfg(op='FBpos', meas="searchVsenseVI") #ASM 1,4,5e-4
            #smu.search_cfg(op='ramp_gt', meas="searchVsenseVI", itime=1e-3) #ASM 1,4,5e-4
            
            smu.write("MM6")
            smu.xe()
            #time.sleep(2)
            #print(smu.opstat())
            #print(smu.errors())
            smu.zero()
            smu.disconnect()
            r=smu.readresult()
            #print(r)
            d=smu.parseresult(r, channels)
            return d['V_G'][0]

class zener:
    def __init__(self, smu, A=2):
        self.smu = smu
        self.A=A
        self.channels=['slot1', 'slot2', 'slot3', 'slot4', 'slot5', 'slot6', 'slot7', 'slot8']
        self.channels[A]='A'

    def meas_diode():
        smu.connect([A])
        smu.sweep_i(A, start=1e-8, stop=100e-3, v_lim=20, mode='log', n=50)
        smu.write("MM2,6\n")
        
        smu.xe()
        smu.zero()
        smu.disconnect()

        r=smu.readresult()
        #print(r)

        d=parseresult(r, channels)

        return d

    def meas_diode_rev():
        smu.connect([A])
        #smu.sweep_v(A, start=-0.1, stop=-10, i_lim=0.01, n=40)
        smu.sweep_i(A, start=-1e-8, stop=-40e-3, v_lim=-20, mode='log', n=50, p_lim=5)
        
        smu.write("MM2,6\n")
        smu.sweep_timing(hold=0.05, delay=0.05)
        smu.xe()
        #    time.sleep(15)
        smu.zero()
        smu.disconnect()
        smu.status()
        
        r=smu.readresult()
        #print(r)
        d=parseresult(r, channels)

        return d
    
    def vz(V_test=40, Iz=10e-3):
        smu.connect([A])
        smu.current(A, -Iz, v_lim=V_test)
        smu.write("MM1,6\n")
        smu.xe()
        print(smu.opstat())
        smu.zero()
        smu.disconnect()
        
        r=smu.readresult()
        print(r)
        d=parseresult(r, channels)
        #print(d)
        return -d['V_A'][0]
    
    #diode=meas_diode()
    #rev=None
    rev=meas_diode_rev()
    i1=0.1e-3
    vz1=vz(Iz=i1)
    i2=35e-3
    vz2=vz(Iz=i2)
    Rz=(vz2-vz1)/(i2-i1)
    
    print("Vz@%f mA = %f" % (1e3*i1, vz1))
    print("Vz@%f mA = %f" % (1e3*i2, vz2))
    print("Rz = %f"%(Rz))
    
    print("Done")
