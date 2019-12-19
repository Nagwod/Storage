import subprocess
import glob

def comandodu(b):
    idx = b.rfind(':')+4
    idxf = b.rfind('\'')
    b = b[idx:idxf]
    list = glob.glob(b+'/*')
    com = 'sudo du -shc'
    com2 = com.split(' ') # Transforma o texto do comando em uma lista
    com2 = com2+list # Acrescenta a lista de caminhos no comando du
    info = subprocess.check_output(com2) # Salva o comando em info
    info2 = str(info).replace('b\'', '') # tira o b'' da variavel resultante comando
    info2 = info2.replace('\'', '')

    du = []
    for i in info2.split('\\n'):
        du.append(i.split('\\t'))
    if du[-1] == ['']:
        du.pop(-1)

    hdu = '<table border="1" align="center">'
    for i in range(len(du)):
        if du[i][-1]!='total':
            hdu = hdu+'<tr><td>'+du[i][0]+"</td><td><button class='btn btn-primary' name='"+du[i][-1]+"'value='"+du[i][-1]+"'>"+du[i][-1]+"</button></td></tr>"
        else:
            hdu = hdu+'<tr><td>'+du[i][0]+"</td><td>"+du[i][-1]+"</td></tr>"
    hdu = hdu+'</table>'

    dutotal = du[-1][0]
    du = formatDU(du, dutotal)

    context = {
        'b': b,
        'hdu': hdu,
        'du': du,
        'dutotal': dutotal
    }

    return(context)





def formatDU(duinfo, dutotal): # Tratamento da informação de du
    for i in range(len(duinfo)):
        if duinfo[i][0].find('K') != -1:
            duinfo[i][0] = duinfo[i][0].replace('K', '')
            if duinfo[i][0].find(',') != -1:
                duinfo[i][0] = duinfo[i][0].replace(',', '')
                duinfo[i][0] = str(float(duinfo[i][0])/10/(2**10))
            else:
                duinfo[i][0] = str(float(duinfo[i][0])/(2**10))
        if duinfo[i][0].find('M') != -1:
            duinfo[i][0] = duinfo[i][0].replace('M', '')
            if duinfo[i][0].find(',') != -1:
                duinfo[i][0] = duinfo[i][0].replace(',', '')
                duinfo[i][0] = str(float(duinfo[i][0])/10)
            else:
                duinfo[i][0] = str(float(duinfo[i][0]))
        if duinfo[i][0].find('G') != -1:
            duinfo[i][0] = duinfo[i][0].replace('G', '')
            if duinfo[i][0].find(',') != -1:
                duinfo[i][0] = duinfo[i][0].replace(',', '')
                duinfo[i][0] = str(float(duinfo[i][0])/10*(2**10))
            else:
                duinfo[i][0] = str(float(duinfo[i][0])*(2**10))
        if duinfo[i][0].find('T') != -1 and duinfo[i][0].find('LOST') == -1:
            duinfo[i][0] = duinfo[i][0].replace('T', '')
            if duinfo[i][0].find(',') != -1:
                duinfo[i][0] = duinfo[i][0].replace(',', '')
                duinfo[i][0] = str(float(duinfo[i][0])/10*(2**20))
            else:
                duinfo[i][0] = str(float(duinfo[i][0])*(2**20))

    total = duinfo[-1][0]
    new_du = []
    cont = 0
    aux = 0
    for i in range(len(duinfo)):
        duinfo[i][0] = float(duinfo[i][0])/float(total)*100
        if duinfo[i][1].find('total')!=-1:
            if cont > 0:
                new_du.append([aux, 'outros'])
                cont = 0
            aux = 0
            if i < 2:
                new_du.append(duinfo[i])
        else:
            if duinfo[i][0] < 1:
                aux = aux + duinfo[i][0]
                cont = cont+1
            else:
                new_du.append(duinfo[i])

    for i in new_du:
        i[0] = round(i[0], 2)

    return new_du
