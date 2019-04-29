
import re

MS2_SCAN_ELEMS = ['scan', 'rt', 'pre_int', 'ion_inj_time', 'activation_type', 'pre_file', 'pre_scan', 'ins_type',
                 'pre_mz', 'pre_charge']

class Ms2Scan(object):
    __slots__ = MS2_SCAN_ELEMS

    def __init__(self):
        self.scan = ''
        self.rt = ''
        self.file = ''
        self.pre_scan = ''
        self.pre_int = ''
        self.ion_inj_time = ''
        self.activation_type = ''
        self.ins_type = ''
        self._pre_charge = ''
        self._pre_mz = ''

    def _add_str(self, member, append, delim = '|'):
        if not member:
            return append
        else:
            return '{}{}{}'.format(member, delim, append)

    def add_pre_charge(self, s):
        self._pre_charge = self._add_str(self._pre_charge, s)

    def add_pre_mz(self, s):
        self._pre_mz = self._add_str(self._pre_mz, s)

    @staticmethod
    def printHeaders(out, delim = '\t'):
        for i, elem in enumerate(MS2_SCAN_ELEMS):
            if i == 0:
                out.write(elem)
            else: out.write('{}{}'.format(delim, elem))
        out.write('\n')

    def write(self, out, delim = '\t'):
        for i, elem in enumerate(MS2_SCAN_ELEMS):
            if i == 0:
                out.write('{}'.format(getattr(self, elem)))
            else: out.write('{}{}'.format(delim, getattr(self, elem)))
        out.write('\n')


class Ms2Scans(object):

    def __init__(self):
        self.scans = list()

    def write(self, ofname, delim = '\t'):
        outF = open(ofname, 'w')
        Ms2Scan.printHeaders(outF, delim = delim)
        for s in self.scans:
            s.write(outF, delim = delim)

    def read(self, fname, multipleMatch = 'first'):
        inF = open(fname, 'r')
        lines = inF.read().splitlines()

        nLines = len(lines)
        curLine = 0
        while curLine < nLines:
            if lines[curLine][0] == 'S':
                #init scan
                scanTemp = Ms2Scan()
                scanMatch = re.search('^S\t([0-9]{6})\t([0-9]{6})\t([0-9.]+)$', lines[curLine])
                scanTemp.scan = int(scanMatch.group(1))

                curLine += 1
                while curLine < nLines:
                    scanMatch = re.search('^(I|Z)\t([A-Za-z0-9]+)\t(.+)$', lines[curLine])
                    if not scanMatch:
                        raise RuntimeError('Improperly formatted ms2 file!')

                    if scanMatch.group(2) == 'RetTime':
                        scanTemp.rt = scanMatch.group(3)
                    elif scanMatch.group(2) == 'PrecursorInt':
                        scanTemp.pre_int = scanMatch.group(3)
                    elif scanMatch.group(2) == 'IonInjectionTime':
                        scanTemp.ion_inj_time = scanMatch.group(3)
                    elif scanMatch.group(2) == 'ActivationType':
                        scanTemp.activation_type = scanMatch.group(3)
                    elif scanMatch.group(2) == 'PrecursorFile':
                        scanTemp.pre_file = scanMatch.group(3)
                    elif scanMatch.group(2) == 'PrecursorScan':
                        scanTemp.pre_scan = scanMatch.group(3)
                    elif scanMatch.group(2) == 'InstrumentType':
                        scanTemp.ins_type = scanMatch.group(3)
                    elif scanMatch.group(1) == 'Z':
                        scanTemp._pre_charge = scanMatch.group(2)
                        scanTemp._pre_mz = scanMatch.group(3)

                        if multipleMatch == 'first' or multipleMatch == 'one_line':
                            self.scans.append(scanTemp)
                            if multipleMatch == 'first':
                                break

                        while curLine < nLines and lines[curLine][0] == 'Z':
                            scanMatch = re.search('^(Z)\t([0-9]+)\t(.+)$', lines[curLine])
                            if not scanMatch:
                                raise RuntimeError('Improperly formatted ms2 file!')

                            if multipleMatch == 'one_line':
                                scanTemp[-1].add_pre_charge(scanMatch.group(2))
                                scanTemp[-1].add_pre_mz(scanMatch.group(3))
                            elif multipleMatch == 'all':
                                scanTemp._pre_charge = scanMatch.group(2)
                                scanTemp._pre_mz = scanMatch.group(3)
                                self.scans.append(scanTemp)
                            else:
                                raise ValueError('{} is an invalid argument for multipleMatch!'.format(multipleMatch))

                            curLine += 1
                        break

                    curLine += 1
            curLine += 1

