from controller import Robot, Camera, Motor
import os

# Constants
SPEED = 4
TIME_STEP = 32

# Ball Type enum
RED, GREEN, BLUE, NONE = range(4)

# Color names and ANSI color codes
color_names = ["red", "green", "blue"]
ansi_colors = ["\x1b[31m", "\x1b[32m", "\x1b[34m"]  # Red, Green, Blue
filenames = ["red_ball.png", "green_ball.png", "blue_ball.png"]

# Initialize the robot
robot = Robot()

# Initialize devices
camera = robot.getDevice("camera")
camera.enable(TIME_STEP)
width = camera.getWidth()
height = camera.getHeight()

left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# Main loop
pause_counter = 0
while robot.step(TIME_STEP) != -1:
    # Get image from camera
    image = camera.getImage()

    # Decrement the pause_counter
    if pause_counter > 0:
        pause_counter -= 1

    if pause_counter > 640 / TIME_STEP:
        left_speed = 0
        right_speed = 0
    elif pause_counter > 0:
        left_speed = -SPEED
        right_speed = SPEED
    elif image is None:
        left_speed = 0
        right_speed = 0
    else:
        # Reset the color sums
        red = 0
        green = 0
        blue = 0

        # Analyze the camera image in the center area
        for i in range(width // 3, 2 * width // 3):
            for j in range(height // 2, 3 * height // 4):
                red += camera.imageGetRed(image, width, i, j)
                green += camera.imageGetGreen(image, width, i, j)
                blue += camera.imageGetBlue(image, width, i, j)

        # Detect the dominant color
        if red > 3 * green and red > 3 * blue:
            current_ball = RED
        elif green > 3 * red and green > 3 * blue:
            current_ball = GREEN
        elif blue > 3 * red and blue > 3 * green:
            current_ball = BLUE
        else:
            current_ball = NONE

        # If no ball is detected, continue turning
        if current_ball == NONE:
            left_speed = -SPEED
            right_speed = SPEED
        else:
            left_speed = 0
            right_speed = 0
            print(f"Color of the ball is {ansi_colors[current_blob]}{color_names[current_blob]}\x1b[0m.")

            # Save the image with the corresponding color name
            user_directory = os.getenv("HOME")  # Get user directory (cross-platform)
            filepath = os.path.join(user_directory, filenames[current_blob])
            camera.saveImage(filepath, 100)

            # Set the pause counter to stop the robot temporarily
            pause_counter = 1280 / TIME_STEP

    # Set the motor speeds
    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)

# Clean up when done
robot.cleanup()

