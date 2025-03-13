from PIL import Image
import os

def get_contact_anchor(upper_part, lower_part):
    """
    Determines the anchor point at the contact point of two images.
    :param upper_part: Image object of the upper body part
    :param lower_part: Image object of the lower body part
    :return: Tuple (x, y) anchor point
    """
    return upper_part.width // 2, upper_part.height  # Center bottom of the upper part

def rotate_part(image, angle, anchor):
    """
    Rotates an image around a given anchor point without cropping.
    :param image: Image to rotate
    :param angle: Rotation angle in degrees (positive for counterclockwise, negative for clockwise)
    :param anchor: The pivot point for rotation
    :return: Rotated image and new position
    """
    expanded_size = (image.width * 2, image.height * 2)
    expanded_image = Image.new("RGBA", expanded_size, (255, 255, 255, 0))
    expanded_anchor = (expanded_size[0] // 2, expanded_size[1] // 2)
    expanded_image.paste(image, (expanded_anchor[0] - anchor[0], expanded_anchor[1] - anchor[1]))
    rotated = expanded_image.rotate(-angle, center=expanded_anchor, resample=Image.BICUBIC)
    return rotated

def assemble_doll(image_dir, output_path, rotations):
    """
    Assembles images from a predefined directory, rotates them, and places them at predefined positions.
    :param image_dir: Directory containing image parts
    :param output_path: Path to save the final image
    :param rotations: Dictionary mapping image names to their rotation angles
    """
    positions = {
        "head.jpg": (150, 50),
        "body.jpg": (120, 150),
        "left_upper_arm.jpg": (250, 200),
        "left_lower_arm.jpg": (250, 250),
        "right_upper_arm.jpg": (100, 200),
        "right_lower_arm.jpg": (100, 250),
        "left_hand.jpg": (250, 350),
        "right_hand.jpg": (120, 350),
        "left_upper_leg.jpg": (200, 400),
        "left_lower_leg.jpg": (200, 500),
        "right_upper_leg.jpg": (160, 400),
        "right_lower_leg.jpg": (160, 500),
        "left_foot.jpg": (200, 550),
        "right_foot.jpg": (160, 550)
    }
    
    canvas_size = (700, 800)
    canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
    images = {}
    
    for img_name in positions.keys():
        img_path = os.path.join(image_dir, img_name)
        if os.path.exists(img_path):
            images[img_name] = Image.open(img_path).convert("RGBA")
    
    anchors = {
        "head.jpg": (images["head.jpg"].width // 2, 0),
        "body.jpg": get_contact_anchor(images["head.jpg"], images["body.jpg"]),
        "left_upper_arm.jpg": get_contact_anchor(images["body.jpg"], images["left_upper_arm.jpg"]),
        "left_lower_arm.jpg": get_contact_anchor(images["left_upper_arm.jpg"], images["left_lower_arm.jpg"]),
        "right_upper_arm.jpg": get_contact_anchor(images["body.jpg"], images["right_upper_arm.jpg"]),
        "right_lower_arm.jpg": get_contact_anchor(images["right_upper_arm.jpg"], images["right_lower_arm.jpg"]),
        "left_hand.jpg": get_contact_anchor(images["left_lower_arm.jpg"], images["left_hand.jpg"]),
        "right_hand.jpg": get_contact_anchor(images["right_lower_arm.jpg"], images["right_hand.jpg"]),
        "left_upper_leg.jpg": get_contact_anchor(images["body.jpg"], images["left_upper_leg.jpg"]),
        "left_lower_leg.jpg": get_contact_anchor(images["left_upper_leg.jpg"], images["left_lower_leg.jpg"]),
        "right_upper_leg.jpg": get_contact_anchor(images["body.jpg"], images["right_upper_leg.jpg"]),
        "right_lower_leg.jpg": get_contact_anchor(images["right_upper_leg.jpg"], images["right_lower_leg.jpg"]),
        "left_foot.jpg": get_contact_anchor(images["left_lower_leg.jpg"], images["left_foot.jpg"]),
        "right_foot.jpg": get_contact_anchor(images["right_lower_leg.jpg"], images["right_foot.jpg"])
    }
    
    for img_name, position in positions.items():
        if img_name in images:
            rotated_img = rotate_part(images[img_name], rotations.get(img_name, 0), anchors[img_name])
            canvas.paste(rotated_img, position, rotated_img)
    
    canvas.save(output_path, format="PNG")
    canvas.show()

if __name__ == "__main__":
    image_directory = r"D:\lutka\model1"  # Change this to the actual path
    output_file = "assembled_doll.png"
    
    user_rotations = {}
    for part in ["head.jpg", "body.jpg", "left_upper_arm.jpg", "left_lower_arm.jpg", "right_upper_arm.jpg", "right_lower_arm.jpg", "left_hand.jpg", "right_hand.jpg", "left_upper_leg.jpg", "left_lower_leg.jpg", "right_upper_leg.jpg", "right_lower_leg.jpg", "left_foot.jpg", "right_foot.jpg"]:
        user_rotations[part] = int(input(f"Enter rotation for {part} (negative for clockwise, positive for counterclockwise): "))
    
    assemble_doll(image_directory, output_file, user_rotations)
