import numpy
import random
from PIL import Image, ImageDraw

rand = random.SystemRandom()

CONFIG = {
    "line": {
        "min_max_length_percent": 0.02,
        "max_max_length_percent": 1.0,
        "magnitude_length_scale": 1.0,
        "min_max_width": 1,
        "max_max_width": 10,
        "magnitude_width_scale": 1.0
    }
}

def random_xy(image):
    return (rand.randint(0, image.size[0] - 1), rand.randint(0, image.size[1] - 1))

def draw_random_line(draw, proposal, magnitude_ratio):  
    # Calculate how long the line should be based on the magnitude progress
    length_ratio = magnitude_ratio * CONFIG["line"]["magnitude_length_scale"]
    length_ratio = min(length_ratio, CONFIG["line"]["max_max_length_percent"])
    length_ratio = max(length_ratio, CONFIG["line"]["min_max_length_percent"])
    max_x_length = round(proposal.size[0] * length_ratio)
    max_y_length = round(proposal.size[1] * length_ratio)

    # Get the starting and ending points of the line
    start_xy = random_xy(proposal)
    end_xy = (rand.randint(max(0, start_xy[0] - max_x_length), min(proposal.size[0] - 1, start_xy[0] + max_x_length - 1)),
              rand.randint(max(0, start_xy[1] - max_y_length), min(proposal.size[1] - 1, start_xy[1] + max_y_length - 1)))
    
    # Calculate the width of the line based on the magnitude progress
    max_width = round(magnitude_ratio * CONFIG["line"]["magnitude_width_scale"] * CONFIG["line"]["max_max_width"])
    max_width = min(max_width, CONFIG["line"]["max_max_width"])
    max_width = max(max_width, CONFIG["line"]["min_max_width"])
    width = CONFIG["line"]["min_max_width"] if max_width == CONFIG["line"]["min_max_width"] else rand.randint(CONFIG["line"]["min_max_width"], max_width)
    
    draw.line(start_xy + end_xy, fill=rand.randint(0, 0xFFFFFF), width=width)

def mean_squared_error(image1_array, image2):
    """Calculate the mean squared error between two images."""
    return numpy.mean(numpy.square(image1_array - numpy.array(image2)))

def peak_signal_to_noise_ratio(image1_array, image2):
    """Calculate the peak signal to noise ratio between two images."""
    mse = mean_squared_error(image1_array, image2)
    return 10 * numpy.log10(255 ** 2 / mse)

def absolute_difference(image1_array, image2):
    """Calculate the absolute difference between two images."""
    return numpy.sum(numpy.abs(image1_array - numpy.array(image2)))

def main():   
    image_file = input("Enter the image file name: ")
    source_image = Image.open(image_file).convert("RGB")
    source_array = numpy.array(source_image)

    white_image = Image.new('RGB', source_image.size, color=0xFFFFFF)
    grey_image = Image.new('RGB', source_image.size, color=0x808080)
    black_image = Image.new('RGB', source_image.size, color=0x000000)

    print(f"White image:\tMSE: {mean_squared_error(source_array, white_image)}, PSNR: {peak_signal_to_noise_ratio(source_array, white_image)}, AD: {absolute_difference(source_array, white_image)}")
    print(f"Grey image:\tMSE: {mean_squared_error(source_array, grey_image)}, PSNR: {peak_signal_to_noise_ratio(source_array, grey_image)}, AD: {absolute_difference(source_array, grey_image)}")
    print(f"Black image:\tMSE: {mean_squared_error(source_array, black_image)}, PSNR: {peak_signal_to_noise_ratio(source_array, black_image)}, AD: {absolute_difference(source_array, black_image)}")

    target_image = grey_image
    difference = mean_squared_error(source_array, target_image)
    MAX_DIFFERENCE = difference
    print(f"Initial difference: {difference}. Starting image:")

    frame = 0  # Frame counter
    
    while True:
        for i in range(100000):
            proposal = target_image.copy()
            draw = ImageDraw.Draw(proposal)
            draw_random_line(draw, proposal, difference / MAX_DIFFERENCE)
            proposal_differcence = mean_squared_error(source_array, proposal)
            if proposal_differcence < difference:
                target_image = proposal
                difference = proposal_differcence
                print(f"New difference: {difference:.5f}\tFrame: {frame}\tTicks: {i}\tDifference percetage: {difference / MAX_DIFFERENCE * 100:.4f}%")
                with open(f"frames/frame{frame:06d}.png", "wb") as f:
                    target_image.save(f)
                    frame += 1
        if input("Continue? (y/n): ") == "n":
            break


if __name__ == "__main__":
    main()