import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import BertConfig, BertModel
import math
from torch.nn import TransformerEncoder, TransformerEncoderLayer


class Msa(nn.Module):
    def __init__(self, args):
        super(Msa, self).__init__()
        self.args = args
        self.act = nn.Softmax(dim=-1)
        self.m_dropout = nn.Dropout(args.dropout_m)
        self.f_dropout = nn.Dropout(args.dropout_f)
        self.activation = _get_activation_fn(args.act)
        #embedding
        self.t_linear1 = nn.Linear(768, args.hidden_size)
        self.a_embedding = Encoder(args.feature_dims[1], 1, args.hidden_size, args.dropout, args.act, 1)
        self.v_embedding = Encoder(args.feature_dims[2], 1, args.hidden_size, args.dropout, args.act, 1)

        # text with two heads
        self.t_linear2 = nn.Linear(args.hidden_size, args.hidden_size * 2)

        #self-attention
        self.a_encoder = InteractLayer(args.hidden_size, args.hidden_size, args.head_ga, args.mid_size, args.dropout,
                                       args.act)
        self.v_encoder = InteractLayer(args.hidden_size, args.hidden_size, args.head_ga, args.mid_size, args.dropout,
                                       args.act)

        #guided attention
        self.t_self = InteractLayer(args.hidden_size, args.hidden_size, args.head_ga, args.mid_size, args.dropout,args.act)
        self.v_interact = InteractLayer(args.hidden_size, args.hidden_size, args.head_ga, args.mid_size, args.dropout, args.act)
        self.a_interact = InteractLayer(args.hidden_size, args.hidden_size, args.head_ga, args.mid_size, args.dropout, args.act)
        #trimodal interaction as multimodal output
        # self.tri_inter = TriInter(args.hidden_size, args.outdim, args.dropout, activation=args.act)
        # as the one of the multimodal representation
        self.tri_inter = TriInter(args.hidden_size, args.outdim, args.dropout, activation=args.act)

        # #memory gate
        self.memo_tfc1 = nn.Linear(args.hidden_size, args.hidden_size)
        self.memo_tfc2 = nn.Linear(args.hidden_size, args.hidden_size)
        self.fogt_tfc1 = nn.Linear(args.hidden_size, args.hidden_size)
        self.fogt_tfc2 = nn.Linear(args.hidden_size, args.hidden_size)
        self.memo_afc1 = nn.Linear(args.hidden_size, args.hidden_size)
        self.memo_afc2 = nn.Linear(args.hidden_size, args.hidden_size)
        self.fogt_afc1 = nn.Linear(args.hidden_size, args.hidden_size)
        self.fogt_afc2 = nn.Linear(args.hidden_size, args.hidden_size)
        self.memo_vfc1 = nn.Linear(args.hidden_size, args.hidden_size)
        self.memo_vfc2 = nn.Linear(args.hidden_size, args.hidden_size)
        self.fogt_vfc1 = nn.Linear(args.hidden_size, args.hidden_size)
        self.fogt_vfc2 = nn.Linear(args.hidden_size, args.hidden_size)

        #last output layer
        self.t_regression = nn.Linear(args.hidden_size, args.output_size)
        self.v_regression = nn.Linear(args.hidden_size, args.output_size)
        self.a_regression = nn.Linear(args.hidden_size, args.output_size)
        # self.tri_regression = nn.Linear(args.hidden_size, 1)
        # # self.cat_regression1 = nn.Linear(args.outdim, args.outdim)
        # self.cat_regression = nn.Linear(args.hidden_size*4, args.outdim)
        self.cat_regression = nn.Linear(args.outdim, args.output_size)

    def forward(self, t, a, v):
        # print(t.shape,a.shape, v.shape)
        # 1/0
        t = torch.tensor(t).unsqueeze(0).float()
        a = torch.tensor(a).unsqueeze(0).float()
        v = torch.tensor(v).unsqueeze(0).float()
        t_encoded = self.t_linear1(t).transpose(0,1)
        v_encoded = self.v_embedding(v).transpose(0, 1)
        a_encoded = self.a_embedding(a).transpose(0, 1)

        for i in range(self.args.num_loop):
            #auxilary
            t_heads = self.t_linear2(t_encoded)
            t_headvt = t_heads[:, :, :self.args.hidden_size]
            t_headat = t_heads[:, :, self.args.hidden_size:]
            t_headvt = self.t_self(t_headvt, t_headvt)
            t_headat = self.t_self(t_headat, t_headat)
            # t_encoded = self.t_self(t_encoded, t_encoded)
            v_encoded = self.v_interact(v_encoded, t_headvt)
            a_encoded = self.a_interact(a_encoded, t_headat)
            m_tv = F.softmax(self.memo_tfc2(self.m_dropout(F.relu(self.memo_tfc1(t_headvt)))), dim=1) * t_headvt
            f_tv = F.softmax(self.memo_tfc2(self.f_dropout(F.relu(self.memo_tfc1(t_headvt)))), dim=1) * t_headvt
            m_ta = F.softmax(self.memo_tfc2(self.m_dropout(F.relu(self.memo_tfc1(t_headat)))), dim=1) * t_headat
            f_ta = F.softmax(self.memo_tfc2(self.f_dropout(F.relu(self.memo_tfc1(t_headat)))), dim=1) * t_headat
            t_headvt = m_tv + f_tv
            t_headat = m_ta + f_ta

            # m_t = F.softmax(self.memo_tfc2(self.m_dropout(F.relu(self.memo_tfc1(t_encoded)))), dim=1) * t_encoded
            # f_t = F.softmax(self.memo_tfc2(self.f_dropout(F.relu(self.memo_tfc1(t_encoded)))), dim=1) * t_encoded
            m_a = F.softmax(self.memo_afc2(self.m_dropout(F.relu(self.memo_afc1(a_encoded)))), dim=1) * a_encoded
            f_a = F.softmax(self.memo_afc2(self.f_dropout(F.relu(self.memo_afc1(a_encoded)))), dim=1) * a_encoded
            m_v = F.softmax(self.memo_vfc2(self.m_dropout(F.relu(self.memo_vfc1(v_encoded)))), dim=1) * v_encoded
            f_v = F.softmax(self.memo_vfc2(self.f_dropout(F.relu(self.memo_vfc1(v_encoded)))), dim=1) * v_encoded

            # t_encoded = m_t + f_t
            v_encoded = m_v + f_v
            a_encoded = m_a + f_a

            v_encoded = self.v_encoder(v_encoded, v_encoded)
            a_encoded = self.a_encoder(a_encoded, a_encoded)

        t_utter = torch.mean(t_encoded, 0)
        v_utter = torch.mean(v_encoded, 0)
        a_utter = torch.mean(a_encoded, 0)

        # trimode = self.tri_inter(a_utter, v_utter)


        # cat_utter = torch.cat([t_utter, a_utter, v_utter, trimode], -1)  #
        cat_utter = self.tri_inter(a_utter, v_utter)

        t_res = self.t_regression(t_utter)
        v_res = self.v_regression(v_utter)
        a_res = self.a_regression(a_utter)
        # tri_res = self.tri_regression(trimode)
        # x = self.activation(self.cat_regression(cat_utter))
        cat_res = self.cat_regression(cat_utter)
        output = cat_res

        return output


class TextEncoder(nn.Module):
    def __init__(self, d_model, dim_feedforward):
        super(TextEncoder, self).__init__()
        bert_path = "/data/ch_sims2_sup/bert_cn/"
        self.config = BertConfig.from_pretrained(bert_path)
        self.model = BertModel.from_pretrained(bert_path, config=self.config)
        self.linear = nn.Linear(d_model, dim_feedforward)

    def forward(self, input_ids):
        outputs = self.model(input_ids)
        encoded = outputs[0]
        encoded = self.linear(encoded)
        return encoded.transpose(0, 1)

class Encoder(nn.Module):
    def __init__(self, d_model, nhead, dim_feedforward, dropout, activation, num_layers):
        super().__init__()
        self.num_heads = nhead
        self.pe = PositionalEncoding(d_model, dropout)
        self.layer = TransformerEncoderLayer(d_model, nhead, dim_feedforward, dropout, activation)
        self.encoder = TransformerEncoder(self.layer, num_layers)
        self.add_norm = AddNorm(d_model, dropout)
        self.linear = nn.Linear(d_model, dim_feedforward)


    def forward(self, inputs):
        inputs = self.pe(inputs)
        encoded = self.encoder(inputs.float())
        encoded = self.add_norm(inputs, encoded)
        output = self.linear(encoded)

        return output

class InteractLayer(nn.Module):
    def __init__(self, d_model, dim_1, nhead, dim_feedforward, dropout=0.1, activation="relu"):
        super().__init__()
        self.num_heads = nhead
        self.multihead_attn_1 = nn.MultiheadAttention(d_model, nhead, dropout=dropout, kdim=dim_1, vdim=dim_1)
        self.add_norm_1 = AddNorm(d_model, dropout)
        self.add_norm_2 = AddNorm(d_model, dropout)
        self.ff = FeedForward(d_model, dim_feedforward, dropout, activation)

    def forward(self, encoded, memory1):
        inter1 = self.multihead_attn_1(encoded, memory1, memory1)[0]#, attn_mask=attn_mask_1)[0]
        attn1 = self.add_norm_1(encoded, inter1)
        ff = self.ff(attn1)
        output = self.add_norm_2(attn1, ff)
        return output

class TriInter(nn.Module):
    def __init__(self, dim_feedforward, outdim, dropout, activation="relu"):
        super().__init__()
        self.hidden = dim_feedforward
        # self.linear1 = nn.Linear((dim_feedforward+1)*(dim_feedforward+1), dim_feedforward)

        self.linear2 = nn.Linear((dim_feedforward+1)*(dim_feedforward+1), outdim)
        self.norm = nn.LayerNorm((dim_feedforward+1)*(dim_feedforward+1))


        self.dropout = nn.Dropout(dropout)
        self.activation = _get_activation_fn(activation)

    def forward(self, a,v):
        batch_size = a.shape[0]
        add_one = torch.ones(size=[batch_size, 1], requires_grad=False).type_as(a).to(a.device)
        # _text_h = torch.cat((add_one, t), dim=1)
        _audio_h = torch.cat((add_one, a), dim=1)
        _video_h = torch.cat((add_one, v), dim=1)

        fusion_tensor = torch.bmm(_audio_h.unsqueeze(2), _video_h.unsqueeze(1))

        fusion_tensor = fusion_tensor.view(-1, (self.hidden + 1) * (self.hidden + 1))

        # layer normalization
        fusion_tensor = self.norm(fusion_tensor)
        fusion_tensor = self.dropout(fusion_tensor)
        ##########

        out = self.activation(self.linear2(fusion_tensor))


        # fusion_tensor = fusion_tensor.unsqueeze(-1)
        # fusion_tensor = torch.bmm(fusion_tensor, _text_h.unsqueeze(1)).view(batch_size, -1)
        # fusion_tensor = fusion_tensor.transpose(1, 2)
        # out = self.dropout(fusion_tensor)
        # out = self.activation(self.linear2(fusion_tensor))

        return out

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout, max_len=256):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        if d_model % 2 == 0:
            pe[:, 1::2] = torch.cos(position * div_term)
        else:
            pe[:, 1::2] = torch.cos(position * div_term[:-1])
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        # print(x.shape, self.pe[:x.size(0), :].shape)
        # print(x.shape, self.pe[:x.size(0), :].shape)
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)

class AddNorm(nn.Module):
    def __init__(self, d_model, dropout):
        super().__init__()
        self.norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, prior, after):
        return self.norm(prior + self.dropout(after))

class FeedForward(nn.Module):
    def __init__(self, d_model, dim_feedforward, dropout, activation="relu"):
        super().__init__()
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(dim_feedforward, d_model)
        self.activation = _get_activation_fn(activation)

    def forward(self, inputs):
        return self.linear2(self.dropout(self.activation(self.linear1(inputs))))



def compute_mask(mask_1, mask_2, num_heads):
    mask_1 = torch.unsqueeze(mask_1, 2)
    mask_2 = torch.unsqueeze(mask_2, 1)
    attn_mask = torch.bmm(mask_1, mask_2)
    attn_mask = attn_mask.repeat(num_heads, 1, 1)
    return attn_mask

def _get_activation_fn(activation):
    if activation == "relu":
        return F.relu
    elif activation == "gelu":
        return F.gelu

    raise RuntimeError("activation should be relu/gelu, not {}".format(activation))
