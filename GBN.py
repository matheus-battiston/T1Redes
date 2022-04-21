class Sender:
    def __init__(self, seq_bits):

        self.primeiro_janela = 0
        self.ultimo_janela = 0
        self.seq_bits = seq_bits
        self.seq = []
        self.janela = (2 ** seq_bits) - 1
        self.timer = 0
        self.prox_envio = self.primeiro_janela
        self.pendentes = 0
        for x in range(0, self.janela + 1):
            self.seq.append(x)
        self.seq = self.seq*100
        self.Sn = 0

    def incrementa_timer(self):
        self.timer += 1

    def timeout(self):
        print('Note over A: TIMEOUT(', self.primeiro_janela+1, ')',sep="")
        self.prox_envio = self.primeiro_janela
        self.timer = 0
        self.pendentes = 0
        self.ultimo_janela = self.primeiro_janela


    def pode_enviar(self):
        if self.pendentes < self.janela:
            return True

        return False

    def send(self):
        self.ultimo_janela += 1
        self.prox_envio += 1
        self.pendentes += 1
        self.Sn += 1
        return self.seq[self.prox_envio - 1], self.prox_envio

    def receive_confirmation(self, ack):
        aux = self.primeiro_janela
        contador = 0
        x = self.primeiro_janela
        ultimo = self.ultimo_janela
        self.timer = 0

        while ack != self.seq[aux]:
            self.primeiro_janela += 1
            contador += 1
            aux += 1

        self.pendentes -= contador
        return contador


class Receiver:

    def __init__(self, seq_bits):
        self.recebidos = []
        self.seq_bits = seq_bits
        self.seq = []
        self.janela = 0
        self.Rn = 0

        aux = (2 ** seq_bits) - 1
        self.window = aux
        for x in range(0, aux+1):
            self.seq.append(x)

        self.seq = self.seq*100

    def receive(self, frame):
        if self.check_duplicate(frame):
            self.recebidos.append(frame)
        elif frame == self.seq[self.Rn]:
            self.recebidos.append(frame)
            self.janela += 1
            self.Rn += 1

    def confirma(self):
        return self.seq[self.recebidos.pop(0) + 1]

    def ackNeeded(self):
        if len(self.recebidos) > 0:
            return True

        return False

    def check_duplicate(self, frame):
        aux = self.Rn -1
        while aux >= 0 and aux > self.Rn - self.seq_bits:
            if frame == self.seq[aux]:
                return True
            aux -= 1
        return False

def executar_gbn(num_frames, seq_bits, pkt_loss):
    sucesso = 0
    sender = Sender(seq_bits)
    receiver = Receiver(seq_bits)
    pacotes = 1
    enviados = []

    while sucesso < num_frames:
        while sender.pode_enviar() and sender.ultimo_janela < num_frames:
            enviado, frame = sender.send()
            if pacotes not in pkt_loss:
                receiver.receive(enviado)
                if frame not in enviados:
                    print("A ->> B : (", frame, ") Frame ", enviado, sep="")
                else:
                    print("A ->> B : (", frame, ") Frame ", enviado, " (RET)",sep="")

            else:
                print("A -x B : (", frame, ") Frame ", enviado, sep="")

            pacotes += 1
            enviados.append(frame)

        while receiver.ackNeeded():
            recebido = receiver.confirma()
            if pacotes not in pkt_loss and (recebido != -1):
                print("B -->> A : Ack", recebido)
                confirmados = sender.receive_confirmation(recebido)
                pacotes += 1
                sucesso += confirmados
            elif pacotes in pkt_loss:
                print("B --x A : Ack", recebido)
                pacotes += 1

        if not receiver.ackNeeded() and not sender.pode_enviar():
            sender.timeout()
