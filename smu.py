import Gpib
import time
import numpy as np
import logging

log = logging.getLogger(__name__)

class ParamError(Exception):
    pass

class hp4142b(object):
    
    def __init__(self, inst):
        self.mode = "NORM"
        self.inst = inst
        self.reset()
        self.write("FMT1,1")
        print(self.idn())

    def channels(self, channels):
        self.channels = channels
        
    def write(self, cmd):
        if not cmd.endswith("\n"):
            cmd = cmd+"\n"
        #print("CMD: %s" % cmd)
        return self.inst.write(cmd)

    def idn(self):
        self.write("*IDN?")
        try:
            return(self.inst.read().decode('ascii'))
        except:
            print(self.gpib_err(self.inst.ibsta()))
            return None   

    def errors(self):
        self.write("ERR?")
        try:
            return(self.inst.read().decode('ascii'))
        except:
            print(self.gpib_err(self.inst.ibsta()))
            return None   
    
    def voltage(self, ch, v=0.0, range=0, i_lim=0.001, lim_mode=0):
        return self.write("DV%d,%d,%+.3e,%+.3e,%d\n" % ( ch, range, v, i_lim, lim_mode ))
    
    def pulsed_v(self, ch, base=0.0, pulse=0.0, range=0, i_lim=0.001):
        self.mode="PULSED"
        return self.write("PDV%d,%d,%+.3e,%+.3e,%+.3e"%(ch, range, base, pulse, i_lim))
    
    def pulsed_i(self, ch, base=0.0, pulse=0.0, v_lim=1):
        self.mode="PULSED"
        return self.write("PDI%d,%d,%+.3e,%+.3e,%+.3e"%(ch, range, base, pulse, v_lim))
    
    def current(self, ch, i=0.0, range=0, v_lim=1, lim_mode=0):
        return self.write("DI%d,%d,%+.3e,%+.3e,%d\n"%(ch, range, i, v_lim, lim_mode))

    def sweep_i(self, ch, mode='lin', range=0, start=0, stop=1e-3, n=50, v_lim=1, p_lim=1):
        self.mode="SWEEP"
        mode_n=1;
        if mode=='log':
            mode_n=2
        if mode=='dlin':
            mode_n=3
        if mode=='dlog':
            mode_n=4
        return self.write("WI%d,%d,%d,%+.3e,%+.3e,%d,%+.3e,%+.3e\n" % (ch, mode_n, range, start, stop, n, v_lim, p_lim))

    def sweep_v(self, ch, mode='lin', range=0, start=0, stop=1, n=50, i_lim=0.001, p_lim=1):
        self.mode="SWEEP"
        mode_n=1;
        if mode=='log':
            mode_n=2
        if mode=='dlin':
            mode_n=3
        if mode=='dlog':
            mode_n=4
        return self.write("WV%d,%d,%d,%+.3e,%+.3e,%d,%+.3e,%+.3e\n" % (ch, mode_n, range, start, stop, n, i_lim, p_lim))

    def sweep_i_follow(self, ch, range=0, start=0.001, stop=0.001, v_lim=1, p_lim=1):
        return self.write("WSI%d,%d,%+.3e,%+.3e,%+.3e,%+.3e"%(ch, range, start, stop, v_lim, p_lim))
        
    def sweep_v_follow(self, ch, range=0, start=0, stop=1, i_lim=0.001, p_lim=1):
        return self.write("WSV%d,%d,%+.3e,%+.3e,%+.3e,%+.3e"%(ch, range, start, stop, i_lim, p_lim))
    
    def sweep_timing(self, hold=0, delay=0):
        return self.write("WT%.3e,%3e" % (hold, delay))
    
    def search_cfg(self, op="FBpos", meas="searchV", itime=5e-3):
        operations={ 'FBpos': 1,
              'FBneg': 2,
              'ramp_gt': 3,
              'ramp_lt': 4 }
        
        measurements = {'searchV': 1,
                        'searchI': 2,
                        'searchVsenseVI': 3,
                        'searchIsenseVI': 4 }
        
        opcode=operations.get(op, None)
        if not opcode:
            raise ParamError("Unknown search mode %s" % op)
        
        mcode = measurements.get(meas, None)
        if not mcode:          
            raise ParamError("Unknown search measurement %s" % meas)
        
        self.write("ASM%d,%d,%f" % (opcode, mcode, itime))
        
    def search(self, ch, start=0, stop=1, rate=500, i_lim=1e-3):
        G=max(abs(start), abs(stop))
        D=abs(start-stop)
        #TODO: check range vs span - see manual
        self.write("ASV%d,%f,%f,%f,%f"%(ch, start, stop, rate, i_lim))
        
    def search_timing(self,hold=0.0, delay=0.0):
        assert hold>0.0 and delay>0.0
        
        self.write("AT%f,%f"%(hold, delay))

    def sense_i(self, ch, v=1.0, i_target=1e-4, i_lim=1e-3):
        self.write("AVI%d,%+.3e,%+.3e,%+.3e"%(ch, v, i_target, i_lim))
    
    def sense_v(self, ch, i=1e-3, v_target=0.1, v_lim=1):
        self.write("AIV%d,%+.3e,%+.3e,%+.3e"%(ch, i, v_target, v_lim))
        
    def connect(self,ch):
        cmd=""
        if ch:
            if type(ch)==type([]):
                cmd = "CN" + (",".join(list(map(str,ch)))) + "\n"
            else:
                cmd = "CN%s\n" % ch
        else:
            cmd="CN\n"
        self.write(cmd)

    def zero(self, ch=None):
        cmd=""
        if ch:
            if type(ch)==type([]):
                cmd = "DZ" + (",".join(list(map(str,ch)))) + "\n"
            else:
                cmd = "DZ%s\n" % ch
        else:
            cmd="DZ\n"
        self.write(cmd)
       
    def calibrate(self):
        self.write("CA")
        time.sleep(10)
        self.status()
        print("IBSTA: "+ self.gpib_err(self.inst.ibsta()))

        print("Calibrated")
    
    def disconnect(self,ch=None):
        cmd=""
        if ch:
            if type(ch)==type([]):
                cmd = "CL" + (",".join(list(map(str,ch)))) + "\n"
            else:
                cmd = "CL%s\n" % ch
        else:
            cmd="CL\n"
        self.write(cmd)
        
    def opstat(self):
        self.write("LOP?")
        codestring = self.readresult()
        codestring = codestring.replace("\n", "").replace("\r", "")
        codes = codestring[3:].split(",")

        codetotext = { '00': 'Not active',
               '01': 'V_SRC',
               '02': 'I_SRC',
               '03': 'I_SINK',
               '10': 'VS_limit',
               '11': 'V_compliance',
               '12': 'I_SRC_compliance',
               '13': 'I_SINK_compliance',
               '20': 'Oscillating',
               '30': 'HVU_not_settled'
              }
        
        return list(map(lambda c: codetotext[c], codes))
        
        
    def status(self):
        self.write("*STB?")
        st = self.inst.read().decode('ascii')
        print("Status: %s %s" %(st,  self.statusdecode(int(st))))
        
    def nub(self):
        self.write("NUB?")
        return self.readresult()
    
    def units(self):
        self.write("UNT?")
        return self.readresult()
    
    def reset(self):
        self.write("*RST")
        
    def readresult(self):
        readmore=True
        outdata=""
        ibread=""
        self._resdata = ""
    
        while readmore:
            try:
                ibread=self.inst.read().decode('ascii')
                if ibread.endswith("\n"):
                    readmore=False
            except:
            
                readmore=False
                
            outdata=outdata+ibread

        print("IBSTA: "+ self.gpib_err(self.inst.ibsta()))
        self._resdata = outdata
        return outdata

    def xe(self):
        return self.write("XE")

    
    def parseresult(self, res, channelnames):
        results = {}
    
        errors_reported = []

        items = res.split(",")
        for i in items:
            st=i[0]
            ch=channelnames[int(ord(i[1])-ord('A'))]
            meas=i[2]
            v=float(i[3:])
            if(st in ('N', 'W', 'E')):
                resname="%s_%s"%(meas, ch)
                resarr=results.get(resname, [])
                resarr.append(v)
                results[resname] = resarr
            else:
                if not(st in errors_reported):
                    print("MEAS_ERR: %s" % i)
                    errors_reported.append(st)
        return results

    hp4142n_status_bits= { 
            'Data ready': 0,
            'Wait': 1,
            'NotUsed': 2,
            'Interlock open': 3,
            'Set ready': 4,
            'Error': 5,
            'RQS': 6,
            'Shut down': 7
        }

    gpib_err_bits={
            'DCAS' : 0,
            'DTAS' : 1,
            'LACS' : 2,
            'TACS' : 3,
            'ATN' : 4,
            'CIC' : 5,
            'REM' : 6,
            'LOK' : 7,
            'Complete' : 8,
            'EVENT' : 9,
            'SPOLL' : 10,
            'RQS' : 11,
            'SRQI' : 12,
            'END' : 13,
            'TIMO' : 14,
            'ERR' : 15
        };

    def gpib_err(self, bits):
            errs = []
            for err in self.gpib_err_bits:
                if bits & (2**self.gpib_err_bits[err]):
                    errs.append(err)

            return " ".join(errs)

    def statusdecode(self, bits):
        stat = []
        for err in self.hp4142n_status_bits:
            if bits & (2**self.hp4142n_status_bits[err]):
                stat.append(err)

        return " ".join(stat)


