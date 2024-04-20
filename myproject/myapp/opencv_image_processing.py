import cv2

# 1. Reading an image
image_path = ""
image = cv2.imread(image_path)

# Check if the image was successfully loaded
if image is None:
    print("Error: Unable to load image.")
    exit()

# 2. Converting the image to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 3. Playing with RGB color channels
blue_channel, green_channel, red_channel = cv2.split(image)

# 4. Resizing the image
resized_image = cv2.resize(image, (300, 300))

# 5. Flipping the image horizontally
flipped_image = cv2.flip(image, 1)  # 1 for horizontal flip, 0 for vertical flip, -1 for both

# 6. Cropping a region of interest (ROI)
x, y, w, h = 100, 100, 200, 200  # Define the ROI coordinates and dimensions
cropped_image = image[y:y+h, x:x+w]

# 7. Saving the image using imwrite
output_image_path = ""
cv2.imwrite(output_image_path, image)

# 8. Stacking multiple images horizontally
stacked_image_horizontal = cv2.hconcat([image, gray_image, blue_channel])
# If the images have different heights, you can resize them first

# 9. Drawing text on an image
text = "OpenCV Image Editing"
cv2.putText(image, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

# Display the original and edited images
cv2.imshow("Original Image", image)
cv2.imshow("Grayscale Image", gray_image)
cv2.imshow("Blue Channel", blue_channel)
cv2.imshow("Resized Image", resized_image)
cv2.imshow("Flipped Image", flipped_image)
cv2.imshow("Cropped Image", cropped_image)
cv2.imshow("Stacked Images (Horizontal)", stacked_image_horizontal)

# Wait for any key press and then close all windows
cv2.waitKey(0)
cv2.destroyAllWindows()
