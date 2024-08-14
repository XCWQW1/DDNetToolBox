import io

from PIL import ImageOps, Image
from PyQt5.QtGui import QImage, QPixmap


def crop_and_generate_image(img):
    """来自DDNetDiscordBot"""
    image = img

    image_body_shadow = image.crop((96, 0, 192, 96))
    image_feet_shadow_back = image.crop((192, 64, 255, 96))
    image_feet_shadow_front = image.crop((192, 64, 255, 96))
    image_body = image.crop((0, 0, 96, 96))
    image_feet_front = image.crop((192, 32, 255, 64))
    image_feet_back = image.crop((192, 32, 255, 64))

    # default eyes
    image_default_left_eye = image.crop((64, 96, 96, 128))
    image_default_right_eye = image.crop((64, 96, 96, 128))

    # evil eyes
    image_evil_l_eye = image.crop((96, 96, 128, 128))
    image_evil_r_eye = image.crop((96, 96, 128, 128))

    # hurt eyes
    image_hurt_l_eye = image.crop((128, 96, 160, 128))
    image_hurt_r_eye = image.crop((128, 96, 160, 128))

    # happy eyes
    image_happy_l_eye = image.crop((160, 96, 192, 128))
    image_happy_r_eye = image.crop((160, 96, 192, 128))

    # surprised eyes
    image_surprised_l_eye = image.crop((224, 96, 255, 128))
    image_surprised_r_eye = image.crop((224, 96, 255, 128))

    def resize_image(image, scale):
        width, height = image.size
        new_width = int(width * scale)
        new_height = int(height * scale)
        return image.resize((new_width, new_height))

    image_body_resized = resize_image(image_body, 0.66)
    image_body_shadow_resized = resize_image(image_body_shadow, 0.66)

    image_left_eye = resize_image(image_default_left_eye, 0.8)
    image_right_eye = resize_image(image_default_right_eye, 0.8)
    image_right_eye_flipped = ImageOps.mirror(image_right_eye)

    image_evil_l_eye = resize_image(image_evil_l_eye, 0.8)
    image_evil_r_eye = resize_image(image_evil_r_eye, 0.8)
    image_evil_r_eye_flipped = ImageOps.mirror(image_evil_r_eye)

    image_hurt_l_eye = resize_image(image_hurt_l_eye, 0.8)
    image_hurt_r_eye = resize_image(image_hurt_r_eye, 0.8)
    image_hurt_r_eye_flipped = ImageOps.mirror(image_hurt_r_eye)

    image_happy_l_eye = resize_image(image_happy_l_eye, 0.8)
    image_happy_r_eye = resize_image(image_happy_r_eye, 0.8)
    image_happy_r_eye_flipped = ImageOps.mirror(image_happy_r_eye)

    image_surprised_l_eye = resize_image(image_surprised_l_eye, 0.8)
    image_surprised_r_eye = resize_image(image_surprised_r_eye, 0.8)
    image_surprised_r_eye_flipped = ImageOps.mirror(image_surprised_r_eye)

    def create_tee_image(image_left_eye, image_right_eye_flipped):
        tee = Image.new("RGBA", (96, 64), (0, 0, 0, 0))

        tee.paste(image_body_shadow_resized, (16, 0))
        tee.paste(image_feet_shadow_back.convert("RGB"), (8, 30), image_feet_shadow_back)
        tee.paste(image_feet_shadow_front.convert("RGB"), (24, 30), image_feet_shadow_front)
        tee.paste(image_feet_back.convert("RGB"), (8, 30), image_feet_back)
        tee.paste(image_body_resized.convert("RGB"), (16, 0), image_body_resized)
        tee.paste(image_feet_front.convert("RGB"), (24, 30), image_feet_front)

        tee.paste(image_left_eye.convert("RGB"), (39, 18), image_left_eye)
        tee.paste(image_right_eye_flipped.convert("RGB"), (47, 18), image_right_eye_flipped)

        return tee

    tee_images = {
        'default': create_tee_image(image_left_eye, image_right_eye_flipped),
        'evil': create_tee_image(image_evil_l_eye, image_evil_r_eye_flipped),
        'hurt': create_tee_image(image_hurt_l_eye, image_hurt_r_eye_flipped),
        'happy': create_tee_image(image_happy_l_eye, image_happy_r_eye_flipped),
        'surprised': create_tee_image(image_surprised_l_eye, image_surprised_r_eye_flipped)
    }
    return tee_images


def draw_tee(file: str) -> QImage:
    """绘制TEE"""
    image = Image.open(file)
    width, height = image.size

    # 检查图像是否为256x128，如果不是则进行缩放
    if width != 256 or height != 128:
        canvas = Image.new('RGBA', (256, 128))
        image = image.resize((256, 128))
        canvas.paste(image, (0, 0))
        image = canvas

    processed_images = crop_and_generate_image(image)

    final_image = Image.new('RGBA', (96, 96), )
    final_image.paste(processed_images['default'], (-3, 0))

    byte_io = io.BytesIO()
    final_image.save(byte_io, format='PNG')
    byte_data = byte_io.getvalue()

    qimage = QImage.fromData(byte_data)

    return QPixmap.fromImage(qimage)