from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import pandas as pd
from reportlab.lib import colors
import Draw
import pandas as pd

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

def create_pdf_4x2(df, output_file="id_cards.pdf",c1=None,c2=None):
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
        
        if row['CourseName'] in ["B.COM","B.A"]:
            if c1==None:
                Draw.Portrait(c, x_pos, y_pos, card_w, card_h, row.to_dict())
            else:
                Draw.Portrait(c, x_pos, y_pos, card_w, card_h, row.to_dict(),c1,c2)

        elif row['CourseName'] in ["B.S.(BBA)"]:
            Draw.PortraitDesigned(c, x_pos, y_pos, card_w, card_h, row.to_dict())
        elif row['CourseName'] in ["MA I", "M COM-I"]:
            Draw.PortraitDesigned2(c, x_pos, y_pos, card_w, card_h, row.to_dict())
        else:
            pass
            # Draw.Portrait(c, x_pos, y_pos, card_w, card_h, row.to_dict())

        if card_index == cards_per_page - 1:
            c.showPage()
    c.save()
    print(f"✅ PDF created: {output_file}")

# import os
# import pandas as pd

# files = [i for i in os.listdir() if i.endswith(".xlsx")]
# # arr = list({"M1663", "M432", "M305", "M364", "M029", "M885", "M621", "M1011", "M806", "M201", "M885", "M621", "M1011", "M806", "M223", "M305", "M323", "M029", "M201", "M1663", "M432", "M364"})

# arr = "M201,M173,M689,M887,M885,M621,M1011,M806,M223,M305,M029,M201,M1663,M432,M364".split(",")
# arr.sort()

# # 1. Use a list to collect DataFrames (much faster than appending in a loop)
# df_list = []
# for file in files:
#     if not file.startswith("C:\\Users\\$"):
#         ndf = pd.read_excel(file)
#         df_list.append(ndf)

# # 2. Combine all dataframes at once
# if df_list:
#     df = pd.concat(df_list, ignore_index=True)
# else:
#     df = pd.DataFrame()

# # 3. Correct the filtering logic
# # Use .isin() to check if values in a column exist in your list
# df_filtered = df[df["RollNumber"].isin(arr)]
# df_filtered["RollNumber_Numeric"] = df_filtered["RollNumber"].str[1:].astype(int)
# df_filtered.sort_values(by="RollNumber_Numeric", inplace=True, ascending=True)
# df_filtered.reset_index(drop=True, inplace=True)

# print(df_filtered)
# print(f"unfiltered rows: {len(df)}")
# print(f"Filtered rows: {len(df_filtered)}")
# ba = df_filtered[df_filtered["CourseName"] == "MA I"]
# print(ba['RollNumber'])
# print(f"Items in list: {len(arr)}")
# # print(f"Items in list: {arr}")
# # print(f"Items in df: {df_filtered['RollNumber']}")

# create_pdf_4x2(df_filtered, "Remaining2.pdf")