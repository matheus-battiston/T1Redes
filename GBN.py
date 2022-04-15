class sender_gbn:
    def __init__(self, seq_bits):

        self.primeiro_janela = 0
        self.ultimo_janela = 0
        self.seq_bits = seq_bits
        self.seq = []
        self.janela = (2 ** seq_bits) - 1
        self.timer = 0
        self.prox_envio = self.primeiro_janela
        self.pendentes = 0
        for x in range (0,self.janela+1):
            self.seq.append(x)
        self.seq = self.seq*100

    def incrementa_timer(self):
        if self.timeout():
            self.prox_envio = self.primeiro_janela
            self.timer = 0
            self.pendentes = 0
            self.ultimo_janela = self.primeiro_janela
        self.timer +=1

    def timeout(self):
        if self.timer == 20:
            return True

        return False

    def pode_enviar(self):
        if self.pendentes < self.janela:
            return True

        return False


    def send(self):
        self.ultimo_janela +=1
        self.prox_envio +=1
        self.pendentes += 1
        return self.seq[self.prox_envio - 1], self.prox_envio

    def receive_confirmation(self, ack):
        contador = 0
        x = self.primeiro_janela
        ultimo = self.ultimo_janela
        self.timer = 0

        while x <= ultimo:
            if self.seq[x] != ack:
                self.primeiro_janela += 1
                contador+=1
            else:
                break

            x += 1
        self.pendentes -= contador
        return contador


class receiver_gbn:

    def __init__(self, seq_bits):
        self.recebidos = []
        self.seq_bits = seq_bits
        self.seq = []
        self.janela = 0

        aux = (2 ** seq_bits) - 1
        self.window = aux
        for x in range (0,aux+1):
            self.seq.append(x)

        self.seq = self.seq*100


    def receive(self,frame):
        if frame == self.seq[self.janela]:
            self.recebidos.append(frame)
            self.janela+=1
        else:
            pass

    def confirma(self):
        if len(self.recebidos) > 0:

            aux = self.recebidos.pop(0)
            if aux < self.window:
                if aux == 3:
                    return 0
                else:
                    return aux+1
            else:
                return 0
        else:
            return -1


def executar_gbn(num_frames,seq_bits,pkt_loss):
    sucesso = 0
    sender = sender_gbn(seq_bits)
    receiver = receiver_gbn(seq_bits)
    pacotes = 1
    enviados = []

    while sucesso < num_frames:
        if pacotes > 45:
            break
        sender.incrementa_timer()
        if sender.pode_enviar() and sender.ultimo_janela < num_frames:
            enviado,frame = sender.send()
            if pacotes not in pkt_loss:
                if frame not in enviados:
                    print("A ->> B : ", frame, " Frame ", enviado)
                else:
                    print("A ->> B : ", frame, " Frame ", enviado, "(RET)")


                receiver.receive(enviado)

            pacotes +=1
        else:
            confirmados = 0
            recebido = receiver.confirma()
            if pacotes not in pkt_loss and (recebido != -1):
                print("B -->> A : Ack", recebido)
                confirmados = sender.receive_confirmation(recebido)

                pacotes +=1
                sucesso +=1

        enviados.append(frame)
