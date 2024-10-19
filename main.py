from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import os
import pyttsx3

say=pyttsx3.init()

def speak(x):
    say.say(x)
    say.runAndWait()

app = FastAPI()

# Directory to save images and audio
MEDIA_DIR = "media"

# Ensure the media directory exists
os.makedirs(MEDIA_DIR, exist_ok=True)

# Mount the media directory to serve uploaded files
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# Serve the HTML page directly
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r") as file:
        return file.read()

# Endpoint to handle image and audio uploads and process the RGB channels
@app.post("/upload/")
async def upload_image(
    image: UploadFile = File(...),
    audio: UploadFile = File(...),
    text: str = Form(...)
):
    print(f"Received text: {text}")  # Debug output for received text
    speak(f"Your input text is {text}")

    # Save the uploaded image to the 'media' directory
    img_path = os.path.join(MEDIA_DIR, image.filename)
    try:
        with open(img_path, "wb") as image_file:
            image_file.write(await image.read())
    except Exception as e:
        return {"error": "Failed to save the uploaded image."}

    # Open the image and split into RGB channels
    try:
        image_obj = Image.open(img_path)
        red_channel, green_channel, blue_channel = image_obj.split()

        # Create RGB images with other channels set to zero
        red_image = Image.new("RGB", image_obj.size)
        green_image = Image.new("RGB", image_obj.size)
        blue_image = Image.new("RGB", image_obj.size)

        for x in range(image_obj.width):
            for y in range(image_obj.height):
                r = red_channel.getpixel((x, y))
                g = green_channel.getpixel((x, y))
                b = blue_channel.getpixel((x, y))

                # Set the corresponding pixel for each channel image
                red_image.putpixel((x, y), (r, 0, 0))  # Red channel
                green_image.putpixel((x, y), (0, g, 0))  # Green channel
                blue_image.putpixel((x, y), (0, 0, b))  # Blue channel

        # Save the RGB channel images
        red_path = os.path.join(MEDIA_DIR, f"red_{image.filename}")
        green_path = os.path.join(MEDIA_DIR, f"green_{image.filename}")
        blue_path = os.path.join(MEDIA_DIR, f"blue_{image.filename}")

        red_image.save(red_path)
        green_image.save(green_path)
        blue_image.save(blue_path)

    except Exception as e:
        return {"error": "Failed to process the uploaded image."}

    # Save the uploaded audio to the 'media' directory
    audio_path = os.path.join(MEDIA_DIR, audio.filename)
    try:
        with open(audio_path, "wb") as audio_file:
            audio_file.write(await audio.read())
    except Exception as e:
        return {"error": "Failed to save the uploaded audio."}

    # Return the paths of the original and processed images and audio
    return {
        "original_image": f"/media/{image.filename}",
        "red_image": f"/media/red_{image.filename}",
        "green_image": f"/media/green_{image.filename}",
        "blue_image": f"/media/blue_{image.filename}",
        "audio": f"/media/{audio.filename}",
        "text": text
    }
