from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from django.conf import settings
from sklearn.decomposition import PCA
from torch.nn.parameter import Parameter
from transformers import BertModel, BertTokenizer

models_dir = Path(settings.BASE_DIR) / "ml" / "ml_models" / "model_data"


class SentimentAnalysis(nn.Module):
    def __init__(
        self,
        feature_dims: Tuple[int, int, int] = (
            768,
            5,
            20,
        ),  # (text, audio33, video128)
        language: str = "en",
        hidden_dims: Tuple[int, int, int] = (64, 64, 64),
        post_text_dim: int = 32,
        post_audio_dim: int = 32,
        post_video_dim: int = 32,
        post_fusion_out: int = 16,
        dropouts: tuple[float, float, float] = (0.1, 0.1, 0.1),
        post_dropouts: tuple[float, float, float, float] = (0.3, 0.3, 0.3, 0.3),
    ):
        super(SentimentAnalysis, self).__init__()

        # dimensions are specified in the order of audio, video and text
        self.text_in, self.audio_in, self.video_in = feature_dims
        self.text_hidden, self.audio_hidden, self.video_hidden = hidden_dims
        self.text_model = BertTextEncoder(language=language)
        self.audio_prob, self.video_prob, self.text_prob = dropouts
        (
            self.post_text_prob,
            self.post_audio_prob,
            self.post_video_prob,
            self.post_fusion_prob,
        ) = post_dropouts

        self.post_text_dim = post_text_dim
        self.post_audio_dim = post_audio_dim
        self.post_video_dim = post_video_dim
        self.post_fusion_out = post_fusion_out

        # define the pre-fusion subnetworks
        self.tliner = nn.Linear(self.text_in, self.text_hidden)
        self.audio_model = SubNet(self.audio_in, self.audio_hidden, self.audio_prob)
        self.video_model = SubNet(self.video_in, self.video_hidden, self.video_prob)

        # define the classify layer for text
        self.post_text_dropout = nn.Dropout(p=self.post_text_prob)
        self.post_text_layer_1 = nn.Linear(self.text_hidden, self.post_text_dim)
        self.post_text_layer_2 = nn.Linear(self.post_text_dim, self.post_text_dim)
        self.post_text_layer_3 = nn.Linear(self.post_text_dim, 1)

        # define the classify layer for audio
        self.post_audio_dropout = nn.Dropout(p=self.post_audio_prob)
        self.post_audio_layer_1 = nn.Linear(self.audio_hidden, self.post_audio_dim)
        self.post_audio_layer_2 = nn.Linear(self.post_audio_dim, self.post_audio_dim)
        self.post_audio_layer_3 = nn.Linear(self.post_audio_dim, 1)

        # define the classify layer for video
        self.post_video_dropout = nn.Dropout(p=self.post_video_prob)
        self.post_video_layer_1 = nn.Linear(self.video_hidden, self.post_video_dim)
        self.post_video_layer_2 = nn.Linear(self.post_video_dim, self.post_video_dim)
        self.post_video_layer_3 = nn.Linear(self.post_video_dim, 1)

        # define the classify layer for fusion
        self.post_fusion_dropout = nn.Dropout(p=self.post_fusion_prob)
        self.post_fusion_layer_1 = nn.Linear(
            self.post_text_dim + self.post_audio_dim + self.post_video_dim,
            self.post_fusion_out,
        )
        # self.post_fusion_layer_1 = nn.Linear(self.post_text_dim, self.post_fusion_out)
        self.post_fusion_layer_2 = nn.Linear(self.post_fusion_out, self.post_fusion_out)
        self.post_fusion_layer_3 = nn.Linear(self.post_fusion_out, 1)

        # Output shift
        self.output_range = Parameter(torch.FloatTensor([2]), requires_grad=False)
        self.output_shift = Parameter(torch.FloatTensor([-1]), requires_grad=False)

    def forward(self, text_x, audio_x, video_x):
        flag = [0, 0, 0]
        res = {}
        if text_x is not None:
            text_x = self.text_model(text_x)[:, 0, :]
            text_x = torch.mean(text_x, dim=0, keepdim=True)
            text_h = self.tliner(text_x)
            # text
            x_t1 = self.post_text_dropout(text_h)
            x_t2 = F.relu(self.post_text_layer_1(x_t1), inplace=True)
            x_t3 = torch.sigmoid(self.post_text_layer_2(x_t2))
            output_text = self.post_text_layer_3(x_t3)
            flag[0] = 1
            res["T"] = output_text

        if audio_x is not None:
            audio_x = F.avg_pool1d(
                audio_x, kernel_size=7, stride=6, count_include_pad=False
            )
            audio_x = torch.mean(audio_x, dim=0, keepdim=True)
            audio_h = self.audio_model(audio_x)
            # audio
            x_a1 = self.post_audio_dropout(audio_h)
            x_a2 = F.relu(self.post_audio_layer_1(x_a1), inplace=True)
            x_a3 = torch.sigmoid(self.post_audio_layer_2(x_a2))
            output_audio = self.post_audio_layer_3(x_a3)
            flag[1] = 1
            res["A"] = output_audio

        if video_x is not None:
            video_x = F.avg_pool1d(
                audio_x, kernel_size=7, stride=6, count_include_pad=False
            )[:, :20]
            video_x = torch.mean(video_x, dim=0, keepdim=True)
            video_h = self.video_model(video_x)
            # video
            x_v1 = self.post_video_dropout(video_h)
            x_v2 = F.relu(self.post_video_layer_1(x_v1), inplace=True)
            x_v3 = torch.sigmoid(self.post_video_layer_2(x_v2))
            output_video = self.post_video_layer_3(x_v3)
            flag[2] = 1
            res["V"] = output_video

        # Transformer fusion
        if sum(flag) == 3:
            fusion_cat = torch.cat([x_t3, x_a3, x_v3], dim=-1)
        elif sum(flag) == 2:
            if flag[0] and flag[1]:
                fusion_cat = torch.cat([x_t3, x_a3, x_a3], dim=-1)
            elif flag[0] and flag[2]:
                fusion_cat = torch.cat([x_t3, x_v3, x_v3], dim=-1)
            elif flag[1] and flag[2]:
                fusion_cat = torch.cat([x_a3, x_v3, x_v3], dim=-1)
        elif sum(flag) == 1:
            if flag[0]:
                fusion_cat = torch.cat([x_t3, x_t3, x_t3], dim=-1)
            elif flag[1]:
                fusion_cat = torch.cat([x_a3, x_a3, x_a3], dim=-1)
            elif flag[2]:
                fusion_cat = torch.cat([x_v3, x_v3, x_v3], dim=-1)
        # fusion_cat = x_t3
        fusion_data = self.post_fusion_dropout(fusion_cat)
        fusion_data = self.post_fusion_layer_1(fusion_data)
        fusion_data = self.post_fusion_layer_2(fusion_data)
        fusion_output = self.post_fusion_layer_3(fusion_data)

        output_fusion = torch.sigmoid(fusion_output)
        output_fusion = output_fusion * self.output_range + self.output_shift

        res["M"] = output_fusion
        return res


class SubNet(nn.Module):
    def __init__(self, in_size, hidden_size, dropout):
        super(SubNet, self).__init__()
        self.norm = nn.BatchNorm1d(in_size)  # only used in training
        self.drop = nn.Dropout(p=dropout)
        self.linear_1 = nn.Linear(in_size, hidden_size)
        self.linear_2 = nn.Linear(hidden_size, hidden_size)
        self.linear_3 = nn.Linear(hidden_size, hidden_size)

    def forward(self, x):
        normed = self.norm(x)
        dropped = self.drop(normed)
        y_1 = F.relu(self.linear_1(dropped))
        y_2 = F.relu(self.linear_2(y_1))
        y_3 = F.relu(self.linear_3(y_2))
        return y_3


class BertTextEncoder(nn.Module):
    def __init__(self, language="en", use_finetune=False):
        """
        language: en / cn
        """
        super(BertTextEncoder, self).__init__()

        assert language in ["en", "cn"]

        tokenizer_class = BertTokenizer
        model_class = BertModel
        # directory is fine
        # pretrained_weights = '/home/sharing/disk3/pretrained_embedding/Chinese/bert/pytorch'
        if language == "en":
            self.tokenizer = tokenizer_class.from_pretrained(
                f"{models_dir}/bert_en", do_lower_case=True
            )
            self.model = model_class.from_pretrained(f"{models_dir}/bert_en")
        elif language == "cn":
            self.tokenizer = tokenizer_class.from_pretrained(f"{models_dir}/bert_cn")
            self.model = model_class.from_pretrained(f"{models_dir}/bert_cn")

        self.use_finetune = use_finetune

    def get_tokenizer(self):
        return self.tokenizer

    def from_text(self, text):
        """
        text: raw data
        """
        input_ids = self.get_id(text)
        with torch.no_grad():
            last_hidden_states = self.model(input_ids)[
                0
            ]  # Models outputs are now tuples
        return last_hidden_states.squeeze()

    def forward(self, text):
        """
        text: (batch_size, 3, seq_len)
        3: input_ids, input_mask, segment_ids
        input_ids: input_ids,
        input_mask: attention_mask,
        segment_ids: token_type_ids
        """
        text = self.tokenizer(text)
        print(text)
        input_ids, input_mask, segment_ids = (
            torch.tensor(text["input_ids"]).long().unsqueeze(0),
            torch.tensor(text["token_type_ids"]).unsqueeze(0).float(),
            torch.tensor(text["attention_mask"]).unsqueeze(0).long(),
        )
        if self.use_finetune:
            last_hidden_states = self.model(
                input_ids=input_ids,
                attention_mask=input_mask,
                token_type_ids=segment_ids,
            )[
                0
            ]  # Models outputs are now tuples
        else:
            with torch.no_grad():
                last_hidden_states = self.model(
                    input_ids=input_ids,
                    attention_mask=input_mask,
                    token_type_ids=segment_ids,
                )[
                    0
                ]  # Models outputs are now tuples
        return last_hidden_states


def pca(input_tensor, out_dim=25):
    input_np = input_tensor.detach().numpy()

    # use PCA to reduce the dimension to 25
    p = PCA(n_components=out_dim)
    transformed_np = p.fit_transform(input_np)

    # transfer numpy to tensor
    output_tensor = torch.from_numpy(transformed_np)
    return output_tensor
