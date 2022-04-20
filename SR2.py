class Timer:
    def __init__(self):
        self.ativo = False
        self.seqno = -1
        self.tempo = 0

    def reseta(self):
        self.seqno = -1
        self.tempo = 0


class SenderSR:
    def __init__(self, num_frames, seq_bits):
        self.Sn = 0
        self.frames_a_enviar = num_frames
        self.tam_janela = 2 ** (seq_bits - 1)
        self.pendentes = 0
        self.Sf = 0
        self.janela = []
        self.numeros = []
        num = (2 ** seq_bits) - 1
        self.timers = []

        for x in range(0, num_frames):
            self.timers.append(Timer())

        for x in range(0, num + 1):
            self.janela.append(x)

        self.janela = self.janela * 100

    def incrementa_timer(self):
        for x in self.timers:
            if x.ativo:
                x.tempo += 1

    def check_timeout(self):
        for x in range(0, len(self.timers)):
            if self.timers[x].ativo and self.timers[x].tempo >= 10:
                return x
        return None

    def comeca_timer(self, frame):
        self.timers[frame].ativo = True
        self.timers[frame].tempo = 0

    def timeout(self, reenviar):
        self.resend(self.janela[reenviar])
        self.timers[reenviar].ativo = True
        self.timers[reenviar].tempo = 0

    def pode_enviar(self):
        if self.Sn - self.Sf < self.tam_janela and self.Sn < self.frames_a_enviar:
            return True

        return False

    def send(self):
        self.timers[self.Sn].ativo = True
        self.pendentes += 1
        self.Sn += 1
        return self.janela[self.Sn - 1]

    def receive_confirmation(self, ack):
        if ack[0] == 'NAK':
            if self.Sf <= self.get_pos(ack[1]) < self.Sn:
                return self.resend(ack[1])
        else:
            if self.Sf < self.get_pos(ack[1]):
                while self.Sf < self.get_pos(ack[1]):
                    self.timers[self.Sf].ativo = False
                    self.Sf += 1
            return self.Sf

    def resend(self, ack):
        enviar = self.get_pos(ack)
        self.comeca_timer(enviar)
        return self.janela[enviar]

    def get_pos(self, seqno):
        x = self.Sf
        ultimo = self.Sn + 1
        while x < ultimo:
            if seqno == self.janela[x]:
                return x
            x += 1

        return 0


class ReceiverSR:
    def __init__(self, seq_bits, num_frames):
        self.num_frames = num_frames
        self.Rn = 0
        self.janela = []
        self.tam_janela = 2 ** (seq_bits - 1)
        self.enviados = []
        self.enviados = [False] * num_frames
        self.ackNeeded = False
        self.nakSent = False
        num = (2 ** seq_bits) - 1

        for x in range(0, num + 1):
            self.janela.append(x)

        self.janela = self.janela * 100

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
        return 'ACK', self.janela[self.Rn]

    def marca(self, frame):
        x = self.Rn
        ultimo = self.Rn + self.tam_janela

        while x <= ultimo and x < self.num_frames:
            if self.janela[x] == frame:
                self.enviados[x] = True
                break
            x += 1


def executarsr(num_frames, seq_bits, pkt_loss):
    sender = SenderSR(num_frames, seq_bits)
    receiver = ReceiverSR(seq_bits, num_frames)
    naks = []
    pacote = 0

    while sender.Sf <= num_frames - 1:
        sender.incrementa_timer()
        check = sender.check_timeout()
        if check is not None:
            print('Note over A: TIMEOUT(', sender.get_pos(check)+1, ')')
            pacote += 1
            enviado = sender.resend(check)
            if pacote not in pkt_loss:
                recebido = receiver.receive(enviado)
                print('A ->> B : (', sender.get_pos(check)+1, ') Frame ', enviado, '(RET)')
                if recebido is not None:
                    if recebido[0] == 'NAK':
                        naks.append(recebido)
            else:
                print('A -x B : (', sender.get_pos(enviado)+1, ') Frame ', enviado, '(RET)')

        elif sender.pode_enviar():
            pacote += 1
            enviado = sender.send()
            if pacote not in pkt_loss:
                recebido = receiver.receive(enviado)
                if recebido is not None:
                    if recebido[0] == 'NAK':
                        naks.append(recebido)
                    else:
                        print('A ->> B : (', sender.Sn, ') Frame ', enviado)
            else:
                print('A -x B : (', sender.Sn, ') Frame ', enviado)

        elif len(naks) > 0:
            pacote += 1
            if pacote not in pkt_loss:
                recebido = sender.receive_confirmation(naks.pop(0))
                print('B -->> A: (', sender.get_pos(recebido), 'NAK', recebido)
            else:
                z = naks.pop(0)
                print('B --x A: (', sender.get_pos(z), 'NAK', z)

        elif receiver.ackNeeded:
            pacote += 1
            ack = receiver.send_ack()
            if pacote not in pkt_loss:
                sender.receive_confirmation(ack)
                print('B -->> A: (', sender.get_pos(ack[1]), 'ACK', ack[1])
            else:
                print('B --x A: (', sender.get_pos(ack[1]), 'ACK', ack[1])
