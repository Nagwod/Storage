from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from diskmng.comandos import comandos
from diskmng.comandodu import comandodu

def menu(request):
    return render(request, 'diskmng/index.html')

def storage(request):
    context = comandos()
    if request.method=='POST':
        return redirect('du')
    return render(request, 'diskmng/storage.html', context)

def du(request):
    botao = request.POST
    request.method = 'GET'
    b = str(botao)
    context = comandodu(b)

    if request.method=='POST':
        return redirect('')
    return render(request, 'diskmng/du.html', context)
