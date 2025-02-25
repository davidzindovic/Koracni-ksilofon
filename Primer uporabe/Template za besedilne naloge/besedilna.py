#pomembne poti:

#slike:
# C:\stopnice\besedilna_slike

#txt:
# C:\stopnice\besedilna_tekst\besedilna.txt

from PIL import Image
import os
import tkinter as tk
from PIL import ImageTk

def load_number_from_file(file_path):
    """Load the number from the .txt file."""
    try:
        with open(file_path, 'r') as file:
            number = int(file.read().strip())  # Read and convert to integer
        return number
    except Exception as e:
        print(f"Error loading number from file: {e}")
        return None

def create_image_grid(folder_path, user_input, file_number, gap=10, scale_factor=0.7, stevilka_scale=0.5):
    image_names = ["beseda.jpg"] + [f"stevilka{i}.jpg" for i in range(1, 9)] + [f"{i}.jpg" for i in range(1, 9)]
    image_paths = [os.path.join(folder_path, name) for name in image_names]
    
    if not all(os.path.exists(path) for path in image_paths):
        raise ValueError("Some required images are missing in the folder.")
    
    images = [Image.open(img).convert("RGBA") for img in image_paths]
    
    grid_width = 4
    grid_height = 2
    uniform_width = int(images[9].width * scale_factor)
    uniform_height = int(images[9].height * scale_factor)
    stevilka_width = int(images[1].width * stevilka_scale)
    stevilka_height = int(images[1].height * stevilka_scale)
    
    resized_images = [img.resize((stevilka_width, stevilka_height)) for img in images[1:9]] + [img.resize((uniform_width, uniform_height)) for img in images[9:]]
    
    total_width = grid_width * (stevilka_width + uniform_width) + (grid_width - 1) * gap
    total_height = (grid_height * uniform_height) + images[0].height
    final_image = Image.new("RGBA", (total_width, total_height), (255, 255, 255, 0))
    
    top_x = (total_width - images[0].width) // 2
    final_image.paste(images[0], (top_x, 0))
    
    # Add the check or wrong image depending on the comparison
    check_image_path = os.path.join(folder_path, "check.jpg")
    wrong_image_path = os.path.join(folder_path, "wrong.jpg")
    
    if user_input!="q":
        if user_input == file_number:
            check_image = Image.open(check_image_path).convert("RGBA")
            final_image.paste(check_image, (top_x + images[0].width, 0))  # Place the check image next to "beseda"
        else:
            wrong_image = Image.open(wrong_image_path).convert("RGBA")
            final_image.paste(wrong_image, (top_x + images[0].width, 0))  # Place the wrong image next to "beseda"
    
    # Place the rest of the images
    for i in range(8):
        num_x_offset = (i % grid_width) * (stevilka_width + uniform_width + gap)
        num_y_offset = images[0].height + (i // grid_width) * uniform_height
        final_image.paste(resized_images[i], (num_x_offset, num_y_offset))
        
        img_x_offset = num_x_offset + stevilka_width
        final_image.paste(resized_images[i + 8], (img_x_offset, num_y_offset))
    
    return final_image

def display_fullscreen_image(image):
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    img = ImageTk.PhotoImage(image)
    label = tk.Label(root, image=img)
    label.pack()
    root.bind("<Escape>", lambda e: root.destroy())
    root.mainloop()

if __name__ == "__main__":
    folder_path = r"C:\stopnice\besedilna_slike"
    
    if not os.path.isdir(folder_path):
        print("Invalid folder path, please try again.")
        exit()

    # Get the file path and the user input number
    
    file_path = r"C:\stopnice\besedilna_tekst\besedilna.txt"
    
    # Load the number from the file
    file_number = load_number_from_file(file_path)
    
    combined_image = create_image_grid(folder_path, "q", file_number)
    display_fullscreen_image(combined_image)
    
    user_input = int(input("Enter a number: "))
    
    if file_number is None:
        print("Error: Could not load the number from the file.")
        exit()
    
    combined_image = create_image_grid(folder_path, user_input, file_number)
    display_fullscreen_image(combined_image)
