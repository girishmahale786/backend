import requests

def generate_image_from_prompt(prompt):
    """
    Function to interact with Cloudflare Worker for image generation.
    :param prompt: The text prompt to generate the image.
    :return: Image data (binary content).
    """
    # Cloudflare Worker URL
    worker_url = "https://c.ulhevedant.workers.dev"  # Update this with your Cloudflare worker URL

    try:
        # Sending the POST request with the prompt
        response = requests.post(worker_url, json={"prompt": prompt})

        # Check if the response is successful
        if response.status_code == 200:
            return response.content  # This should be the image in binary format
        else:
            raise Exception(f"Failed to generate image. Status code: {response.status_code}")

    except Exception as e:
        raise Exception(f"Error generating image: {str(e)}")
