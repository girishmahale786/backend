import torch
from torch import nn
from torchvision import  models
from torchvision.models import EfficientNet_B4_Weights
from torchvision import transforms
from transformers import BartTokenizer
from PIL import Image
import timm
import math

# --- EfficientNet Encoder ---
class EfficientNetEncoder(nn.Module):
    def __init__(self):
        super(EfficientNetEncoder, self).__init__()
        # Load pretrained EfficientNet-B4 model
        efficientnet = models.efficientnet_b4(weights=EfficientNet_B4_Weights.IMAGENET1K_V1)
        # Use the convolutional features (exclude the classification head)
        self.features = efficientnet.features
        # Optionally, add adaptive pooling to get fixed spatial dimensions
        self.pool = nn.AdaptiveAvgPool2d((7, 7))

    def forward(self, images):
        features = self.features(images)  # shape: (batch, C, H, W)
        features = self.pool(features)      # shape: (batch, C, 7, 7)
        batch, C, H, W = features.shape
        # Flatten spatial dimensions: each image becomes a sequence of (H*W) tokens
        features = features.view(batch, C, H * W)  # (batch, C, 49)
        features = features.transpose(1, 2)        # (batch, 49, C)
        return features  # e.g., (batch, 49, feature_dim)


# --- DeiT Encoder ---
class DeiTEncoder(nn.Module):
    def __init__(self):
        super(DeiTEncoder, self).__init__()
        self.deit = timm.create_model("deit_base_patch16_224", pretrained=True)
        self.embed_dim = self.deit.embed_dim
        self.deit.reset_classifier(0)  # Remove classification head

    def forward(self, images):
        features = self.deit.forward_features(images)  # (batch, 1+num_patches, embed_dim)
        return features  # Keep class token (global context)


# --- Decoder with Spatial Attention and Teacher Forcing ---
class TransformerDecoder(nn.Module):
    def __init__(self, embed_dim, num_heads, hidden_dim, vocab_size, num_layers, max_length, feature_dim, dropout, num_image_tokens):
        """
        Args:
            embed_dim: Embedding dimension for target tokens.
            num_heads: Number of attention heads.
            hidden_dim: Dimension of the feedforward network.
            vocab_size: Size of the target vocabulary.
            num_layers: Number of transformer decoder layers.
            max_length: Maximum length for target sequences.
            feature_dim: Dimension of encoder output channels.
            dropout: Dropout rate.
            num_image_tokens: Number of spatial tokens from the encoder (e.g., 7x7=49).
        """
        super(TransformerDecoder, self).__init__()
        self.embed_dim = embed_dim
        self.max_length = max_length

        # Token embedding for target captions.
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.dropout = nn.Dropout(dropout)
        self.register_buffer('positional_encoding', self._generate_positional_encoding(max_length, embed_dim))

        # Project encoder's spatial features to decoder embedding space.
        self.feature_proj = nn.Sequential(
            nn.Linear(feature_dim, embed_dim),
            nn.LayerNorm(embed_dim)  # Normalize features for stability
        )

        # Learnable positional embeddings for image tokens.
        self.image_pos_embedding = nn.Parameter(torch.randn(1, num_image_tokens, embed_dim))

        # Extra Transformer encoder block for image features
        encoder_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=num_heads, dim_feedforward=hidden_dim, dropout=dropout, batch_first=True)
        self.image_feature_encoder = nn.TransformerEncoder(encoder_layer, num_layers=1)

        # Transformer decoder layers.
        decoder_layer = nn.TransformerDecoderLayer(d_model=embed_dim, nhead=num_heads, dim_feedforward=hidden_dim, dropout=dropout, batch_first=True)
        self.transformer_decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_layers)

        # Final output projection.
        self.fc_out = nn.Linear(embed_dim, vocab_size)

        # Final layer norm for stability
        self.layer_norm = nn.LayerNorm(embed_dim)


    def _generate_positional_encoding(self, max_len, d_model):
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe.unsqueeze(0)  # (1, max_len, d_model)

    def generate_square_subsequent_mask(self, sz):
        """Generates a causal mask (upper-triangular) for target tokens."""
        return torch.triu(torch.ones(sz, sz, dtype=torch.bool), diagonal=1)


    def forward(self, encoder_features, tgt_input, tgt_mask=None, tgt_key_padding_mask=None):
        """
        Args:
            encoder_features: Output from encoder, shape (batch, num_image_tokens, feature_dim).
            tgt_input: Tokenized target sequence (teacher forcing input), shape (batch, tgt_seq_len).
            tgt_mask: (Optional) Causal mask for the target sequence.
            tgt_key_padding_mask: (Optional) Padding mask for target tokens.
        Returns:
            Logits for each target token, shape (batch, tgt_seq_len, vocab_size).
        """
        # Project encoder features and add image positional embeddings.
        memory = self.feature_proj(encoder_features) + self.image_pos_embedding  # (batch, num_image_tokens, embed_dim)
        # Process image features through an extra encoder block.
        memory = self.image_feature_encoder(memory)

        # Embed target tokens and add positional encoding.
        tgt_embedded = self.embedding(tgt_input) * math.sqrt(self.embed_dim)
        seq_len = tgt_input.size(1)
        pos_enc = self.positional_encoding[:, :seq_len, :].to(tgt_input.device)
        tgt_embedded = tgt_embedded + pos_enc
        tgt_embedded = self.dropout(tgt_embedded)

        # Create causal mask if needed.
        if tgt_mask is None:
            tgt_mask = self.generate_square_subsequent_mask(seq_len).to(tgt_input.device)

        # Pass through Transformer decoder.
        decoder_output = self.transformer_decoder(tgt_embedded, memory, tgt_mask=tgt_mask, tgt_key_padding_mask=tgt_key_padding_mask)
        decoder_output = self.layer_norm(decoder_output)
        logits = self.fc_out(decoder_output)
        return logits


# --- Image Captioning Model ---
class ImageCaptionModel(nn.Module):
    def __init__(self, encoder, decoder, use_features=False):
        super(ImageCaptionModel, self).__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.use_features = use_features

    def forward(self, x, tgt_input, tgt_mask=None, tgt_key_padding_mask=None):
        # If features are precomputed, x is already the encoder output.
        if self.use_features:
            features = x
        else:
            features = self.encoder(x)
        outputs = self.decoder(features, tgt_input, tgt_mask=tgt_mask, tgt_key_padding_mask=tgt_key_padding_mask)
        return outputs


def beam_search_decode(encoder_features, model, tokenizer, device, max_length, beam_width=3, length_penalty=0.7, repetition_penalty=1.2):
    start_token_id = tokenizer.bos_token_id if tokenizer.bos_token_id is not None else tokenizer.pad_token_id
    eos_token_id = tokenizer.eos_token_id if tokenizer.eos_token_id is not None else tokenizer.pad_token_id

    # Each beam is a tuple: (generated_sequence, cumulative_score)
    beams = [([start_token_id], 0.0)]

    for _ in range(max_length - 1):
        new_beams = []
        for seq, score in beams:
            if seq[-1] == eos_token_id:
                new_beams.append((seq, score))
                continue
            seq_tensor = torch.tensor(seq, dtype=torch.long, device=device).unsqueeze(0)
            outputs = model.decoder(encoder_features, seq_tensor)
            next_token_logits = outputs[0, -1, :]  # (vocab_size,)

            # Apply repetition penalty for tokens already generated.
            for token_id in set(seq):
                next_token_logits[token_id] /= repetition_penalty

            log_probs = torch.log_softmax(next_token_logits, dim=-1)
            top_log_probs, top_indices = torch.topk(log_probs, beam_width)
            for log_prob, token_id in zip(top_log_probs, top_indices):
                new_seq = seq + [token_id.item()]
                # Normalize the score by length (raise length to a penalty exponent)
                new_score = (score + log_prob.item()) / (len(new_seq) ** length_penalty)
                new_beams.append((new_seq, new_score))

        # Keep the best beams
        beams = sorted(new_beams, key=lambda x: x[1], reverse=True)[:beam_width]
        if all(seq[-1] == eos_token_id for seq, _ in beams):
            break

    best_sequence = beams[0][0]
    caption = tokenizer.decode(best_sequence, skip_special_tokens=True)
    return caption

def generate_caption_for_image(image_path, model, tokenizer, transform, device, max_length):
    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0).to(device)

    model.eval()
    with torch.no_grad():
        encoder_features = model.encoder(image)
        caption = beam_search_decode(encoder_features, model, tokenizer, device, max_length)
    return caption

def inference_captioning(model_path, image_path):
    MAX_LENGTH = 100

    embed_dim = 256
    num_heads = 4
    hidden_dim = 1024
    num_layers = 4
    dropout = 0.2

    if "efficientnet" in model_path.lower():
        encoder = EfficientNetEncoder()
        feature_dim = 1792
        num_image_tokens = 49
        weights = EfficientNet_B4_Weights.IMAGENET1K_V1
        transform = weights.transforms()
    else:
        encoder = DeiTEncoder()
        feature_dim = 768
        num_image_tokens = 197
        transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = BartTokenizer.from_pretrained("facebook/bart-base")

    decoder = TransformerDecoder(
        embed_dim=embed_dim,
        num_heads=num_heads,
        hidden_dim=hidden_dim,
        vocab_size=tokenizer.vocab_size,
        num_layers=num_layers,
        max_length=MAX_LENGTH,
        feature_dim=feature_dim,
        dropout=dropout,
        num_image_tokens=num_image_tokens
    )
    model = ImageCaptionModel(encoder, decoder)

    model.load_state_dict(torch.load(model_path, weights_only=True, map_location=device))
    caption = generate_caption_for_image(image_path, model, tokenizer, transform, device, MAX_LENGTH)
    return caption
