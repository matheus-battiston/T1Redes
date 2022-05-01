# Classe para simular o sender de Go Back N
class Sender:
    def __init__(self, seq_bits):

        self.primeiro_janela = 0  # Referencia para o primeiro frame da janela
        self.ultimo_janela = 0  # Referencia para o ultimo frame da janela
        self.seq_bits = seq_bits
        self.seq = []  # Lista que irá representar a lista de sequencia
        self.janela = (2 ** seq_bits) - 1  # Tamanho da janela
        self.prox_envio = self.primeiro_janela
        self.pendentes = 0  # Quantidade de frames esperando confirmação
        for x in range(0, self.janela + 1):
            self.seq.append(x)
        self.seq = self.seq*100
        self.Sn = 0  # Variável para referenciar qual o proximo frame a ser enviado

    # Função para simular um timeout
    # Irá retornar todos os valores para o começo da janela para começar a reenviar todos os frames
    def timeout(self):
        print('Note over A: TIMEOUT(', self.primeiro_janela+1, ')', sep="")
        self.prox_envio = self.primeiro_janela
        self.pendentes = 0
        self.ultimo_janela = self.primeiro_janela

    # Função para definir se o sender pode enviar algum frame.
    # Se quantidade de frames pendentes forem menor que o tamanho da janela pode enviar
    def pode_enviar(self):
        if self.pendentes < self.janela:
            return True

        return False

    # Função para simular o envio do frame
    # Atualiza todos os valores para o proximo envio
    # Retorna o valor de sequencia enviado e qual deve ser o proximo enviado
    def send(self):
        self.ultimo_janela += 1
        self.prox_envio += 1
        self.pendentes += 1
        self.Sn += 1
        return self.seq[self.prox_envio - 1], self.prox_envio

    # Função que recebe o ack
    # Lógica para verificar se algum frame anterior deve ser considerado confirmado também
    # retorna quantos frames confirmados
    def receive_confirmation(self, ack):
        aux = self.primeiro_janela
        contador = 0

        while ack != self.seq[aux]:
            self.primeiro_janela += 1
            contador += 1
            aux += 1

        self.pendentes -= contador
        return contador


# Classe para simular o receiver do Go Back n
class Receiver:

    def __init__(self, seq_bits):
        self.recebidos = []  # Lista que armazena os frames que forem recebidos
        self.seq_bits = seq_bits
        self.seq = []  # Lista que terá os números de sequencia
        self.Rn = 0  # Variavel para controlar qual o frame esperado.

        aux = (2 ** seq_bits) - 1
        for x in range(0, aux+1):
            self.seq.append(x)

        self.seq = self.seq*100

    # Função para simular o recebimento de um ack
    # Irá primeiramente checar se o ack é duplicado e adicionalo novamente a lista de recebidos
    # Caso nao seja duplicado e for o frame esperado irá considerar recebido e atualizar a variável Rn
    def receive(self, frame):
        if self.check_duplicate(frame):
            self.recebidos.append(frame)
        elif frame == self.seq[self.Rn]:
            self.recebidos.append(frame)
            self.Rn += 1

    # Função que irá enviar um ack
    # Pop sempre será feito no primeiro elemento da lista para confirmar em ordem
    def confirma(self):
        return self.seq[self.recebidos.pop(0) + 1]

    # Função para definir se existe um ack a ser mandado
    def ackNeeded(self):
        if len(self.recebidos) > 0:
            return True

        return False

# Função que checa se o frame recebido é duplicado
# Garante que nao checara o numero errado caso tenham sido enviados menos frames que a o tamanho da janela
    def check_duplicate(self, frame):
        aux = self.Rn - 1
        if self.Rn < (2 ** self.seq_bits) - 1:
            while aux >= 0 and aux > self.Rn:
                if frame == self.seq[aux]:
                    return True
                aux -= 1
        else:
            while aux >= 0 and aux > self.Rn - (2 ** self.seq_bits) - 1:
                if frame == self.seq[aux]:
                    return True
                aux -= 1
        return False


def executar_gbn(num_frames, seq_bits, pkt_loss):
    sucesso = 0
    sender = Sender(seq_bits)
    receiver = Receiver(seq_bits)
    pacotes = 1
    enviados = []  # Lista para guardar os frames enviados

    # Preferencia para enviar frames. Irá continuar no laço enquanto nao forem todos confirmados
    while sucesso < num_frames:
        # Preferencia para o envio de frames, irá continuar nesse laço enquanto puder enviar frames
        while sender.pode_enviar() and sender.ultimo_janela < num_frames:
            # Irá simular o envio do frame
            enviado, frame = sender.send()
            if pacotes not in pkt_loss:
                # Caso o pacote nao seja um dos que devem ser perdidos o receiver irá receber
                receiver.receive(enviado)
                # Este if formata o print de forma correta checando se o frame ja foi enviado
                if frame not in enviados:
                    print("A ->> B : (", frame, ") Frame ", enviado, sep="")
                else:
                    print("A ->> B : (", frame, ") Frame ", enviado, " (RET)", sep="")

            else:
                print("A -x B : (", frame, ") Frame ", enviado, sep="")

            pacotes += 1
            enviados.append(frame)

        # Caso nao possa enviar um frame irá tentar enviar um ack. Continuara aqui até nao ter mais acks para enviar
        while receiver.ackNeeded():
            # Simula o envio do ack
            recebido = receiver.confirma()
            if pacotes not in pkt_loss:
                # Caso o pacote nao esteja entre os que devem ser perdidos o sender receberá o ack
                print("B -->> A : Ack", recebido)
                confirmados = sender.receive_confirmation(recebido)
                pacotes += 1
                sucesso += confirmados
            elif pacotes in pkt_loss:
                print("B --x A : Ack", recebido)
                pacotes += 1

        # Caso nao possa enviar nem ack nem frame será simulado um timeout
        if not receiver.ackNeeded() and not sender.pode_enviar():
            sender.timeout()
