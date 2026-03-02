import BarCode
import pandas as pd
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, Paragraph
from io import BytesIO


styles = getSampleStyleSheet()
blue = colors.HexColor("#191970")
c1 = colors.HexColor("#FFF8E1")
c2 = colors.HexColor("#FFE0B2")

pink = colors.HexColor("#FF00B1")
Blue2 = colors.HexColor("#0019FF")
white = colors.white
black = colors.black
red = colors.red


# Optimize the slogo.png
slogo_img = Image.open("slogo.png")
slogo_img.thumbnail((100, 100)) # Resize to 100x100 pixels
slogo_buffer = BytesIO()
slogo_img.save(slogo_buffer, format='PNG', quality=85)
slogo_buffer.seek(0)
slogo_reader = ImageReader(slogo_buffer)

# img_sign = Image.open("sign.png")
# img_sign.thumbnail((150, 150)) # Compress
# sign_buffer = BytesIO()
# img_sign.save(sign_buffer, format='PNG', quality=95) # Save as PNG (for transparency)
# sign_buffer.seek(0)
# sign_reader = ImageReader(sign_buffer)

# img_bg = Image.open("bg.png")
# img_bg.thumbnail((1016, 638)) # Compress
# bg_buffer = BytesIO()
# img_bg.save(bg_buffer, format='PNG') # Save as PNG (for transparency)
# bg_buffer.seek(0)
# bg_reader = ImageReader(bg_buffer)


def draw_gradient_background(c, x, y, w, h, top_color, bottom_color):
    steps = 100
    for i in range(steps):
        r = top_color.red + (bottom_color.red - top_color.red) * i / steps
        g = top_color.green + (bottom_color.green - top_color.green) * i / steps
        b = top_color.blue + (bottom_color.blue - top_color.blue) * i / steps
        c.setFillColorRGB(r, g, b)
        c.rect(x, y + (i * h / steps), w, h / steps, stroke=0, fill=1)


def draw_horizontal_gradient(c, x, y, w, h, left_color, right_color):
    """Draw a smooth left-to-right gradient background"""
    steps = 100  # More steps = smoother gradient
    for i in range(steps):
        ratio = i / steps
        r = left_color.red + (right_color.red - left_color.red) * ratio
        g = left_color.green + (right_color.green - left_color.green) * ratio
        b = left_color.blue + (right_color.blue - left_color.blue) * ratio
        c.setFillColorRGB(r, g, b)
        c.rect(x + (i * w / steps), y, w / steps, h, stroke=0, fill=1)

def draw_passport_photo(c, img_path, x, y, w=1.667*cm, h=2.5*cm, pad=1,sign=True,border=0):
    """Crop, resize, compress photo and draw"""
    try:
        img = Image.open(img_path)
        iw, ih = img.size
        target_ratio = 2 / 3  # fixed 2:3 vertical

        img_ratio = iw / ih
        if img_ratio > target_ratio:
            # Image too wide → crop width
            new_width = int(ih * target_ratio)
            left = (iw - new_width) // 2
            img = img.crop((left, 0, left + new_width, ih))
        else:
            # Image too tall → crop height
            new_height = int(iw / target_ratio)
            top = (ih - new_height) // 2
            img = img.crop((0, top, iw, top + new_height))

        # Resize the image to a smaller dimension
        img.thumbnail((300, 450))

        # Save the image to a memory buffer as a compressed JPEG
        buffer = BytesIO()
        img.save(buffer, format='PNG', quality=85) # Quality can be adjusted from 1 (worst) to 95 (best)
        buffer.seek(0)

        # Convert to ImageReader and draw at passport size
        img_reader = ImageReader(buffer)
        c.drawImage(img_reader, x, y, width=w, height=h, mask='auto')

        if(border!=0):
            # 🔲 Draw black frame around photo
            c.setLineWidth(border)
            c.setStrokeColorRGB(0, 0, 0)  # black
            c.rect(x, y, w, h, stroke=1, fill=0)

        # Draw signature below photo
        if(sign):
            c.drawImage("sign.png", x, y-pad*cm, width=w, height=1*cm, mask='auto')

    except Exception as e:
        print(f"Error loading photo {img_path}: {e}")

def Landscape(c, x, y, w=8.6*cm, h=5.4*cm, data=None):
    """Draw one ID card at given position using Table for alignment"""
    normal = styles["Normal"]
    normal.fontSize = 7
    normal.leading = 9

    bold = styles["Normal"]
    bold.fontSize = 7
    bold.leading = 9
    bold.textColor = blue


    # Bottom orange strip
    c.setFillColorRGB(1, 0.5, 0)  # orange
    c.rect(x, y, w, 1.7*1.063*cm, stroke=0, fill=1)
    c.setFillColor(black)

    # Border
    c.setStrokeColor(black)
    c.setLineWidth(1) 
    c.rect(x, y, w, h)

    # Photo
    if data and "PhotoPath" in data and pd.notna(data["PhotoPath"]):
        draw_passport_photo(c, data["PhotoPath"], x+(0.2*1.063)*cm, y+h-2.35*cm-(0.15*1.174)*cm, (1.7*1.063)*cm, (2*1.174)*cm)
    address = Paragraph(data.get("Address1", ""),normal)
    # Table content: labels and values
    info_data = [
        ["Name:", data.get("FirstName", "")],
        ["Address:", address, ],
        ["Mobile No:", data.get("Mobile", "")],
        ["Sem/Med:", data.get("Semester", "")],
        ["Subject:", data.get("Subject", "")],
        ["Roll No:", data.get("RollNumber", "")]
    ]

    table = Table(info_data, colWidths=[1.3*cm, w-4.1*cm])  
    # subtract photo space (3 cm approx)

    table.setStyle(TableStyle([
        ("FONT", (0,0), (-1,-1), "Helvetica", 7),
        ("ALIGN", (0,0), (0,-1), "LEFT"),   # Labels left
        ("ALIGN", (1,0), (1,-1), "LEFT"),   # Values left
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TEXTCOLOR", (1,0), (1,-1), blue),
        ("TEXTCOLOR", (0,0), (0,-1), red),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("LEFTPADDING", (0,0), (-1,-1), 2),
        ("RIGHTPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 1),
        ("FONTNAME", (-1,-1), (-1,-1), "Helvetica-Bold",8),
    ]))

    # Wrap and draw table next to photo
    # Wrap table to get size
    tw, th = table.wrapOn(c, w, h)
    # Fix anchor so table starts from top, not bottom
    table.drawOn(c, x+2.6*cm, y+h - th) # 2.6cm margin for photo

    # Barcode text
    barcodeText = data.get("BarCodeNumber", "not-found")
    c.setFont("Helvetica", 7)
    c.drawString(x+1*cm, y+0.5*cm, barcodeText)
    
    BarCode.encode(barcodeText,"barcode\\"+barcodeText)
    c.drawImage("barcode\\"+barcodeText+".png", x +0.5*cm , y+0.93*cm, 3.2*cm , 0.5*cm, preserveAspectRatio=False)


    # Logo
    # if data and "LogoPath" in data and pd.notna(data["LogoPath"]):
    try:
        # Define image position and size
        img_x = x + w - (4.3 * 1.063) * cm
        img_y = y + 0.2 * cm
        img_w = (4 * 1.055) * cm
        img_h = (1.2 * 1.174) * cm

        # Draw cyan border (rectangle outline)
        c.setStrokeColorRGB(0, 1, 1)     # Cyan color
        c.setLineWidth(1.5)              # Border thickness
        c.drawImage("logo.png", img_x, img_y, img_w, img_h, preserveAspectRatio=True)
        c.rect(img_x, img_y, img_w, img_h, stroke=1, fill=0)
        # Draw image inside
    except:
        pass

def Portrait(c, x, y, w=8.6*cm, h=5.4*cm, data=None,hcolor1=c1,hcolor2=c2):
    """Draw one ID card at given position using Table for alignment"""
    normal = styles["BodyText"]
    normal.fontSize = 7
    normal.textColor = black
    normal.leading = 9


    c.setLineWidth(1) 

    # Bottom box
    c.setStrokeColor(black)
    c.rect(x, y, w, 2.5*1.063*cm)
    c.setFillColor(black)

    # Border
    c.rect(x, y, w, h)

    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(red)
    c.drawString(x+(w/2)-0.7*cm, y+h-1.5821*cm, str(data.get("CourseYear","")))
    c.setFillColor(black)

    # Photo
    if data and "PhotoPath" in data and pd.notna(data["PhotoPath"]):
        draw_passport_photo(c, data["PhotoPath"], x+(1.5*1.063)*cm, y+h-2.65*cm-(1.2*1.174)*cm, (1.7*1.063)*cm, (2*1.174)*cm, pad=0.6)
    
    # Barcode text
    barcodeText = data.get("BarCodeNumber", "not-found")
    c.setFont("Helvetica", 6)
    c.drawString(x+(2*.973)*cm, y+3.28*cm, barcodeText)
    
    BarCode.encode(barcodeText,"barcode\\"+barcodeText)
    c.drawImage("barcode\\"+barcodeText+".png", x+1*cm, y+h-2.7*cm-(2*1.174)*cm, (3*1.063)*cm, (0.5*1.174)*cm, preserveAspectRatio=False)

    text_x = x+(.077)*cm
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(blue)
    c.drawString(text_x, y+2.79*cm, f"{data["Semester"]}")
    c.drawString(x+w/2+.6*cm, y+2.79*cm, f"Roll No:{data["RollNumber"]}")
    c.setFillColor(black)

    c.setFillColor(pink)
    c.drawString(text_x, y+2.3*cm, f"SUBJECT: {data["Subject"]}")
    c.setFillColor(black)
    
    available_width = w - .077*cm*2 
    available_height = 2 * cm 

    paragraph = Paragraph(f'<h4><b><font color="#0019FF">{data["FirstName"]} {data["Gender"]}</font><br/>ABC ID: {str(data.get("ABC ID","")).split('.')[0]} <br/>(M): {data["Mobile"]}</b></h4><br/>{data["Address1"]}', normal)
    px,py = paragraph.wrapOn(c, available_width, available_height)
    paragraph.drawOn(c,text_x,y-py+2.3*cm-4)
    # c.drawString(text_x, y+2.3*cm - 12, f"{data["FirstName"]} {data["Gender"]}\n")
    # Logo
    # if data and "LogoPath" in data and pd.notna(data["LogoPath"]):
    try:
        # Define image position and size
        img_w = 1.05 * cm
        img_h = 1.05 * cm
        img_x = x + .5 * cm
        img_y = y + 7.45 * cm

        draw_gradient_background(c, x+0.5,y+7.4*cm-2,w-1,img_h+.2*cm,hcolor1,hcolor2)

        c.drawImage("slogo.png", x+.25*cm, img_y, img_w, img_h, preserveAspectRatio=True, mask='auto')
        # c.drawImage(slogo_reader, x+.25*cm, img_y, img_w, img_h, preserveAspectRatio=True, mask='auto')

        justify = ParagraphStyle(
            'Justified',
            parent=normal,      # inherit base font etc.
            alignment=TA_JUSTIFY
        )
        justify.fontSize = 7.5
        paragraph = Paragraph(f"<b>BHAVAN'S SHETH R. A. COLLEGE OF ARTS AND COMMERCE AHMEDABAD</b>", justify)
        px,py = paragraph.wrapOn(c, w-2*cm, 2*cm)
        paragraph.drawOn(c,img_x+1*cm,img_y+1)

    except Exception as e:
        print(f"Error in Portrait function while drawing logo: {e}")

def PortraitDesigned(c, x, y, w=8.6*cm, h=5.4*cm, data=None):
    c.drawImage("bg.png", x, y, width=w, height=h, preserveAspectRatio=False)

    normal = styles["BodyText"]
    normal.fontSize = 7
    normal.textColor = white
    normal.leading = 9

    c.setLineWidth(1) 
    # Border
    c.rect(x, y, w, h)

    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(red)
    c.drawString(x+(w/2)-0.7*cm, y+h-1.34*cm, str(data.get("CourseYear","")))
    c.setFillColor(black)
    # Photo
    if data and "PhotoPath" in data and pd.notna(data["PhotoPath"]):
        draw_passport_photo(c, data["PhotoPath"], x+(1.5*1.063)*cm, y+h-2.65*cm-(1.174)*cm, (1.7*1.063)*cm, (2*1.174)*cm, pad=0.6, sign=False,border=0.75)

    c.drawImage("trans-sign.png", x+3.463*cm, y+0.75*cm, width=(1.7*1.063)*cm, height=0.5*cm, mask='auto')
    c.drawString( x+3.463*cm, y+0.5*cm ,"Principal Sign")
    
    # Barcode text
    barcodeText = data.get("BarCodeNumber", "not-found")
    c.setFont("Helvetica", 6)
    c.drawString(x+(1.25*.973)*cm, y+0.25*cm, barcodeText)
    c.setFillColor(white)
    
    BarCode.encode(barcodeText,"barcode\\"+barcodeText)
    c.drawImage("barcode\\"+barcodeText+".png", x+0.25*cm, y+0.5*cm, (3*1.063)*cm, (0.5*1.174)*cm, preserveAspectRatio=False)

    text_x = x+(.077)*cm+.077*cm
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(white)
    c.drawString(text_x, y+4.29*cm, f"{data["Semester"]}")
    c.drawString(x+w/2+0.2*cm, y+4.29*cm, f"Roll No:{data["RollNumber"]}")
    c.setFillColor(white)

    c.setFillColor(pink)
    c.drawString(text_x, y+4.29*cm-10, f"Subject: {data["Subject"]}")
    c.setFillColor(white)
    
    available_width = w - .077*cm*3 
    available_height = 2 * cm 

    paragraph = Paragraph(f'<h4><b><font color="#000000">{data["FirstName"]} {data["Gender"]}</font><br/>ABC ID: {str(data["ABC ID"]).split('.')[0]} <br/>Mobile No: {data["Mobile"]}</b></h4><br/>Address: {str(data["Address1"]).upper()}', normal)
    px,py = paragraph.wrapOn(c, available_width, available_height)
    paragraph.drawOn(c,text_x,y-py+4.2*cm-10)

def PortraitDesigned2(c, x, y, w=8.6*cm, h=5.4*cm, data=None):
    c.drawImage("bg2.png", x, y, width=w, height=h, preserveAspectRatio=False)

    normal = styles["BodyText"]
    normal.fontSize = 7
    normal.textColor = white
    normal.leading = 9

    c.setLineWidth(1) 
    # Border
    c.rect(x, y, w, h)

    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(blue)
    c.drawString(x+(w/2)-0.7*cm, y+h-1.34*cm, str(data.get("CourseYear","")))
    c.setFillColor(black)
    # Photo
    if data and "PhotoPath" in data and pd.notna(data["PhotoPath"]):
        draw_passport_photo(c, data["PhotoPath"], x+(1.5*1.063)*cm, y+h-2.65*cm-(1.174)*cm, (1.7*1.063)*cm, (2*1.174)*cm, pad=0.6, sign=False,border=0.75)

    c.drawImage("trans-sign.png", x+3.463*cm, y+0.75*cm, width=(1.7*1.063)*cm, height=0.5*cm, mask='auto')
    c.drawString( x+3.463*cm, y+0.5*cm ,"Principal Sign")
    
    # Barcode text
    barcodeText = data.get("BarCodeNumber", "not-found")
    c.setFont("Helvetica", 6)
    c.drawString(x+(1.25*.973)*cm, y+0.25*cm, barcodeText)
    c.setFillColor(white)
    
    BarCode.encode(barcodeText,"barcode\\"+barcodeText)
    c.drawImage("barcode\\"+barcodeText+".png", x+0.25*cm, y+0.5*cm, (3*1.063)*cm, (0.5*1.174)*cm, preserveAspectRatio=False)

    text_x = x+(.077)*cm+.077*cm
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(white)
    c.drawString(text_x, y+4.29*cm-5, f"{data["Semester"]}")
    c.drawString(x+w/2, y+4.29*cm-5, f"Roll No:{data["RollNumber"]}")
    c.setFillColor(white)

    c.setFillColor(pink)
    c.drawString(text_x, y+4.29*cm-10-5, f'SUBJECT: {data["Subject"]}')
    c.setFillColor(white)
    
    available_width = w - .077*cm*3 
    available_height = 2 * cm 

    paragraph = Paragraph(f'<h4><b><font color="#000000">{data["FirstName"]} {data["Gender"]}</font><br/>ABC ID: {str(data["ABC ID"]).split('.')[0]} <br/>Mobile No: {data["Mobile"]}</b></h4><br/>Address: <font color="#0019ff">{data["Address1"]}</font>'.upper(), normal)
    px,py = paragraph.wrapOn(c, available_width, available_height)
    paragraph.drawOn(c,text_x,y-py+4.2*cm-10-5)
