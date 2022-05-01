class Timer:
    def __init__(self):
        self.ativo = False
        self.tempo = 0

    def reseta(self):
        self.tempo = 0


class SenderSR:
    def __init__(self, num_frames, seq_bits):
        self.Sn = 0  # Referencia para qual frame deve ser enviado a seguir
        self.frames_a_enviar = num_frames
        self.tam_janela = 2 ** (seq_bits - 1)
        self.pendentes = 0  # Frames esperando confirmação
        self.Sf = 0  # Referencia para qual frame é o começo da janela
        self.janela = []  # Lista com os numeros de sequencia
        num = (2 ** seq_bits) - 1
        self.timers = []
        self.naks = []  # Lista para controlar naks recebidos

        for x in range(0, num_frames):
            self.timers.append(Timer())

        for x in range(0, num + 1):
            self.janela.append(x)

        self.janela = self.janela * 100

    # Função para definir se pode enviar um frame ou reenviar caso tenha algum nak
    def pode_enviar(self):
        if self.Sn - self.Sf < self.tam_janela and self.Sn < self.frames_a_enviar:
            return True
        if len(self.naks) > 0:
            return True
        return False

    # Função que recebe um número de sequencia e retorna sua posição na lista
    def get_pos(self, seqno):
        x = self.Sf
        ultimo = self.Sn + 1
        while x < ultimo:
            if seqno == self.janela[x]:
                return x
            x += 1

        return 0

    # Ativa o timer de um frame
    def comeca_timer(self, frame):
        self.timers[frame].ativo = True
        self.timers[frame].tempo = 0

    # Incrementa 1 no timer de todos os frames
    def incrementa_timer(self):
        for x in self.timers:
            if x.ativo:
                x.tempo += 1

    # Checa se algum frame deve ser dado timeout
    # Retorna o frame que estourou o tempo limite
    def check_timeout(self):
        for x in range(0, len(self.timers)):
            if self.timers[x].ativo and self.timers[x].tempo >= 100:
                return x
        return None

    # Reenvia um frame e recomeça o seu timer
    def timeout(self, reenviar):
        self.resend(self.janela[reenviar])
        self.timers[reenviar].ativo = True
        self.timers[reenviar].tempo = 0

    # Faz a simulação do envio de um frame
    # Caso seja um frame que esteja sendo enviado por ter recebido um NAK retorna junto uma indicação
    # e o número de sequencia do frame
    def send(self):
        if len(self.naks) > 0:
            z = self.resend(self.naks.pop(0)[1])
            return 'ret', z

        else:
            self.timers[self.Sn].ativo = True
            self.pendentes += 1
            self.Sn += 1
            return self.janela[self.Sn - 1]

    # Recebe um NAK ou um ACK
    # Caso seja um nak coloca na lista de naks
    # Caso seja um ack incrementa o Sf e desativa o timer do frame
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

    # Reenvia um frame e recomeça seu timer, retorna o número de sequencia
    def resend(self, ack):
        enviar = self.get_pos(ack)
        self.comeca_timer(enviar)
        return self.janela[enviar]


class ReceiverSR:
    def __init__(self, seq_bits, num_frames):
        self.num_frames = num_frames
        self.Rn = 0  # Referencia para a posição do frame esperado
        self.janela = []  # Lista dos numeros de sequencia
        self.tam_janela = 2 ** (seq_bits - 1)
        self.enviados = []  # Lista para marcar os frames que tiveram NAK enviado
        self.enviados = [False] * (num_frames + 1)
        self.ackNeeded = False
        self.nakNeeded = False
        self.ack_fila = 0
        self.naks = []
        self.atrasado = False  # Informa se algum ack foi recebido com atraso e será utilizado ack cumulativo

        num = (2 ** seq_bits) - 1

        for x in range(0, num + 1):
            self.janela.append(x)

        self.janela = self.janela * 100

    # Função para simular o recebimento do frame
    def receive(self, frame):
        # Caso seja o frame esperado
        if self.janela[self.Rn] == frame:
            self.marca(frame)
            self.Rn += 1
            self.remove_nak(frame)
            self.ackNeeded = True
            if self.ta_atrasado(frame):
                self.atrasado = True
        # Caso nao seja o frame esperado checa se é um frame duplicado
        # Se for é necessário enviar um ack novamente
        elif self.check_duplicate(frame):
            self.ackNeeded = True
            self.atrasado = True
        # Caso nao seja duplicado e nem o frame esperado informa que necessita um NAK
        # Marca o frame para saber que não é necessário enviar outro NAK desse frame
        elif self.janela[self.Rn] != frame:
            self.nakNeeded = True
            self.marca(frame)
            self.add_naks(frame)

    # Função que checa se o frame está atrasado
    def ta_atrasado(self, frame):
        posi = self.get_pos(frame)
        if self.enviados[posi + 1]:
            return True
        return False

    # Adiciona os naks que devem ser enviados a lista caso eles nao estejam marcados que ja enviou
    def add_naks(self, frame):
        for x in range(self.ack_fila, self.get_pos(frame)):
            if not self.enviados[x]:
                if ('NAK', self.janela[x]) not in self.naks:
                    self.naks.append(('NAK', self.janela[x]))

    # Remove um NAK da lista de naks
    def remove_nak(self, frame):
        for x in range(0, len(self.naks)):
            if self.naks[x] == frame:
                self.naks.pop(x)
                return

    # Checa se um frame é duplicado
    def check_duplicate(self, frame):
        aux = self.ack_fila

        while aux >= 0 and aux >= self.ack_fila - self.tam_janela:
            if self.janela[aux] == frame and self.enviados[aux]:
                return True
            aux -= 1

        return False

    # Função que simula o envio de um ACK
    def send_ack(self):
        aux = self.ack_fila
        # Caso tenha tido algum frame que chegou atrasado será enviado um ack cumulativo
        # A logica abaixo ira garantir que sejam considerados confirmados todos os frames necessarios
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
            # Caso nao tenha tido nenhum frame atrasado sera enviado o ack "normal"
            aux = self.ack_fila
            if aux == self.Rn - 1:
                self.ackNeeded = False
            self.ack_fila += 1
            return 'ACK', self.janela[aux + 1]

    # Serão enviados os NAKS
    def send_nak(self):
        self.nakNeeded = False
        aux = self.naks
        self.naks = []

        return aux

    # Será marcado o frame que ja estiver na lista para ser enviado
    def marca(self, frame):
        x = self.Rn
        ultimo = self.Rn + self.tam_janela

        while x <= ultimo and x < self.num_frames:
            if self.janela[x] == frame:
                self.enviados[x] = True
                break
            x += 1

    # Função que recebe um numero da sequencia e retorna a posição na lista janela
    def get_pos(self, frame):
        if type(frame) is int:
            for x in range(self.ack_fila, self.ack_fila + self.tam_janela + 1):
                if self.janela[x] == frame:
                    return x
        else:
            for x in range(self.ack_fila, self.ack_fila + self.tam_janela + 1):
                if self.janela[x] == frame[1]:
                    return x


# Simula a execução completa
def executarsr(num_frames, seq_bits, pkt_loss):
    sender = SenderSR(num_frames, seq_bits)
    receiver = ReceiverSR(seq_bits, num_frames)
    pacote = 0

    # Irá permanecer no laço enquanto nao tiverem sido todos confirmados
    while sender.Sf <= num_frames - 1:
        # Enquanto puder ser enviado um frame irá permanecer nesse laço
        while sender.pode_enviar():
            # Simula o envio do pacote
            pacote += 1
            enviado = sender.send()
            if pacote not in pkt_loss:
                # Caso o pacote nao esteja entre os que devem ser perdidos o receiver recebe o frame
                # Caso seja um dos frames reenviados ele terá uma identificação junto com o frame
                # portanto, é checado se essa identificação existe para formatar o print
                if type(enviado) is not int:
                    receiver.receive(enviado[1])
                    print('A ->> B : (', receiver.get_pos(enviado[1]) + 1, ') Frame ', enviado[1], "(RET)", sep=" ")
                else:
                    receiver.receive(enviado)
                    print('A ->> B : (', sender.Sn, ') Frame ', enviado, sep=" ")
            else:
                # Caso o pacote esteja entre os que devem ser perdidos nada acontece alem dos prints
                # Mesma checagem anterior para saber se é um frame reenviado ou não
                if type(enviado) is not int:
                    print('A -x B : (', receiver.get_pos(enviado[1]), ') Frame ', enviado[1], "(RET)", sep=" ")
                else:
                    print('A -x B : (', sender.Sn, ') Frame ', enviado, sep=" ")

        # Caso nao se possa enviar nenhum frame, a prioridade é para enviar os acks
        # Pemanecerá nesse laço enquanto tiverem acks para mandar
        while receiver.ackNeeded:
            pacote += 1
            ack = receiver.send_ack()
            if pacote not in pkt_loss:
                # Caso o pacote nao esteja entre os que devem ser perdidos, o sender recebe o ack
                sender.receive_confirmation(ack)
                print("B -->> A : ACK", ack[1])
            else:
                print("B --x A : ACK", ack[1])

        # Caso exista a necessidade de enviar naks
        if receiver.nakNeeded:
            nak = receiver.send_nak()
            # nak recebeu uma lista de naks e o laço ira continuar enquanto existirem itens na lista
            while len(nak) > 0:
                pacote += 1
                aux = nak.pop(0)
                if pacote not in pkt_loss:
                    # Caso o pacote nao esteja entre os que devem ser perdidos o NAK será enviado e
                    # o Rn será ajustado para o frame do NAK
                    receiver.Rn = aux[1]
                    print("B -->> A : NAK", aux[1])
                    sender.receive_confirmation(aux)
                else:
                    print("B --x A : NAK", aux[1])

        sender.incrementa_timer()
        # Caso nao se possa enviar frames, acks ou naks
        if not sender.pode_enviar() and not receiver.ackNeeded and not receiver.nakNeeded:
            # Será checado se algum frame ja estourou o limite de tempo
            # Caso a função nao retorne nada é sinal que nenhum timeout deve ser dado ainda
            timeout = sender.check_timeout()
            if timeout is not None:
                # Caso algum frame tenha tido timeout será reenviado
                pacote += 1
                print('Note over A: TIMEOUT(', timeout + 1, ')', sep=" ")
                enviado = sender.resend(sender.janela[timeout])
                if pacote not in pkt_loss:
                    # Caso o pacote nao esteja entre os que devem ser perdidos o receiver recebera o pacote
                    print("A ->> B : (", timeout + 1, ") Frame ", enviado, " (RET)", sep=" ")
                    receiver.receive(enviado)
                else:
                    print("A -x B : (", timeout + 1, ") Frame ", enviado, " (RET)", sep=" ")
