import torch
from transformers import AutoTokenizer, AutoModel

print("Loading MuRIL Embedding Model...")

MODEL_NAME = "google/muril-base-cased"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
model.eval()

print("Model Loaded Successfully!")


def mean_pooling(model_output, attention_mask):
    """MuRIL is a raw BERT encoder — it has no built-in pooling layer,
    so we mean-pool the token embeddings ourselves (masking out padding)."""
    token_embeddings = model_output[0]  # (batch, seq_len, hidden)
    mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    summed = torch.sum(token_embeddings * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / counts


def get_embedding(text):
    inputs = tokenizer(
        text,
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors="pt"
    )

    with torch.no_grad():
        output = model(**inputs)

    embedding = mean_pooling(output, inputs["attention_mask"])

    return embedding[0].numpy()
