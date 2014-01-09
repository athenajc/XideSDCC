import re
import os

#-------------------------------------------------------------------
def read_file(file_path):    
    if not os.path.exists(file_path):
        return ""
    
    f = open(file_path, 'r')
    s = f.read()
    f.close()
    return s

#-------------------------------------------------------------------
def copy_file(src, dst):    
    if not os.path.exists(src):
        return ""
    
    f = open(src, 'r')
    s = f.read()
    f.close()
    
    f = open(dst, 'w+')
    f.write(s)
    f.close()


#-------------------------------------------------------------------
def read_file_lines(file_path):
    if not os.path.exists(file_path):
        return []    
    f = open(file_path, 'r')
    lst = []
    for line in f.readlines():
        lst.append(line)
    f.close()
    return lst

#-------------------------------------------------------------------
def c_pre_process(s):
    s = re.sub("/\*[^\*]*\*/", "[$BC]", s)        # replace block comment
    s = re.sub("([//][^\n]*[\n])", "[$LC]\n", s)  # replace line comment
    s = re.sub("\([^\(\)]*\)", " () ", s)         # replace parenthesis
    s = re.sub("\"[^\"\n]*\"", "[$ST]", s)        # replace string
    
    p_blk = "{[^{^}]*}"
    match = re.search(p_blk, s)
    if (match):
        s = re.sub(p_blk, "[$BLK]", s)
        while (match) :
            s = re.sub(p_blk, "[$BLK]", s)
            match = re.search(p_blk, s)

    s = re.sub(",", " , ", s)
    s = re.sub("=", " = ", s)
    return s

#-------------------------------------------------------------------
def check_if_with_main(file_path):
    s = read_file(file_path)
 
    if s.find('main') < 0:
        return False
    
    s = c_pre_process(s)
            
    match = re.findall(r"\w+\s+\(\)\s+[\[]+", s)
    #log(match)
    #print match
    for t in match :
        t = re.sub("[\[\n\(\)]", "", t)
        #print '------------', t
        if t.find('main') == 0:
            return True
        
    return False

#-------------------------------------------------------------------
def pre_process(s):
    s = re.sub("/\*[^\*]*\*/", "[$BC]", s)        # replace block comment
    s = re.sub("([//][^\n]*[\n])", "[$LC]\n", s)  # replace line comment
    s = re.sub("\([^\(\)]*\)", " () ", s)         # replace parenthesis
    s = re.sub("\"[^\"\n]*\"", "[$ST]", s)        # replace string
    
    p_blk = "{[^{^}]*}"
    match = re.search(p_blk, s)
    if match:
        s = re.sub(p_blk, "[$BLK]", s)
        while match :
            s = re.sub(p_blk, "[$BLK]", s)
            match = re.search(p_blk, s)

    s = re.sub(",", " , ", s)
    s = re.sub("=", " = ", s)
    return s
    
#-------------------------------------------------------------------
def read_match_list(file_path, patten):
    if not os.path.exists(file_path):
        return []
    
    s = read_file(file_path)
    
    match = re.findall(patten, s)
    
    #print(match)
    return match

#-------------------------------------------------------------------
def remove_duplicate_items(lst):
    new_lst = []
    for s in lst:
        if s not in new_lst:
            new_lst.append(s)
    return new_lst

#-------------------------------------------------------------------
def proc_file(file_path):
    match = read_match_list(file_path, r"--[\w\-\_]+")
    match = remove_duplicate_items(match)
    match.sort()
    print 'key_dict = {'
    for s in match:
        print '    \'' + s + '\'' + ':0,'
    print '}'
    
def test_dict():
    flag_dict = {
        '--Werror':0,
        '--acall-ajmp':0,
        '--all-callee-saves':0,
        '--asm':0,
        '--c1mode':0,
        '--callee-saves':0,
        '--callee-saves-bc':0,
        '--calltree':0,
        '--code-loc':0,    
    }
    flag_dict['--Werror'] = ['true', 1]
    print flag_dict
    
def gen_table():
    title = "Internal debugging options:"
    s = """      
      --stack-auto          Stack automatic variables
      --xstack              Use external stack
      --int-long-reent      Use reentrant calls on the int and long support functions
      --float-reent         Use reentrant calls on the float support functions
      --xram-movc           Use movc instead of movx to read xram (xdata)
      --callee-saves        <func[,func,...]> Cause the called function to save registers instead of the caller
      --profile             On supported ports, generate extra profiling information
      --fomit-frame-pointer  Leave out the frame pointer.
      --all-callee-saves    callee will always save registers used
      --stack-probe         insert call to function __stack_probe at each function prologue
      --no-xinit-opt        don't memcpy initialized xram from code
      --no-c-code-in-asm    don't include c-code as comments in the asm file
      --no-peep-comments    don't include peephole optimizer comments
      --short-is-8bits      Make short 8 bits (for old times sake)
      --codeseg             <name> use this name for the code segment
      --constseg            <name> use this name for the const segment
      """
    i = 27
    for t in s.split('\n'):        
        n = len(t)
        t0 = t[0:i].strip()
        t1 = t[i:n].strip()
        print "[\'" + t0 + "\', \'" + t1 + "\'],"

    
def get_device_list(p):
    print p
    lst = os.listdir(p)
    new_lst = []
    for s in lst:
        s = s.replace('.h', '')
        new_lst.append(s)
    new_lst.sort()
    print new_lst
    
def get_device_list_all():
    #get_device_list('/usr/local/share/sdcc/include/mcs51')
    get_device_list('/usr/local/share/sdcc/non-free/include/pic14')
    get_device_list('/usr/local/share/sdcc/non-free/include/pic16')
    #get_device_list('/usr/local/share/sdcc/include/z180')
    #get_device_list('/usr/local/share/sdcc/include/ds390')
    #get_device_list('/usr/local/share/sdcc/include/ds400')
    #get_device_list('/usr/local/share/sdcc/include/hc08')
    '''
    /usr/local/share/sdcc/non-free/include/pic14
    -p18f2321
['pic10f320', 'pic10f322', 'pic12f1501', 'pic12f1822', 'pic12f1840', 'pic12f609', 'pic12f615', 'pic12f617', 'pic12f629', 'pic12f635', 'pic12f675', 'pic12f683', 'pic12f752', 'pic12lf1552', 'pic14regs', 'pic16c432', 'pic16c433', 'pic16c554', 'pic16c557', 'pic16c558', 'pic16c62', 'pic16c620', 'pic16c620a', 'pic16c621', 'pic16c621a', 'pic16c622', 'pic16c622a', 'pic16c63a', 'pic16c65b', 'pic16c71', 'pic16c710', 'pic16c711', 'pic16c715', 'pic16c717', 'pic16c72', 'pic16c73b', 'pic16c745', 'pic16c74b', 'pic16c765', 'pic16c770', 'pic16c771', 'pic16c773', 'pic16c774', 'pic16c781', 'pic16c782', 'pic16c925', 'pic16c926', 'pic16f1454', 'pic16f1455', 'pic16f1458', 'pic16f1459', 'pic16f1503', 'pic16f1507', 'pic16f1508', 'pic16f1509', 'pic16f1512', 'pic16f1513', 'pic16f1516', 'pic16f1517', 'pic16f1518', 'pic16f1519', 'pic16f1526', 'pic16f1527', 'pic16f1704', 'pic16f1708', 'pic16f1782', 'pic16f1783', 'pic16f1784', 'pic16f1786', 'pic16f1787', 'pic16f1788', 'pic16f1789', 'pic16f1823', 'pic16f1824', 'pic16f1825', 'pic16f1826', 'pic16f1827', 'pic16f1828', 'pic16f1829', 'pic16f1847', 'pic16f1933', 'pic16f1934', 'pic16f1936', 'pic16f1937', 'pic16f1938', 'pic16f1939', 'pic16f1946', 'pic16f1947', 'pic16f610', 'pic16f616', 'pic16f627', 'pic16f627a', 'pic16f628', 'pic16f628a', 'pic16f630', 'pic16f631', 'pic16f636', 'pic16f639', 'pic16f648a', 'pic16f676', 'pic16f677', 'pic16f684', 'pic16f685', 'pic16f687', 'pic16f688', 'pic16f689', 'pic16f690', 'pic16f707', 'pic16f716', 'pic16f72', 'pic16f720', 'pic16f721', 'pic16f722', 'pic16f722a', 'pic16f723', 'pic16f723a', 'pic16f724', 'pic16f726', 'pic16f727', 'pic16f73', 'pic16f737', 'pic16f74', 'pic16f747', 'pic16f753', 'pic16f76', 'pic16f767', 'pic16f77', 'pic16f777', 'pic16f785', 'pic16f818', 'pic16f819', 'pic16f84', 'pic16f84a', 'pic16f87', 'pic16f870', 'pic16f871', 'pic16f872', 'pic16f873', 'pic16f873a', 'pic16f874', 'pic16f874a', 'pic16f876', 'pic16f876a', 'pic16f877', 'pic16f877a', 'pic16f88', 'pic16f882', 'pic16f883', 'pic16f884', 'pic16f886', 'pic16f887', 'pic16f913', 'pic16f914', 'pic16f916', 'pic16f917', 'pic16f946', 'pic16fam', 'pic16hv616', 'pic16hv753', 'pic16lf1704', 'pic16lf1708', 'pic16lf1902', 'pic16lf1903', 'pic16lf1904', 'pic16lf1906', 'pic16lf1907']
/usr/local/share/sdcc/non-free/include/pic16
['pic18f1220', 'pic18f1230', 'pic18f1320', 'pic18f1330', 'pic18f13k22', 'pic18f13k50', 'pic18f14k22', 'pic18f14k50', 'pic18f2220', 'pic18f2221', 'pic18f2320', 'pic18f2321', 'pic18f2331', 'pic18f23k20', 'pic18f23k22', 'pic18f2410', 'pic18f242', 'pic18f2420', 'pic18f2423', 'pic18f2431', 'pic18f2439', 'pic18f2450', 'pic18f2455', 'pic18f2458', 'pic18f248', 'pic18f2480', 'pic18f24j10', 'pic18f24j11', 'pic18f24j50', 'pic18f24k20', 'pic18f24k22', 'pic18f24k50', 'pic18f2510', 'pic18f2515', 'pic18f252', 'pic18f2520', 'pic18f2523', 'pic18f2525', 'pic18f2539', 'pic18f2550', 'pic18f2553', 'pic18f258', 'pic18f2580', 'pic18f2585', 'pic18f25j10', 'pic18f25j11', 'pic18f25j50', 'pic18f25k20', 'pic18f25k22', 'pic18f25k50', 'pic18f25k80', 'pic18f2610', 'pic18f2620', 'pic18f2680', 'pic18f2682', 'pic18f2685', 'pic18f26j11', 'pic18f26j13', 'pic18f26j50', 'pic18f26j53', 'pic18f26k20', 'pic18f26k22', 'pic18f26k80', 'pic18f27j13', 'pic18f27j53', 'pic18f4220', 'pic18f4221', 'pic18f4320', 'pic18f4321', 'pic18f4331', 'pic18f43k20', 'pic18f43k22', 'pic18f4410', 'pic18f442', 'pic18f4420', 'pic18f4423', 'pic18f4431', 'pic18f4439', 'pic18f4450', 'pic18f4455', 'pic18f4458', 'pic18f448', 'pic18f4480', 'pic18f44j10', 'pic18f44j11', 'pic18f44j50', 'pic18f44k20', 'pic18f44k22', 'pic18f4510', 'pic18f4515', 'pic18f452', 'pic18f4520', 'pic18f4523', 'pic18f4525', 'pic18f4539', 'pic18f4550', 'pic18f4553', 'pic18f458', 'pic18f4580', 'pic18f4585', 'pic18f45j10', 'pic18f45j11', 'pic18f45j50', 'pic18f45k20', 'pic18f45k22', 'pic18f45k50', 'pic18f45k80', 'pic18f4610', 'pic18f4620', 'pic18f4680', 'pic18f4682', 'pic18f4685', 'pic18f46j11', 'pic18f46j13', 'pic18f46j50', 'pic18f46j53', 'pic18f46k20', 'pic18f46k22', 'pic18f46k80', 'pic18f47j13', 'pic18f47j53', 'pic18f6310', 'pic18f6390', 'pic18f6393', 'pic18f63j11', 'pic18f63j90', 'pic18f6410', 'pic18f6490', 'pic18f6493', 'pic18f64j11', 'pic18f64j90', 'pic18f6520', 'pic18f6525', 'pic18f6527', 'pic18f6585', 'pic18f65j10', 'pic18f65j11', 'pic18f65j15', 'pic18f65j50', 'pic18f65j90', 'pic18f65j94', 'pic18f65k22', 'pic18f65k80', 'pic18f65k90', 'pic18f6620', 'pic18f6621', 'pic18f6622', 'pic18f6627', 'pic18f6628', 'pic18f6680', 'pic18f66j10', 'pic18f66j11', 'pic18f66j15', 'pic18f66j16', 'pic18f66j50', 'pic18f66j55', 'pic18f66j60', 'pic18f66j65', 'pic18f66j90', 'pic18f66j93', 'pic18f66j94', 'pic18f66j99', 'pic18f66k22', 'pic18f66k80', 'pic18f66k90', 'pic18f6720', 'pic18f6722', 'pic18f6723', 'pic18f67j10', 'pic18f67j11', 'pic18f67j50', 'pic18f67j60', 'pic18f67j90', 'pic18f67j93', 'pic18f67j94', 'pic18f67k22', 'pic18f67k90', 'pic18f8310', 'pic18f8390', 'pic18f8393', 'pic18f83j11', 'pic18f83j90', 'pic18f8410', 'pic18f8490', 'pic18f8493', 'pic18f84j11', 'pic18f84j90', 'pic18f8520', 'pic18f8525', 'pic18f8527', 'pic18f8585', 'pic18f85j10', 'pic18f85j11', 'pic18f85j15', 'pic18f85j50', 'pic18f85j90', 'pic18f85j94', 'pic18f85k22', 'pic18f85k90', 'pic18f8620', 'pic18f8621', 'pic18f8622', 'pic18f8627', 'pic18f8628', 'pic18f8680', 'pic18f86j10', 'pic18f86j11', 'pic18f86j15', 'pic18f86j16', 'pic18f86j50', 'pic18f86j55', 'pic18f86j60', 'pic18f86j65', 'pic18f86j72', 'pic18f86j90', 'pic18f86j93', 'pic18f86j94', 'pic18f86j99', 'pic18f86k22', 'pic18f86k90', 'pic18f8720', 'pic18f8722', 'pic18f8723', 'pic18f87j10', 'pic18f87j11', 'pic18f87j50', 'pic18f87j60', 'pic18f87j72', 'pic18f87j90', 'pic18f87j93', 'pic18f87j94', 'pic18f87k22', 'pic18f87k90', 'pic18f95j94', 'pic18f96j60', 'pic18f96j65', 'pic18f96j94', 'pic18f96j99', 'pic18f97j60', 'pic18f97j94', 'pic18fam']

    /usr/local/share/sdcc/include/pic14
    ['errno', 'float', 'limits', 'math', 'p16f_common.inc', 'pic14devices.txt', 'pic16regs', 'sdcc-lib']
    /usr/local/share/sdcc/include/pic16
    ['adc', 'ctype', 'delay', 'errno', 'float', 'gstack', 'i2c', 'limits', 'malloc', 'math', 'p18fxxx.inc', 'pic16devices.txt', 'pic18fregs', 'sdcc-lib', 'signal', 'stdarg', 'stddef', 'stdint', 'stdio', 'stdlib', 'string', 'usart']
    /usr/local/share/sdcc/include/z180
    ['z180']
    /usr/local/share/sdcc/include/ds390
    ['serial390']
    /usr/local/share/sdcc/include/ds400
    ['ds400rom']
    /usr/local/share/sdcc/include/hc08
    ['mc68hc908apxx', 'mc68hc908gp32', 'mc68hc908jb8', 'mc68hc908jkjl', 'mc68hc908qy']
'''

#---- for testing -------------------------------------------------------------
if __name__ == '__main__':
    #proc_file('/home/athena/myproject/py_ide/sdcc.help')
    #test_dict()
    #gen_table()
    
    
    get_device_list_all()

