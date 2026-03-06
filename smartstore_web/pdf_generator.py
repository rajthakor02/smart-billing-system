from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
import os


def generate_pdf(invoice_number, customer, cart, subtotal, gst_amount, total):

    if not os.path.exists("invoices"):
        os.makedirs("invoices")

    file_path = f"invoices/Invoice_{invoice_number}.pdf"

    doc = SimpleDocTemplate(file_path, pagesize=pagesizes.A4)
    elements = []

    styles = getSampleStyleSheet()

    elements.append(Paragraph(f"Invoice No: {invoice_number}", styles["Normal"]))
    elements.append(Paragraph(f"Customer: {customer}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Table Data
    data = [["Product", "Price", "Qty", "Total"]]

    for item in cart:
        data.append([
            item["name"],
            f"₹{item['price']}",
            item["qty"],
            f"₹{item['price'] * item['qty']}"
        ])

    data.append(["", "", "Subtotal", f"₹{subtotal:.2f}"])
    data.append(["", "", "GST (18%)", f"₹{gst_amount:.2f}"])
    data.append(["", "", "Grand Total", f"₹{total:.2f}"])

    table = Table(data)
    table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    elements.append(table)

    doc.build(elements)

    return file_path   # ✅ VERY IMPORTANT