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
        self.naks = []

        for x in range(0, num_frames):
            self.timers.append(Timer())

        for x in range(0, num + 1):
            self.janela.append(x)

        self.janela = self.janela * 100

    def pode_enviar(self):
        if self.Sn - self.Sf < self.tam_janela and self.Sn < self.frames_a_enviar:
            return True
        if len(self.naks) > 0:
            return True
        return False

    def get_pos(self, seqno):
        x = self.Sf
        ultimo = self.Sn + 1
        while x < ultimo:
            if seqno == self.janela[x]:
                return x
            x += 1

        return 0

    def comeca_timer(self, frame):
        self.timers[frame].ativo = True
        self.timers[frame].tempo = 0

    def incrementa_timer(self):
        for x in self.timers:
            if x.ativo:
                x.tempo += 1

    def check_timeout(self):
        for x in range(0, len(self.timers)):
            if self.timers[x].ativo and self.timers[x].tempo >= 100:
                return x
        return None

    def timeout(self, reenviar):
        self.resend(self.janela[reenviar])
        self.timers[reenviar].ativo = True
        self.timers[reenviar].tempo = 0

    def send(self):
        if len(self.naks) > 0:
            z = self.resend_nak(self.naks.pop(0)[1])
            return 'ret', z

        else:
            self.timers[self.Sn].ativo = True
            self.pendentes += 1
            self.Sn += 1
            return self.janela[self.Sn - 1]

    def receive_confirmation(self, ack):
        if ack[0] == 'NAK':
            if self.Sf <= self.get_pos(ack[1]) < self.Sn:
                self.naks.append(ack)
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

    def resend_nak(self,nak):
        enviar = self.get_pos(nak)
        self.comeca_timer(enviar)
        return self.janela[enviar]

class ReceiverSR:
    def __init__(self, seq_bits, num_frames):
        self.num_frames = num_frames
        self.Rn = 0
        self.janela = []
        self.tam_janela = 2 ** (seq_bits - 1)
        self.enviados = []
        self.enviados = [False] * (num_frames+1)
        self.ackNeeded = False
        self.nakNeeded = False
        self.ack_fila = 0
        self.naks = []
        self.atrasado = False

        num = (2 ** seq_bits) - 1

        for x in range(0, num + 1):
            self.janela.append(x)

        self.janela = self.janela * 100

    def receive(self, frame):
        if self.janela[self.Rn] == frame:
            self.marca(frame)
            self.Rn += 1
            self.remove_nak(frame)
            self.ackNeeded = True
            if self.ta_atrasado(frame):
                self.atrasado = True
        elif self.check_duplicate(frame):
            self.ackNeeded = True
            self.atrasado = True
        elif self.janela[self.Rn] != frame:
            #print(frame,'dif')
            self.nakNeeded = True
            self.marca(frame)
            self.add_naks(frame)
            #return 'NAK', self.janela[self.Rn]

    def ta_atrasado(self, frame):
        posi = self.get_pos(frame)
        if self.enviados[posi+1]:
            return True
        return False


    def add_naks(self, frame):
        for x in range (self.ack_fila, self.get_pos(frame)):
            if not self.enviados[x]:
                if ('NAK', self.janela[x]) not in self.naks:
                    self.naks.append(('NAK', self.janela[x]))

    def remove_nak(self,frame):
        for x in range(0, len(self.naks)):
            if self.naks[x] == frame:
                self.naks.pop(x)
                return

    def check_duplicate(self, frame):
        aux = self.ack_fila

        while aux >= 0 and aux >= self.ack_fila - self.tam_janela:
            if self.janela[aux] == frame and self.enviados[aux]:
                return True
            aux -= 1

        return False

    def send_ack(self):
        aux = self.ack_fila
        if self.atrasado:
            self.atrasado = False
            self.ackNeeded = False
            while aux < self.ack_fila + self.tam_janela:
                if self.enviados[aux]:
                    self.ack_fila += 1
                else:
                    break
                aux += 1
            self.Rn = self.ack_fila
            return 'ACK', self.janela[self.ack_fila]
        else:
            aux = self.ack_fila
            if aux == self.Rn-1:
                self.ackNeeded = False
            self.ack_fila += 1
            return 'ACK', self.janela[aux+1]

    def send_nak(self):
        self.nakNeeded = False
        aux = self.naks
        self.naks = []

        return aux

    def marca(self, frame):
        x = self.Rn
        ultimo = self.Rn + self.tam_janela

        while x <= ultimo and x < self.num_frames:
            if self.janela[x] == frame:
                self.enviados[x] = True
                break
            x += 1

    def get_pos(self, frame):
        if type(frame) is int:
            for x in range(self.ack_fila, self.ack_fila + self.tam_janela+1):
                if self.janela[x] == frame:
                    return x
        else:
            for x in range(self.ack_fila, self.ack_fila + self.tam_janela+1):
                if self.janela[x] == frame[1]:
                    return x


def executarsr(num_frames, seq_bits, pkt_loss):
    sender = SenderSR(num_frames, seq_bits)
    receiver = ReceiverSR(seq_bits, num_frames)
    naks = []
    pacote = 0

    while sender.Sf <= num_frames - 1:
        while sender.pode_enviar():
            pacote += 1
            enviado = sender.send()
            if pacote not in pkt_loss:
                if type(enviado) is not int:
                    receiver.receive(enviado[1])
                    print('A ->> B : (', receiver.get_pos(enviado[1]+1), ') Frame ', enviado[1], "(RET)",pacote, sep=" ")
                else:
                    receiver.receive(enviado)
                    print('A ->> B : (', sender.Sn, ') Frame ', enviado, pacote, sep=" ")
            else:
                if type(enviado) is not int:
                    print('A -x B : (', receiver.get_pos(enviado[1]), ') Frame ', enviado[1], "(RET)",pacote, sep=" ")
                else:
                    print('A -x B : (', sender.Sn, ') Frame ', enviado, pacote,sep=" ")


        while receiver.ackNeeded:
            pacote += 1
            ack = receiver.send_ack()
            if pacote not in pkt_loss:
                sender.receive_confirmation(ack)
                print("B -->> A : ACK", ack[1], pacote)
            else:
                print("B --x A : ACK", ack[1], pacote)

        if receiver.nakNeeded:
            nak = receiver.send_nak()
            while len(nak) > 0:
                pacote += 1
                aux = nak.pop(0)
                if pacote not in pkt_loss:
                    receiver.Rn = aux[1]
                    print("B -->> A : NAK", aux[1], pacote)
                    recebido = sender.receive_confirmation(aux)
                else:
                    print("B --x A : NAK", aux[1],pacote)

        sender.incrementa_timer()
        if not sender.pode_enviar() and not receiver.ackNeeded and not receiver.nakNeeded:
            timeout = sender.check_timeout()
            if timeout is not None:
                pacote += 1
                print('Note over A: TIMEOUT(', timeout + 1, ')', sep=" ")
                enviado = sender.resend(sender.janela[timeout])
                if pacote not in pkt_loss:
                    print("A ->> B : (", timeout + 1, ") Frame ", enviado, " (RET)",pacote, sep=" ")
                    receiver.receive(enviado)
                else:
                    print("A -x B : (", timeout + 1, ") Frame ", enviado, " (RET)", pacote, sep=" ")

