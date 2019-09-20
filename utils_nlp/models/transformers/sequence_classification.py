# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


from enum import Enum

from pytorch_transformers.modeling_bert import (
    BERT_PRETRAINED_MODEL_ARCHIVE_MAP,
    BertForSequenceClassification,
)
from pytorch_transformers.modeling_distilbert import (
    DISTILBERT_PRETRAINED_MODEL_ARCHIVE_MAP,
    DistilBertForSequenceClassification,
)
from pytorch_transformers.modeling_roberta import (
    ROBERTA_PRETRAINED_MODEL_ARCHIVE_MAP,
    RobertaForSequenceClassification,
)
from pytorch_transformers.modeling_xlnet import (
    XLNET_PRETRAINED_MODEL_ARCHIVE_MAP,
    XLNetForSequenceClassification,
)

from utils_nlp.dataset.pytorch import SCDataSet
from utils_nlp.models.transformers.common import fine_tune
from utils_nlp.models.transformers.common import TOKENIZER_CLASS


MODEL_CLASS = {}
MODEL_CLASS.update({k: BertForSequenceClassification for k in BERT_PRETRAINED_MODEL_ARCHIVE_MAP})
MODEL_CLASS.update(
    {k: RobertaForSequenceClassification for k in ROBERTA_PRETRAINED_MODEL_ARCHIVE_MAP}
)
MODEL_CLASS.update({k: XLNetForSequenceClassification for k in XLNET_PRETRAINED_MODEL_ARCHIVE_MAP})
MODEL_CLASS.update(
    {k: DistilBertForSequenceClassification for k in DISTILBERT_PRETRAINED_MODEL_ARCHIVE_MAP}
)


def list_supported_models():
    return list(MODEL_CLASS)


def create_dataset_from_df(df, text_col, label_col):
    return SCDataSet(df, text_col, label_col)


class Processor:
    def __init__(self, pt_model_name, tokenizer=None, to_lower=False):
        self.tokenizer = TOKENIZER_CLASS[pt_model_name].from_pretrained(
            pt_model_name, do_lower_case=to_lower, cache_dir=cache_dir
        )
        self.custom_tokenizer = tokenizer

    def preprocess(self, text, labels, max_len, batch_size=32, distributed=False):
        """preprocess data or batches"""
        if self.custom_tokenizer:
            tokens = [self.custom_tokenizer.tokenize(x) for x in text]
        else:
            tokens = [tokenizer.custom_tokenizer.tokenize(x) for x in text]

        input_ids = [tokenizer.convert_tokens_to_ids(x) for x in tokens]
        # pad sequence
        input_ids = [x + [0] * (max_len - len(x)) for x in input_ids]
        # create input mask
        input_mask = [[min(1, x) for x in y] for y in tokens]

        td = TensorDataset(input_ids, input_mask, segment_ids, labels)
        sampler = DistributedSampler(td) if distributed else RandomSampler(td)
        data_loader = DataLoader(ds, sampler=sampler, batch_size=batch_size)
        return data_loader


class SequenceClassifier:
    def __init__(
        self, pt_model_name="bert-base-cased", num_labels=2, cache_dir=".", fp16=False, seed=0
    ):
        self.model = MODEL_CLASS[pt_model_name].from_pretrained(
            pt_model_name, cache_dir=cache_dir, num_labels=num_labels
        )
        self.seed = seed
        self.fp16 = fp16

    def fit(train_dataloader, num_epochs, num_gpus, device):
        fine_tune(
            model=self.model,
            model_type=pt_model_name.split["-"][0],
            train_dataloader=train_dataloader,
            num_epochs=num_epochs,
            n_gpus=num_gpus,
            local_rank=local_rank,
            device=device,
            gradient_accumulation_steps=gradient_accumulation_steps,
            fp16=self.fp16,
            seed=self.seed,
        )

    def predict():
        pass
