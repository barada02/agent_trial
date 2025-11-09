# tools.py
import os
import io
from google import genai
from google.genai import types
from PIL import Image

# Initialize the Gemini client (ADK handles authentication)
client = genai.Client()

def generate_image(prompt: str, size: str = "1024x1024") -> dict:
    """
    Generates an image from a detailed text prompt using the gemini-2.5-flash-image model.

    The image is saved locally and its filename is returned in a dictionary.
    The size parameter must be one of the supported resolutions (e.g., '1024x1024').
    """
    print(f"\n--- TOOL: Calling Image Generator with Prompt: '{prompt[:50]}...' ---")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
            config=types.GenerateContentConfig(
                image_generation_config=types.ImageGenerationConfig(
                    number_of_images=1,
                    aspect_ratio=size
                )
            )
        )

        if response.candidates and response.candidates[0].content.parts:
            image_data = response.candidates[0].content.parts[0].inline_data.data
            image_bytes = io.BytesIO(image_data)
            image = Image.open(image_bytes)
            
            # Save the image locally (ADK Artifacts would be better in a real app)
            filename = f"generated_image_{os.getpid()}_{hash(prompt) % 1000}.png"
            image.save(filename)

            print(f"--- TOOL RESULT: Image saved as '{filename}' ---")
            
            # The tool must return a dict for the ADK agent to process
            return {"status": "success", "filename": filename, "message": f"Image generated and saved as {filename}. Inform the user."}
        
        return {"status": "error", "message": "Image generation failed: No image data returned."}

    except Exception as e:
        return {"status": "error", "message": f"An internal error occurred during image generation: {e}"}