import torch
import librosa
from transformers import AutoProcessor, AutoModel, AutoModelForImageTextToText


class MemoryJournal:
    device = torch.device("xpu" if torch.xpu.is_available() else "cpu")
    audio_model_path = "efficient-speech/lite-whisper-small-fast"
    audio_processor_path = "openai/whisper-small"
    video_model_path = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"

    def __init__(self):
        audio_processor, audio_model = self.get_audio_model()
        video_processor, video_model = self.get_video_model()
        self.audio_processor = audio_processor
        self.audio_model = audio_model
        self.video_processor = video_processor
        self.video_model = video_model

    def get_audio_model(self):
        processor = AutoProcessor.from_pretrained(self.audio_processor_path, trust_remote_code=True)
        model = AutoModel.from_pretrained(self.audio_model_path, trust_remote_code=True).to(self.device)
        return processor, model

    def get_video_model(self):
        processor = AutoProcessor.from_pretrained(self.video_model_path)
        model = AutoModelForImageTextToText.from_pretrained(self.video_model_path).to(self.device)
        return processor, model

    def transcribe(self, audio_path):
        # Load audio
        audio, sr = librosa.load(audio_path, sr=16000)
        inputs = self.audio_processor(audio, sampling_rate=16000, return_tensors="pt", padding=True).input_features.to(self.audio_model.device)
        attention_mask = torch.ones(inputs.shape[:-1], dtype=torch.long, device=self.audio_model.device)

        # Generate transcription
        generated_ids = self.audio_model.generate(inputs, attention_mask=attention_mask)
        transcription = self.audio_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return transcription

    def video_caption(self, video_path):
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "video", "path": video_path},
                    {"type": "text", "text": "Summarize this video in one sentence."}
                ]
            },
        ]

        inputs = self.video_processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.video_model.device, dtype=torch.bfloat16)

        generated_ids = self.video_model.generate(**inputs, do_sample=False, max_new_tokens=64)
        generated_texts = self.video_processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )
        caption = generated_texts[0].split("Assistant: ")[-1].strip()
        return caption

    def text_summary(self, video_caption, audio_transcript):
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Video Caption: {video_caption}\nAudio Transcript: {audio_transcript}\n\nSummarize above video and audio caption in one meaningful sentence."}
                ]
            },
        ]

        inputs = self.video_processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.video_model.device, dtype=torch.bfloat16)

        generated_ids = self.video_model.generate(**inputs, do_sample=False, max_new_tokens=64)
        generated_texts = self.video_processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )
        caption = generated_texts[0].split("Assistant: ")[-1].strip()
        return caption
