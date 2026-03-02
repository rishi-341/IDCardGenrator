from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import pandas as pd
from reportlab.lib import colors
import Draw

def create_pdf_2x5(df, output_file="id_cards.pdf"):
    """Create PDF with ID cards in 2x5 layout (10 per page)"""
    width, height = A4
    c = canvas.Canvas(output_file, pagesize=A4)

    # Card size
    card_w = 8.6 * cm
    card_h = 5.4 * cm

    # Margins/gaps
    x_margin = 1.75 * cm
    y_margin = 0.5 * cm
    x_gap = 0.25 * cm
    y_gap = 0.25 * cm

    cards_per_row = 2
    cards_per_col = 5
    cards_per_page = cards_per_row * cards_per_col

    for idx, row in df.iterrows():
        card_index = idx % cards_per_page
        col = card_index % cards_per_row
        row_index = card_index // cards_per_row

        x_pos = x_margin + col * (card_w + x_gap)
        y_pos = height - y_margin - (row_index + 1) * card_h - row_index * y_gap

        Draw.Landscape(c, x_pos, y_pos, card_w, card_h, row.to_dict())

        if card_index == cards_per_page - 1:
            c.showPage()

    c.save()
    print(f"✅ PDF created: {output_file}")

def create_pdf_4x2(df, output_file="id_cards.pdf",index=0,c1=None,c2=None):
    """Create PDF with ID cards in 2x5 layout (10 per page)"""
    width, height = landscape(A4)
    c = canvas.Canvas(output_file, pagesize=landscape(A4))

    # Card size
    card_h = 8.6 * cm
    card_w = 5.4 * cm

    # Margins/gaps
    x_margin = 0.2 * cm
    y_margin = 0.2 * cm
    x_gap = 0.2 * cm
    y_gap = 0.2 * cm

    cards_per_row = 5
    cards_per_col = 2
    cards_per_page = cards_per_row * cards_per_col
    i=0
    for idx, row in df.iterrows():
        card_index = idx % cards_per_page
        col = card_index % cards_per_row
        row_index = card_index // cards_per_row

        x_pos = x_margin + col * (card_w + x_gap)
        y_pos = height - y_margin - (row_index + 1) * card_h - row_index * y_gap

        i+=1
        # if i==25:
        #     index=1
        # if i==26:
        #     index=2
        # if i==1:
        #     Draw.Portrait(c, x_pos, y_pos, card_w, card_h, row.to_dict())
        # else:
        #     Draw.PortraitDesigned(c, x_pos, y_pos, card_w, card_h, row.to_dict())

        if index==0:
            if c1==None:
                Draw.Portrait(c, x_pos, y_pos, card_w, card_h, row.to_dict())
            else:
                Draw.Portrait(c, x_pos, y_pos, card_w, card_h, row.to_dict(),c1,c2)

        elif index==1:
            Draw.PortraitDesigned(c, x_pos, y_pos, card_w, card_h, row.to_dict())
        elif index==2:
            Draw.PortraitDesigned2(c, x_pos, y_pos, card_w, card_h, row.to_dict())
        else:
            pass
            # Draw.Portrait(c, x_pos, y_pos, card_w, card_h, row.to_dict())

        if card_index == cards_per_page - 1:
            c.showPage()
    c.save()
    print(f"✅ PDF created: {output_file}")

# -------------------
# Example usage
# create_pdf_4x2(df,"BBA.pdf",1)
# df = pd.read_excel("FINAL B COM SEM 1 06 11 2025.xlsx")
# df2 = pd.read_excel("BBA SEM 1 ID CARD 2025 26.xlsx")
# df["ABC ID"].fillna("-",inplace=True)
# df["CourseYear"].fillna("",inplace=True)
# create_pdf_4x2(df[:150],"BA-1.pdf",0)
# create_pdf_4x2(df[150:300],"BA-2.pdf",0)
# create_pdf_4x2(df[0:10],"Mcom-1.pdf",2)
# data = df[75:85]
# filtered = df[df["RollNumber"] == "M432"]

# # Take all rows from index 300 onward
# sliced = df2[df2["RollNumber"] == "M1663"]

# Combine both and remove duplicates (optional)
# new_df = pd.concat([filtered, sliced]).drop_duplicates().reset_index(drop=True)

# create_pdf_4x2(new_df,"Remaining.pdf",0)
# create_pdf_4x2(df[200:400],"Bcom-2.pdf",0)    
# create_pdf_4x2(df[400:465],"Bcom-3.pdf",0)
# data = df[df["ABC ID"]==None]


# b1 = colors.HexColor("#00efff")
# b2 = colors.HexColor("#00bfff")
# create_pdf_4x2(df,"BJMS.pdf",0,b1,b2)