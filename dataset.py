"""
Shapes dataset.
"""
from itertools import product

import torch
from torch.utils.data import Dataset
from torchvision.transforms import ToTensor
from PIL import Image, ImageDraw


SHAPES = ['square', 'circle', 'triangle']
COLORS = ['red', 'green', 'blue', 'white']
POSITIONS = ['top-left', 'top-right', 'bottom-left', 'bottom-right']


class ShapeDataset(Dataset):
    """Dataset class for shapes."""

    def __init__(self, image_size=64, transform=None, augmentation_transform=None, n_augmentations=8, device=None):
        self.image_size = image_size
        self.targets_info = []
        self.images = []
        self.targets = []

        if transform is None:
          transform = ToTensor()
        
        _eye = torch.eye(len(list(product(SHAPES, COLORS, [True, False], POSITIONS))))
        for class_id, (shape, color, fill, position) in enumerate(product(SHAPES, COLORS, [True, False], POSITIONS)):
            img = generate_shape_image(shape=shape, color=color, fill=fill, position=position, image_size=image_size)
            _target_info = dict(shape=shape, color=color, fill=fill, position=position)
            _target_ohe = _eye[class_id]
            self.images.append(transform(img))
            self.targets_info.append(_target_info)
            self.targets.append(_target_ohe)

            if augmentation_transform is not None:
              for _ in range(n_augmentations):
                  self.images.append(augmentation_transform(img))
                  self.targets.append(_target_ohe)


        self.images = torch.stack(self.images, dim=0)
        self.targets = torch.stack(self.targets, dim=0)

        if device is not None:
            self.images.to(device)
            self.targets.to(device)
            

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        return self.images[idx], self.targets[idx]


def generate_shape_image(shape, color, fill, position, image_size=64):
    """
    Generates an image with the specified shape, color, fill, and position.

    Parameters:
        shape (str): The shape to draw ('square', 'circle', 'triangle').
        color (str): The color of the shape ('red', 'green', 'blue', 'white').
        fill (bool): Whether the shape is filled (True) or empty (False).
        position (str): The quadrant to place the shape ('top-left', 'top-right', 'bottom-left', 'bottom-right').
        image_size (int): The size of the image in pixels (default is 64).

    Returns:
        Image object: The generated image.
    """
    # Validate inputs
    assert shape in SHAPES, f"Invalid shape. Must be 'square', 'circle', or 'triangle'. Got: {shape}"
    assert color in COLORS, f"Invalid color. Must be 'red', 'green', 'blue', or 'white'. Got: {color}"
    assert position in POSITIONS, f"Invalid position. Got: {position}"

    # Map color names to RGB values
    color_map = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'white': (255, 255, 255),
    }

    shape_color = color_map[color]

    # Create a blank black image
    image = Image.new("RGB", (image_size, image_size), "gray")
    draw = ImageDraw.Draw(image)

    # Define the shape's bounding box
    quarter_size = image_size // 2
    padding = image_size // 8

    if position == 'top-left':
        box = (padding, padding, quarter_size, quarter_size)
    elif position == 'top-right':
        box = (quarter_size, padding, image_size - padding, quarter_size)
    elif position == 'bottom-left':
        box = (padding, quarter_size, quarter_size, image_size - padding)
    elif position == 'bottom-right':
        box = (quarter_size, quarter_size, image_size - padding, image_size - padding)

    # Draw the specified shape
    if shape == 'square':
        if fill:
            draw.rectangle(box, fill=shape_color)
        else:
            draw.rectangle(box, outline=shape_color, width=2)
    elif shape == 'circle':
        if fill:
            draw.ellipse(box, fill=shape_color)
        else:
            draw.ellipse(box, outline=shape_color, width=2)
    elif shape == 'triangle':
        if position == 'top-left':
            points = [(padding, quarter_size), (quarter_size, padding), (padding, padding)]
        elif position == 'top-right':
            points = [(quarter_size, padding), (image_size - padding, padding), (image_size - padding, quarter_size)]
        elif position == 'bottom-left':
            points = [(padding, image_size - padding), (quarter_size, image_size - padding), (padding, quarter_size)]
        elif position == 'bottom-right':
            points = [(quarter_size, image_size - padding), (image_size - padding, image_size - padding), (image_size - padding, quarter_size)]

        if fill:
            draw.polygon(points, fill=shape_color)
        else:
            draw.polygon(points, outline=shape_color, width=2)

    return image
