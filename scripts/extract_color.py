'''

	Anton lindstrand

	How to use: python3 extract_color.py <filename> <majority_threshold>

'''

import sys
import numpy as np
import matplotlib.pyplot as plt
from skimage.exposure import histogram
from skimage import io
from skimage.viewer import ImageViewer


def handleArguments():
	if len(sys.argv) != 3:
		print("wrong argument: incorrect number of arguments")
		exit()

	filepath = sys.argv[1]
	threshold = sys.argv[2]

	splitted = filepath.split('.')
	if len(splitted) == 1:
		return splitted, ""
		print("wrong argument: not a file")
		exit()

	return filepath, float(threshold)


def is_greater(first, others):
	return all(first > other_elem for other_elem in others)


def normalize_color(sum, count):
	# divide sum with count
	return (sum/count)[0] if count != 0  else [0, 0, 0]


def normalize_colors(red_sum, red_count, green_sum, green_count, blue_sum, blue_count, total_sum, total_count):
	# divide sums with their respective count
	red_sum = normalize_color(red_sum, red_count)
	green_sum = normalize_color(green_sum, green_count)
	blue_sum = normalize_color(blue_sum, blue_count)
	total_sum = normalize_color(total_sum, total_count)

	return red_sum, green_sum, blue_sum, total_sum


def format_float_in_sums(red_sum, green_sum, blue_sum, total_sum):
	# format floats to 2 decimal points
	red_sum = [ float("{0:.2f}".format(elem)) for elem in red_sum ]
	green_sum = [ float("{0:.2f}".format(elem)) for elem in green_sum ]
	blue_sum = [ float("{0:.2f}".format(elem)) for elem in blue_sum ]
	total_sum = [ float("{0:.2f}".format(elem)) for elem in total_sum ]

	return red_sum, green_sum, blue_sum, total_sum


def format_to_percentages(red_count, green_count, blue_count, total_count):
	red_percentage = float("{0:.2f}".format(red_count/total_count*100)) 	if red_count != 0 else 0
	green_percentage = float("{0:.2f}".format(green_count/total_count*100))	if green_count != 0 else 0
	blue_percentage = float("{0:.2f}".format(blue_count/total_count*100)) 	if blue_count != 0 else 0

	return red_percentage, green_percentage, blue_percentage


def is_ripe(color, ripe_color):
	# if color is between (150-255, 0-90, 0-100)
	return color[0] > ripe_color[0] and color[1] < ripe_color[1] and color[2] < ripe_color[2]


def extract_color_from_rectangles(filepath, rectangles, output_to_file=False, print_info=False):
	ripe_colors = []
	non_ripe_colors = []
	prediction = io.imread(filepath)

	for points, count in zip(rectangles, range(len(rectangles))):
		left, top, right, bottom = points[0], points[1], points[2], points[3]

		# is used to display the color on a new file, but depends on what value 'output_to_file' has
		result_rectangle = np.zeros((bottom-top, right-left,3), np.uint8)
		ripe = False
		ripe_color = [150, 90, 100]

		shape = np.shape(result_rectangle)

		total_sum, total_count, red_sum, red_count, green_sum, green_count, blue_sum, blue_count = get_colors(prediction, points)
		red_sum, green_sum, blue_sum, total_sum = normalize_colors(red_sum, red_count, green_sum, green_count, blue_sum, blue_count, total_sum, total_count)
		red_sum, green_sum, blue_sum, total_sum = format_float_in_sums(red_sum, green_sum, blue_sum, total_sum)
		red_percentage, green_percentage, blue_percentage = format_to_percentages(red_count, green_count, blue_count, total_count)

		result_sum = total_sum

		if print_info:
			print(f"TOTAL\tcount: {total_count}\t\t\tavg color: {total_sum}")
			print(f"RED\tcount: {red_count}\tpercentage: {red_percentage}%\tavg color: {red_sum}")
			print(f"GREEN\tcount: {green_count}\tpercentage: {green_percentage}%\tavg color: {green_sum}")
			print(f"BLUE\tcount: {blue_count}\tpercentage: {blue_percentage}%\tavg color: {blue_sum}")

		for y in range(shape[0]):
			for x in range(shape[1]):
					result_rectangle[y, x] = result_sum

		if is_ripe(total_sum, ripe_color):
			ripe = True
			ripe_colors.append([total_sum, points])
		else:
			non_ripe_colors.append([total_sum, points])

		if output_to_file:
			filename = f"extractions/test{count}"
			filename += "_ripe.png" if ripe else ".png"
			io.imsave(filename, result_rectangle, plugin=None, check_contrast=False)

			if print_info:
				print(f"successfully created {filename} with points: {points}")

	return { "ripe" : ripe_colors, "non_ripe" : non_ripe_colors }


def get_colors(image, points):
	# get the total rgb values and the count of each rgb channel where the channel is the majority of the pixel color
	left, top, right, bottom = points[0], points[1], points[2], points[3]

	total_sum = np.zeros((1,3), np.uint64)
	red_sum = np.zeros((1,3), np.uint64)
	green_sum = np.zeros((1,3), np.uint64)
	blue_sum = np.zeros((1,3), np.uint64)
	total_count = red_count = green_count = blue_count = 0

	shape = np.shape(image)
	dim_y, dim_x = shape[0], shape[1]

	for y in range(top, bottom):
		for x in range(left, right):
			val_y = y if y < dim_y else dim_y - 1
			val_x = x if x < dim_x else dim_x - 1
			rgb = image[val_y, val_x]
			np.add(total_sum, rgb, total_sum)

			if is_greater(rgb[0], [rgb[1], rgb[2]]): # red is greatest
				np.add(red_sum, rgb, red_sum)
				red_count += 1
			elif is_greater(rgb[1], [rgb[0], rgb[2]]): # green is greatest
				np.add(green_sum, rgb, green_sum)
				green_count += 1
			elif is_greater(rgb[2], [rgb[1], rgb[0]]): # blue is greatest
				np.add(blue_sum, rgb, blue_sum)
				blue_count += 1

	total_count = red_count + green_count + blue_count

	return total_sum, total_count, red_sum, red_count, green_sum, green_count, blue_sum, blue_count


def extract_color_from_image(filepath, majority_threshold):
	new_filepath = filepath.split('.')[0] + "_color.png"

	prediction = io.imread(filepath)
	shape = np.shape(prediction)
	total_sum = np.zeros((1,3), np.uint64)
	red_sum = np.zeros((1,3), np.uint64)
	green_sum = np.zeros((1,3), np.uint64)
	blue_sum = np.zeros((1,3), np.uint64)
	total_count = 0
	red_count = 0
	green_count = 0
	blue_count = 0

	result_rectangle = np.copy(prediction)

	for y in range(shape[0]):
		for x in range(shape[1]):
			rgb = prediction[y, x]
			np.add(total_sum, rgb, total_sum)

			if is_greater(rgb[0], [rgb[1], rgb[2]]): # red
				np.add(red_sum, rgb, red_sum)
				red_count += 1
			elif is_greater(rgb[1], [rgb[0], rgb[2]]): # green
				np.add(green_sum, rgb, green_sum)
				green_count += 1
			elif is_greater(rgb[2], [rgb[1], rgb[0]]): # blue
				np.add(blue_sum, rgb, blue_sum)
				blue_count += 1


	total_count = red_count + green_count + blue_count
	red_sum = (red_sum/red_count)[0]			if red_count != 0  else [0, 0, 0]
	green_sum = (green_sum/green_count)[0]		if green_count != 0 else [0, 0, 0]
	blue_sum = (blue_sum/blue_sum)[0]			if blue_count != 0 else [0, 0, 0]
	total_sum = (total_sum/total_count)[0]

	red_sum = [ float("{0:.2f}".format(elem)) for elem in red_sum ]
	green_sum = [ float("{0:.2f}".format(elem)) for elem in green_sum ]
	blue_sum = [ float("{0:.2f}".format(elem)) for elem in blue_sum ]

	red_percentage = float("{0:.2f}".format(red_count/total_count*100)) if red_count != 0 else 0
	green_percentage = float("{0:.2f}".format(green_count/total_count*100)) if green_count != 0 else 0
	blue_percentage = float("{0:.2f}".format(blue_count/total_count*100)) if blue_count != 0 else 0

	total_string = f"TOTAL\tcount: {total_count}"
	red_string = f"RED\tcount: {red_count}\tpercentage: {red_percentage}%\tavg color: {red_sum}"
	green_string = f"GREEN\tcount: {green_count}\tpercentage: {green_percentage}%\tavg color: {green_sum}"
	blue_string = f"BLUE\tcount: {blue_count}\tpercentage: {blue_percentage}%\tavg color: {blue_sum}"

	red_sum = np.asarray(red_sum)
	green_sum = np.asarray(green_sum)
	blue_sum = np.asarray(blue_sum)

	majority = any(percentage > majority_threshold for percentage in [red_percentage, green_percentage, blue_percentage])

	if majority or majority_threshold == 0:
		print(f"Using majority color on {filepath.split('/')[-1]}")

		if is_greater(red_percentage, [green_percentage, blue_percentage]):
			result_sum = red_sum
			print(red_string)
		elif is_greater(green_percentage, [red_percentage, blue_percentage]):
			result_sum = green_sum
			print(green_string)
		else:
			result_sum = blue_sum
			print(blue_string)
	else:
		print(f"Using all colors on {filepath.split('/')[-1]}")
		print(total_string)
		print(red_string)
		print(green_string)
		print(blue_string)

		result_sum = total_sum

	print(total_sum)
	if total_sum[0] > 130 and total_sum[0] < 255:
		if total_sum[1] > 0 and total_sum[1] < 70:
			if total_sum[2] > 0 and total_sum[2] < 100:
				new_filepath = filepath.split('.')[0] + "_color_ripe.png"


	for y in range(shape[0]):
		for x in range(shape[1]):
				result_rectangle[y, x] = result_sum

	io.imsave(new_filepath, result_rectangle, plugin=None, check_contrast=False)
	print(f"successfully created {new_filepath}")


def main():
	filepath, majority_threshold = handleArguments()
	extract_msc_from_image(filepath, majority_threshold)


if __name__ == "__main__":
	main()
