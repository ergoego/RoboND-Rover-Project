import numpy as np
import cv2

# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'forward': 
            # Check the extent of navigable terrain
            if Rover.near_sample:
                Rover.mode == 'stop'
            if len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                if len(Rover.sample_angles) >= 1: #LEFT OFF JUST TRYING TO SWAP OUT STEERING ON THIS CONDITION
                    # Set steering to average angle clipped to the range +/- 15
                    Rover.steer = np.clip(np.mean(Rover.sample_angles * 180/np.pi), -15, 15)
                else:
                	Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'

    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
    
    return Rover

def sample_seen(Rover):
    
    # Create a scaled map for plotting and clean up obs/nav pixels a bit
    if np.max(Rover.worldmap[:,:,2]) > 0:
        nav_pix = Rover.worldmap[:,:,2] > 0
        navigable = Rover.worldmap[:,:,2] * (255 / np.mean(Rover.worldmap[nav_pix, 2]))
    else: 
        navigable = Rover.worldmap[:,:,2]
    
    if np.max(Rover.worldmap[:,:,0]) > 0:
        obs_pix = Rover.worldmap[:,:,0] > 0
        obstacle = Rover.worldmap[:,:,0] * (255 / np.mean(Rover.worldmap[obs_pix, 0]))
    else:
        obstacle = Rover.worldmap[:,:,0]

    likely_nav = navigable >= obstacle
    obstacle[likely_nav] = 0
    plotmap = np.zeros_like(Rover.worldmap)
    plotmap[:, :, 0] = obstacle
    plotmap[:, :, 2] = navigable
    plotmap = plotmap.clip(0, 255)

    # Overlay obstacle and navigable terrain map with ground truth map
    map_add = cv2.addWeighted(plotmap, 1, Rover.ground_truth, 0.5, 0)
    # Check whether any rock detections are present in worldmap
    rock_world_pos = Rover.worldmap[:,:,1].nonzero()
      # If there are, we'll step through the known sample positions
      # to confirm whether detections are real 
    samples_located = 0
    if rock_world_pos[0].any():
            
        rock_size = 2
        for idx in range(len(Rover.samples_pos[0])):
            test_rock_x = Rover.samples_pos[0][idx]
            test_rock_y = Rover.samples_pos[1][idx]
            rock_sample_dists = np.sqrt((test_rock_x - rock_world_pos[1])**2 + \
                                        (test_rock_y - rock_world_pos[0])**2)
            # If rocks were detected within 3 meters of known sample positions
            # consider it a success and plot the location of the known
            # sample on the map. 
            if np.min(rock_sample_dists) < 3:
                samples_located += 1

                map_add[test_rock_y-rock_size:test_rock_y+rock_size, 
                        test_rock_x-rock_size:test_rock_x+rock_size, :] = 255
                
                #Store the confirmed location so we can go to it
                Rover.sample_x_pos = test_rock_x
                Rover.sample_y_pos = test_rock_y
                #Go to the sample at the now confirmed location
                #Rover.mode = 'move to sample'

    return Rover, samples_located, map_add, plotmap