import sys


class sender_saw:
    def __init__(self, nro_frames):
        self.N = 0
        self.nro_frames = nro_frames
        self.frame = []
        self.seqno = 0
        self.retry = False

        for x in range(0, int(nro_frames)):
            if x % 2 == 0:
                self.frame.append(0)
            else:
                self.frame.append(1)

    def send(self):
        if not self.retry:
            print("A ->> B : (", self.N + 1, ") Frame ", self.seqno)
            self.retry = False
            return self.seqno
        else:
            print("A ->> B : (", self.N + 1, ") Frame ", self.seqno, "(RET)")
            self.retry = False
            return self.seqno

    def send_fail(self):
        print("A -x B : (", self.N + 1, ") Frame ", self.seqno)
        print("Note over A : TIMEOUT (", self.N + 1, ")")
        self.retry = True

    def receive(self, ack):
        if type(ack) == int:
            self.seqno = ack
            self.N += 1
        else:
            if self.seqno == 0:
                seq_1 = 1
            else:
                seq_1 = 0
            self.retry = True


class receiver_saw:
    def __init__(self, nro_frames):
        self.seqno = 1
        self.frame = []
        self.primeiro = True

        for x in range(0, int(nro_frames)):
            if x % 2 == 0:
                self.frame.append(0)
            else:
                self.frame.append(1)


    def confirma(self):
        print("B --> A: Ack ", self.seqno)
        antigo = self.seqno
        if self.seqno == 0:
            self.seqno = 1
        else:
            self.seqno = 0
        return antigo

    def confirma_loss(self):
        print("B --x A: Ack ", self.seqno)

        return False

    def redundant(self, seqno):
        print(seqno, self.seqno)
        if seqno == self.seqno:
            return True

        return False

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


def executar(algo, num_frames, seq_bits, pkt_loss):
    pacotes = 1
    sender = sender_saw(num_frames)
    receiver = receiver_saw(num_frames)
    sucesso = 0

    while (sucesso < 10):
        if pacotes in pkt_loss:
            sender.send_fail()
            pacotes += 1
        else:
            seqno = sender.send()
            pacotes += 1
            if pacotes in pkt_loss:
                pacotes += 1
                ack = receiver.confirma_loss()
            else:
                pacotes +=1
                ack = receiver.confirma()
                sucesso += 1

            sender.receive(ack)

if __name__ == '__main__':
    argumentos = sys.argv[1:]
    argumentos = ["saw", "1", "10", "3,10,15"]
    algo = define_algo(argumentos)
    num_frames = define_numframes(argumentos)
    seq_bits = define_seqbits(argumentos)
    pkt_loss = define_pkt(argumentos)
    executar(algo, num_frames, seq_bits, pkt_loss)
