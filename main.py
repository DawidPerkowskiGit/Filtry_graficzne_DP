import PIL as pillow
from PIL import Image, ImageTk
from tkinter import *
import shutil
import numpy as np
import math
import cv2

WIDTH = 600
HEIGHT = 400

FILTER_WINDOW_SIZE = 3

DEBUG = False


#Rozmiar dwuwyamirowego wektora maski, MASK_RADIUS = 3 -> 3x3
MASK_RADIUS = 2

def backup_image():
    shutil.copy("backup.jpg", "image.jpg")

def open_image_to_display():
    #var = pillow.Image.open("image.jpg")
    var = ImageTk.PhotoImage(pillow.Image.open("image.jpg"))
    return var



# def image_open_to_edit():
#     image = pillow.Image.open("image.jpg")
#     loaded_image = image.load()
#     return loaded_image

def open_image_to_edit():
    image = pillow.Image.open("image.jpg")
    #image = image.load()
    return image


def image_resize():
    size = WIDTH, HEIGHT

    file = "image.jpg"

    image = pillow.Image.open(file)
    image.thumbnail(size)
    image.save(file, "JPEG")

def create_new_image(image):
    img = pillow.Image.new("RGB", [image.width, image.height], color="white")
    return img

class FilteringImages:

    def __init__(self):
        self.root = Tk()
        self.root.geometry(str(WIDTH+ 100)+"x"+str(HEIGHT+100))

        # self.frame = Frame(self.root, width=WIDTH, height=HEIGHT)
        # self.frame.pack()
        # self.frame.place(anchor='nw')

        self.image_to_display = open_image_to_display()
        self.label_image = Label(self.root, image=self.image_to_display)
        self.label_image.pack()

###############
        #
        # self.canvas = Canvas(width=WIDTH, height=HEIGHT, bg='white')
        # self.canvas.pack()
        #
        #
        # self.photo = open_image_to_display()
        # self.img = self.canvas.create_image(150, 100, image=self.photo)
        #
        #

####3333333

        self.btn_frame = Frame(self.root)
        self.btn_frame.pack(side=BOTTOM)

        self.avaraging_filter_button = Button(self.btn_frame, text="Filtr wygładzający", command=self.avaraging_filter)
        self.avaraging_filter_button.grid(row=0, column=0, sticky=S + E)
        self.median_filter_button = Button(self.btn_frame, text="Filtr medianowy", command=self.median_filter)
        self.median_filter_button.grid(row=0, column=1, sticky=S + E)
        self.sobel_filter_button = Button(self.btn_frame, text="Filtr wykrywania krawędzi", command=lambda: self.sobel())
        self.sobel_filter_button.grid(row=0, column=2, sticky=S + E)
        self.dyletation_filter_button = Button(self.btn_frame, text="Dylatacja", command=lambda: self.dyletation())
        self.dyletation_filter_button.grid(row=0, column=3, sticky=S + E)
        self.erosion_filter_button = Button(self.btn_frame, text="Erozja", command=lambda: self.erosion())
        self.erosion_filter_button.grid(row=0, column=4, sticky=S + E)
        self.erosion_filter_button = Button(self.btn_frame, text="Przeładuj", command=lambda: self.backup_and_reload())
        self.erosion_filter_button.grid(row=0, column=5, sticky=S + E)

        self.mask = []

        self.image_to_edit = open_image_to_edit()

        self.new_image = 0

        self.current_points_to_process = PointsToProcessDataStructure()

        self.root.mainloop()



    def avaraging_filter(self):

        self.mask = ([1, 1, 1], [1, 1, 1], [1, 1, 1])
        self.setup_mask_weights()

        self.image_to_edit = open_image_to_edit()

        image_width, image_height = self.image_to_edit.width, self.image_to_edit.height

        self.new_image = create_new_image(self.image_to_edit)

        for x in range(MASK_RADIUS - 1, image_width - MASK_RADIUS + 1):
            for y in range(MASK_RADIUS - 1, image_height - MASK_RADIUS + 1):
                self.load_pixels_to_process(x, y)
                new_rgb_colors = self.avaraging_filter_caclulate()
                self.change_colors_of_pixel([x, y], new_rgb_colors)

        print("Filtrowanie uśredniające zakończone")
        self.copy_border_to_new_image()
        self.image_save()
        self.reload_image()

    def setup_mask_weights(self):
        sum = 0
        for i in range(MASK_RADIUS + 1):
            for j in range(MASK_RADIUS + 1):
                sum = sum + self.mask[i][j]
        for i in range(MASK_RADIUS + 1):
            for j in range(MASK_RADIUS + 1):
                self.mask[i][j] = self.mask[i][j] / sum

    def avaraging_filter_caclulate(self):
        RGB = [0, 0, 0]
        for i in range((MASK_RADIUS + 1) * (MASK_RADIUS + 1)):
            for color in range(3):
                RGB[color] = RGB[color] + self.current_points_to_process.RGB_colors[i][color] * self.mask[int(i/(MASK_RADIUS+1))][math.floor(i % (MASK_RADIUS+1))]

        for i in range(3):
            RGB[i] = int(RGB[i])
        return RGB

    def change_colors_of_pixel(self, coordinates, colors):
        #self.image_to_edit.load()[coordinates[0], coordinates[1]] = (colors[0], colors[1], colors[2])
        self.new_image.load()[coordinates[0], coordinates[1]] = (colors[0], colors[1], colors[2])

    def copy_border_to_new_image(self):
        old = self.image_to_edit.load()
        #new = self.new_image.load()
        for w in range(self.image_to_edit.width - 1):
            self.new_image.load()[w, 0] = old[w, 0]
            self.new_image.load()[w, self.image_to_edit.height - 1] = old[w, self.image_to_edit.height - 1]
        for h in range(self.image_to_edit.height - 1):
            self.new_image.load()[0, h] = old[0, h]
            self.new_image.load()[self.image_to_edit.width-1, h] = old[self.image_to_edit.width - 1, h]


    def image_save(self):
        #self.image_to_edit.save("image.jpg")
        self.new_image.save("image.jpg")

    def reload_image(self):
        self.image_to_display = open_image_to_display()
        self.label_image.config(image=self.image_to_display)

    def median_filter(self):
        self.image_to_edit = open_image_to_edit()

        image_width, image_height = self.image_to_edit.width, self.image_to_edit.height

        self.new_image = create_new_image(self.image_to_edit)

        for x in range(MASK_RADIUS - 1, image_width - MASK_RADIUS + 1):
            for y in range(MASK_RADIUS - 1, image_height - MASK_RADIUS + 1):
                self.load_pixels_to_process(x, y)
                new_rgb_colors = self.median_filter_calculate()
                self.change_colors_of_pixel([x, y], new_rgb_colors)

        print("Filtrowanie medianowe zakończone")
        self.copy_border_to_new_image()
        self.image_save()
        self.reload_image()

    def median_filter_calculate(self):
        RGB = [0, 0, 0]
        grey_scale = []
        dict = {}
        vector_size = (MASK_RADIUS + 1) * (MASK_RADIUS + 1)
        for i in range(vector_size):
            grey_scale.append((self.current_points_to_process.RGB_colors[i][0] + self.current_points_to_process.RGB_colors[i][1] + self.current_points_to_process.RGB_colors[i][2]) / 3)
            dict[i] = [self.current_points_to_process.RGB_colors[i], grey_scale[i]]
        grey_scale.sort()

        middle_point = math.floor(vector_size / 2)
        middle_point_greyscale_value = grey_scale[middle_point]

        for i in range(vector_size):
            if (dict[i][1] == middle_point_greyscale_value):
                RGB = dict[i][0]
                break

        return RGB

    def sobel(self):
        intesivity = 2
        self.mask = ([-intesivity, -2 * intesivity, -intesivity], [0, 0, 0], [intesivity, 2 * intesivity, intesivity])
        self.image_to_edit = open_image_to_edit()

        image_width, image_height = self.image_to_edit.width, self.image_to_edit.height

        self.new_image = create_new_image(self.image_to_edit)

        for x in range(MASK_RADIUS - 1, image_width - MASK_RADIUS + 1):
            for y in range(MASK_RADIUS - 1, image_height - MASK_RADIUS + 1):
                self.load_pixels_to_process(x, y)
                new_rgb_colors = self.sobel_filter_calculate()
                self.limit_rgb_values(new_rgb_colors)
                self.change_colors_of_pixel([x, y], new_rgb_colors)

        self.image_save()
        self.mask = ([-intesivity, 0, intesivity], [-2 * intesivity, 0, 2 * intesivity], [-intesivity, 0, intesivity])

        for x in range(MASK_RADIUS - 1, image_width - MASK_RADIUS - 1):
            for y in range(MASK_RADIUS - 1, image_height - MASK_RADIUS - 1):
                self.load_pixels_to_process(x, y)
                new_rgb_colors = self.sobel_filter_calculate()
                self.limit_rgb_values(new_rgb_colors)
                self.change_colors_of_pixel([x, y], new_rgb_colors)

        print("Wykrywanie krawędzi zakończone")
        self.copy_border_to_new_image()
        self.image_save()
        self.reload_image()

    def limit_rgb_values(self, new_rgb_colors):
        for i in range(MASK_RADIUS + 1):
            if new_rgb_colors[i] > 255:
                new_rgb_colors[i] = 255
            elif new_rgb_colors[i] < 0:
                new_rgb_colors[i] = 0

    def sobel_filter_calculate(self):
        RGB = [0, 0, 0]
        grey_scale = 0
        for i in range((MASK_RADIUS + 1) * (MASK_RADIUS + 1)):
            grey_scale = (self.current_points_to_process.RGB_colors[i][0] + self.current_points_to_process.RGB_colors[i][1] + self.current_points_to_process.RGB_colors[i][2]) / 3
            RGB[0] = RGB[0] + grey_scale * self.mask[int(i / (MASK_RADIUS + 1))][math.floor(i % (MASK_RADIUS + 1))]
        RGB[2] = RGB[1] = RGB[0]
        for i in range(3):
            RGB[i] = int(RGB[i])
        return RGB

    def dyletation(self):
        pass

    def erosion(self):
        pass

    def load_pixels_to_process(self, x_coordinate_of_filtered_point, y_coordinate_of_filtered_point):

        acess_pixel = self.image_to_edit.load()
        #acess_pixel = self.image_to_edit

        colors = []
        coordiantes = []
        offset = MASK_RADIUS - 1
        for i in range(2 * MASK_RADIUS - 1):
            for j in range(2 * MASK_RADIUS - 1):
                x = x_coordinate_of_filtered_point + i - offset
                y = y_coordinate_of_filtered_point + j - offset
                colors.append(acess_pixel[x,y])
                if (DEBUG):
                    print("color")
                    print(acess_pixel[x, y])
                #coordiantes.append([x, y])
                if (DEBUG):
                    print("coordiantes")
                    print([x, y])
                    print("--------")

        if (DEBUG):
            print(colors)
            print(coordiantes)
        self.current_points_to_process.setColors(colors)
        #self.current_points_to_process.setCoordinates(coordiantes)

    def backup_and_reload(self):
        backup_image()
        image_resize()
        self.reload_image()

class PointsToProcessDataStructure:
    def __init__(self):
        self.RGB_colors = 0
        self.pixel_coordinates = 0

    def setColors(self, colors):
        self.RGB_colors = colors

    # def setCoordinates(self, coordiantes):
    #     self.pixel_coordinates = coordiantes

    def getColors(self):
        return self.RGB_colors

    # def getCoordinates(self):
    #     return self.pixel_coordinates





if __name__ == '__main__':
    backup_image()
    image_resize()
    FilteringImages()
