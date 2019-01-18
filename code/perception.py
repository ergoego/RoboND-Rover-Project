import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh_lower=(160, 160, 160), rgb_thresh_upper=(255, 255, 255)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    # the below is mapping over all values in the img array, so we will return an array of the same dimensions. 
    above_thresh = (img[:,:,0] > rgb_thresh_lower[0]) & (img[:,:,0] < rgb_thresh_upper[0]) \
                & (img[:,:,1] > rgb_thresh_lower[1]) & (img[:,:,1] < rgb_thresh_upper[1]) \
                & (img[:,:,2] > rgb_thresh_lower[2]) & (img[:,:,2] < rgb_thresh_upper[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select

# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    scale = 10 #Assume scale factor of 10:1 worldspace pixels:roverspace pixels
    xpix_translated = np.int_(xpos + (xpix_rot / scale))
    ypix_translated = np.int_(ypos + (ypix_rot / scale)) 
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # We need to account for the fact that the camera is mounted some height above the ground,
    # so we cannot assume the front of the Rover is located precisely at the bottom of the 
    # image. We can guestimate where the bottom of the camera is located ahead of the rover
    # using the grid and 3rd-person view in the simulator. If we know the grid is 1x1m, 
    # we can get a pretty good estimate. 
    bottom_offset = 1
    # 1) Define source and destination points for perspective transform
    # We define 4 source points on the "ground" of the image and transform
    # them to fit a top-down view, where in the grid_image 1 square is 1m^2, 
    # we will make that, in top down view on the map, correspond to a 10x10 pix
    # box. This is important as we need to know the shape and size of our destination
    # for our transformation.
    dst_size = 5
    # The values for source are hard-coded, and are taken from overlaying a grid on the ground  
    # in the simulator, capturing an image, and then using jupyter notebooks matplotlib to
    # interacively mouse over the corners, check the RGB values to make sure we are at the 
    # corner (the intersection will be darkest), and then record the coordinate.  
    source = np.float32([[114, 118], #bottom left
                        [307, 120], #bottom right
                        [220, 94], #top right
                        [148, 94]]) #top left
    destination = np.float32([[Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - bottom_offset], #bottom left
                  [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - bottom_offset], #bottom right
                  [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset], #top right
                  [Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset], #top left
                  ])
    # 2) Apply perspective transform
    warped = perspect_transform(Rover.img, source, destination)

    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    sample_thresh = color_thresh(warped, rgb_thresh_lower=(140, 110, 0), rgb_thresh_upper=(250, 210, 100))
    obstacle_thresh = color_thresh(warped, rgb_thresh_lower=(0, 0, 0), rgb_thresh_upper=(160, 160, 160))
    path_thresh = color_thresh(warped)

    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    Rover.vision_image[:,:,0] = obstacle_thresh
    Rover.vision_image[:,:,1] = sample_thresh
    Rover.vision_image[:,:,2] = path_thresh

    # 5) Convert map image pixel values to rover-centric coords
    obstacle_x_rover_coords, obstacle_y_rover_coords = rover_coords(obstacle_thresh)
    sample_x_rover_coords, sample_y_rover_coords = rover_coords(sample_thresh)
    path_x_rover_coords, path_y_rover_coords = rover_coords(path_thresh)

    # 6) Convert rover-centric pixel values to world coordinates
    obstacle_x_world, obstacle_y_world = pix_to_world(obstacle_x_rover_coords, obstacle_y_rover_coords, Rover.pos[0], Rover.pos[1], Rover.yaw, 200, 10)
    sample_x_world, sample_y_world = pix_to_world(sample_x_rover_coords, sample_y_rover_coords, Rover.pos[0], Rover.pos[1], Rover.yaw, 200, 10)
    path_x_world, path_y_world = pix_to_world(path_x_rover_coords, path_y_rover_coords, Rover.pos[0], Rover.pos[1], Rover.yaw, 200, 10)

    # 7) Update Rover worldmap (to be displayed on right side of screen)
    Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
    Rover.worldmap[sample_y_world, sample_x_world, 1] += 1
    Rover.worldmap[path_y_world, path_x_world, 2] += 1

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
    Rover.nav_dists, Rover.nav_angles = to_polar_coords(path_x_rover_coords, path_y_rover_coords)

    return Rover