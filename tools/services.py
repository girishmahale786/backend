from utils.image_captioner import inference_captioning
from utils.phishing_detector import inference_phishing
from utils.image_generator import generate_image_from_prompt


class ImageCaptionService:

    def __init__(self, agent, image_path):
        self.agent = agent
        self.image_path = image_path

    def generate_caption(self):
        """
        Generate a caption for the given image using the specified agent.
        """
        if self.agent.tool == "image-captioning":
            try:
                model_path = self.agent.name + ".pth"
                caption = inference_captioning(model_path, self.image_path)
                return caption
            except Exception as e:
                raise RuntimeError("Error generating caption")
        else:
            raise ValueError("Unsupported agent tool type")


class ImageGenerationService:

    def __init__(self, agent, prompt):
        self.agent = agent
        self.prompt = prompt

    def generate_image(self):
        """
        Generate an image from the given text using the specified agent.
        """
        if self.agent.tool == "image-generation":
            try:
                model_path = self.agent.name
                image_data = generate_image_from_prompt(self.prompt)
                return image_data
            except Exception as e:
                raise RuntimeError("Error generating image")
        else:
            raise ValueError("Unsupported agent tool type")


class PhishingDetectionService:

    def __init__(self, agent, url):
        self.agent = agent
        self.url = url

    def detect_phishing(self):
        """
        Detect phishing using the specified agent.
        """
        if self.agent.tool == "phishing-detection":
            try:
                model_path = f"models/{self.agent.name}"
                result = inference_phishing(model_path, self.url)
                return result
            except Exception as e:
                raise RuntimeError("Error detecting phishing")
        else:
            raise ValueError("Unsupported agent tool type")
