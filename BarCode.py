from barcode.writer import ImageWriter
from pyzbar.pyzbar import decode
from PIL import Image, ImageOps
import barcode

def decode(filepath):
    # Load barcode image
    img = Image.open(filepath)

    # Decode
    decoded_objects = decode(img)

    for obj in decoded_objects:    
        print("Type:", obj.type)
        print("Decoded Number:", obj.data.decode("utf-8"))
    
def encode(number,filepath):
    # Choose barcode format (EAN13, Code128, etc.)
    ean = barcode.get("Code128", number, writer=ImageWriter())

    # Save as image
    ean.save(filepath,{
        "write_text": False,   # 🚫 hide number below
        "quiet_zone": 0,       # optional: reduce white border
        "module_width": 0.6,   # width of each bar (increase = stretch wider)
        "module_height": 40,   # height of barcode
    })
    img = Image.open(filepath+".png")
    bordered = ImageOps.expand(img, border=(20,0,20,0), fill="white")  
    bordered.save(filepath+".png")

    print("Barcode saved as:", filepath)

# encode("202526K510","202526K510")
# decode("my_barcode.png")
