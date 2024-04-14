import cv2

def process_image(image_path):
    # Read the image
    img = cv2.imread(image_path)

    # Process the image (example: convert to grayscale)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Display the processed image
    cv2.imshow('Processed Image', img_gray)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Save the processed image
    output_path = 'processed_image.jpg'
    cv2.imwrite(output_path, img_gray)
    print(f"Processed image saved to {output_path}")

if __name__ == "__main__":
    image_path = 'app/images/fruits.jpg'  # Path to your input image
    process_image(image_path)

