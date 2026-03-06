import streamlit as st
import pandas as pd
from database import init_db
from billing import get_products, add_product, save_invoice
from pdf_generator import generate_pdf
from datetime import datetime
from billing import reduce_stock
from billing import save_sale
from billing import get_current_stock
import streamlit as st
import pandas as pd
from datetime import datetime
from billing import update_product, delete_product
from billing import restore_product, get_deleted_products

from database import init_db, get_connection
from billing import (
    get_products,
    add_product,
    reduce_stock,
    save_sale,
    get_current_stock
)
from pdf_generator import generate_pdf


init_db()

st.set_page_config(
    page_title="SmartStore Pro",
    page_icon="🛒",
    layout="wide"
)


st.markdown("""
    <style>
        .main {
            background-color: #0E1117;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
            height: 3em;
            width: 100%;
            font-weight: bold;
        }
        .stMetric {
            background-color: #1E222A;
            padding: 15px;
            border-radius: 12px;
        }
        div[data-testid="stDataFrame"] {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "cart" not in st.session_state:
    st.session_state.cart = []

st.title("🛒 SmartStore Pro - GST Billing System")

menu = st.sidebar.selectbox(
    "Menu",
    ["Add Product", "Billing", "View Products", "Sales Dashboard", "Restore Products"]
)

# ================== ADD PRODUCT ==================
if menu == "Add Product":
    st.subheader("Add New Product")

    name = st.text_input("Product Name")
    price = st.number_input("Price", min_value=0.0)
    stock = st.number_input("Stock", min_value=0)

    if st.button("Add Product"):

        if not name.strip():
            st.error("Product name cannot be empty")
        elif price <= 0:
            st.error("Price must be greater than 0")
        elif stock < 0:
            st.error("Stock cannot be negative")
        else:
            add_product(name, price, stock)
            st.success("Product Added Successfully!")

# ================== VIEW PRODUCTS ==================
elif menu == "View Products":
    st.subheader("Inventory Management")

    products = get_products()

    if products:
        df = pd.DataFrame(products, columns=["ID", "Name", "Price", "Stock"])
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.subheader("✏ Edit or Delete Product")

        product_dict = {f"{p[1]} (ID:{p[0]})": p for p in products}
        selected = st.selectbox("Select Product", list(product_dict.keys()))

        selected_product = product_dict[selected]

        new_name = st.text_input("Edit Name", value=selected_product[1])
        new_price = st.number_input("Edit Price", value=float(selected_product[2]))
        new_stock = st.number_input("Edit Stock", value=int(selected_product[3]))

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Update Product"):
                update_product(selected_product[0], new_name, new_price, new_stock)
                st.success("Product Updated Successfully")
                st.rerun()

        with col2:
            if st.button("Delete Product"):
                delete_product(selected_product[0])
                st.warning("Product Deleted Successfully")
                st.rerun()

        # LOW STOCK ALERT
        low_stock = df[df["Stock"] < 5]
        if not low_stock.empty:
            st.error("⚠ Low Stock Alert!")
            st.dataframe(low_stock)

    else:
        st.warning("No products available")

# ================== dashboard ui ==============
elif menu == "Sales Dashboard":
    st.subheader("📊 Sales Dashboard")

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM sales", conn)
    conn.close()

    if df.empty:
        st.warning("No sales data available")
    else:
        total_sales = df["total_price"].sum()
        total_orders = len(df)

        col1, col2 = st.columns(2)
        col1.markdown("### 💰 Total Revenue")
        col1.metric("", f"₹{total_sales:,.2f}")

        col2.markdown("### 📦 Total Orders")
        col2.metric("", total_orders)

        st.subheader("Sales by Product")
        product_sales = df.groupby("product_name")["total_price"].sum()
        st.bar_chart(product_sales)

        st.subheader("Daily Sales Trend")
        daily_sales = df.groupby("date")["total_price"].sum()
        st.line_chart(daily_sales) 
# ================== restore product ==================
elif menu == "Restore Products":
    st.subheader("♻ Restore Deleted Products")

    deleted_products = get_deleted_products()

    if deleted_products:
        df = pd.DataFrame(deleted_products, columns=["ID", "Name", "Price", "Stock"])
        st.dataframe(df, use_container_width=True)

        product_dict = {f"{p[1]} (ID:{p[0]})": p for p in deleted_products}
        selected = st.selectbox("Select Product to Restore", list(product_dict.keys()))

        selected_product = product_dict[selected]

        if st.button("Restore Product"):
            restore_product(selected_product[0])
            st.success("Product Restored Successfully")
            st.rerun()
    else:
        st.info("No deleted products found.")
# ================== BILLING ==================
elif menu == "Billing":
    st.subheader("Generate GST Invoice")

    products = get_products()

    # LOW STOCK ALERT (Billing Page)
    low_stock_items = [p for p in products if p[3] < 5]

    if low_stock_items:
        st.warning("⚠ Some products are running low on stock!")  

    if not products:
        st.warning("Add products first")
    else:
        # Create dictionary: Name -> Full product tuple
        product_dict = {p[1]: p for p in products}

        col1, col2 = st.columns(2)

        with col1:
            selected_product_name = st.selectbox("Select Product", list(product_dict.keys()))
        with col2:
            qty = st.number_input("Quantity", min_value=1)

        if st.button("Add to Cart"):

            product = product_dict[selected_product_name]

            product_id = product[0]     # ✅ ID
            product_name = product[1]   # ✅ Name
            price = product[2]          # ✅ Price
            stock = product[3]          # ✅ Stock

            # STOCK VALIDATION
            if qty > stock:
                st.error("Not enough stock available!")
            else:
                st.session_state.cart.append({
                    "id": product_id,
                    "name": product_name,
                    "price": price,
                    "qty": qty
                })
                st.success("Added to Cart")

        # ---------------- CART DISPLAY ----------------
        if st.session_state.cart:
            st.subheader("Cart Items")

            cart_df = pd.DataFrame(st.session_state.cart)
            st.markdown("### 🛍 Current Cart")
            st.dataframe(
                cart_df.drop(columns=["id"]),
                use_container_width=True,
                hide_index=True
            )

            subtotal = sum(item["price"] * item["qty"] for item in st.session_state.cart)

            GST_RATE = 18
            gst_amount = subtotal * GST_RATE / 100
            total = subtotal + gst_amount

            st.markdown(f"**Subtotal:** ₹{subtotal:.2f}")
            st.markdown(f"**GST (18%):** ₹{gst_amount:.2f}")
            st.markdown(
                f"""
                <div style='
                    background-color:#1E222A;
                    padding:20px;
                    border-radius:15px;
                    text-align:center;
                    font-size:24px;
                    font-weight:bold;
                '>
                    Grand Total: ₹{total:,.2f}
                </div>
                """,
                unsafe_allow_html=True
            )

            customer = st.text_input("Customer Name")

            if st.button("Generate Invoice"):

                # 🔒 CUSTOMER NAME VALIDATION
                if not customer.strip():
                    st.error("Customer name is required")
                    st.stop()

                stock_error = False

                # 🔎 Double-check stock before reducing
                for item in st.session_state.cart:
                    current_stock = get_current_stock(item["id"])

                    if item["qty"] > current_stock:
                        st.error(f"Not enough stock for {item['name']}! Available: {current_stock}")
                        stock_error = True

                # ✅ Only reduce if everything is valid
                if not stock_error:

                    for item in st.session_state.cart:
                        reduce_stock(item["id"], item["qty"])
                        save_sale(
                            item["id"],
                            item["name"],
                            item["qty"],
                            item["price"] * item["qty"]
                        )

                    # ✅ Generate PDF
                    invoice_number = datetime.now().strftime("%Y%m%d%H%M%S")

                    pdf_file = generate_pdf(
                        invoice_number,
                        customer,
                        st.session_state.cart,
                        subtotal,
                        gst_amount,
                        total
                    )

                    st.success("Invoice Generated Successfully")

                    # ✅ Download Button
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="📥 Download Invoice PDF",
                            data=f,
                            file_name=f"Invoice_{invoice_number}.pdf",
                            mime="application/pdf"
                        )

                    st.session_state.cart = []
                if st.button("Clear Cart"):
                    st.session_state.cart = []
                    st.warning("Cart Cleared")
st.markdown("---")
st.markdown(
    "<center>© 2026 SmartStore Pro | Developed by Raj Patanvadiya</center>",
    unsafe_allow_html=True
)
