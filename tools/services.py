from utils.image_captioner import inference


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
