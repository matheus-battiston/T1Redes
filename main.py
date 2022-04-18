import sys
from GBN import *
from SR2 import *
from SAW2 import *

"""Configurar dados ==================="""


def define_algo(parametros):
    if parametros[0] == 'saw' or parametros[0] == 'gbn' or parametros[0] == 'sr':
        return parametros[0]
    else:
        print('Formato de entrada inválido')
        exit()


def define_seqbits(parametros):
    if not parametros[1].isnumeric():
        print('Formato de entrada invalido')
        exit()
    return int(parametros[1])


def define_numframes(parametros):
    if not parametros[2].isnumeric():
        print('Formato de entrada invalido')
        exit()
    else:
        return int(parametros[2])


def define_pkt(parametros):
    if len(parametros[3]) == 1 and parametros[3] == 0:
        return parametros[3]
    else:
        numeros = [int(x) for x in parametros[3].split(',')]
        return numeros


"""Executar o simulador"""


def executar(algoritmo, numero_frames, sequencia_bits, pacote_perdido):
    if algoritmo == "saw":
        executar_saw(numero_frames, pkt_loss)
    elif algoritmo == "gbn":
        executar_gbn(numero_frames, sequencia_bits, pacote_perdido)
    elif algoritmo == "sr":
        executarsr(numero_frames, sequencia_bits, pacote_perdido)


if __name__ == '__main__':
    argumentos = sys.argv[1:]
    algo = define_algo(argumentos)
    num_frames = define_numframes(argumentos)
    seq_bits = define_seqbits(argumentos)
    pkt_loss = define_pkt(argumentos)

    executar(algo, num_frames, seq_bits, pkt_loss)
