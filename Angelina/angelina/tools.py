# tools.py
import os
import io
from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Gemini client for Vertex AI
client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("CLOUD_PROJECT_REGION", "us-central1")
)

def generate_image(prompt: str, aspect_ratio: str = "1:1") -> dict:
    """
    Generates an image from a detailed text prompt using the gemini-2.5-flash-image model.

    The image is saved locally and its filename is returned in a dictionary.
    The size parameter must be one of the supported resolutions (e.g., '1024x1024').
    """
    print(f"\n--- TOOL: Calling Image Generator with Prompt: '{prompt[:50]}...' ---")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt]
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