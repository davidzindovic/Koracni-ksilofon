import os
import tkinter as tk
from PIL import Image, ImageTk
import threading

def get_stopmotion_config(filename="/media/lmk/stopnice/izvedba.txt"):
    """Reads the file and extracts the folder name and display mode for stopmotion."""
    with open(filename, "r") as file:
        for line in file:
            if "stopmotion:" in line:
                parts = line.strip().split(":")[-1].split(";")
                folder = "/media/lmk/stopnice/stopmotion/"+parts[0]
                mode = int(parts[1]) if len(parts) > 1 else 2
                return folder, mode
    return None, 2

def display_images(folder, mode):
    """Displays images based on user input in sequence, with fullscreen or centered mode."""
    root = tk.Tk()
    root.title("Stopmotion Viewer")
    
    if mode == 1:
        root.attributes("-fullscreen", True)
    
    label = tk.Label(root)
    label.pack()
    
    current_index = [1]  # Track the current displayed image index
    
    def update_image():
        image_path = os.path.join(folder, f"{current_index[0]}.jpg")
        if os.path.exists(image_path):
            img = Image.open(image_path)
            if mode == 1:
                screen_width = root.winfo_screenwidth()
                screen_height = root.winfo_screenheight()
                img = img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((500, 500), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            label.config(image=img_tk)
            label.image = img_tk
            print(f"Correct input for next step: {current_index[0] + 1} or {current_index[0] - 1 if current_index[0] > 1 else '-'}")
        else:
            print(f"Image {current_index[0]}.jpg not found in {folder}")
            return
    
    def input_listener():
        while True:
            try:
                user_input = int(input("Enter the next number in sequence: "))
                if user_input == current_index[0] + 1:
                    current_index[0] += 1
                    update_image()
                elif user_input == current_index[0] - 1 and current_index[0] > 1:
                    current_index[0] -= 1
                    update_image()
                else:
                    print(f"Incorrect sequence. Try again. Correct input: {current_index[0] + 1} or {current_index[0] - 1 if current_index[0] > 1 else '-'}")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    update_image()
    threading.Thread(target=input_listener, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    folder, mode = get_stopmotion_config()
    if folder and os.path.exists(folder):
        display_images(folder, mode)
    else:
        print("Stopmotion folder not found or does not exist.")
