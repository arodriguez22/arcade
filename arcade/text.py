# --- BEGIN TEXT FUNCTIONS # # #

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from arcade.sprite import Sprite
from arcade.arcade_types import Color


class Text:
    def __init__(self):
        self.size = (0, 0)
        self.text_sprite_list = None


def draw_text(text: str,
              start_x: float, start_y: float,
              color: Color,
              font_size: float=12,
              width: int=0,
              align="left",
              font_name=('Calibri', 'Arial'),
              bold: bool=False,
              italic: bool=False,
              anchor_x="left",
              anchor_y="baseline",
              rotation: float=0
              ):

    """

    Args:
        :text: Text to display.
        :start_x: x coordinate of top left text point.
        :start_y: y coordinate of top left text point.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.

    Example:

    >>> import arcade
    >>> arcade.open_window(800, 600, "Drawing Example")
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_text("Text Example", 250, 300, arcade.color.BLACK, 10)
    >>> arcade.draw_text("Text Example", 250, 300, (0, 0, 0, 100), 10)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """

    # Scale the font up, so it matches with the sizes of the old code back
    # when pyglet drew the text.
    font_size *= 1.25

    # Text isn't anti-aliased, so we'll draw big, and then shrink
    scale_up = 5
    scale_down = 5

    font_size *= scale_up

    # If the cache gets too large, dump it and start over.
    if len(draw_text.cache) > 5000:
        draw_text.cache = {}

    key = f"{text}{color}{font_size}{width}{align}{font_name}{bold}{italic}"
    if key in draw_text.cache:
        label = draw_text.cache[key]
        text_sprite = label.text_sprite_list[0]

        if anchor_x == "left":
            text_sprite.center_x = start_x + text_sprite.width / 2
        elif anchor_x == "center":
            text_sprite.center_x = start_x
        elif anchor_x == "right":
            text_sprite.right = start_x
        else:
            raise ValueError(f"anchor_x should be 'left', 'center', or 'right'. Not '{anchor_x}'")

        if anchor_y == "top":
            text_sprite.center_y = start_y - text_sprite.height / 2
        elif anchor_y == "center":
            text_sprite.center_y = start_y
        elif anchor_y == "bottom" or anchor_y == "baseline":
            text_sprite.bottom = start_y
        else:
            raise ValueError(f"anchor_x should be 'left', 'center', or 'right'. Not '{anchor_y}'")

        text_sprite.angle = rotation

        label.text_sprite_list.update_positions()
    else:
        label = Text()

        # Figure out the font to use
        font = None

        # Font was specified with a string
        if isinstance(font_name, str):
            try:
                font = PIL.ImageFont.truetype(font_name, int(font_size))
            except OSError:
                pass

            if font is None:
                try:
                    font = PIL.ImageFont.truetype(font_name + ".ttf", int(font_size))
                except OSError:
                    pass

        # We were instead given a list of font names, in order of preference
        if font is not None:
            for font_string_name in font_name:
                try:
                    font = PIL.ImageFont.truetype(font_string_name, int(font_size))
                except OSError:
                    pass

                if font is None:
                    try:
                        font = PIL.ImageFont.truetype(font_string_name + ".ttf", int(font_size))
                    except OSError:
                        pass

                if font is not None:
                    break

        # Default font if no font
        if font is None:
            font_names = ("arial.ttf",
                          "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
                          '/System/Library/Fonts/SFNSDisplay.ttf')
            for font_string_name in font_names:
                try:
                    font = PIL.ImageFont.truetype(font_string_name, int(font_size))
                    break
                except OSError:
                    pass

        # This is stupid. We have to have an image to figure out what size
        # the text will be when we draw it. Of course, we don't know how big
        # to make the image. Catch-22. So we just make a small image we'll trash
        text_image_size = (10, 10)
        image = PIL.Image.new("RGBA", text_image_size)
        draw = PIL.ImageDraw.Draw(image)

        # Get size the text will be
        text_image_size = draw.multiline_textsize(text, font=font)

        # Create image of proper size
        text_height = text_image_size[1]
        text_width = text_image_size[0]

        image_start_x = 0
        if width == 0:
            width = text_image_size[0]
        else:
            # Wait! We were given a field width.
            if align == "center":
                # Center text on given field width
                field_width = width * scale_up
                text_image_size = field_width, text_height
                image_start_x = (field_width - text_width) // 2
                width = field_width
            else:
                image_start_x = 0

        # If we draw a y at 0, then the text is drawn with a baseline of 0,
        # cutting off letters that drop below the baseline. This shoves it
        # up a bit.
        image_start_y = - font_size * scale_up * 0.03
        image = PIL.Image.new("RGBA", text_image_size)
        draw = PIL.ImageDraw.Draw(image)
        draw.multiline_text((image_start_x, image_start_y), text, color, align=align, font=font)
        image = image.resize((width // scale_down, text_height // scale_down), resample=PIL.Image.LANCZOS)

        text_sprite = Sprite()
        text_sprite.image = image
        text_sprite.texture_name = key
        text_sprite.width = image.width
        text_sprite.height = image.height

        if anchor_x == "left":
            text_sprite.center_x = start_x + text_sprite.width / 2
        elif anchor_x == "center":
            text_sprite.center_x = start_x
        elif anchor_x == "right":
            text_sprite.right = start_x
        else:
            raise ValueError(f"anchor_x should be 'left', 'center', or 'right'. Not '{anchor_x}'")

        if anchor_y == "top":
            text_sprite.center_y = start_y + text_sprite.height / 2
        elif anchor_y == "center":
            text_sprite.center_y = start_y
        elif anchor_y == "bottom" or anchor_y == "baseline":
            text_sprite.bottom = start_y
        else:
            raise ValueError(f"anchor_x should be 'left', 'center', or 'right'. Not '{anchor_y}'")

        text_sprite.angle = rotation

        from arcade.sprite_list import SpriteList
        label.text_sprite_list = SpriteList()
        label.text_sprite_list.append(text_sprite)

        draw_text.cache[key] = label

    label.text_sprite_list.draw()


draw_text.cache = {}
