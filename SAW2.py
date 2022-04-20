class Sender:
    def __init__(self):
        self.Sn = 0
        self.pode_enviar = True
        self.seq = [0, 1]*100
        self.confirmados = 0
        self.timer = 0

    def send(self):
        self.pode_enviar = False
        self.Sn += 1
        return self.seq[self.Sn - 1]

    def receive_confirmation(self, ack):
        if ack == self.seq[self.Sn]:
            self.pode_enviar = True
            self.confirmados += 1

    def resend(self):
        self.pode_enviar = False
        return self.seq[self.Sn - 1]


class Receiver:
    def __init__(self):
        self.Rn = 0
        self.seq = [0, 1] * 100
        self.confirma = False

    def receive(self, frame):
        if frame == self.seq[self.Rn]:
            self.Rn += 1
        self.confirma = True
        return self.seq[self.Rn]

    def envia_ack(self):
        self.confirma = False
        return self.seq[self.Rn]


def executar_saw(num_frames, pkt_loss):
    sender = Sender()
    receiver = Receiver()
    pacotes = 0

    while sender.confirmados < num_frames:
        if sender.pode_enviar:
            pacotes += 1
            enviado = sender.send()
            if pacotes not in pkt_loss:
                receiver.receive(enviado)
                print('A ->> B : (', sender.Sn, ') Frame ', enviado)
            else:
                print('A -x B : (', sender.Sn, ') Frame ', enviado)

        elif receiver.confirma:
            pacotes += 1
            confirma = receiver.envia_ack()
            if pacotes not in pkt_loss:
                sender.receive_confirmation(confirma)
                print("B -->> A : Ack", confirma)
            else:
                print("B --x A : Ack", confirma)
        else:
            print('Note over A: TIMEOUT(', sender.Sn, ')')
            pacotes += 1
            enviado = sender.resend()
            if pacotes not in pkt_loss:
                print("A ->> B : (", sender.Sn, ") Frame ", enviado, '(RET)')
                receiver.receive(enviado)
            else:
                print("A -x B : (", sender.Sn, ") Frame ", enviado, '(RET)')
