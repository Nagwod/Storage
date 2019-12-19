from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
import subprocess
import glob


def index(request):
    c = []
    c.append('sudo pvdisplay')
    c.append('sudo vgdisplay')
    c.append('sudo lvdisplay')
    c.append('df -hx tmpfs')
    c.append('mount')
    c.append('sudo du -shxc --exclude=proc --exclude=dev')

    res = []
    for i in range(len(c)-1):
        res.append(makeCommand(c[i]))

    s = []
    for i in range(3):
        s.append(['<table>'])
        cont = 0
        for j in res[i]:
            info = replacestr(str(j))
            if info != '':
                if info.find('Physical volume') != -1 or info.find('Volume group') != -1 or info.find('Logical volume') != -1:
                    cont = cont+1
                if info.find('VG Name') != -1:
                    if i == 0:
                        s[i].insert(2+9*(cont-1), '<tr><td>'+info+'</td></tr>')
                    if i == 1:
                        s[i].insert(2+19*(cont-1), '<tr><td>'+info+'</td></tr>')
                    if i == 2:
                        s[i].insert(2+15*(cont-1), '<tr><td>'+info+'</td></tr>')
                else:
                    s[i].append('<tr><td>'+info+'</td></tr>')
        s[i].append('</table>')

    s.append(['<table>'])
    for i in res[3]:
        info = replacestr2(str(i))
        s[3].append('<tr><td>'+info+'</td></tr>')
    s[3].append('</table>')

    s.append(['<table>'])
    for i in res[4]:
        if i.find('mapper') != -1:
            info = str(i).replace(' ', '</td><td>|</td><td>')
            s[4].append('<tr><td>'+info+'</td></tr>')
    s[4].append('</table>')

    s.append('<table>')
    for i in res[3]:
        if i.find('mapper') != -1:
            path = i.split(' ')
            list = glob.glob(path[-1]+'/*')
            r = makeCommand2(c[5], list)
            for j in r:
                info = j.replace('\\t', '</td><td>|</td><td>')
                s[5] = s[5]+'<tr><td>'+info+'</td></tr>'
    s[5] = s[5]+'</table>'
    s[5] = s[5].replace('total</td></tr>', 'total</td></tr><tr><td><br></td></tr>')

    for i in range(len(c)):
        c[i] = c[i].replace('sudo ', '')

    t = []
    s.append('')
    for i in s[0]:
        if i.find('VG Name') != -1:
            idx_vgi = i.rfind('<td>')+4
            idx_vgf = i.rfind('</td>')
            vg = i[idx_vgi:idx_vgf]
        if i.find('Allocated PE') != -1:
            s[6] = s[6]+str(i)+'<tr><td><br></td></tr>'
            cont = 0
            for j in s[1]:
                if j.find('table>') != -1:
                        j = j.replace('</table>','')
                        j = j.replace('<table>','')
                if j.find(vg) != -1 and cont == 0:
                    cont = 1
                    s[6] = s[6]+'<tr><td>--- Volume group ---</td></tr>'
                if cont > 0:
                    if j.find('Free') != -1:
                        s[6] = s[6]+str(j)+'<tr><td><br></td></tr>'
                        cont = cont-1
                        cont2 = 0
                        for k in s[2]:
                            if k.find('table>') != -1:
                                k = k.replace('</table>','')
                                k = k.replace('<table>','')
                            if k.find(vg) != -1 and cont2 == 0:
                                cont2 = 1
                                s[6] = s[6]+'<tr><td>--- Logical volume ---</td></tr>'
                                s[6] = s[6]+'<tr><td>--- Logical volume ---</td></tr>'
                            if cont2 > 0:
                                if k.find('LV Path') != -1:
                                    lv_vgi = k.rfind('<td>')+9
                                    lv_vgf = k.rfind('</td>')
                                    lv = k[lv_vgi:lv_vgf]
                                    lv = lv.replace('-', '--')
                                    lv = lv.replace('/', '-')
                                if k.find('Block') != -1:
                                    s[6] = s[6]+str(k)+'<tr><td><br></td></tr>'
                                    cont2 = cont2-1
                                    for l in s[3]:
                                        if l.find('Filesystem') != -1:
                                            s[6] = s[6]+'</table><table>'+str(l)
                                        if l.find(lv) != -1:
                                            s[6] = s[6]+str(l).replace('</tr>','')
                                            idxi = str(l).rfind('%')-2
                                            idxf = str(l).rfind('<td>|</td>type')-4
                                            aux = (l[idxi:idxf])
                                            aux = aux.replace('</td>','')
                                            aux = aux.replace('<td>','')
                                            aux = aux.replace('%', '')
                                            aux = aux.replace('>', '')
                                            aux2 = aux.split('|')
                                            t.append(aux2)
                                            for m in s[4]:
                                                if m.find('table>') != -1:
                                                    m = m.replace('</table>','')
                                                    m = m.replace('<table>','')
                                                if m.find(lv) != -1:
                                                    idx = str(m).rfind('type')
                                                    s[6] = s[6]+'<td>|</td><td>'+str(m[idx:])+'<tr><td><br></td></tr></table><table>'
                                else:
                                    s[6] = s[6]+str(k)
                    else:
                        s[6] = s[6]+str(j)
        else:
            s[6] = s[6]+str(i)

    t=formatT(t)

    context = {
        'c': c,
        's': s,
        't': t
    }
    return render(request, 'teste/home2.html', context)

def formatT(t):
    aux=[]
    aux2=[]
    aux3=[]
    new_t=[]
    for i in t:
        aux.append(int(i[0]))
        aux2.append(i[1])
        aux3.append(100)
    new_t.append(aux3)
    new_t.append(aux)
    new_t.append(aux2)

    return new_t


def makeCommand(command):
    c = command.split(' ')
    s = subprocess.check_output(c)

    t = str(s).replace('b\'', '')
    t = t.replace('\'', '')
    res = t.split('\\n')

    return res

def makeCommand2(cstr, clist):
    c = cstr.split(' ')
    c = c+clist
    s = subprocess.check_output(c)

    t = str(s).replace('b\'', '')
    t = t.replace('\'', '')
    res = t.split('\\n')

    return res

def replacestr(info):
    l=['PV Name','VG Name','PV Size','Allocatable','PE Size','Total PE','Free PE','Allocated PE']
    l=l+['Format','Metadata Areas','Metadata Sequence No','VG Access','VG Status','MAX LV','Cur LV','Open LV','Max PV','Cur PV','Act PV','VG Size','Alloc PE / Size','FreePE / Size']
    l=l+['LV Path','LV Name','LV Write Access','LV Creation host, time','LV Status','# open','LV Size','Current LE','Segments','Allocation','Read ahead sectors','- currently set to','Block device']
    r=['System ID','PV UUID','VG UUID','LV UUID']
    info = info.replace('                    ', '')
    info = info.replace('                   ', '')
    info = info.replace('                  ', '')
    info = info.replace('                 ', '')
    info = info.replace('                ', '')
    info = info.replace('               ', '')
    info = info.replace('              ', '')
    info = info.replace('             ', '')
    info = info.replace('            ', '')
    info = info.replace('           ', '')
    info = info.replace('          ', '')
    info = info.replace('         ', '')
    info = info.replace('        ', '')
    info = info.replace('       ', '')
    info = info.replace('      ', '')
    info = info.replace('     ', '')
    info = info.replace('    ', '')
    info = info.replace('   ', '')
    info = info.replace('  ', '')
    for i in l:
        info = info.replace(i, i+'</td><td>|</td><td>')
    for i in r:
        if info.find(i) != -1:
            info = info.replace(info, '')

    return info

def replacestr2(info):
    info = info.replace('Mounted on', 'Mounted_on')
    info = info.replace('                           ', '</td><td>|</td><td>')
    info = info.replace('                          ', '</td><td>|</td><td>')
    info = info.replace('                         ', '</td><td>|</td><td>')
    info = info.replace('                        ', '</td><td>|</td><td>')
    info = info.replace('                       ', '</td><td>|</td><td>')
    info = info.replace('                      ', '</td><td>|</td><td>')
    info = info.replace('                     ', '</td><td>|</td><td>')
    info = info.replace('                    ', '</td><td>|</td><td>')
    info = info.replace('                   ', '</td><td>|</td><td>')
    info = info.replace('                  ', '</td><td>|</td><td>')
    info = info.replace('                 ', '</td><td>|</td><td>')
    info = info.replace('                ', '</td><td>|</td><td>')
    info = info.replace('               ', '</td><td>|</td><td>')
    info = info.replace('              ', '</td><td>|</td><td>')
    info = info.replace('             ', '</td><td>|</td><td>')
    info = info.replace('            ', '</td><td>|</td><td>')
    info = info.replace('           ', '</td><td>|</td><td>')
    info = info.replace('          ', '</td><td>|</td><td>')
    info = info.replace('         ', '</td><td>|</td><td>')
    info = info.replace('        ', '</td><td>|</td><td>')
    info = info.replace('       ', '</td><td>|</td><td>')
    info = info.replace('      ', '</td><td>|</td><td>')
    info = info.replace('     ', '</td><td>|</td><td>')
    info = info.replace('    ', '</td><td>|</td><td>')
    info = info.replace('   ', '</td><td>|</td><td>')
    info = info.replace('  ', '</td><td>|</td><td>')
    info = info.replace(' ', '</td><td>|</td><td>')
    return info
