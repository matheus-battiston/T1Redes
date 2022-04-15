import sys
from SAW import *
from GBN import *
from SR import *

"""Configurar dados ==================="""
def define_algo(argumentos):
    if argumentos[0] == 'saw' or argumentos[0] == 'gbn' or argumentos[0] == 'sr':
        return argumentos[0]
    else:
        print('Formato de entrada inválido')
        exit()


def define_seqbits(argumentos):
    if not argumentos[1].isnumeric():
        print('Formato de entrada invalido')
        exit()
    return int(argumentos[1])


def define_numframes(argumentos):
    if not argumentos[2].isnumeric():
        print('Formato de entrada invalido')
        exit()
    else:
        return int(argumentos[2])


def define_pkt(argumentos):
    if len(argumentos[3]) == 1 and argumentos[3] == 0:
        return argumentos[3]
    else:
        numeros = [int(x) for x in argumentos[3].split(',')]
        return numeros
"""Configurar dados ==================="""


"""Executar o simulador"""

def executar(algo,num_frames,seq_bits,pkt_loss):
    if algo =="saw":
        executar_saw(algo,num_frames,seq_bits,pkt_loss)
    elif algo == "gbn":
        executar_gbn(num_frames,seq_bits,pkt_loss)
    elif algo == "sr":
        executar_sr(num_frames,seq_bits,pkt_loss)

if __name__ == '__main__':
    #argumentos = sys.argv[1:]
    argumentos = ["gbn", "2", "20", "5"]
    algo = define_algo(argumentos)
    num_frames = define_numframes(argumentos)
    seq_bits = define_seqbits(argumentos)
    pkt_loss = define_pkt(argumentos)

    executar(algo, num_frames, seq_bits, pkt_loss)

