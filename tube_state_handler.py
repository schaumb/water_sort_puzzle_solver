import cv2
import adb_connector


class Task:
    to_color_char = {
        (88, 218, 241): 'y',
        (35, 42, 197): 'r',
        (147, 43, 114): 'p',
        (66, 140, 232): 'o',
        (7, 74, 126): 'b',
        (195, 46, 58): 'd',
        (229, 163, 85): 'c',
        (51, 101, 16): 'g',
        (124, 214, 98): 'q',
        (101, 100, 99): 'e',
        (14, 150, 120): 'l',
        (123, 94, 234): 'm'
    }

    def __init__(self):
        self.tube_positions = []
        self.sh = None

    def __enter__(self):
        self.sh = adb_connector.Shell().__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sh.__exit__(exc_type, exc_val, exc_tb)

    def get_start_state(self):
        self.tube_positions.clear()
        img = self.sh.get_an_image()
        topcrop = img.shape[0] // 5
        img = img[topcrop:img.shape[0] * 5 // 6]
        for c in reversed(cv2.findContours(
                cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 60, 255, cv2.THRESH_BINARY)[1],
                cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]):
            x, y, w, h = cv2.boundingRect(c)
            self.tube_positions.append((x + w // 2, y + h // 2 + topcrop))
            elem_height = round(h / 4.5)
            yield map(lambda i: Task.to_color_char.get(tuple(img[y + h - elem_height * i - elem_height // 2,
                                                                 x + w // 2]), ' '), reversed(range(4)))

    def apply_solution(self, sol_list):
        wait_from = []
        wait_to = []
        wait_count = 1
        for i, j, c in sol_list:
            if i in wait_from or i in wait_to or j in wait_from:
                self.sh.sleep(wait_count)
                wait_from.clear()
                wait_count = 1
            self.sh.touch(self.tube_positions[i])
            self.sh.touch(self.tube_positions[j])
            wait_from.append(i)
            wait_to.append(j)
            wait_count = max(wait_count - 1, c)

        self.sh.sleep(0.3)

        tube_count = len(self.tube_positions)
        self.sh.touch(self.tube_positions[tube_count // 2 + tube_count % 2 + tube_count // 2 // 2 + tube_count // 2 % 1])

        self.sh.sleep(3)