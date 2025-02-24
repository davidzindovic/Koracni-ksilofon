#pomembna direktorija:

#txt file z racunom:
#C:\stopnice\tekst

#direktorij s slikami:
#C:\stopnice\slike

import matplotlib.pyplot as plt
import cv2
import numpy as np
import os

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

if __name__ == "__main__":
    txt_file = r"C:\stopnice\tekst\racun.txt"
    image_folder = r"C:\stopnice\slike"
    
    if not os.path.exists(txt_file):
        print("Text file not found!")
    else:
        with open(txt_file, 'r') as file:
            text_content = file.read().strip()  # Read entire file and strip whitespace
        
        correct_answer = get_correct_answer(text_content)
        masked_text = mask_numbers_before_underscore(text_content)
        equation_parts = list(masked_text)
        underscore_index = masked_text.index("_")
        
        print(correct_answer)
        print(masked_text)
        print(equation_parts)
        print(underscore_index)
        
        # Initial display with "_" placeholder
        image_paths = [os.path.join(image_folder, name + ".jpg") for name in equation_parts]
        display_images(image_paths)
        
        #user_input = input("Enter your answer for '_': ")
        
        index_update = 0
        user_answer=0
        for cifra in correct_answer:
            user_input = input("Števka '_': ")
            user_answer+=pow(10,len(correct_answer)-(index_update+1))*int(user_input)
            image_paths[underscore_index + index_update] = os.path.join(image_folder, user_input + ".jpg")
            index_update += 1
            display_images(image_paths)
        print(str(type(user_answer)) + " " + str(type(correct_answer)))
        if int(user_answer) == int(correct_answer):
            image_paths.append(os.path.join(image_folder, "check.jpg"))
        else:
            image_paths.append(os.path.join(image_folder, "wrong.jpg"))
        
        display_images(image_paths, reserve_space=False)
        
        print("Press any key to exit...")
        cv2.waitKey(0)  # Wait for key press before closing
        cv2.destroyAllWindows()
