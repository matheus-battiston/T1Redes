import sys


class sender_saw:

    def __init__(self, pkt_loss, num_frames):
        self.Sn = 0
        self.pkt_loss = pkt_loss
        self.num_frames = num_frames
        self.seq = []
        self.Enviando = 1
        self.confirmation = True
        self.retry = False

        for x in range (0,999):
            self.seq.append(x%2)

    def send(self):
        self.confirmation = False
        return self.seq[self.Sn]


    def receive_confirmation(self, confirmation,ack):
        if not confirmation:
            print("A -x B : ", self.Enviando, " Frame ", self.seq[self.Sn])
            print('Note over A: TIMEOUT(',self.Enviando, ")")
            self.retry = True
        elif self.retry:
            print("A ->> B : ", self.Enviando, " Frame ", self.seq[self.Sn], "(RET)")
            print("B -->> A : Ack", ack)
            self.Sn+=1
            self.Enviando +=1
            self.retry = False
        else:
            print("A ->> B : ", self.Enviando, " Frame ", self.seq[self.Sn])
            print("B -->> A : Ack", ack)

            self.Sn +=1
            self.Enviando +=1

class receiver_saw:
    def __init__(self, nro_frames):
        self.Sn = 1
        self.seq = []

        for x in range(0,999):
            self.seq.append(x%2)


    def is_redundant(self,seq_frame):
        if self.seq[self.Sn] == seq_frame:
            return True

        return False

    def receive(self,seqno):
        if not self.is_redundant(seqno):
            self.Sn +=1
            return self.seq[self.Sn-1]
        else:
            return self.seq[self.Sn]


def executar(algo, num_frames, seq_bits, pkt_loss):
    sender = sender_saw(pkt_loss,num_frames)
    receiver = receiver_saw(num_frames)
    sucesso = 0
    pacotes = 1

    while sucesso < 10:
        enviado = sender.send()
        if pacotes not in pkt_loss:
            pacotes += 1
            recebido = receiver.receive(enviado)
            if pacotes not in pkt_loss:
                pacotes+=1
                sender.receive_confirmation(True,recebido)
                sucesso +=1
            else:
                print("B -x A : Ack", recebido)
                pacotes+=1
                sender.receive_confirmation(False,recebido)
        else:
            sender.send()
            sender.receive_confirmation(False,None)
            pacotes+=1




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
    return argumentos[1]


def define_numframes(argumentos):
    if not argumentos[2].isnumeric():
        print('Formato de entrada invalido')
        exit()
    else:
        return argumentos[2]


def define_pkt(argumentos):
    if len(argumentos[3]) == 1 and argumentos[3] == 0:
        return argumentos[3]
    else:
        numeros = [int(x) for x in argumentos[3].split(',')]
        return numeros
"""Configurar dados ==================="""


"""Executar o simulador"""


if __name__ == '__main__':
    #argumentos = sys.argv[1:]
    argumentos = ["saw", "1", "10", "3,10,15"]
    algo = define_algo(argumentos)
    num_frames = define_numframes(argumentos)
    seq_bits = define_seqbits(argumentos)
    pkt_loss = define_pkt(argumentos)
    executar(algo, num_frames, seq_bits, pkt_loss)