from utils.image_captioner import inference
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
                caption = inference(model_path, self.image_path)
                return caption
            except Exception as e:
                raise RuntimeError("Error generating caption")
        else:
            raise ValueError("Unsupported agent tool type")


class TextToImageService:

    def __init__(self, agent, prompt):
        self.agent = agent
        self.prompt = prompt
        self.image_path = None

    def generate_image(self):
        """
        Generate an image from the given text using the specified agent.
        """
        if self.agent.tool == "image-generation":
            try:
                model_path = self.agent.name 
                self.image_path = generate_image_from_prompt(model_path, self.prompt)
                return self.image_path
            except Exception as e:
                raise RuntimeError("Error generating image")
        else:
            raise ValueError("Unsupported agent tool type")

