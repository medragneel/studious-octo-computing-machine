from PIL import Image, ImageDraw, ImageFont,ImageEnhance

# Open the image
image = Image.open('./jujutsu-kaisen.webp')

# Create a drawing context
draw = ImageDraw.Draw(image)

# Get image size
width, height = image.size

# Calculate the position to place the text in the center
text = "HIGH NOON"
font = ImageFont.truetype("./fonts/Painted Lady.otf", 140)  # You can change the font and size
text_width, text_height = draw.textsize(text, font)
x = (width - text_width) / 2
y = (height - text_height) / 2

# Define text color
text_color = (255, 255, 255)  # White color

# Draw the text on the image
draw.text((x, y), text, fill=text_color, font=font)
enhancer = ImageEnhance.Brightness(image)

image_with_contrast = enhancer.enhance(1.2)

# Save or display the modified image
image_with_contrast.save('output_image.jpg')
image_with_contrast.show()

