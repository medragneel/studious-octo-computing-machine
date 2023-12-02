from PIL import Image, ImageDraw, ImageFont
import sys
import uuid

# Thumbnail dimensions
width = 2560
height = 1440
image_input = sys.argv[1]
image_output = f"{uuid.uuid4()}.png"

# Background color (white)
background_color = (255, 255, 255)

# Create a new image with the specified dimensions and background color
image = Image.new("RGB", (width, height), background_color)
draw = ImageDraw.Draw(image)

# Centered text
text = sys.argv[2]
font_size = 200
font = ImageFont.truetype("./fonts/Anurati-Regular.otf", font_size)
text_color = (0, 0, 0)  # Black color

# Calculate text size and position
text_width, text_height = draw.textsize(text, font)
x = (width - text_width) / 2
y = (height - text_height) / 2

# Add the centered text to the image
draw.text((x, y), text, fill=text_color, font=font)

# Load and resize the PNG image
png_image = Image.open(image_input)
# png_image = png_image.resize((width // 2, height // 2))
# Load and resize the PNG image to make it bigger
new_width = int(width * float(sys.argv[3]))  # Adjust the scaling factor as needed
new_height = int(height * float( sys.argv[3] ))  # Adjust the scaling factor as needed
png_image = png_image.resize((new_width, new_height))


# Calculate the position to center the PNG image on the thumbnail
png_x = (width - png_image.width) // 2
png_y = height - png_image.height

# Paste the PNG image onto the thumbnail
image.paste(png_image, (png_x, png_y), png_image)

# Save the final thumbnail
image.save(image_output)

# Close the image
image.close()

