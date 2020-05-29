from imageai.Detection.Custom import CustomObjectDetection
import numpy as np
import extract_color
import sys
from skimage import io
from skimage.viewer import ImageViewer
from mysql import *
import mysql.connector
from mysql.connector import Error

"""
script to test model / predict
Models in tomato/models

	How to use: python predict_image.py <image_path> <minimum_percentage> <extract_detected_objects[True/False]>
"""

def handleArguments():
	if (len(sys.argv) != 4):
		print("wrong arguments: incorrect number of arguments")
		exit()

	extract_detected_objects = True if sys.argv[3] == "True" else False

	return sys.argv[1], int(sys.argv[2]), extract_detected_objects


def get_center_point(box_points):
	left, top, right, bottom = box_points[0], box_points[1], box_points[2], box_points[3]
	width = right - left
	height = bottom - top
	x, y = right - width/2, bottom - height/2

	return [x, y]


def point_is_in_rectangle(center_point, box_points):
	left, top, right, bottom = box_points[0], box_points[1], box_points[2], box_points[3]
	center_x, center_y = center_point[0], center_point[1]

	# check if center_x, center_y is inside the box
	return (center_x > left and center_y > top and center_x < right and center_y < bottom)


def main():
	filepath, minimum_percentage, extract_detected_objects = handleArguments()
	predict_image(filepath, minimum_percentage, extract_detected_objects, load_model())


def filter_rectangle_duplicates(objects):
	total_duplicates = []
	final = []

	for i in range(len(objects)):
		duplicates = []
		final.append(objects[i])

		for j in range(i + 1, len(objects)):
			box_points = objects[j][-1]
			center_point = get_center_point(objects[i][-1])

			if point_is_in_rectangle(center_point, box_points):
				duplicates.append(objects[j]) # store [j] in duplicates if [i] is inside [j]

		if len(duplicates) != 0: # it there were duplicates, add to list and add list to total_duplicates
			duplicates.append(objects[i])
			total_duplicates.append(duplicates)


	for duplicates in total_duplicates:
		sorted_list = sorted(duplicates, key=lambda obj: obj[1], reverse=True)

		for elem in sorted_list[1:]: # don't remove the first one because its sorted with the highest probability first, we want to keep the best one
			if elem in final:
				final.remove(elem)

	return final


def filter_rectangle_ratios(objects):
	total_duplicates = []
	final = []

	for object in objects:
		points = object[-1]
		left, top, right, bottom = points[0], points[1], points[2], points[3]
		width = right - left
		height = bottom - top

		ratio = width/height if width >= height else height/width

		# include rectangles that has a ratio less than 2; this will exclude rectangles with ratio bigger than 2
		if not ratio > 2:
			final.append(object)

	return final


def write_rectangles_to_file(objects, filepath, new_filepath):
	image = io.imread(filepath)
	shape = np.shape(image)
	dim_y, dim_x = shape[0], shape[1]

	for object in objects:
		white_pixel = ([255, 255, 255])
		points = object[-1]

		left, top, right, bottom = points[0], points[1], points[2], points[3]
		for y in range(top, bottom):
			# out-of-bounds check
			val_y = y if y < dim_y else dim_y - 1

			image[val_y, left] = white_pixel # set the 'left' pixel border

			# out-of-bounds check
			if right >= dim_x:
				image[val_y, dim_x - 1] = white_pixel # set the 'right' pixel border
			else:
				image[val_y, right] = white_pixel # set the 'right' pixel border

		for x in range(left, right):
			# out-of-bounds check
			val_x = x if x < dim_x else dim_x - 1

			image[top, val_x] = white_pixel # set the 'top' pixel border

			# out-of-bounds check
			if bottom >= dim_y:
				image[dim_y - 1, val_x] = white_pixel # set the 'bottom' pixel border
			else:
				image[bottom, val_x] = white_pixel # set the 'bottom' pixel border


	io.imsave(new_filepath, image, plugin=None, check_contrast=False)


def load_model():
	detector = CustomObjectDetection()
	detector.setModelTypeAsYOLOv3()
	detector.setModelPath("tomato/models/detection_model-ex-052--loss-0033.691.h5")
	detector.setJsonPath("tomato/json/detection_config.json")
	detector.loadModel()

	return detector


def predict_image(filepath, minimum_percentage, extract_detected_objects, detector):
	output_path = "predictions/" + filepath.split('/')[-1]

	detections = detector.detectObjectsFromImage(input_image=filepath,
												output_image_path=output_path,
												minimum_percentage_probability=minimum_percentage,
												extract_detected_objects=extract_detected_objects,
												display_percentage_probability=False,
												display_object_name=False
												)

	if extract_detected_objects:
		formatted = [ [obj["percentage_probability"], obj_path] for obj, obj_path in zip(detections[0], detections[1]) ]
		sorted_list = sorted(formatted, key=lambda obj: obj[0], reverse=True)

		for elem in sorted_list:
			print(elem)
			extract_color.extract_color_from_image(elem[1], 0)
		print(f"number of detected elements: {len(sorted_list)}")

	else:
		formatted = [ [obj["name"], obj["percentage_probability"], obj["box_points"]] for obj in detections ]
		sorted_list = sorted(formatted, key=lambda obj: obj[2], reverse=True)

		# uncomment the following write_rectangles_to_file lines to see the difference for each filter

		#write_rectangles_to_file(formatted, filepath, "predictions/original.jpg")
		final1 = filter_rectangle_duplicates(formatted)
		#write_rectangles_to_file(final1, filepath, "predictions/no_duplicates.jpg")
		final2 = filter_rectangle_ratios(formatted)
		#write_rectangles_to_file(final2, filepath, "predictions/no_weird_ratios.jpg")
		final = filter_rectangle_ratios(final1)
		#write_rectangles_to_file(final, filepath, "predictions/no_weird_ratios_or_duplicates.jpg")

		print(f"total: {len(formatted)}, nr of weird ratios: {len(formatted) - len(final2)}, nr of duplicates: {len(formatted) - len(final1)}, total nr after removing both: {len(final)}")

		all_points = [ elem[-1] for elem in final ]

		tomatoes = extract_color.extract_color_from_rectangles(filepath, all_points, print_info=False)

		output = ""
		if "ripe" in tomatoes:
			output += f'{len(tomatoes["ripe"])} ripe tomatoes\n'
		if "non_ripe" in tomatoes:
			output += f'{len(tomatoes["non_ripe"])} non-ripe tomatoes'
			write_rectangles_to_file(tomatoes["non_ripe"], filepath, "predictions/non_ripe.jpg")

		ripeTomatoes = len(tomatoes['ripe'])
		nonRipeTomatoes = len(tomatoes['non_ripe'])

		return tomatoes


if __name__ == "__main__":
	main()
