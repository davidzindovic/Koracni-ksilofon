import cv2
import os
import numpy as np
import vlc
import time

MAX_WIDTH = 1920
MAX_HEIGHT = 1080

folder_name = ""
mode = 1
display_time = 2

os.environ["DIPLAY"]=":0"
os.environ["QT_QPA_PLATFORM"]="xcb"

def process_slideshow(folder_name, mode, image_time):
    print(f"Processing slideshow in folder: {folder_name}, mode: {mode}, image time: {image_time}")
    run_slideshow(folder_name, mode, image_time)

def read_settings(file_path):
    global folder_name
    global mode
    global display_time

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("slideshow"):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    slideshow_details = parts[1]
                    folder_name, mode_time = slideshow_details.split(';')
                    folder_name = "/media/lmk/stopnice/slideshow/"+folder_name.strip()
                    mode, display_time = mode_time.split('$')
                    mode = int(mode.strip())
                    display_time = float(display_time.strip())
                    process_slideshow(folder_name.strip(), mode, display_time)

def display_image(image_path, display_time):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Read with alpha channel if present
    if img is None:
        print(f"Error loading image: {image_path}")
        return

    if len(img.shape) == 3 and img.shape[2] == 4:  # If image has transparency (RGBA)
        # Separate the alpha channel
        alpha_channel = img[:, :, 3] / 255.0
        img = img[:, :, :3]  # Remove the alpha channel

        # Create a white background
        white_background = np.ones_like(img, dtype=np.uint8) * 255  # White background
        img = (img * alpha_channel[:, :, None] + white_background * (1 - alpha_channel[:, :, None])).astype(np.uint8)

    img_h, img_w = img.shape[:2]

    # Scale down if too large
    if img_w > MAX_WIDTH or img_h > MAX_HEIGHT:
        scale = min(MAX_WIDTH / img_w, MAX_HEIGHT / img_h)
        img_w = int(img_w * scale)
        img_h = int(img_h * scale)
        img = cv2.resize(img, (img_w, img_h), interpolation=cv2.INTER_AREA)

    # Create a white background
    canvas = np.ones((MAX_HEIGHT, MAX_WIDTH, 3), dtype=np.uint8) * 255

    # Center the image
    x_offset = (MAX_WIDTH - img_w) // 2
    y_offset = (MAX_HEIGHT - img_h) // 2
    canvas[y_offset:y_offset+img_h, x_offset:x_offset+img_w] = img

    cv2.namedWindow('Slideshow', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Slideshow', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    cv2.imshow('Slideshow', canvas)
    cv2.waitKey(int(display_time * 1000))

def play_video(video_path):
    # Create VLC instance
    instance = vlc.Instance('--no-xlib --fullscreen')
    
    # Create media player
    player = instance.media_player_new()
    
    # Load media
    media = instance.media_new(video_path)
    player.set_media(media)
    
    # Set fullscreen
    player.set_fullscreen(True)
    
    # Play the video
    player.play()
    
    # Wait for video to start playing
    time.sleep(0.5)
    
    # Wait while video is playing
    while player.is_playing():
        time.sleep(0.01)
    
    # Stop when done
    player.stop()

def run_slideshow(folder_name, mode, display_time):
    files = sorted(os.listdir(folder_name))

    for filename in files:
        file_path = os.path.join(folder_name, filename)

        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')) and mode in [1, 3]:
            display_image(file_path, display_time)
        elif file_path.lower().endswith(('.mp4', '.avi', '.mov')) and mode in [2, 3]:
            play_video(file_path)

    cv2.destroyAllWindows()

# Example usage
settings_file = r"/media/lmk/stopnice/izvedba.txt"
read_settings(settings_file)
