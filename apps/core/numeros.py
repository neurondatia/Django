import random

def verificar_intervalo(n_fim, n_inicio, qtd_numeros):
    quantidade_intervalo =  n_fim - n_inicio + 1

    return qtd_numeros > quantidade_intervalo

def sequencia_numeros(qtd_numeros, n_inicio, n_fim):

        numeros = []
        while len(numeros) < qtd_numeros:
            numero = str(random.randint(n_inicio, n_fim))
            if numero not in numeros:
                numeros.append(numero)

        numeros_gerados = ', '.join(numeros)

        return numeros_gerados

