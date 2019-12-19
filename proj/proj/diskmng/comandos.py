import subprocess
import glob
from datetime import datetime

def comandos():
    com = [] #Armazena os comandos
    com.append('sudo pvdisplay') # 0
    com.append('sudo vgdisplay') # 1
    com.append('sudo lvdisplay') # 2
    com.append('df -hx tmpfs')   # 3
    com.append('mount')          # 4
    com.append('sudo du -shxc --exclude=proc --exclude=dev') # 5

    res = [] #Guarda as informações dos comandos
    for i in range(len(com)-1):
        res.append(makeCommand(com[i]))

    infos = [] #Guarda as informações tratadas
    for i in range(3): # Comandos de 0 a 2
        infos.append([])
        cont = 0
        for j in res[i]:
            info = replacestr(str(j))
            if info != '': # Informações removidas ficam vazias, esse if evita que essas informações vazias sejam adicionadas na lista
                if info.find('Physical volume') != -1 or info.find('Volume group') != -1 or info.find('Logical volume') != -1:
                    cont = cont+1 # controle para saber quantas ocorrências de pv, vg e lv houve
                if info.find('VG Name') != -1: # Encontra o VG Name para coloca-lo em primeiro
                    if i == 0:
                        infos[i].insert(2+9*(cont-1), info) # Coloca o VG name na primeira posição do respectivo pv
                    if i == 1:
                        infos[i].insert(2+19*(cont-1), info) # Coloca o VG name na primeira posição do respectivo vg
                    if i == 2:
                        infos[i].insert(2+15*(cont-1), info) # Coloca o VG name na primeira posição do respectivo lv
                else:
                    infos[i].append(info) # As outras informações são simplesmente adicionadas em sequência

    infos.append([])
    for i in res[3]: # Comando 3
        info = replacestr2(str(i))
        if info.find('udev') == -1:
            infos[3].append(info)

    infos.append([])
    for i in res[4]: # Comando 4
        if i.find('dev') != -1:
            info = str(i).replace(' ', '*split*')
            infos[4].append(info)

    localDu = '' # Guarda os locais usados no comando du para por no gráfico

    mountedOn = [] #Guarda os nomes dos pontos de montagem
    infos.append([])
    f = open('/home/ti_estagio/gerdisk/proj/proj/diskmng/comandoDu.txt','w') #Abre o arquivo para salvar os comandos du
    for i in res[3]: # Comando 5
        if i.find('/dev/') != -1: # Só serão informados os lugares /dev/
            path = i.split(' ') # Separa os espaços
            mountedOn.append(path[-1])
            localDu = localDu+(path[-1]+'*split*') # Pega a ultima informação da linha (que é o caminho)
            list = glob.glob(path[-1]+'/*') # adiciona os caminhos na lista
            du = makeCommand2(com[5], list, path[-1])
            list2 = ''
            for i in list:
             list2 = list2+' '+i
            f.write(com[5]+list2+'\n')
            for j in du:
                info = j.replace('\\t', '*split*') # Substitui o tab por um *split*
                infos[5].append(info)
    f.close()
    lvinfo=[] # Guarda as informações de lvdisplay para por no gráfico
    vginfo=[] # Guarda as informações de vgdisplay para por no gráfico
    infosf=[] # Guarda as informações finais
    contador = -1
    for i in infos[0]: # PV
        if i.find('Physical volume') != -1:
            contador = contador+1 # Controle de ocorrências de pv
            infosf.append([])
        if i.find('VG Name') != -1:
            idx_vgi = i.find('*split*')+7 # Pega o nome do vg no VG Name
            vg = i[idx_vgi:] # guarda o nome do vg
        if i.find('Allocated PE') != -1: # Espera a ultima linha de informação
            infosf[contador].append(str(i).split('*split*')) # Guarda a linha de informação separando no *split*
            cont = 0
            for j in infos[1]: # VG
                if j.find(vg) != -1 and cont == 0: # Espera pelo valor de vg
                    cont = 1
                    infosf[contador].append(['--- Volume group ---'])
                if cont > 0:
                    if j.find('VG Size') != -1 or j.find('Alloc PE / Size') != -1 or j.find('FreePE / Size') != -1:
                        idx = str(j).find('*split*')+7
                        aux = (j[idx:])
                        vginfo.append(aux) # Recebe o valor de VG Size, Alloc PE e FreePE para o gráfico
                    if j.find('FreePE') != -1: # Espera a ultima linha de informação
                        infosf[contador].append(str(j).split('*split*')) # Guarda a linha de informação separando no *split*
                        cont = cont-1
                        cont2 = 0
                        for k in infos[2]: # LV
                            if k.find(vg) != -1 and cont2 == 0: # Espera pelo valor de vg
                                cont2 = 1
                                infosf[contador].append(['--- Logical volume ---'])
                            if cont2 > 0:
                                if k.find('LV Path') != -1:
                                    lv_vgi = k.find('*split*')+12
                                    lv = k[lv_vgi:]
                                    lv = lv.replace('-', '--')
                                    lv = lv.replace('/', '-') # Recebe o caminho do lv
                                if k.find('Block') != -1: # Espera a ultima linha de informação
                                    infosf[contador].append(str(k).split('*split*')) # Guarda a linha de informação separando no *split*
                                    cont2 = cont2-1
                                    for list in infos[3]: #DF
                                        if list.find('Filesystem') != -1:
                                            infosf[contador].append(str(list).split('*split*')) # Guarda a linha de informação separando no *split*
                                        if list.find(lv) != -1:
                                            idxi = str(list).find('*split*')+7
                                            aux = (list[idxi:])
                                            lvinfo.append(aux.split('*split*')) # Recebe as informações de lv para o gráfico
                                            for m in infos[4]: # mount
                                                if m.find(lv) != -1:
                                                    idx = str(m).rfind('type')
                                                    infosf[contador].append((str(list)+'*split*'+str(m[idx:])).split('*split*')) # Guarda a linha de informação separando no *split*
                                else:
                                    infosf[contador].append(str(k).split('*split*')) # Guarda a linha de informação separando no *split*
                    else:
                        infosf[contador].append(str(j).split('*split*')) # Guarda a linha de informação separando no *split*
        else:
            infosf[contador].append(str(i).split('*split*')) # Guarda a linha de informação separando no *split*

    dfcominfo = '<table border="1" align="center">' # Prepara as informações de df para o html
    for i in infos[3]:
        dfcominfo = dfcominfo+('<tr><td>')
        dfcominfo = dfcominfo+(i.replace('*split*', '</td><td>'))
        dfcominfo = dfcominfo+('</td></tr>')
    dfcominfo = dfcominfo+('</table><br>')
    dfcominfo = dfcominfo.replace('<tr><td></td></tr>', '')
    dfcominfo = dfcominfo.replace('<td>Filesystem', '<th align="center">Filesystem</th>')
    dfcominfo = dfcominfo.replace('<td>Size</td>', '<th align="center">Size</th>')
    dfcominfo = dfcominfo.replace('<td>Used</td>', '<th align="center">Used</th>')
    dfcominfo = dfcominfo.replace('<td>Avail</td>', '<th align="center">Avail</th>')
    dfcominfo = dfcominfo.replace('<td>Use%</td>', '<th align="center">Use%</th>')
    dfcominfo = dfcominfo.replace('<td>Mounted_on</td>', '<th align="center">Mounted on</th>')

    duinfo = [] # Guarda as informações de du para por no gráfico
    duinfo.append([])
    cont = 0
    ultimo = False
    ducominfo = '<table border="1" align="center">' # Prepara as informações de du para o html
    for i in infos[5]:
        if i != '':
            if ultimo:
                duinfo.append([])
                ultimo = False
            duinfo[cont].append(i.split('*split*')) # Acrescenta tudo menos o total para por no gráfico
            if i.find('total') != -1:
                cont = cont+1
                ultimo = True
            ducominfo = ducominfo+('<tr><td>')
            info = i.split('*split*')
            if i.find('total') == -1:
                info[1] = "<button class='btn btn-primary' name='"+ info[1] +" 'value='"+info[1]+"'>"+info[1]+"</button>"
            ducominfo = ducominfo+info[0]+'</td><td>'+info[1]
            ducominfo = ducominfo+('</td></tr>')
    ducominfo = ducominfo.replace('total</td></tr><tr><td>', 'total</td></tr></table><br><table border="1" align="center"><tr><td>')
    ducominfo = ducominfo+('</table>')

    swap = False
    h = '' # Prepara as informações para o html
    for i in range(len(infosf)):
        for j in range(len(infosf[i])):
            if infosf[i][j][0].find('LV Name') != -1:
                    swap = False
                    if infosf[i][j][-1].find('swap_1') != -1:
                        swap = True
            if swap and str(infosf[i][j]).find('Filesystem') != -1:
                continue
            h = h+'<tr>'
            for k in range(len(infosf[i][j])):
                h = h+'<td>'+infosf[i][j][k]+'</td>'
            h = h+'</tr>'
    h = h.replace('<tr><td>--- Physical volume ---</td>','</table><br><table border="1" align="center"><tr><th colspan="2" align="center">--- Physical volume ---</th>')
    h = h.replace('<tr><td>--- Volume group ---</td>','</table><br><table border="1" align="center"><tr><th colspan="2" align="center">--- Volume group ---</th>')
    h = h.replace('<tr><td>--- Logical volume ---</td>','</table><br><table border="1" align="center"><tr><th colspan="2" align="center">--- Logical volume ---</th>')
    h = h.replace('<tr><td>Filesystem</td>','</table><br><table border="1" align="center"><tr><th>Filesystem</th>')
    h = h.replace('<td>Size</td>', '<th>Size</th>')
    h = h.replace('<td>Used</td>', '<th>Used</th>')
    h = h.replace('<td>Avail</td>', '<th>Avail</th>')
    h = h.replace('<td>Use%</td>', '<th>Use%</th>')
    h = h.replace('<td>Mounted_on</td>', '<th>Mounted on</th>')
    h = h+'</table>'

    h2 = '<table cellspacing="10" align="center" width="1000">' # Prepara os gráficos de du
    for i in range(len(duinfo)):
        if i%2 == 0:
            h2 = h2+'<tr><td width="50%"><div id="charts'+ str(i) +'"></div></td>'
        else:
            h2 = h2+'<td><div id="charts'+ str(i) +'"></div></td></tr>'
    h2 = h2+'</table>'

    lvinfo = formatLV(lvinfo)
    vgsize = vginfo[0]
    vginfo = formatVG(vginfo)
    dutotal2 = []
    dutotal2 = formatDT2(duinfo)
    duinfo = formatDU(duinfo)
    dutotal = [] # Valor total do du
    dutotal = formatDUtotal(duinfo)
    duinfo = formatDU2(duinfo, dutotal)
    dutotal = formatDUtotal2(dutotal)

    for i in range(len(com)):
        com[i] = com[i].replace('sudo ', '') # Tira o sudo dos comandos para exibir na tela

    duHist = []
    duh = []
    mounton = []
    duData = []
    for i in range(len(mountedOn)):
        mounton.append('')
        if len(mountedOn[i]) == 1:
            mounton[i] = mountedOn[i].replace('/', 'root')
        else:
            mounton[i] = mountedOn[i].replace('/', '_')
        mounton[i] = mounton[i].replace('/', '_')
        duHist.append([])
        duh.append([])

        paths = subprocess.check_output(['ls', '/home/ti_estagio/gerdisk/proj/proj/diskmng/dutmp/'+mounton[i]+'/']) #Pega os nomes das pastas de arquivos de histárico do du
        pathstr = str(paths).replace('b\'', '')
        pathstr = pathstr.replace('\'', '')
        pathlist = pathstr.split('\\n')
        for j in range(len(pathlist)):
            if pathlist[j] == '': #Se j for vazio, pula para o próximo valor de j
                continue
            f = open('/home/ti_estagio/gerdisk/proj/proj/diskmng/dutmp/'+mounton[i]+'/'+pathlist[j], 'r') #Abre os arqivos de histórico para recuperar os dados
            if(i==0): #Para pegar a data e o horário para por no gráfico (uma vez, pois são os mesmos valores em todos)
                duData.append(pathlist[j])
                duData[j] = duData[j].replace('.out', '')
                duData[j] = duData[j].replace('-', '/')
                duData[j] = duData[j].replace('_', ' - ')
            duHist[i].append(f.read()) #Pega os dados dos arquivos
            idx = duHist[i][-1].rfind('\\n')+2
            idxf = duHist[i][-1].rfind('\\t')
            duh[i].append(duHist[i][-1][idx:idxf]) #Tratando as informações que vieram do arquivo
            f.close() #Fecha o arquivo

    duh = formatDuH(duh)
    duGrafico = []
    duGrafico = formatDuGrafico(duh, mountedOn)

    #Mantém as últimas 30 informações dobre o histórico de du
    while len(duData) > 30:
        duData.pop(0)
    for i in duGrafico:
        while len(i[1]) > 30:
            i[1].pop(0)

    context = { # Passa variáveis para o template
        'h': h,
        'h2': h2,
        'com': com,
        'dfcominfo': dfcominfo,
        'ducominfo': ducominfo,
        'lvinfo': lvinfo,
        'vginfo': vginfo,
        'vgsize': vgsize,
        'duinfo': duinfo,
        'dutotal2': dutotal2,
        'localDu': localDu,
        'duData': duData,
        'duGrafico': duGrafico
    }

    return context


#-------------------------------------------->Métodos<----------------------------------------------------------------


def formatLV(lvinfo): # Tratamento da informação de lv
    aux=[]
    total=[]
    usado=[]
    livre=[]
    prcnt=[]
    local=[]
    new_t=[]
    for i in lvinfo:
        for j in range(0,3):
            if i[j].find('K') != -1:
                i[j] = i[j].replace('K', '')
                if i[j].find(',') != -1:
                    i[j] = i[j].replace(',', '')
                    i[j] = str(int(i[j])/10/(2**20))
                else:
                    i[j] = str(int(i[j])/(2**20))
            if i[j].find('M') != -1:
                i[j] = i[j].replace('M', '')
                if i[j].find(',') != -1:
                    i[j] = i[j].replace(',', '')
                    i[j] = str(int(i[j])/10/(2**10))
                else:
                    i[j] = str(int(i[j])/(2**10))
            if i[j].find('G') != -1:
                i[j] = i[j].replace('G', '')
                if i[j].find(',') != -1:
                    i[j] = i[j].replace(',', '')
                    i[j] = str(int(i[j])/10)
                else:
                    i[j] = str(int(i[j]))
            if i[j].find('T') != -1:
                i[j] = i[j].replace('T', '')
                if i[j].find(',') != -1:
                    i[j] = i[j].replace(',', '')
                    i[j] = str(int(i[j])/10*(2**10))
                else:
                    i[j] = str(int(i[j])*(2**10))
            if i[j].find('P') != -1:
                i[j] = i[j].replace('P', '')
                if i[j].find(',') != -1:
                    i[j] = i[j].replace(',', '')
                    i[j] = str(int(i[j])/10*(2**20))
                else:
                    i[j] = str(int(i[j])*(2**20))
        aux.append(100)
        total.append(float(i[0]))
        usado.append(float(i[1]))
        livre.append(float(i[2]))
        prcnt.append(int(i[3].replace('%', '')))
        local.append(i[4])
    new_t.append(aux)
    new_t.append(prcnt)
    new_t.append(total)
    new_t.append(livre)
    new_t.append(usado)
    new_t.append(local)

    return new_t

def formatVG(vginfo): # Tratamento da informação de vg
    aux_u = []
    cont = 0
    cont2= 0
    for i in range(len(vginfo)):
        if cont == 0:
            aux_u.append([])
        aux_u[cont2].append(vginfo[i])
        cont = cont+1
        if cont == 3:
            cont = 0
            cont2 = cont2+1

    total=[]
    usado=[]
    livre=[]
    new_u=[]
    for i in aux_u:
        for j in range(0,3):
            if i[j].find('/') != -1:
                idx = i[j].rfind('/')+2
                i[j] = i[j][idx:]
                i[j] = i[j].replace('<','')
            if i[j].find('KiB') != -1:
                i[j] = i[j].replace('KiB', '')
                if i[j].find(',') != -1:
                    i[j] = i[j].replace(',', '')
                    i[j] = str(int(i[j])/10000000)
                else:
                    i[j] = str(int(i[j])/1000000)
            if i[j].find('MiB') != -1:
                i[j] = i[j].replace('MiB', '')
                if i[j].find(',') != -1:
                    i[j] = i[j].replace(',', '')
                    i[j] = str(int(i[j])/10000)
                else:
                    i[j] = str(int(i[j])/1000)
            if i[j].find('GiB') != -1:
                i[j] = i[j].replace('GiB', '')
                if i[j].find(',') != -1:
                    i[j] = i[j].replace(',', '')
                    i[j] = str(int(i[j])/10)
                else:
                    i[j] = str(int(i[j]))
            if i[j].find('TiB') != -1:
                i[j] = i[j].replace('TiB', '')
                if i[j].find(',') != -1:
                    i[j] = i[j].replace(',', '')
                    i[j] = str(int(i[j])*100)
                else:
                    i[j] = str(int(i[j])*1000)
            if i[j].find('PiB') != -1:
                i[j] = i[j].replace('PiB', '')
                if i[j].find(',') != -1:
                    i[j] = i[j].replace(',', '')
                    i[j] = str(int(i[j])*100000)
                else:
                    i[j] = str(int(i[j])*1000000)

        total.append(round(float(i[0])/float(i[0])*100, 2))
        usado.append(round(float(i[1])/float(i[0])*100, 2))
        livre.append(round(float(i[2])/float(i[0])*100, 2))
    new_u.append(total)
    new_u.append(usado)
    new_u.append(livre)

    return new_u

def formatDU(duinfo): # Tratamento da informação de du
    for i in range(len(duinfo)):
        for j in range(len(duinfo[i])):
            if duinfo[i][j][0].find('K') != -1:
                duinfo[i][j][0] = duinfo[i][j][0].replace('K', '')
                if duinfo[i][j][0].find(',') != -1:
                    duinfo[i][j][0] = duinfo[i][j][0].replace(',', '')
                    duinfo[i][j][0] = str(float(duinfo[i][j][0])/10/(2**10))
                else:
                    duinfo[i][j][0] = str(float(duinfo[i][j][0])/(2**10))
            if duinfo[i][j][0].find('M') != -1:
                duinfo[i][j][0] = duinfo[i][j][0].replace('M', '')
                if duinfo[i][j][0].find(',') != -1:
                    duinfo[i][j][0] = duinfo[i][j][0].replace(',', '')
                    duinfo[i][j][0] = str(float(duinfo[i][j][0])/10)
                else:
                    duinfo[i][j][0] = str(float(duinfo[i][j][0]))
            if duinfo[i][j][0].find('G') != -1:
                duinfo[i][j][0] = duinfo[i][j][0].replace('G', '')
                if duinfo[i][j][0].find(',') != -1:
                    duinfo[i][j][0] = duinfo[i][j][0].replace(',', '')
                    duinfo[i][j][0] = str(float(duinfo[i][j][0])/10*(2**10))
                else:
                    duinfo[i][j][0] = str(float(duinfo[i][j][0])*(2**10))
            if duinfo[i][j][0].find('T') != -1 and duinfo[i][j][0].find('LOST') == -1:
                duinfo[i][j][0] = duinfo[i][j][0].replace('T', '')
                if duinfo[i][j][0].find(',') != -1:
                    duinfo[i][j][0] = duinfo[i][j][0].replace(',', '')
                    duinfo[i][j][0] = str(float(duinfo[i][j][0])/10*(2**20))
                else:
                    duinfo[i][j][0] = str(float(duinfo[i][j][0])*(2**20))

    return duinfo

def formatDU2(duinfo, dutotal): # Tratamento da informação de du e total de du
    new_v = []
    cont = 0
    cont2 = 0
    aux = 0
    for i in range(len(duinfo)):
        new_v.append([])
        for j in range(len(duinfo[i])):
            duinfo[i][j][0] = round(float(duinfo[i][j][0])/float(dutotal[cont])*100, 2)
            if duinfo[i][j][1].find('total')!=-1:
                if cont2 > 0:
                    if aux > 0:
                        new_v[i].append([aux, 'outros'])
                    cont2 = 0
                aux = 0
                if j < 2:
                    new_v[i].append(duinfo[i][j])
            else:
                if duinfo[i][j][0] < 1:
                    aux = aux + duinfo[i][j][0]
                    cont2 = cont2+1
                else:
                    new_v[i].append(duinfo[i][j])
        cont = cont+1

    return new_v

def formatDT2(duinfo):
    dutotal = []
    dutotal2 = ''
    cont = 0
    for i in duinfo:
        dutotal.append([])
        for j in i:
            dutotal[cont] = j[0] # Armazena o último valor (total)
        cont = cont+1

    for i in dutotal:
        dutotal2 = dutotal2+i+'*split*'

    return dutotal2

def formatDUtotal(duinfo): # Tratamento da informação do total de du
    dutotal = []
    cont = 0
    for i in duinfo:
        dutotal.append([])
        for j in i:
            dutotal[cont] = j[0] # Armazena o último valor (total)
        cont = cont+1

    return dutotal

def formatDUtotal2(dutotal): # Tratamento da informação do total de du
    new_dutotal = ""
    for i in dutotal:
        new_dutotal = new_dutotal+i+'*split*'

    return new_dutotal

def formatDuH(duh): #Tratamento da informação do histórico de du
    for i in range(len(duh)):
        for j in range(len(duh[i])):
            if duh[i][j].find('K') != -1:
                duh[i][j] = duh[i][j].replace('K', '')
                if duh[i][j].find(',') != -1:
                    duh[i][j] = duh[i][j].replace(',', '')
                    duh[i][j] = str(float(duh[i][j])/10/(2**10))
                else:
                    duh[i][j] = str(float(duh[i][j])/(2**10))
            if duh[i][j].find('M') != -1:
                duh[i][j] = duh[i][j].replace('M', '')
                if duh[i][j].find(',') != -1:
                    duh[i][j] = duh[i][j].replace(',', '')
                    duh[i][j] = str(float(duh[i][j])/10)
                else:
                    duh[i][j] = str(float(duh[i][j]))
            if duh[i][j].find('G') != -1:
                duh[i][j] = duh[i][j].replace('G', '')
                if duh[i][j].find(',') != -1:
                    duh[i][j] = duh[i][j].replace(',', '')
                    duh[i][j] = str(float(duh[i][j])/10*(2**10))
                else:
                    duh[i][j] = str(float(duh[i][j])*(2**10))
            if duh[i][j].find('T') != -1 and duh[i][j].find('LOST') == -1:
                duh[i][j] = duh[i][j].replace('T', '')
                if duh[i][j].find(',') != -1:
                    duh[i][j] = duh[i][j].replace(',', '')
                    duh[i][j] = str(float(duh[i][j])/10*(2**20))
                else:
                    duh[i][j] = str(float(duh[i][j])*(2**20))

    return duh

def formatDuGrafico(duh, mountedOn):
    duGrafico = []
    for i in range(len(mountedOn)):
        duGrafico.append([])
        duGrafico[i].append(mountedOn[i]) #0
        duGrafico[i].append(duh[i])       #1

    return duGrafico

def makeCommand(command): # Trata os comandos de 0 a 4
    com = command.split(' ') # Transforma o texto do comando em uma lista
    info = subprocess.check_output(com) # Salva o comando em info

    lvinfo = str(info).replace('b\'', '') # tira o b'' da variavel resultante comando
    lvinfo = lvinfo.replace('\'', '')
    res = lvinfo.split('\\n') # Separa as linhas

    return res

def makeCommand2(comstr, clist, mountedOn): #Trata o comando du
    com = comstr.split(' ') # Transforma o texto do comando em uma lista
    com = com+clist # Acrescenta a lista de caminhos no comando du
    info = subprocess.check_output(com) # Salva o comando em info

    lvinfo = str(info).replace('b\'', '') # tira o b'' da variavel resultante comando
    lvinfo = lvinfo.replace('\'', '')
    res = lvinfo.split('\\n') # Separa as linhas

    min = str(datetime.now().minute) #Armazena o minuto atual
    hora = str(datetime.now().hour) #Armazena a hora atual
    if datetime.now().minute<10:
        min = '0'+str(datetime.now().minute)
    if datetime.now().hour<10:
        hora = '0'+str(datetime.now().hour)
    time = str(datetime.now().day)+'-'+str(datetime.now().month)+'_'+hora+':'+min #Formata a informação de dia/mês_hora:minuto (o nome do arquivo)

    lista = []
    if len(mountedOn) == 1:
        mountedOn = mountedOn.replace('/', 'root')
    mountedOn = mountedOn.replace('/', '_')

    dirs = subprocess.check_output(['ls', '/home/ti_estagio/gerdisk/proj/proj/diskmng/dutmp/']) #Verifica os diretórios e arquivos na pasta de histórico de du
    dirstr = str(dirs).replace('b\'', '')
    dirstr = dirstr.replace('\'', '')
    if dirstr.find(mountedOn) == -1: #Se não achar o diretório correspondente do ponto de montagem, cria o diretório
        subprocess.run(['mkdir', '/home/ti_estagio/gerdisk/proj/proj/diskmng/dutmp/'+mountedOn])

    lvinfo2 = lvinfo.replace('\\n', '*split*\\n')
    lvinfo3 = lvinfo2.split('*split*')
    for i in lvinfo3:
        lista.append(i) #Coloca as informações do du numa lista
        if i.find('total') != -1: #Total é a ultima linha
            files = subprocess.check_output(['ls', '/home/ti_estagio/gerdisk/proj/proj/diskmng/dutmp/'+mountedOn]) #verifica os arquivos de histórico em cada diretório
            filestr = str(files).replace('b\'', '')
            filestr = filestr.replace('\'', '')
            if filestr.find(time) == -1: #Se não houver um arquivo criado no mesmo minuto, cria um arquivo de histórico novo
                f = open('/home/ti_estagio/gerdisk/proj/proj/diskmng/dutmp/'+mountedOn+'/'+time+'.out', 'a')
                for j in lista:
                    f.write(str(j)) #Coloca no arquivo as informações da lista
                f.close() #Fecha o arquivo
                lista = [] #Reseta a lista a cada 'total'

    return res

def replacestr(info): #Trata as informações dos comandos de 0 a 2
    list=['PV Name','VG Name','PV Size','Allocatable','PE Size','Total PE','Free PE','Allocated PE'] # Nomes dos campos de informação
    list=list+['Format','Metadata Areas','Metadata Sequence No','VG Access','VG Status','MAX LV','Cur LV','Open LV','Max PV','Cur PV','Act PV','VG Size','Alloc PE / Size','FreePE / Size']
    list=list+['LV Path','LV Name','LV Write Access','LV Creation host, time','LV Status','# open','LV Size','Current LE','Segments','Allocation','Read ahead sectors','- currently set to','Block device']
    remover=['System ID','PV UUID','VG UUID','LV UUID'] # Informações a serem removidas
    info = info.replace('                    ', '') # Remove os espaços vazios no meio das informações
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
    for i in list:
        info = info.replace(i, i+'*split*') # Acrescenta um *split* entre o nome da informação e a informação
    for i in remover:
        if info.find(i) != -1:
            info = info.replace(info, '') # Remove as informações em remover

    return info

def replacestr2(info):
    info = info.replace('Mounted on', 'Mounted_on') # Tira o espaço do Mounted on para não separar com o *split*
    info = info.replace('                           ', '*split*') # Troca qualquer quantidade de espaços por *split*
    info = info.replace('                          ', '*split*')
    info = info.replace('                         ', '*split*')
    info = info.replace('                        ', '*split*')
    info = info.replace('                       ', '*split*')
    info = info.replace('                      ', '*split*')
    info = info.replace('                     ', '*split*')
    info = info.replace('                    ', '*split*')
    info = info.replace('                   ', '*split*')
    info = info.replace('                  ', '*split*')
    info = info.replace('                 ', '*split*')
    info = info.replace('                ', '*split*')
    info = info.replace('               ', '*split*')
    info = info.replace('              ', '*split*')
    info = info.replace('             ', '*split*')
    info = info.replace('            ', '*split*')
    info = info.replace('           ', '*split*')
    info = info.replace('          ', '*split*')
    info = info.replace('         ', '*split*')
    info = info.replace('        ', '*split*')
    info = info.replace('       ', '*split*')
    info = info.replace('      ', '*split*')
    info = info.replace('     ', '*split*')
    info = info.replace('    ', '*split*')
    info = info.replace('   ', '*split*')
    info = info.replace('  ', '*split*')
    info = info.replace(' ', '*split*')

    return info



def duindu(self, request):
    response.write("<h1>teste</h1>")
