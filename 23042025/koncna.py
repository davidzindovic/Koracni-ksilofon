
import os
from PIL import Image
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import cv2
import numpy as np
import time
import threading
import matplotlib.patches as patches
import vlc

from bluetooth import *
buf_size = 1024;

MAX_WIDTH = 1920
MAX_HEIGHT = 1080
os.environ["DIPLAY"]=":0"
os.environ["QT_QPA_PLATFORM"]="xcb"

img=None
root=None

#cakanje podaj v sekundah:
cakanje_med_nalogami=3
cakanje_pri_prikazu_pravilnega_rezultata=2

#---------------USB----------------------------
def find_usb_drive():
    # Check common mount points for USB drives (Linux/macOS)
    mount_points = ['/media', '/mnt', '/Volumes']
    
    for mount in mount_points:
        if os.path.exists(mount):
            for device in os.listdir(mount):
                usb_path = os.path.join(mount, device)
                if os.path.isdir(usb_path):
                    return usb_path+"/stopnice"  # Return the first detected USB drive
    
    # Windows-based detection (check drives D: to Z:)
    for drive in range(68, 91):  # ASCII codes for D-Z
        drive_letter = chr(drive) + ':\\'
        if os.path.exists(drive_letter):
            return drive_letter
    
    return None

def read_and_split_file(file_name):
    usb_path = find_usb_drive()
    if usb_path is None:
        print("No USB drive detected.")
        return
    
    file_path = os.path.join(usb_path, file_name)

    if not os.path.exists(file_path):
        print(f"File '{file_name}' not found on USB drive.")
        return
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        rows = content.split('\n')
        split_content = [[item.strip() for item in row.replace('!', ':').replace(';', ':').replace('$', ':').split(':')] for row in rows]
        
    #print("Split content:", split_content)
    return split_content
#-----------USB KONC-----------------------------------------

#--------------BESEDILNA------------------
def load_number_from_file(file_path):
    """Load the number from the .txt file."""
    try:
        with open(file_path, 'r') as file:
            number = int(file.read().strip())  # Read and convert to integer
        return number
    except Exception as e:
        print(f"Error loading number from file: {e}")
        return None

def create_image_grid(folder_path,naloga, user_input, file_number, gap=10, scale_factor=0.7, stevilka_scale=0.5):
    #potencialni dodatni parametri: stevilo_stolpcev,stevilo_vrstic,stevilo_slik,
    image_names = [naloga+".JPG"] + [f"stevilka{i}.JPG" for i in range(1, 9)] + [f"{i}.JPG" for i in range(1, 9)]
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
    check_image_path = os.path.join(folder_path, "check.JPG")
    wrong_image_path = os.path.join(folder_path, "wrong.JPG")

    if user_input!="q":
        if str(user_input) == str(file_number):
            check_image = Image.open(check_image_path).convert("RGBA")
            final_image.paste(check_image, (top_x + images[0].width, 0))  # Place the check image next to "beseda"
        else:
            wrong_image = Image.open(wrong_image_path).convert("RGBA")
            final_image.paste(wrong_image, (top_x + images[0].width, 0))  # Place the wrong image next to "beseda"
    
    # Place the rest of the images
    for i in range(8):
        if i<len(resized_images):
            num_x_offset = (i % grid_width) * (stevilka_width + uniform_width + gap)
            num_y_offset = images[0].height + (i // grid_width) * uniform_height
            final_image.paste(resized_images[i], (num_x_offset, num_y_offset))
            
            img_x_offset = num_x_offset + stevilka_width
            final_image.paste(resized_images[i + 8], (img_x_offset, num_y_offset))
    
    return final_image

def display_fullscreen_image(image, input=2):
    global root, img
    
    # If the root window already exists and is open, destroy it before creating a new one
    try:
        root.destroy()
    except:
        pass  # If root doesn't exist yet, ignore the exception
    
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    img = ImageTk.PhotoImage(image)
    label = tk.Label(root, image=img)
    label.pack()
    
    #root.img=img
    
    #4 DEBUG:
    #print("INPUT: ",input)
    
    #root.bind("<Escape>", lambda e: root.destroy())
    if input==1:
        input_thread = threading.Thread(target=close_img)
        input_thread.daemon = True  # This allows the thread to exit when the main program exits
        input_thread.start()
        root.mainloop()
    elif input==0:
        root.after(cakanje_pri_prikazu_pravilnega_rezultata*1000, root.destroy)
        root.mainloop()

    #root.mainloop()

def close_img():
    global user_input,root
    user_input=rx_and_echo() 
    #user_input = int(input("Enter a number: "))
    root.after(0, root.destroy)

def besedilna_main(path_za_slike,naloga,resitev):
    folder_path = r"/media/lmk/stopnice/besedilna_slike/"+path_za_slike
    global user_input
    if not os.path.isdir(folder_path):
        print("Invalid folder path, please try again.")
        exit()

    # Get the file path and the user input number
    
    #file_path = r"D:\stopnice\besedilna_tekst\besedilna.txt"
    
    # Load the number from the file
    #file_number = load_number_from_file(file_path)
    file_number=resitev

    combined_image = create_image_grid(folder_path,naloga, "q", file_number)
    display_fullscreen_image(combined_image,1)
    
    #user_input = int(input("Enter a number: "))
    
    if file_number is None:
        print("Error: Could not load the number from the file.")
        exit()
    
    combined_image = create_image_grid(folder_path,naloga, user_input, file_number)
    display_fullscreen_image(combined_image,0)
#--------------BESEDILNA KONC-------------------------------------

#------------------ENAČBE----------------------
change_flag=0
aspect=0

def display_images(image_paths, reserve_space=True):
    """
    Displays all images in a single line in fullscreen with black bars on top and bottom,
    ensuring a fixed horizontal size by reserving space for the "wrong" or "check" symbol.
    :param image_paths: List of image file paths
    :param reserve_space: Whether to reserve space for the final symbol
    """
    global change_flag
    global aspect
    
    if not image_paths:
        print("No images found!")
        return
    
    images = [cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2RGB) for img in image_paths if cv2.imread(img) is not None]
    
    if not images:
        print("No valid images found!")
        return
    
    # Resize images to the smallest height for consistency
    #min_height = min(img.shape[0] for img in images)
    min_height=400
    #images_resized = [cv2.resize(img, (int(img.shape[1] * (min_height / img.shape[0])), min_height)) for img in images]
    images_resized = [cv2.resize(img,(int(1920/(len(image_paths)+1)), min_height), interpolation= cv2.INTER_LINEAR) for img in images]

    # If reserving space, add a placeholder image (black space) for the final symbol
    if reserve_space:
        placeholder = np.full((min_height, min_height, 3), (0, 0, 0), dtype=np.uint8)
        images_resized.append(placeholder)
    
    # Arrange images in a single row
    img_grid = np.hstack(images_resized)
       
    # Get screen size
    screen_width = 1920
    screen_height = 1080
    
    if change_flag == 0:
        aspect_ratio = (img_grid.shape[1]) / img_grid.shape[0]
        aspect=aspect_ratio
        change_flag=1
       
    new_width = screen_width
    new_height = int(screen_width / aspect)
    
    if new_height > screen_height:
        new_height = screen_height
        new_width = int(screen_height * aspect)
        
    # Resize final image with black bars (letterbox effect)
    final_image = np.full((screen_height, screen_width, 3), (255, 255, 255), dtype=np.uint8)
    x_offset = (screen_width - new_width) // 2
    y_offset = (screen_height - new_height) // 2

    resized_grid = cv2.resize(img_grid, (new_width, new_height))
    
    final_image[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_grid
    
    # Display in fullscreen
    cv2.namedWindow("Image Display", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Image Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Image Display", cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR))
    cv2.waitKey(1)  # Ensure the window updates

def get_correct_answer(equation_text):
    """
    Extracts the correct answer before '_'
    """
    if "_" in equation_text:
        underscore_index = equation_text.index("_")
        num_start = underscore_index - 1
        while num_start >= 0 and equation_text[num_start].isdigit():
            num_start -= 1
        return equation_text[num_start + 1:underscore_index]
    return None

def mask_numbers_before_underscore(equation_text):
    """
    Replaces only the numbers directly before each '_' with '_' to keep the equation format correct.
    """
    masked_text = list(equation_text)
    i = 0
    while i < len(masked_text):
        if masked_text[i] == "_":
            j = i - 1
            while j >= 0 and masked_text[j].isdigit():
                masked_text[j] = ""
                j -= 1
        i += 1
    return "".join(masked_text)
    
def enacba_main(path_za_slike,naloga,resitev):
	image_folder = r"/media/lmk/stopnice/enacba_slike/"+path_za_slike
	"""
    if not os.path.exists(txt_file):
        print("Text file not found!")
    else:
        with open(txt_file, 'r') as file:
            text_content = file.read().strip()  # Read entire file and strip whitespace
	"""    
	correct_answer = resitev
	masked_text = mask_numbers_before_underscore(naloga)
	equation_parts = list(masked_text)
	underscore_index = masked_text.index("_")
    
    #print(correct_answer)
    #print(masked_text)
    #print(equation_parts)
    #print(underscore_index)
    
    # Initial display with "_" placeholder
	image_paths = [os.path.join(image_folder, name + ".JPG") for name in equation_parts]
	display_images(image_paths)
    
    #user_input = input("Enter your answer for '_': ")
    
	index_update = 0
	user_answer=0
	for cifra in correct_answer:
		cifra_odg = 99
		#user_input = input("Števka '_': ")
		while (cifra_odg == 99):
			cifra_odg = rx_and_echo()
			if (cifra_odg > 9):
				cifra_odg = 99
		user_input=str(cifra_odg)
		user_answer+=pow(10,len(correct_answer)-(index_update+1))*int(user_input)
		image_paths[underscore_index + index_update] = os.path.join(image_folder, user_input + ".JPG")
		index_update += 1
		display_images(image_paths)
	#print(str(type(user_answer)) + " " + str(type(correct_answer)))
	if int(user_answer) == int(correct_answer):
		image_paths.append(os.path.join(image_folder, "check.JPG"))
	else:
		image_paths.append(os.path.join(image_folder, "wrong.JPG"))
    
	display_images(image_paths, reserve_space=False)
    
    #print("Press any key to exit...")
	cv2.waitKey(cakanje_pri_prikazu_pravilnega_rezultata*1000)  # Wait for key press before closing
	cv2.destroyAllWindows()
#-----------------------ENAČBE KONC-------------------------------------

#----------------------BARVE -------------------------------------
# A function to blend two hex colors and return the mixed color in hex
def blend_colors(color1, color2):
    # Convert hex to RGB
    r1, g1, b1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
    r2, g2, b2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
    
    # Blend the colors (average the RGB values)
    r = int((r1 + r2) / 2)
    g = int((g1 + g2) / 2)
    b = int((b1 + b2) / 2)
    
    # Convert the blended RGB back to hex
    return f'#{r:02x}{g:02x}{b:02x}'

def plot_colors(hex_colors, indices):
    # Create a figure and axis
	fig, ax = plt.subplots(figsize=(6, 4))
    
    # Define the spacing for the squares
	spacing = 0.2
	square_size = 0.1
    
    # Plot the selected color squares
	for i, idx in enumerate(indices):
		color = hex_colors[idx - 1]  # Adjust for 1-based index
		ax.add_patch(patches.Rectangle((i * (square_size + spacing), 0), square_size, square_size, color=color))
    
    # Blend the selected colors and plot the mixed color square
	blended_color = blend_colors(hex_colors[indices[0] - 1], hex_colors[indices[1] - 1])
	ax.add_patch(patches.Rectangle(((len(indices) + 0.5) * (square_size + spacing), 0), square_size, square_size, color=blended_color))
    
    # Set axis limits and hide axes
	ax.set_xlim(0, (len(indices) + 1) * (square_size + spacing))
	ax.set_ylim(0, square_size + 0.1)
	ax.axis('off')
    
    # Show the plot in full screen
	mngr = plt.get_current_fig_manager()
    #mngr.window.state('zoomed')  # Full screen
	mngr.window.state('normal') #POPRAVI    
    

	input_thread = threading.Thread(target=close_plt)
	input_thread.daemon = True  # This allows the thread to exit when the main program exits
	input_thread.start()
    
    # Show the plot
	plt.show()
    
# Function to handle the complex barvanje (mixing) process
def complex_barvanje(hex_colors):#POPRAVI
    # Start with a white color (you can change this to any initial color)
	current_mix = '#ffffff'
    
    # Create the plot
	fig, ax = plt.subplots(figsize=(6, 6))
    
    # Make the figure full-screen
	mngr = plt.get_current_fig_manager()
    #mngr.window.state('zoomed')  # Full screen
	mngr.window.state('normal') #POPRAVI
    
	# Display the current mixed color and keep the window open
	ax.set_xlim(0, 1)
	ax.set_ylim(0, 1)
	ax.axis('off')  # Hide axes
    
    # Plot the initial mix (white by default)
	mix_rect = ax.add_patch(patches.Rectangle((0, 0), 1, 1, color=current_mix))
    
	while True:
        # Show the current mix color
		print(f"Current mixed color: {current_mix}")
		print("Available colors:", ', '.join(hex_colors))
        
		try:
			#selected_index = int(input(f"Enter color index to add (1 to {len(hex_colors)}), or 0 to stop: "))
			selected_index=rx_and_echo()
			if selected_index == 25:
				# Reset drawing board
				current_mix = "#ffffff"
				mix_rect.set_facecolor(current_mix)  # Update the color of the mix
				plt.draw()  

                #break  
			elif 1 <= selected_index <= len(hex_colors):
                # Blend the selected color with the current mix
				current_mix = blend_colors(current_mix, hex_colors[selected_index - 1])
                
                # Update the displayed mixed color
				mix_rect.set_facecolor(current_mix)  # Update the color of the mix
				plt.draw()  # Redraw the plot to reflect the changes

			else:
				print("Invalid color index, please try again.")
		except ValueError:
			print("Invalid input. Please enter a valid number.")



def close_plt():
	global user_input
	user_input=0
	while user_input!=25:
		user_input=rx_and_echo()
	plt.close()


def barve_main(mode, attempts,colors_all):
	colors = colors_all.split(',')
	num_inputs = len(colors)
	selected_indices = []
	
	if mode=="simple":
		for i in range(int(attempts)):
			while True:
				try:
					#selected_index = int(input(f"Please select color {i+1} (between 1 and {num_inputs}): "))
					selected_index=rx_and_echo()
					if 1 <= selected_index <= num_inputs:
						selected_indices.append(selected_index)
						break
					else:
						#print(f"Please enter a number between 1 and {num_inputs}.")
						pass
				except ValueError:
					#print("Invalid input. Please enter a valid number.")
					pass
		plot_colors(colors, selected_indices)
	elif mode=="complex":
		complex_barvanje(colors)
#------------------------BARVE KONC-------------------------------------

#------------------------STOPMOTION-------------------------------------
def display_images(folder, mode):
	"""Displays images based on user input in sequence, with fullscreen or centered mode."""
	root = tk.Tk()
	root.title("Stopmotion Viewer")
	files=os.listdir(folder)
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
                #user_input = int(input("Enter the next number in sequence: "))
				user_input=rx_and_echo()
				if (user_input == current_index[0] + 1) and (current_index[0]!=len(files)):
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
    
def stopmotion_main(folder, mode):
	folder="/media/lmk/stopnice/stopmotion/"+folder
	display_images(folder, mode)

#------------------------STOPMOTION KONC--------------------------------

#------------------------SLIDESHOW--------------------------------------
def process_slideshow(folder_name, mode, image_time):
    print(f"Processing slideshow in folder: {folder_name}, mode: {mode}, image time: {image_time}")
    run_slideshow(folder_name, mode, image_time)

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
    
def slideshow_main(folder_name,mode,image_time):
	folder_name = "/media/lmk/stopnice/slideshow/"+folder_name.strip()
	mode = int(mode.strip())
	image_time = float(image_time.strip())
	process_slideshow(folder_name.strip(), mode, image_time)
#------------------------SLIDESHOW KONC---------------------------------

#------------------------BLUETOOTH FUNKCIJE:----------------------------
def rx_and_echo():
	global sock
	sock.send("\nsend anything\n")
	cifra=0
	while cifra==0:
		data = sock.recv(buf_size)

		if data:
			neki=str(data)
			if(neki[3]=='t'):
				cifra=9
			elif(neki[3]=='n'):
				cifra=10
			elif(neki[3]=='r'):
				cifra=13
			else:
				cifra=int(neki[4],16)*16+int(neki[5],16)
			print("INPUT: "+str(cifra))
			return cifra
            
def bluetooth_setup():
	global sock
	#MAC address of ESP32
	addr = "C8:F0:9E:E1:50:F2"
	service_matches = find_service( address = addr )

	if len(service_matches) == 0:
		print("couldn't find the SampleServer service =(")
		sys.exit(0)

	first_match = service_matches[0]
	port = first_match["port"]
	name = first_match["name"]
	host = first_match["host"]

	port=1

	# Create the client socket
	sock=BluetoothSocket(RFCOMM)
	sock.connect((host, port))

	#sock.close()
#-----------------------BLUETOOTH FUNKCIJE KONC-----------------

bluetooth_setup()

# Example usage
file_name = "izvedba.txt"  # Change to your actual file name
naloga=read_and_split_file(file_name)
#print(naloga)
for i in range(len(naloga)):
	print(naloga[i][:])
	task_flag=0
	if naloga[i][0]=="besedilna":
		besedilna_main(naloga[i][1],naloga[i][2],naloga[i][3])
		task_flag=1
	elif naloga[i][0]=="enacba":
		enacba_main(naloga[i][1],naloga[i][2],naloga[i][3])
		task_flag=1
	elif naloga[i][0]=="barve":
		barve_main(naloga[i][1],naloga[i][2],naloga[i][3])
		task_flag=1
	elif naloga[i][0]=="stopmotion":
		stopmotion_main(naloga[i][1],naloga[i][2])
		task_flag=1
	elif naloga[i][0]=="slideshow":
		slideshow_main(naloga[i][1],naloga[i][2],naloga[i][3])
		task_flag=1
	print("novo")
	if task_flag==1:
		time.sleep(cakanje_med_nalogami)
		task_flag=0
