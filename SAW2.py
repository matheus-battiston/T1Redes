# Classe que irá simular o sender
class Sender:
    def __init__(self):
        self.Sn = 0  # Referencia de posição na lista dos números de sequencia
        self.pode_enviar = True  # Informação se pode ou nao ser enviado um frame
        self.seq = [0, 1] * 100  # Lista dos números de sequencia
        self.confirmados = 0  # Frames confirmados

    # Função send - Coloca que não pode fazer um envio e incrementa o Sn, retorna o número de sequencia para o print
    def send(self):
        self.pode_enviar = False
        self.Sn += 1
        return self.seq[self.Sn - 1]

    # Função para receber um ack
    def receive_confirmation(self, ack):
        if ack == self.seq[self.Sn]:
            self.pode_enviar = True
            self.confirmados += 1

    # Função de reenvio de um frame. Retorna o último frame enviado utilizando a variável Sn
    def resend(self):
        self.pode_enviar = False
        return self.seq[self.Sn - 1]


# Classe para simular o receiver
class Receiver:
    def __init__(self):
        self.Rn = 0  # Referencia de posição na lista dos numeros de sequencia
        self.seq = [0, 1] * 100  # Lista dos numeros de sequencia
        self.confirma = False  # Variavel para definir se pode enviar um ack

# Função que simula o recebimento de um frame. Incrementa o Rn,
# informa que pode enviar um ack e retorna o numero de sequencia do proximo ack
    def receive(self, frame):
        if frame == self.seq[self.Rn]:
            self.Rn += 1
        self.confirma = True
        return self.seq[self.Rn]

# Função de envio de ack. Utiliza o Rn para retornar o numero de sequencia
    def envia_ack(self):
        self.confirma = False
        return self.seq[self.Rn]


def executar_saw(num_frames, pkt_loss):
    sender = Sender()
    receiver = Receiver()
    pacotes = 0

    # Simulador dos envios, Irá continuar enquanto nao tiverem sido recebidos e confirmados dos os frames
    while sender.confirmados < num_frames:
        # Prioridade para enviar pacotes, enviará o pacote caso possa.
        if sender.pode_enviar:
            pacotes += 1
            enviado = sender.send()
            if pacotes not in pkt_loss:
                # Caso o pacote nao seja um dos que devem ser perdidos o recebedor irá receber
                # Caso contrario nada irá acontecer.
                receiver.receive(enviado)
                print('A ->> B : (', sender.Sn, ') Frame ', enviado, sep="")
            else:
                print('A -x B : (', sender.Sn, ') Frame ', enviado, sep="")
        # Caso o sender nao possa enviar o pacote e o recebedor possa confirmar o pacote será enviado o ack
        elif receiver.confirma:
            pacotes += 1
            confirma = receiver.envia_ack()
            if pacotes not in pkt_loss:
                # Caso o pacote nao seja um dos que devem ser perdidos o sender receberá o ack
                # Caso contrario nada acontece
                sender.receive_confirmation(confirma)
                print("B -->> A : Ack", confirma)
            else:
                print("B --x A : Ack", confirma)
        else:
            # Se nao possa enviar frame ou receber ack sera simulado um timeout e o frame será reenviado
            print('Note over A: TIMEOUT (', sender.Sn, ')', sep="")
            pacotes += 1
            enviado = sender.resend()
            if pacotes not in pkt_loss:
                # Caso o pacote nao seja um dos que devem ser perdidos o receiver receberá o pacote
                print("A ->> B : (", sender.Sn, ") Frame ", enviado, ' (RET)', sep="")
                receiver.receive(enviado)
            else:
                print("A -x B : (", sender.Sn, ") Frame ", enviado, ' (RET)', sep="")
