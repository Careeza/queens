import cv2
import numpy as np
import mss
from collections import defaultdict
import threading
from pynput import keyboard
import pyautogui

have_highdpi = False
double_click = True

def solution_valid_for_paving(paving, solution):
	queens_color = [paving[queen_x, queen_y] for queen_x, queen_y in enumerate(solution)]
	if len(set(queens_color)) != len(queens_color):
		return False
	return True

def solve(paving):
	n = len(paving)
	try:
		with open(f'solution_{n}.txt', 'r') as f:
			solutions = [[int(x) for x in line.strip().split(',')] for line in f]
	except FileNotFoundError:
		print(f"Solutions for {n}x{n} not found")
		return 0
	for solution in solutions:
		if solution_valid_for_paving(paving, solution):
			return solution
	print(f"No valid solution found for {n}x{n}")
	return None

def detect_grid(image):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	edges = cv2.Canny(blurred, 50, 150)

	contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	contours = sorted(contours, key=cv2.contourArea, reverse=True)

	if len(contours) == 0:
		return None

	grid_contour = contours[0]
	x, y, w, h = cv2.boundingRect(grid_contour)

	grid = image[y:y+h, x:x+w]
	return grid, (x, y, w, h)

def is_duplicate(square1, square2, tolerance=10):
	x1, y1, w1, h1 = square1
	x2, y2, w2, h2 = square2

	return (
		abs(x1 - x2) <= tolerance and
		abs(y1 - y2) <= tolerance and
		abs(w1 - w2) <= tolerance and
		abs(h1 - h2) <= tolerance
	)

def align_squares(squares, tolerance=10):
	x_coords = [x for x, _, _, _ in squares]
	y_coords = [y for _, y, _, _ in squares]

	unique_x = np.unique([np.median([x for x in x_coords if abs(x - ref_x) <= tolerance]) for ref_x in x_coords])
	unique_y = np.unique([np.median([y for y in y_coords if abs(y - ref_y) <= tolerance]) for ref_y in y_coords])

	aligned_squares = []
	for x, y, w, h in squares:
		# Snap x and y to the nearest unique value
		closest_x = min(unique_x, key=lambda ref_x: abs(x - ref_x))
		closest_y = min(unique_y, key=lambda ref_y: abs(y - ref_y))
		aligned_squares.append((int(closest_x), int(closest_y), w, h))

	return aligned_squares

def extract_cells(grid):
	gray = cv2.cvtColor(grid, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	_, binary = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY_INV)
	contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	# find all squares in the image
	squares = []
	for contour in contours:
		epsilon = 0.05 * cv2.arcLength(contour, True)
		approx = cv2.approxPolyDP(contour, epsilon, True)

		if len(approx) == 4 and cv2.contourArea(approx) > 100:
			x, y, w, h = cv2.boundingRect(approx)
			aspect_ratio = float(w) / h
			if 0.9 <= aspect_ratio <= 1.1:  # Square aspect ratio
				squares.append((x, y, w, h))

	# Filter squares based on area
	if len(squares) > 0:
		areas = [w * h for _, _, w, h in squares]
		median_area = np.median(areas)

		area_tolerance = 0.2
		filtered_squares = [
			(x, y, w, h)
			for (x, y, w, h) in squares
			if abs(w * h - median_area) / median_area <= area_tolerance
		]
		squares = filtered_squares


	# Filter squares based on similarity
	filtered_squares = []
	for square in squares:
		duplicate_found = False
		for filtered_square in filtered_squares:
			if is_duplicate(square, filtered_square):
				duplicate_found = True
				break
		if not duplicate_found:
			filtered_squares.append(square)

	squares = filtered_squares
	squares = align_squares(squares)
	return squares

def extract_colors(grid, squares):
	color_map = defaultdict(list)
	colors_detected = []

	for square_idx, (x, y, w, h) in enumerate(squares):
		margin = 0.4
		x_center_start = int(x + margin * w)
		x_center_end = int(x + (1 - margin) * w)
		y_center_start = int(y + margin * h)
		y_center_end = int(y + (1 - margin) * h)

		center_region = grid[y_center_start:y_center_end, x_center_start:x_center_end]

		avg_color = cv2.mean(center_region)[:3]
		matched = False
		for idx, ref_color in enumerate(colors_detected):
			if np.linalg.norm(np.array(avg_color) - np.array(ref_color)) < 1:
				color_map[idx].append((square_idx, (x, y, w, h)))
				matched = True
				break
		if not matched:
			colors_detected.append(avg_color)
			color_map[len(colors_detected) - 1].append((square_idx, (x, y, w, h)))
	return color_map, colors_detected

def extract_grid(grid_image):
	cells = extract_cells(grid_image)

	if len(cells) == 0:
		return None,None
	if len(cells) != int(np.sqrt(len(cells))) ** 2:
		return None, None

	n = int(np.sqrt(len(cells)))
	if n < 5:
		return None,None
	cells = sorted(cells, key=lambda sq: (sq[1], sq[0]))
	color_map, colors_detected = extract_colors(grid_image, cells)

	if len(color_map) != n:
		return None, None

	grid = np.zeros((n, n), dtype=int)
	for idx, squares_group in color_map.items():
		for square_idx, (x, y, w, h) in squares_group:
			grid[square_idx // n, square_idx % n] = idx

	return cells, grid

def click_mouse(x, y):
	pyautogui.click(x, y, _pause=False, interval=0)
	# pyautogui.click(x, y, _pause=False, interval=0)
	# pyautogui.click(x, y)

def solve_puzzle(offset_x, offset_y, cells, grid):
	global have_highdpi
	global double_click

	solution = solve(grid)
	for i in range(len(solution)):
		index = i * len(solution) + solution[i]
		x, y, w, h = cells[index]
		if have_highdpi:
			click_mouse(offset_x + x // 2 + 10, offset_y + y // 2 + 10)
			if double_click:
				click_mouse(offset_x + x // 2 + 10, offset_y + y // 2 + 10)
		else:
			click_mouse(offset_x + x + 10, offset_y + y + 10)
			if double_click:
				click_mouse(offset_x + x + 10, offset_y + y + 10)

stop_flag = False
capture_flag = False

def on_press(key):
	global stop_flag
	global capture_flag
	try:
		if key.char == 'q':  # Exit the program when 'q' is pressed
			print("Exiting...")
			stop_flag = True
			return False  # Stop the listener
		if key.char == 'c':
			capture_flag = not capture_flag
			print(f"Capture flag: {capture_flag}")
	except AttributeError:
		pass  # Handle special keys (if needed)

def keyboard_listener():
	# Start the listener in a blocking way
	with keyboard.Listener(on_press=on_press) as listener:
		listener.join()

def main():
	global stop_flag
	global capture_flag
	global have_highdpi

	listener_thread = threading.Thread(target=keyboard_listener)
	listener_thread.start()
	last_x, last_y = 0, 0
	solution = [0, 4, 7, 5, 2, 6, 1, 3]
	with mss.mss() as sct:
		while not stop_flag:
			screen = np.array(sct.grab(sct.monitors[0]))

			if capture_flag:
				grid_image, (x, y, w, h) = detect_grid(screen)
				if grid_image is not None:
					cells, grid = extract_grid(grid_image)
					if grid is not None:
						print(x,y)
						if x == last_x and y == last_y:
							if have_highdpi:
								solve_puzzle(x//2, y//2, cells, grid)
							else:
								solve_puzzle(x, y, cells, grid)
								
							capture_flag = False
				last_x, last_y = x, y
			cv2.waitKey(1)
		cv2.destroyAllWindows()


if __name__ == "__main__":
	main()
