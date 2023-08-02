from django.shortcuts import render, redirect


from apps.core.models import Ferramentas
from django.http import HttpResponse
from pytube import YouTube
from django.contrib import messages

import qrcode
from io import BytesIO

from reportlab.lib.pagesizes import landscape, letter, A5
from reportlab.pdfgen import canvas
from apps.core.forms import ReciboForm

from apps.core.recibo import gerador_recibo
from apps.core.senha import gerar_senha


from apps.core.numeros import verificar_intervalo, sequencia_numeros


def home(request):

    qrcode = Ferramentas.objects.get(nome="Gerador de QR Code")
    recibo = Ferramentas.objects.get(nome="Gerador de Recibo")
    senha = Ferramentas.objects.get(nome="Gerador de Senha")
    numeros = Ferramentas.objects.get(nome="Números Aleatórios")

    context = {'qrcode':qrcode,'recibo':recibo,'senha':senha,'numeros':numeros,}
    return render(request, 'index.html', context)

def ferramenta_youtube(request):
    youtube = Ferramentas.objects.get(nome="Download de Vídeo do YouTube")
    if not youtube.ativa:
        return redirect('home')

    if request.method == "GET":

        return render(request, 'youtube.html')
    else:
        try:
            url = request.POST.get("url")
            yt = YouTube(url)
            video = yt.streams.get_highest_resolution()
            video_filename = f'{yt.title}.mp4'

            response = HttpResponse(content_type='video/mp4')
            response['Content-Disposition'] = f'attachment; filename="{video_filename}"'
            video.stream_to_buffer(response)
        except:
            messages.error(request, "Informe uma URL válida")
            return render(request, 'youtube.html')

        return response

def ferramenta_qrcode(request):
    qrcodee = Ferramentas.objects.get(nome="Gerador de QR Code")
    if not qrcodee.ativa:
        return redirect('home')

    if request.method == "GET":
        return render(request, 'qrcode.html')
    else:
        info = request.POST.get("informacao")
        # Gera o QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(info)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")

        # Cria um buffer de imagem
        buffer = BytesIO()
        qr_image.save(buffer)
        buffer.seek(0)

        # Define o cabeçalho de resposta para exibir a imagem
        response = HttpResponse(content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="qrcode.png"'
        response.write(buffer.getvalue())

        return response


def ferramenta_recibos(request):
    recibo = Ferramentas.objects.get(nome="Gerador de Recibo")
    if not recibo.ativa:
        return redirect('home')

    if request.method == 'POST':
        form = ReciboForm(request.POST)
        if form.is_valid():
            # Obter os dados do formulário
            nome_pagador = form.cleaned_data['nome_pagador']
            endereco_pagador = form.cleaned_data['endereco_pagador']
            cpf_cnpj_pagador = form.cleaned_data['cpf_cnpj_pagador']
            cpf_cnpj_receptor = form.cleaned_data['cpf_cnpj_receptor']
            nome_receptor = form.cleaned_data['nome_receptor']
            descricao_servico = form.cleaned_data['descricao_servico']
            valor = form.cleaned_data['valor']
            cidade = form.cleaned_data['cidade']
            data_emissao = form.cleaned_data['data_emissao']

            # Cria um objeto Canvas para o PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="recibo.pdf"'

            # Define o tamanho da página como paisagem (landscape)
            width, height = landscape(letter)

            # Cria o PDF no objeto Canvas

            pdf = canvas.Canvas(response, pagesize=(A5[1], A5[0]))
            gerador_recibo(pdf, nome_pagador, cpf_cnpj_pagador, descricao_servico, cidade, data_emissao, valor,
                           nome_receptor, cpf_cnpj_receptor, endereco_pagador)


            return response

    else:
        form = ReciboForm()
    return render(request, 'recibo.html', {'form': form})




def ferramenta_senha(request):
    senha = Ferramentas.objects.get(nome="Gerador de Senha")
    if not senha.ativa:
        return redirect('home')

    if request.method == "GET":
        senha_gerada = ""
        return render(request, 'senha.html', {"senha_gerada":senha_gerada})

    else:
        caracter = request.POST.get("qtdcaracter")
        senha_gerada = gerar_senha(int(caracter))

        return render(request, 'senha.html', {"senha_gerada":senha_gerada})


def ferramenta_numeros(request):
    numeros = Ferramentas.objects.get(nome="Números Aleatórios")
    if not numeros.ativa:
        return redirect('home')


    if request.method == "GET":

        numeros_gerados = ""
        return render(request, 'numeros.html', {"numeros_gerados":numeros_gerados})

    else:
        qtd_numeros = int(request.POST.get("qtdnumeros"))
        n_inicio = int(request.POST.get("ninicio"))
        n_fim = int(request.POST.get("nfim"))
        if n_inicio > n_fim:
            numeros_gerados = "Você informou o número de início maior do que o número de fim"
            return render(request, 'numeros.html', {"numeros_gerados": numeros_gerados})
        intervalo = verificar_intervalo(n_fim, n_inicio, qtd_numeros)
        if intervalo:
            numeros_gerados = "Você informou um intervalo de número insuficiente para a quantidade de número desejada"
            return render(request, 'numeros.html', {"numeros_gerados": numeros_gerados})



        numeros_gerados = sequencia_numeros(qtd_numeros, n_inicio, n_fim)

        return render(request, 'numeros.html', {"numeros_gerados":numeros_gerados})