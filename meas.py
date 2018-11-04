import logging
import time

log = logging.getLogger(__name__)

class measurement:
    def __init__(self, smu):
        self.smu=smu
        self.channels = self.channels=['_slot_cpu', '_slot1', '_slot2', '_slot3', '_slot4', '_slot5', '_slot6', '_slot7', '_slot8']
        
    def connect(self):
        cc = []
        for ch in self.channels:
            if not ch.startswith('_slot'):
                cc.append(ch)

        self.smu.connect(cc)

    def xe_and_read(self, delay=0.0):
        self.smu.xe()
        time.sleep(delay)
        
        self.smu.disconnect()
        
        print(self.smu.errors())
        
        r=self.smu.readresult()
        #print(r)
        d=self.smu.parseresult(r, self.channels)
        
        return d
        pass


class bjt(measurement):
    pass

class pnp(bjt):
    def __init__(self, smu, B=2, C=4):
        assert(B!=C)
        self.smu = smu
        self.C=C
        self.B=B
        self.channels=['_slot1', '_slot2', '_slot3', '_slot4', '_slot5', '_slot6', '_slot7', '_slot8']
        self.channels[C]='C'
        self.channels[B]='B'

    def hfe(self, Ic=1e-3, Vce=-3, minhfe=10, Ic_max=0.15):
        B=self.B
        C=self.C
        smu = self.smu
        self.connect()
        smu.search(B, start=-0.01, stop=-1, rate=20, i_lim=-Ic/minhfe) #ASV B, 0, 1, rate=200, i_compl=1e-4
        smu.sense_i(C, v=Vce, i_target=-Ic, i_lim=12*Ic) #AVI C, Vc=1, Ic_target=1e-3, ic_comp=1.2e-3
        smu.search_timing(hold=10e-3, delay=10e-3)
        smu.search_cfg(op='FBpos', meas="searchIsenseVI") #ASM 1,4,5e-4
        smu.write("MM6")

        d=self.xe_and_read()
        return d['I_C'][0]/d['I_B'][0]

    def vce_sat(self):
        B=self.B
        c=self.C
        self.connect()
        smu.sweep_i(C, start=-1e-6, stop=-100e-3, v_lim=30, mode='log')
        smu.sweep_i_follow(B, start=-1e-6, stop=-10e-3, v_lim=-2)
        #smu.current(B,i=1e-3,v_lim=2)
        smu.write("MM2,2,4\n")

        d=self.xe_and_read()
        
        return d

    #Measure BE reverse voltage
    def vebo(self, Vebo_test=10, Iebo=1e-6, Vce=-1, Ic_max=-0.001):
        C=self.C
        B=self.B
        self.connect()
        
        smu.voltage(C, Vce, -Ic_max)
        smu.current(B, Iebo, v_lim=Vebo_test)
        smu.write("MM1,2,4\n")

        d=self.xe_and_read()

        return d['V_B'][0]

    def ce_curve(self, Ibe=-100e-6, Vc_max=-30, Ic_max=-0.15):
       B=self.B
       C=self.C
    
       self.connect()
       
       smu.current(B, Ibe, v_lim=-4)
       smu.sweep_v(C, start=-0.1, stop=Vc_max, i_lim=Ic_max, mode='log')
       smu.write("MM2,2,4\n")

       smu.xe()
       smu.zero()
       smu.disconnect()

       d=self.xe_and_read()

       return d
                                                   
    def hfe_curve(self, Vce=-5.0, Ic_max=-0.15):
        B=self.B
        C=self.C
        smu.connect([B,C])
        
        smu.voltage(C, Vce, i_lim=Ic_max)
        smu.sweep_timing(hold=0.05, delay=0.05)
        smu.sweep_i(B, start=-1e-6, stop=-0.9e-3, v_lim=4, mode='log')
        smu.write("MM2,2,4\n")

        d=self.xe_and_read()

        return d

class npn(bjt):
    def __init__(self, smu, B=2, C=4):
        assert(B!=C)
        self.smu = smu
        self.C=C
        self.B=B
        self.channels=['_slot1', '_slot2', '_slot3', '_slot4', '_slot5', '_slot6', '_slot7', '_slot8']
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
                        
        d=self.xe_and_read()

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

        d=self.xe_and_read()

        return d['I_C'][0]/d['I_B'][0]

    def vebo(self, Vebo_test=10, Iebo=1e-6, Vce=1, Ic_max=0.001):
        smu = self.smu
        B = self.B
        C = self.B
        smu.connect([B,C])
        
        smu.voltage(C, Vce, Ic_max)
        smu.current(B, -Iebo, v_lim=-Vebo_test)
        smu.write("MM1,2,4\n")

        d=self.xe_and_read()
        
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

        d=self.xe_and_read()
        
        return d

class jfet(measurement):
    pass

class njfet(jfet):
    def __init__(self, smu, G=2, D=4):
        assert(D!=G)
        self.smu = smu
        self.G=G
        self.D=D
        self.channels=['_slot1', '_slot2', '_slot3', '_slot4', '_slot5', '_slot6', '_slot7', '_slot8']
        self.channels[G]='G'
        self.channels[D]='D'    

    def ids_vds_curve(self, Vgs=0.0, Vds_max=10, Ids_max=0.1, Igs_max=1e-3):
        smu=self.smu
        G=self.G
        D=self.D        
        smu.connect([G,D])
        
        smu.voltage(G, Vgs, i_lim=Igs_max)
        smu.sweep_v(D, start=0.01, stop=Vds_max, i_lim=Ids_max, mode='log')
        smu.write("MM2,2,4\n")

        d=self.xe_and_read()

        return d

    def vgs_ids_curve(self, Vds=10, Vgs_min=-2, Vgs_max=0.5, Ids_max=10e-3):
        smu=self.smu
        G=self.G
        D=self.D
        smu.connect([G,D])
        
        smu.voltage(D, Vds, i_lim=Ids_max)
        smu.sweep_v(G, start=Vgs_min, stop=Vgs_max, i_lim=1e-3)
        smu.write("MM2,2,4\n")

        d=self.xe_and_read()

        return d

    def idss(self, Vds=10.0, Vgs=0.0, Ids_max=0.1):
        smu=self.smu
        G=self.G
        D=self.D
        smu.connect([G,D])
        
        smu.voltage(G, Vgs, i_lim=1e-3)
        smu.voltage(D, Vds, i_lim=Ids_max)        
        smu.write("MM1,2,4")

        d=self.xe_and_read()
        return d['I_D'][0]
    
    def vgs_off(self, Ids=1e-6, Vds=1, Ids_max=0.15):
        smu=self.smu
        G=self.G
        D=self.D        
        smu.connect([D,G])
        
        smu.search(G, start=-2, stop=1, rate=10, i_lim=100e-6)
        smu.sense_i(D, v=Vds, i_target=Ids, i_lim=1.2*Ids)
        smu.search_timing(hold=10e-3, delay=10e-3)
        smu.search_cfg(op='FBpos', meas="searchVsenseVI") #ASM 1,4,5e-4        
        smu.write("MM6")

        d=self.xe_and_read()
        
        return d['V_G'][0]

class mosfet(measurement):
    pass

class nmosfet(mosfet):
    def __init__(self, smu, G=2, D=4):
        assert(D!=G)
        self.smu = smu
        self.G=G
        self.D=D
        self.channels=['_slot1', '_slot2', '_slot3', '_slot4', '_slot5', '_slot6', '_slot7', '_slot8']
        self.channels[G]='G'
        self.channels[D]='D'    
        
        def ids_vds(self, Vgs=0.0, Vds_max=10, Ids_max=0.1, Igs_max=1e-3, P_max=1):
            smu=self.smu
            G=self.G
            D=self.D            
            smu.connect([G,D])
            
            smu.voltage(G, Vgs, i_lim=Igs_max)
            smu.sweep_v(D, start=0.01, stop=Vds_max, i_lim=Ids_max, mode='log', p_lim=P_max)
            smu.write("MM2,2,4\n")

            time.sleep(0.5)
            d=self.xe_and_read(delay=0.5)
    
            return d

        def vgs_ids(self, Vds=5, Vgs_min=0, Vgs_max=12, Ids_max=10e-3):
            smu=self.smu
            G=self.G
            D=self.D            
            smu.connect([G,D])
            
            smu.voltage(D, Vds, i_lim=Ids_max)            
            smu.sweep_v(G, start=Vgs_min, stop=Vgs_max, i_lim=1e-3)
            smu.write("MM2,2,4\n")
            
            d=self.xe_and_read()
            
            return d
        
        
        def idss(self, Vds=10.0, Vgs=0.0, Ids_max=1e-4):
            smu=self.smu
            G=self.G
            d=self.D            
            smu.connect([G,D])
            
            smu.voltage(G, Vgs, i_lim=1e-3)
            smu.voltage(D, Vds, i_lim=Ids_max)
            smu.write("MM1,2,4")
            
            d=self.xe_and_read()
            
            return d['I_D'][0]
        
        def vgs_on(self, Ids=1e-3, Vds=10, Ids_max=0.15):
            smu=self.smu
            G=self.G
            D=self.D            
            smu.connect([D,G])
            
            smu.search(G, start=0, stop=10, rate=10, i_lim=100e-6)
            smu.sense_i(D, v=Vds, i_target=Ids, i_lim=1.2*Ids)
            smu.search_timing(hold=10e-3, delay=10e-3)
            smu.search_cfg(op='FBpos', meas="searchVsenseVI") #ASM 1,4,5e-4
            smu.write("MM6")

            d=self.xe_and_read(delay=2)

            return d['V_G'][0]

class pmosfet(mosfet):
    def __init__(self, smu, G=4, D=2):
        super(pmosfet, self).__init__(smu=smu)        
        assert(D!=G)
        self.G=G
        self.D=D
        self.channels[G]='G'
        self.channels[D]='D'

    def ids_vds(self, Vgs=0.0, Vds_max=-10, Ids_max=0.1, Igs_max=-1e-3, P_max=1):
        smu=self.smu
        G=self.G
        D=self.D
            
        smu.connect([G,D])

        smu.voltage(G, Vgs, i_lim=Igs_max)
        smu.sweep_v(D, start=-0.01, stop=Vds_max, i_lim=Ids_max, mode='log', p_lim=P_max)
        smu.write("MM2,2,4\n")
            
        d=self.xe_and_read(delay=2)
            
        return d
        
    def ids_vgs(self, Vds=-5, Vgs_min=0, Vgs_max=-12, Ids_max=-10e-3):
        smu=self.smu
        G=self.G
        D=self.D        
        smu.connect([G,D])
        
        smu.voltage(D, Vds, i_lim=Ids_max)
            
        smu.sweep_v(G, start=Vgs_min, stop=Vgs_max, i_lim=1e-3)
        smu.write("MM2,2,4\n")
            
        return self.xe_and_read()
        
        
    def idss(self, Vds=-10.0, Vgs=0.0, Ids_max=-1e-3):
        smu=self.smu
        G=self.G
        D=self.D        
        smu.connect([G,D])
        
        smu.voltage(G, Vgs, i_lim=1e-6)
        smu.voltage(D, Vds, i_lim=Ids_max)            
        smu.write("MM1,2,4")
        
        d=self.xe_and_read()
        
        return d['I_D'][0]
        
    def vgs_on(self, Ids=10e-3, Vds=-10, Ids_max=0.15):
        smu=self.smu
        D=self.D
        G=self.G
        smu.connect([D,G])
        
        smu.search(G, start=-0.01, stop=-10, rate=10, i_lim=1e-3)
        smu.sense_i(D, v=Vds, i_target=-Ids, i_lim=2*Ids)
        smu.search_timing(hold=10e-3, delay=10e-3)
        smu.search_cfg(op='FBpos', meas="searchVsenseVI") #ASM 1,4,5e-4
        
        smu.write("MM6")

        d=self.xe_and_read()
        
        return d['V_G'][0]

class zener(measurement):
    def __init__(self, smu, A=2):
        super(zener, self).__init__(smu=smu)        
        self.A=A
        self.channels[A]='A'

    def fwd_curve(self, v_lim=40, i_lim=100e-3):
        assert(v_lim>0)
        assert(i_lim>0)
        
        smu=self.smu
        A=self.A
        
        smu.connect([A])
        smu.sweep_i(A, start=1e-8, stop=i_lim, v_lim=v_lim, mode='log', n=50)
        smu.write("MM2,2\n")
        
        d=self.xe_and_read()

        return d

    def rev_curve(self, v_lim=-40, i_lim=-40e-3):
        assert(v_lim < 0)
        assert(i_lim < 0)
        
        smu=self.smu
        A=self.A        
        smu.connect([A])
        
        smu.sweep_i(A, start=-1e-8, stop=i_lim, v_lim=v_lim, mode='log', n=50, p_lim=5)
        smu.write("MM2,2\n")
        smu.sweep_timing(hold=0.1, delay=0.1)

        d=self.xe_and_read()

        return d

    def vz(self, V_test=40, Iz=10e-3):
        smu=self.smu
        A=self.A        
        smu.connect([A])
        
        smu.current(A, -Iz, v_lim=V_test)
        smu.write("MM1,2\n")

        d=self.xe_and_read()

        return -d['V_A'][0]

    def rz(self, i1=10e-3, i2=20e-3, V_test=40):
        vz1=self.vz(Iz=i1, V_test=V_test)
        vz2=self.vz(Iz=i2, V_test=V_test)
        Rz=(vz2-vz1)/(i2-i1)
        
        print("Vz@%f mA = %f" % (1e3*i1, vz1))
        print("Vz@%f mA = %f" % (1e3*i2, vz2))
        print("Rz = %f"%(Rz))
    
        print("Done")
