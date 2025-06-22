from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QTimer


class SnowmanDrawing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 400)
        self.max_parts = 7
        self.parts_remaining = self.max_parts
        self.animating = False
        self.melt_step = 0
        self.current_melting = None
        self.part_scales = [1.0] * self.max_parts  # scale of each part (1.0 = full size)
        self.part_y_offset = [0] * self.max_parts

    def set_wrong_guesses(self, count):
        if self.animating:
            return  # prevent overlapping animations

        melt_index = self.max_parts - count
        if melt_index < 0 or melt_index >= self.max_parts:
            return

        self.current_melting = melt_index
        self.animating = True
        self.melt_step = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_melt)
        self.timer.start(40)  # every 40ms

    def animate_melt(self):
        if self.melt_step < 10:
            # shrink part by 10% each time
            self.part_scales[self.current_melting] -= 0.1
            self.part_y_offset[self.current_melting] += 6
            self.melt_step += 1
            self.update()
        else:
            # Done melting
            self.part_scales[self.current_melting] = 0.0
            self.part_y_offset[self.current_melting] = 0
            self.animating = False
            self.current_melting = None
            self.timer.stop()
            self.update()
        
        # self.melt_sound.play()
        

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.black, 2.5)
        painter.setPen(pen)
        center_x = 150
        painter.setBrush(Qt.white)  # Solid white snowballs


        def draw_scaled_ellipse(x, y, w, h, scale, offset_y):
            if scale > 0:
                x = int(center_x - w * scale / 2 + x)
                y = int(y + (1 - scale) * h + offset_y)
                w = int(w * scale)
                h = int(h * scale)
                painter.drawEllipse(x, y, w, h)

        def draw_scaled_line(x1, y1, x2, y2, scale, offset_y):
            if scale > 0:
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                x1 = int(cx + (x1 - cx) * scale)
                y1 = int(cy + (y1 - cy) * scale + offset_y)
                x2 = int(cx + (x2 - cx) * scale)
                y2 = int(cy + (y2 - cy) * scale + offset_y)
                painter.drawLine(x1, y1, x2, y2)


        if self.part_scales[0] > 0:
            draw_scaled_ellipse(0, 200, 140, 140, self.part_scales[0], self.part_y_offset[0])  # Base
        if self.part_scales[1] > 0:
            draw_scaled_ellipse(0, 120, 110, 110, self.part_scales[1], self.part_y_offset[1])  # Middle
        if self.part_scales[2] > 0:
            draw_scaled_ellipse(0, 60, 80, 80, self.part_scales[2], self.part_y_offset[2])    # Head

        if self.part_scales[3] > 0:
            draw_scaled_line(center_x - 40, 170, center_x - 90, 140, self.part_scales[3], self.part_y_offset[3])  # Left arm
        if self.part_scales[4] > 0:
            draw_scaled_line(center_x + 40, 170, center_x + 90, 140, self.part_scales[4], self.part_y_offset[4])  # Right arm
        if self.part_scales[5] > 0:
            # Face
            painter.drawEllipse(
                int(center_x - 15),
                int(90 + self.part_y_offset[5]),
                int(5 * self.part_scales[5]),
                int(5 * self.part_scales[5])
            )
            painter.drawEllipse(
                int(center_x + 10),
                int(90 + self.part_y_offset[5]),
                int(5 * self.part_scales[5]),
                int(5 * self.part_scales[5])
            )

            painter.drawArc(int(center_x - 15), int(105 + self.part_y_offset[5]), 30, 15, 0, -180 * 16)
        if self.part_scales[6] > 0:
            painter.drawLine(int(center_x - 40), int(65 + self.part_y_offset[6]), int(center_x + 40), 65)  # Hat brim
            painter.drawRect(int(center_x - 25), int(25 + self.part_y_offset[6]), 50, 40)  # Hat top
        
    def reset(self):
        self.parts_remaining = self.max_parts
        self.animating = False
        self.current_melting = None
        self.part_scales = [1.0] * self.max_parts
        self.update()