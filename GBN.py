class sender_gbn:
    def __init__(self, seq_bits):
        self.seq_bits = seq_bits
        seq = []
        aux = (2 ** seq_bits) - 1
        for x in range (0,aux):
            seq.append(x)

        seq = seq*100


class receiver_gbn:
    def __init__(self, seq_bits):
        self.seq_bits = seq_bits
        seq = []
        aux = (2 ** seq_bits) - 1
        for x in range (0,aux):
            seq.append(x)

        seq = seq*100




def executar_gbn(num_frames,seq_bits,pkt_loss):
    sucesso = 0
    sender = sender_gbn(seq_bits)
    receiver = receiver_gbn(seq_bits)




    while sucesso < num_frames:
        pass