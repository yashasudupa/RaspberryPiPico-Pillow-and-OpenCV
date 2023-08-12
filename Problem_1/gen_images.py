"""This is the main script of Problem 1

Program is written to generate non-overlapping output images as stated in problem statement:
i) Read N images from the input folder. 
ii) Generated M x M pixel output images which have a distribution of all the shapes in it.
iii) A given output image contained k*k images of each type. 
iv) K is computed based on the input image sizes and M*M. Please refer TODO1 to understand about the 
logic that i used to calculate K
v) Each shape is placed at a random position within the image, without getting
cut.
vi) Each shape is randomly scaled between 0.75 and 1.
viii) Image shape is rotated randomly between 0 and 90 degrees.
ix) Support required command line arguments is added (see below) for the program. Error checking is added as well.
x) Boundary conditions are added to avoid overlapping of images
"""
import cv2 as cv
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import sys
import os
import random
import argparse
import io
from PIL import Image


"""Helper Method to detect the overlap of the co-ordinates

    Args: augmented_image : rect1, rect2 
    Returns : True : Images are overlapping with each other, False : Images are not overlapping with each othere 
        
""" 
def do_rectangles_overlap(rect1, rect2):
    x1_1, y1_1, x2_1, y2_1 = rect1
    x1_2, y1_2, x2_2, y2_2 = rect2

    # Check for non-overlapping conditions
    if x1_1 > x2_2 or x2_1 < x1_2 or y1_1 > y2_2 or y2_1 < y1_2:
        return False
    return True


"""Helper Method to detect the overlap of the images and update the image list with co-odinates of the non-overlapping images

    Args: augmented_image : Cropped, rotated and scaled image
          positions : list of non-overlapping PIL images
          x : Random x co-ordinate
          y : Random y co-ordinate
          
    Returns : Updated list of x, y, PIL images
        
""" 
def check_overlap_coordinates(augmented_image, positions, x, y):
    overlap_status = False

    #This condition becomes true when the first image comes from this function
    #Extracts co-ordinate values and appends co-ordinates and PIL image to the list
    if len(positions) == 0:
        augmented_image_gray = augmented_image.convert("L")
        augmented_w, augmented_h = augmented_image_gray.size
        position = (x, y, augmented_image_gray)
        positions.append(position)

    if len(positions) > 0:
        for px, py, gray_image in positions:
            gray_image_array = np.array(gray_image)
            gray_w, gray_h = gray_image.size
            aug_w, aug_h = augmented_image.size

            existing_rect = (px, py, px + gray_w, py + gray_h)
            new_rect = (x, y, x + aug_w, y + aug_h)

            #Overlapping is detected by passing the image to this function
            if do_rectangles_overlap(new_rect, existing_rect):
                overlap_status = True
                break

    if not overlap_status:
        try:
            augmented_image_gray = augmented_image.convert("L")
            positions.append((x, y, augmented_image_gray))
            augmented_image_array = np.array(augmented_image_gray)

            augmented_w, augmented_h = augmented_image_gray.size

            #If images are not overlapped with each other then the foreground image is added
            #to the background image
            if y + augmented_h <= bg.shape[0] and x + augmented_w <= bg.shape[1]:
                bg[y : y + augmented_h, x : x + augmented_w] = np.array(
                    augmented_image_array
                )
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise

    return positions

"""Helper Method to define random scaling and random rotation of the image

    Args: img : PIL image
          x : Random x co-ordinate
          y : Random y co-ordinate
          
    Returns : Augmented PIL image
        
"""

def augment_image(x, y, img):
    try:
        # Randomly choose a scaling factor between 0.75 and 1
        scaling_factor = random.uniform(0.75, 1)

        original_image_width, original_image_height = img.size

        # Scale the x co-ordinate and y co-ordinate by the scaling factor
        scaled_width = int(scaling_factor * original_image_width)
        scaled_height = int(scaling_factor * original_image_height)
        
        # Randomly choose a rotation angle between 0 and 90 degrees
        random_angle = random.uniform(0, 90)
        
        # x<=0 or y<=0 corner case is handled below
        # if the value of the scaled x-co-ordinate or y-cordinate becomes less
        # than or equal to 0 the coordinate is updated with 1 
        # Also the x update and y update is done as per rotation by
        # by mutliplying x with cos(random_angle) and y with sin(random_angle) 
        scaled_width = max(int (scaled_width * np.cos(random_angle)), 1)
        scaled_height = max(int (scaled_height * np.sin(random_angle)), 1)
        
        # Resize the image with the scaled dimensions
        scaled_img = img.resize((original_image_width - scaled_width , original_image_height - scaled_height))
        
        # Rotate the scaled image
        rotated_img = scaled_img.rotate(random_angle)
        return rotated_img
    
    except OSError:
        print("augment_image: Error in augmentation")

"""Helper Method to define the logic of addition of foreground image on background image without overlapping with each other

    Args: positions : list of non-overlapping PIL images
          img : PIL image
          pixel_x : Co-ordinate specified by user
          pixel_y : Co-ordinate specified by user
          bg : Background Image
    Returns : Augmented PIL image
        
"""

# Defines logic of addition of foreground image on background image without any foreground images overlapping with each other
def add_obj(positions, img, pixel_x, pixel_y):
    """
    K is computed based on the below calculation.
    Background image is of 1024*1024 pixels.
    Each foreground image is of 50*50 pixels.
    Number of images that could be accomodated
    without being overlapped irrespective of images'
    augmentation would be (1024/50)-1 = 19.

    So, 19*19 of foreground shape images could be accomodated in the
    background image.

    Since, there are 4 shapes that are present of size 50 * 50,
    value of K would be 19 * 19 / 4 = 90."""
    K = 19
    
    shape_width, shape_height = img.size

    #x>=0 and y>=0 corner case is handled
    max_x = pixel_x - shape_width
    max_y = pixel_y - shape_height

    #The incoming messages are normalised
    #by the size 50*50 for the convenience
    #of computation
    img = img.resize((50, 50))

    for i in range(0, K):
        print(i, "th iteration")
        x = random.randint(0, max_x)
        y = random.randint(0, max_y)

        augmented_image  = augment_image(x, y, img)
        positions = check_overlap_coordinates(augmented_image, positions, x, y)
    return positions


# Defining main function
def main(args):
    print('Enter python gen_images.py to know more about the input format \n')

    #Parse the arguments from the user
    input_folder = args.input
    output_folder = args.output
    image_dimensions = args.dimensions
    num_images = args.num_images

    #If the image dimensions don't match each other then exits from the main function
    if image_dimensions[0] != image_dimensions[1]:
        print("Invalid image size")
        exit()
    
    background=np.zeros((image_dimensions[0], image_dimensions[1]),  dtype="uint8")

    global bg
    bg = np.array(background)
    positions = []

    try:
        cropped_cube_img = Image.open('./input_images/cube_shape.png')
        cropped_cube_img = cropped_cube_img.crop((55, 1, 225, 178))
    
        cropped_dodecahedon_img = Image.open('./input_images/Pyramid_augmented_dodecahedron.png')
        cropped_dodecahedon_img = cropped_dodecahedon_img.crop((30, 7, 710, 718))

        cropped_rectangle_img = Image.open('./input_images/Extended_Rectangle.png')
        cropped_rectangle_img = cropped_rectangle_img.crop((46, 32, 104, 227))

        cropped_prism_img = Image.open('./input_images/prism.png')
        cropped_prism_img = cropped_prism_img.crop((15, 23, 335, 320))

    except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise
    
    for i in range(0, num_images):
        positions = add_obj(positions, cropped_prism_img, image_dimensions[0], image_dimensions[1])
        print("Finished 1st execution and positions size", len(positions))
        positions = add_obj(positions, cropped_cube_img, image_dimensions[0], image_dimensions[1])
        print("Finished 2nd execution and positions size", len(positions))
        positions = add_obj(positions, cropped_dodecahedon_img, image_dimensions[0], image_dimensions[1])
        print("Finished 3rd execution and positions size", len(positions))
        positions = add_obj(positions, cropped_rectangle_img, image_dimensions[0], image_dimensions[1])
        print("Finished last execution and positions size", len(positions))

        try :
            plt.figure(figsize=(15, 15))
            cv.imshow('Problem 1', cv.UMat(bg))
            cv.imwrite(output_folder +"/Output_Image_" + str(i) + ".png", bg)

        except cv.error as e:
            print('An Exception Occurred')
            print('Exception Details ->', e)

        positions = []
        bg = np.array(background)
    
# Using the special variable 
# __name__
if __name__=="__main__":

    #Enter python gen_images.py to know more about the input format
    parser = argparse.ArgumentParser(description="Generate images with non-overlapping shapes.",
             epilog="For more information, see the project documentation."
    )
    
    parser.add_argument("--input", required=True,
        help="Path to the input images folder."
    )

    parser.add_argument("--output", required=True,
        help="Path to the output images folder."
    )
    
    parser.add_argument("--dimensions", nargs=2, type=int, required=True,
        help="Output image dimensions (width height)."
    )
    
    parser.add_argument("--num-images", type=int, required=True,
        help="Number of output images to generate."
    )

    main(parser.parse_args())