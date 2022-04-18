class Timer:
    def __init__(self):
        self.seqno = -1
        self.tempo = 0

    def reseta(self):
        self.seqno = -1
        self.tempo = 0


class SenderSR:
    def __init__(self, num_frames, seq_bits):
        self.Sn = 0
        self.frames_a_enviar = num_frames
        self.tam_janela = 2**(seq_bits-1)
        self.pendentes = 0
        self.Sf = 0
        self.janela = []

        for x in range(0, self.tam_janela):
            self.janela.append(x)

        self.janela = self.janela*100

    def pode_enviar(self):
        if self.Sn - self.Sf < self.tam_janela and self.Sn < self.frames_a_enviar:
            return True

        return False

    def send(self):

        self.pendentes += 1
        self.Sn += 1
        return self.janela[self.Sn - 1]

    def receive_confirmation(self, ack):
        if ack[0] == 'NAK':
            if self.Sf <= self.get_pos(ack[1]) < self.Sn:
                return self.resend(ack[1])
        else:
            if self.Sf < self.get_pos(ack[1]) < self.Sn:
                while self.Sf <= self.get_pos(ack[1]):
                    self.Sf += 1

            return self.Sf

    def get_pos(self, seqno):
        x = self.Sf
        ultimo = self.Sn+1
        while x < ultimo:
            if seqno == self.janela[x]:
                return x
            x += 1

        return 0

    def resend(self, ack):
        x = self.Sf
        ultimo_janela = x + self.tam_janela
        while x < ultimo_janela:
            if self.janela[x] == ack:
                return self.janela[x]
            x += 1


class ReceiverSR:
    def __init__(self, seq_bits, num_frames):
        self.num_frames = num_frames
        self.Rn = 0
        self.janela = []
        self.tam_janela = 2**(seq_bits-1)
        self.enviados = []
        self.enviados = [False]*num_frames
        self.ackNeeded = False
        self.nakSent = False

        for x in range(0, self.tam_janela):
            self.janela.append(x)

        self.janela = self.janela*100

    def receive(self, frame):
        if self.janela[self.Rn] != frame and not self.nakSent:
            self.nakSent = True
            self.marca(frame)
            return 'NAK', self.janela[self.Rn]
        elif self.janela[self.Rn] != frame:
            self.marca(frame)
        else:
            self.marca(frame)
            while self.Rn < self.num_frames and self.enviados[self.Rn]:
                self.Rn += 1
                self.ackNeeded = True

    def send_ack(self):
        self.ackNeeded = self.nakSent = False
        return 'ACK', self.janela[self.Rn-1]

    def marca(self, frame):
        x = self.Rn
        ultimo = self.Rn + self.tam_janela

        while x <= ultimo and x < 20:
            if self.janela[x] == frame:
                self.enviados[x] = True
                break
            x += 1


def executarsr(num_frames, seq_bits, pkt_loss):
    sender = SenderSR(num_frames, seq_bits)
    receiver = ReceiverSR(seq_bits, num_frames)
    naks = []
    pacote = 0
    recebido = None

    while sender.Sf <= num_frames - 1:
        pacote += 1
        if sender.pode_enviar():
            enviado = sender.send()
            if pacote not in pkt_loss:
                recebido = receiver.receive(enviado)
            if recebido is not None:
                naks.append(recebido)
        else:
            print(receiver.enviados)
            if receiver.ackNeeded:
                ack = receiver.send_ack()
                sender.receive_confirmation(ack)
            elif len(naks) > 0:
                enviado = sender.receive_confirmation(naks.pop(0))
                receiver.receive(enviado)
