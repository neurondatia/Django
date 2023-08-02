from django.test import TestCase, Client
from django.urls import reverse
from apps.core.models import Ferramentas

from django.contrib.messages import get_messages

from io import BytesIO
from PIL import Image

from unittest.mock import patch


from apps.core.numeros import verificar_intervalo, sequencia_numeros


class HomeViewTest(TestCase):
    def setUp(self):
        # Criação de objetos Ferramentas para simular dados do banco de dados
        self.qrcode = Ferramentas.objects.create(nome="Gerador de QR Code")
        self.recibo = Ferramentas.objects.create(nome="Gerador de Recibo")
        self.senha = Ferramentas.objects.create(nome="Gerador de Senha")
        self.numeros = Ferramentas.objects.create(nome="Números Aleatórios")

    def test_home_view(self):
        # Obtenção da URL da view "home" usando o reverse
        url = reverse('home')

        # Solicitação GET para a URL da view
        response = self.client.get(url)

        # Verificação do código de status da resposta
        self.assertEqual(response.status_code, 200)

        # Verificação do template utilizado na resposta
        self.assertTemplateUsed(response, 'index.html')

        # Verificação dos objetos Ferramentas no contexto da resposta
        self.assertEqual(response.context['qrcode'], self.qrcode)
        self.assertEqual(response.context['recibo'], self.recibo)
        self.assertEqual(response.context['senha'], self.senha)
        self.assertEqual(response.context['numeros'], self.numeros)



class FerramentaQRCodeTest(TestCase):
    def setUp(self):
        # Cria o objeto Ferramentas para o teste
        Ferramentas.objects.create(nome="Gerador de QR Code", ativa=True)

    def test_ferramenta_qrcode_get(self):
        # Teste quando é feita uma requisição GET
        client = Client()
        response = client.get(reverse('ferramenta_qrcode'))
        self.assertEqual(response.status_code, 200)  # Verifica se a resposta foi bem-sucedida

    def test_ferramenta_qrcode_post(self):
        # Teste quando é feita uma requisição POST
        client = Client()
        info = "Teste de informação"
        response = client.post(reverse('ferramenta_qrcode'), {'informacao': info})
        self.assertEqual(response.status_code, 200)  # Verifica se a resposta foi bem-sucedida

        # Verifica se a resposta é uma imagem PNG
        self.assertEqual(response['Content-Type'], 'image/png')

        # Verifica se a imagem do QR Code é gerada corretamente
        qr_image = Image.open(BytesIO(response.content))
        self.assertEqual(qr_image.format, 'PNG')
        self.assertEqual(qr_image.size, (350, 350))





class FerramentaRecibosTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_envio_formulario_post_valido(self):
        # Criando objeto Ferramentas simulado para o teste
        ferramentas = Ferramentas.objects.create(nome="Gerador de Recibo", ativa=True)

        url = reverse('ferramenta_recibos')

        # Dados do formulário válidos para o teste
        data = {
            'nome_pagador': 'João Silva',
            'endereco_pagador': 'Rua Teste, 123',
            'cpf_cnpj_pagador': '123.456.789-10',
            'cpf_cnpj_receptor': '987.654.321-00',
            'nome_receptor': 'Maria Souza',
            'descricao_servico': 'Serviço de Consultoria',
            'valor': '500.00',
            'cidade': 'São Paulo',
            'data_emissao': '2023-07-22',
        }

        # Faz uma requisição POST à view
        response = self.client.post(url, data)


        # Verifica se o PDF gerado não está vazio
        self.assertTrue(len(response.content) > 0)

        # Verifica se a view está retornando uma resposta com o content type correto
        self.assertEqual(response['Content-Type'], 'application/pdf')

        # Verifica se o nome do arquivo do PDF está definido corretamente na resposta
        self.assertIn('recibo.pdf', response['Content-Disposition'])



class FerramentaSenhaTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Criando objeto Ferramentas simulado para o teste
        self.senha_ferramenta = Ferramentas.objects.create(nome="Gerador de Senha", ativa=True)

    @patch('apps.core.views.gerar_senha')
    def test_geracao_senha_view(self, mock_gerar_senha):
        # Configura o comportamento simulado para a função gerar_senha
        tamanho_senha = 10

        # Define a URL da view
        url = reverse('ferramenta_senha')

        # Faz uma requisição GET à view
        response = self.client.get(url)

        # Verifica se a view retornou o template correto
        self.assertTemplateUsed(response, 'senha.html')


        # Faz uma requisição POST à view para gerar uma senha
        data = {'qtdcaracter': tamanho_senha}
        response_post = self.client.post(url, data)

        # Verifica se a view retornou o template correto após a requisição POST
        self.assertTemplateUsed(response_post, 'senha.html')


        # Verifica se a função gerar_senha foi chamada com o tamanho correto
        mock_gerar_senha.assert_called_once_with(tamanho_senha)


class FerramentaNumerosTest(TestCase):

    def setUp(self):
        self.ferramenta_numeros_url = reverse('ferramenta_numeros')
        self.ferramenta = Ferramentas.objects.create(nome="Números Aleatórios", ativa=True)


    def test_get_request(self):
        # Testa se a view é carregada corretamente quando uma solicitação GET é feita.
        response = self.client.get(self.ferramenta_numeros_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'numeros.html')

    def test_invalid_interval(self):
        # Testa se a mensagem correta é exibida quando o intervalo informado é inválido.
        response = self.client.post(self.ferramenta_numeros_url, data={'qtdnumeros': '5', 'ninicio': '10', 'nfim': '5'})
        self.assertContains(response, "Você informou o número de início maior do que o número de fim")
        self.assertTemplateUsed(response, 'numeros.html')

    def test_insufficient_interval(self):
        # Testa se a mensagem correta é exibida quando o intervalo informado é insuficiente para a quantidade de números desejada.
        response = self.client.post(self.ferramenta_numeros_url, data={'qtdnumeros': '10', 'ninicio': '1', 'nfim': '5'})
        self.assertContains(response, "Você informou um intervalo de número insuficiente para a quantidade de número desejada")
        self.assertTemplateUsed(response, 'numeros.html')

    def test_valid_sequence_generation(self):
        # Testa se a sequência de números é gerada corretamente quando uma solicitação POST válida é feita.
        response = self.client.post(self.ferramenta_numeros_url, data={'qtdnumeros': '5', 'ninicio': '1', 'nfim': '10'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'numeros.html')


