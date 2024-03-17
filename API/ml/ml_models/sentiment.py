import math

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import TransformerEncoder, TransformerEncoderLayer
from transformers import BertConfig, BertModel

from .subNets import BertTextEncoder


class FineTuneModel(nn.Module):
    def __init__(self,
                 act: str = 'relu',
                 use_finetune: bool = False,
                 transformers: str = 'bert-base-chinese',
                 pretrained: str = 'bert-base-uncased',
                 hidden_size: int = 64,
                 mid_size: int = 768,
                 head_sa: int = 4,
                 head_ga: int = 8,
                 dropout_m: float = 0.5,
                 dropout_f: float = 0.7,
                 outdim: int = 512,
                 output_size: int = 1,
                 dropout: float = 0.5,
                 num_loop: int = 1,
                 feature_dims=None
                 ):
        super(FineTuneModel, self).__init__()

        if feature_dims is None:
            feature_dims = [768, 33, 709]
        self.act = nn.Softmax(dim=-1)
        self.activation = _get_activation_fn(act)
        # embedding
        self.t_embedding = BertTextEncoder(use_finetune=use_finetune,
                                           transformers=transformers,
                                           pretrained=pretrained)
        self.t_linear = nn.Linear(768, hidden_size)
        self.a_embedding = Encoder(feature_dims[1], 1, hidden_size, dropout, act, 1)
        self.v_embedding = Encoder(feature_dims[2], 1, hidden_size, dropout, act, 1)
        # self-attention
        self.t_encoder = Encoder(hidden_size, head_sa, hidden_size, dropout, act, 1)
        self.a_encoder = Encoder(hidden_size, head_sa, hidden_size, dropout, act, 1)
        self.v_encoder = Encoder(hidden_size, head_sa, hidden_size, dropout, act, 1)
        # guided attention
        self.v_interact = InteractLayer(hidden_size, hidden_size, head_ga, mid_size, dropout,
                                        act)
        self.a_interact = InteractLayer(hidden_size, hidden_size, head_ga, mid_size, dropout,
                                        act)
        # trimodal interaction as multimodal output
        # self.tri_inter = TriInter(args.hidden_size, args.outdim, args.dropout, activation=args.act)
        # as the one of the multimodal representation
        self.tri_inter = TriInter(hidden_size, outdim, dropout, activation=act)

        # #memory gate
        self.memo_t = nn.Linear(hidden_size, hidden_size)
        self.memo_a = nn.Linear(hidden_size, hidden_size)
        self.memo_v = nn.Linear(hidden_size, hidden_size)
        # self.memo_tri = nn.Linear(hidden_size, hidden_size)
        # last output layer
        self.t_regression = nn.Linear(hidden_size, output_size)
        self.v_regression = nn.Linear(hidden_size, output_size)
        self.a_regression = nn.Linear(hidden_size, output_size)
        # self.tri_regression = nn.Linear(hidden_size, 1)
        # # self.cat_regression1 = nn.Linear(outdim, outdim)
        # self.cat_regression = nn.Linear(hidden_size*4, outdim)
        self.cat_regression = nn.Linear(outdim, output_size)

    def forward(self, text, a, v):
        t_encoded = self.t_linear(text).transpose(0, 1)
        v_encoded = self.v_embedding(v).transpose(0, 1)
        a_encoded = self.a_embedding(a).transpose(0, 1)

        for i in range(self.args.num_loop):
            # auxiliary
            v_encoded = self.v_interact(v_encoded, t_encoded)
            a_encoded = self.a_interact(a_encoded, t_encoded)

            # m_t = self.act(self.memo_t(t_encoded)) * t_encoded
            # m_a = self.act(self.memo_a(a_encoded)) * a_encoded
            # m_v = self.act(self.memo_v(v_encoded)) * v_encoded

            t_encoded = self.t_encoder(t_encoded)
            v_encoded = self.v_encoder(v_encoded)
            a_encoded = self.a_encoder(a_encoded)

        # t_utter = torch.mean(t_encoded, 0)
        v_utter = torch.mean(v_encoded, 0)
        a_utter = torch.mean(a_encoded, 0)

        tri_mode = self.tri_inter(a_utter, v_utter)

        # cat_utter = self.tri_inter(a_utter, v_utter)

        # t_res = self.t_regression(t_utter)
        # v_res = self.v_regression(v_utter)
        # a_res = self.a_regression(a_utter)
        # tri_res = self.tri_regression(tri_mode)
        output = {
            # 'M': cat_res,
            # 'T': t_res,
            # 'A': a_res,
            # 'V': v_res,
        }

        return output


class TextEncoder(nn.Module):
    def __init__(self, d_model, dim_feedforward):
        super(TextEncoder, self).__init__()
        self.config = BertConfig.from_pretrained('bert-base-chinese')
        self.model = BertModel.from_pretrained('bert-base-chinese', config=self.config)
        self.linear = nn.Linear(d_model, dim_feedforward)

    def forward(self, input_ids):
        outputs = self.model(input_ids)
        encoded = outputs[0]
        encoded = self.linear(encoded)
        return encoded.transpose(0, 1)


class Encoder(nn.Module):
    def __init__(self, d_model, n_head, dim_feedforward, dropout, activation, num_layers):
        super().__init__()
        self.num_heads = n_head
        self.pe = PositionalEncoding(d_model, dropout)
        self.layer = TransformerEncoderLayer(d_model, n_head, dim_feedforward, dropout, activation)
        self.encoder = TransformerEncoder(self.layer, num_layers)
        self.add_norm = AddNorm(d_model, dropout)
        self.linear = nn.Linear(d_model, dim_feedforward)

    def forward(self, inputs):
        inputs = self.pe(inputs)
        encoded = self.encoder(inputs)
        encoded = self.add_norm(inputs, encoded)
        output = self.linear(encoded)

        return output


class InteractLayer(nn.Module):
    def __init__(self, d_model, dim_1, n_head, dim_feedforward, dropout=0.1, activation="relu"):
        super().__init__()
        self.num_heads = n_head
        self.multi_head_attn_1 = nn.MultiheadAttention(d_model, n_head, dropout=dropout, kdim=dim_1, vdim=dim_1)
        self.add_norm_1 = AddNorm(d_model, dropout)
        self.add_norm_2 = AddNorm(d_model, dropout)
        self.ff = FeedForward(d_model, dim_feedforward, dropout, activation)

    def forward(self, encoded, memory1):
        inter1 = self.multi_head_attn_1(encoded, memory1, memory1)[0]  # , attn_mask=attn_mask_1)[0]
        attn1 = self.add_norm_1(encoded, inter1)
        ff = self.ff(attn1)
        output = self.add_norm_2(attn1, ff)
        return output


class TriInter(nn.Module):
    def __init__(self, dim_feedforward, outdim, dropout, activation="relu"):
        super().__init__()
        self.hidden = dim_feedforward
        # self.linear1 = nn.Linear((dim_feedforward+1)*(dim_feedforward+1), dim_feedforward)

        self.linear2 = nn.Linear((dim_feedforward + 1) * (dim_feedforward + 1), outdim)
        self.norm = nn.LayerNorm((dim_feedforward + 1) * (dim_feedforward + 1))

        self.dropout = nn.Dropout(dropout)
        self.activation = _get_activation_fn(activation)

    def forward(self, a, v):
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
    def __init__(self, d_model, dropout, max_len=500):
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
