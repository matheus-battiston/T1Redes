class sender_saw:
    def __init__(self, pkt_loss, num_frames):
        self.Sn = 0
        self.pkt_loss = pkt_loss
        self.num_frames = num_frames
        self.seq = []
        self.Enviando = 1
        self.confirmation = True
        self.retry = False

        self.seq = [0,1] * 500

    def send(self):
        self.confirmation = False
        return self.seq[self.Sn]


    def receive_confirmation(self, confirmation,ack):
        if not confirmation:
            print("A -x B : ", self.Enviando, " Frame ", self.seq[self.Sn])
            print('Note over A: TIMEOUT(',self.Enviando, ")")
            self.retry = True
        elif self.retry:
            print("A ->> B : ", self.Enviando, " Frame ", self.seq[self.Sn], "(RET)")
            print("B -->> A : Ack", ack)
            self.Sn+=1
            self.Enviando +=1
            self.retry = False
        else:
            print("A ->> B : ", self.Enviando, " Frame ", self.seq[self.Sn])
            print("B -->> A : Ack", ack)

            self.Sn +=1
            self.Enviando +=1

class receiver_saw:
    def __init__(self, nro_frames):
        self.Sn = 1
        self.seq = []
        self.seq = [0,1] * 500


    def is_redundant(self,seq_frame):
        if self.seq[self.Sn] == seq_frame:
            return True

        return False

    def receive(self,seqno):
        if not self.is_redundant(seqno):
            self.Sn +=1
            return self.seq[self.Sn-1]
        else:
            return self.seq[self.Sn]


def executar_saw(algo, num_frames, seq_bits, pkt_loss):
    sender = sender_saw(pkt_loss,num_frames)
    receiver = receiver_saw(num_frames)
    sucesso = 0
    pacotes = 1

    while sucesso < num_frames:
        enviado = sender.send()
        if pacotes not in pkt_loss:
            pacotes += 1
            recebido = receiver.receive(enviado)
            if pacotes not in pkt_loss:
                pacotes+=1
                sender.receive_confirmation(True,recebido)
                sucesso +=1
            else:
                print("B -x A : Ack", recebido)
                pacotes+=1
                sender.receive_confirmation(False,recebido)
        else:
            sender.send()
            sender.receive_confirmation(False,None)
            pacotes+=1