import cv2
import numpy as np
import mss
from collections import defaultdict
import threading
from pynput import keyboard
import pyautogui

have_highdpi = False
double_click = True
stop_flag = False
capture_flag = False

def is_symbole_possible(grid_symbole, x, y, symbole):
	old_symbole = grid_symbole[y, x]
	grid_symbole[y, x] = symbole
	symbole_in_line = (grid_symbole[y] == symbole).sum()
	symbole_in_col = (grid_symbole[:, x] == symbole).sum()
	if symbole_in_line > 3 or symbole_in_col > 3:
		grid_symbole[y, x] = old_symbole
		return False
	# check if there is 3 symbole in a row
	for i in range(min(0, x-2), max(6, x+2)):
		if (grid_symbole[y, i:i+3] == symbole).sum() == 3:
			grid_symbole[y, x] = old_symbole
			return False
	for i in range(min(0, y-2), max(6, y+2)):
		if (grid_symbole[i:i+3, x] == symbole).sum() == 3:
			grid_symbole[y, x] = old_symbole
			return False
	grid_symbole[y, x] = old_symbole
	return True

def possible_symboles(grid, x, y):
	possible = []
	for symbole in range(1, 3):
		if is_symbole_possible(grid, x, y, symbole):
			possible.append(symbole)
	return possible

def solve(solutions, grid, x, y):
	if x == 6:
		solutions.append(grid.copy())
		return
	if y == 6:
		solve(solutions, grid, x+1, 0)
		return
	possible = possible_symboles(grid, x, y)
	for symbole in possible:
		grid[y, x] = symbole
		solve(solutions, grid, x, y+1)
		grid[y, x] = 0

def generate_all_solutions():
	grid = np.zeros((6, 6), dtype=np.uint8)
	solutions = []
	solve(solutions, grid, 0, 0)
	return np.array(solutions)

def detect_grid(image):
	line_extension=5
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	binary = cv2.adaptiveThreshold(
		blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
	)
	lines = cv2.HoughLinesP(binary, rho=1, theta=np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
	if lines is not None:
		for line in lines:
			x1, y1, x2, y2 = line[0]
			dx = x2 - x1
			dy = y2 - y1
			length = np.sqrt(dx**2 + dy**2)
			nx = dx / length
			ny = dy / length
			x1_ext = int(x1 - line_extension * nx)
			y1_ext = int(y1 - line_extension * ny)
			x2_ext = int(x2 + line_extension * nx)
			y2_ext = int(y2 + line_extension * ny)
			cv2.line(binary, (x1_ext, y1_ext), (x2_ext, y2_ext), (255, 255, 255), 2)
	contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	contours = sorted(contours, key=cv2.contourArea, reverse=True)	
	
	if len(contours) == 0:
		return None, (0,0,0,0)

	for contour in contours:
		epsilon = 0.02 * cv2.arcLength(contour, True)
		approx = cv2.approxPolyDP(contour, epsilon, True)
		if len(approx) >= 4:
			grid_contour = approx
			x, y, w, h = cv2.boundingRect(grid_contour)
			if abs(w - h) < 50:
				break
	if w * h < 100000:
		return None, (0,0,0,0)
	grid = image[y:y+h, x:x+w]
	return grid, (x, y, w, h)

def detect_symbole_moon_sun(cell_image):
	gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	binary = cv2.adaptiveThreshold(
		blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
	)
	contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	contain_symbole = False
	is_sun = False
	for contour in contours:
		epsilon = 0.02 * cv2.arcLength(contour, True)
		approx = cv2.approxPolyDP(contour, epsilon, True)
		grid_contour = approx
		x, y, w, h = cv2.boundingRect(grid_contour)
		if len(approx) <= 3 or w * h >= 0.9 * cell_image.shape[0] * cell_image.shape[1]:
			continue
		if x > 0.1 * cell_image.shape[1] and y > 0.1 * cell_image.shape[0] and x+w < 0.9 * cell_image.shape[1] and y+h < 0.9 * cell_image.shape[0]:
			if cv2.isContourConvex(approx):
				is_sun = True
			contain_symbole = True
	return contain_symbole, is_sun

def detect_symbole_cross_equal(cell_image):
	gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	binary = cv2.adaptiveThreshold(
		blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
	)
	contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	contain_symbole = False
	is_cross = True
	for contour in contours:
		epsilon = 0.02 * cv2.arcLength(contour, True)
		approx = cv2.approxPolyDP(contour, epsilon, True)
		grid_contour = approx
		x, y, w, h = cv2.boundingRect(grid_contour)
		if len(approx) <= 3 or w * h >= 0.9 * cell_image.shape[0] * cell_image.shape[1]:
			continue
		if x > 0.1 * cell_image.shape[1] and y > 0.1 * cell_image.shape[0] and x+w < 0.9 * cell_image.shape[1] and y+h < 0.9 * cell_image.shape[0]:
			contain_symbole = True
			if cv2.isContourConvex(approx):
				is_cross = False
	return contain_symbole, is_cross

def process_grid_image(grid_image):
	grid_symbole = np.zeros((6, 6), dtype=np.uint32)
	link = {}
	w,h = grid_image.shape[:2]
	cell_w = w // 6
	cell_h = h // 6
	cells = []
	for i in range(6):
		for j in range(6):
			cell = grid_image[i*cell_w:(i+1)*cell_w, j*cell_h:(j+1)*cell_h]
			cells.append(cell)
	for i, cell in enumerate(cells):
		contain_symbole, is_sun = detect_symbole_moon_sun(cell)
		if contain_symbole:
			grid_symbole[i // 6, i % 6] = 1 if is_sun else 2

	lines_vertical = []
	lines_horizontal = []
	for i in range(1, 6):
		line_w = cell_w//5
		line_h = cell_h//5
		for j in range(0, 6):
			lines_vertical.append(grid_image[j*cell_h+cell_h//2-line_h:j*cell_h+cell_h//2+line_h, i*cell_w-line_w:i*cell_w+line_w])
			lines_horizontal.append(grid_image[i*cell_h-line_h:i*cell_h+line_h, j*cell_w+cell_w//2-line_w:j*cell_w+cell_w//2+line_w])

	for i, line in enumerate(lines_vertical):
		contain_symbole, is_cross = detect_symbole_cross_equal(line)
		if contain_symbole:
			if (i % 6, i // 6) not in link:
				link[(i % 6, i // 6)] = []
			link[(i % 6, i // 6)].append(((i % 6, i // 6 + 1), is_cross))
	for i, line in enumerate(lines_horizontal):
		contain_symbole, is_cross = detect_symbole_cross_equal(line)
		if contain_symbole:
			if (i // 6, i % 6) not in link:
				link[(i // 6, i % 6)] = []
			link[(i // 6, i % 6)].append(((i // 6 + 1, i % 6), is_cross))
	return grid_symbole, link

def extract_tango_grid(filename):
	grid_image = detect_grid(filename)
	if grid_image is None:
		print("No grid found.")
		return None
	return process_grid_image(grid_image)

def solution_is_valid(solution, grid_symbole, links):
	if not (solution[grid_symbole == 1] == 1).all():
		return False
	if not (solution[grid_symbole == 2] == 2).all():
		return False
	for cell in links:
		for link in links[cell]:
			if link[1]:
				if solution[cell] == solution[link[0]]:
					return False
			else:
				if solution[cell] != solution[link[0]]:
					return False
	return True

def solve_tango(solutions, grid_symbole, links):
	for solution in solutions:
		if solution_is_valid(solution, grid_symbole, links):
			return solution
	return None

def solve_puzzle(offset_x, offset_y, grid_w, grid_h, solutions, grid_symbole, links):
	global capture_flag

	solution = solve_tango(solutions, grid_symbole, links)
	if solution is not None:
		cell_w = grid_w // 6
		cell_h = grid_h // 6
		capture_flag = False
		for i in range(6):
			for j in range(6):
				if grid_symbole[i][j] != 0:
					continue
				x = offset_x + j * cell_w + cell_w // 2
				y = offset_y + i * cell_h + cell_h // 2
				for k in range(0, solution[i][j]):
					pyautogui.click(x, y, _pause=False, interval=0)

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

def load_solutions():
	try:
		return np.load("solution.npy")
	except FileNotFoundError:
		solutions = generate_all_solutions()
		np.save("solution.npy", solutions)
		return solutions

def main():
	global stop_flag
	global capture_flag
	global have_highdpi

	listener_thread = threading.Thread(target=keyboard_listener)
	listener_thread.start()
	last_x, last_y = 0, 0
	solutions = load_solutions()
	with mss.mss() as sct:
		while not stop_flag:
			screen = np.array(sct.grab(sct.monitors[0]))

			if capture_flag:
				grid_image, (x, y, w, h) = detect_grid(screen)
				if grid_image is not None:
					grid_symbole, links = process_grid_image(grid_image)
					if x == last_x and y == last_y:
						if have_highdpi:
							solve_puzzle(x//2, y//2, w//2, h//2, solutions, grid_symbole, links)
						else:
							solve_puzzle(x, y, w, h, solutions, grid_symbole, links)								
				last_x, last_y = x, y
			cv2.waitKey(1)
		cv2.destroyAllWindows()

if __name__ == "__main__":
	main()
