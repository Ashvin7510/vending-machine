import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Vending Machine",
    page_icon="🧃",
    layout="wide"
)

prices_inr = [
    124.50, 83.00, 53.95, 83.00, 166.00,
    249.00, 207.50, 145.25, 99.60, 207.50,
    83.00, 166.00, 124.50, 103.75, 145.25,
    290.50, 166.00, 249.00, 186.75, 207.50,
    124.50, 103.75
]

items = [
    "Soda", "Chips", "Candy", "Water", "Juice",
    "Energy Drink", "Protein Bar", "Sparkling Water",
    "Granola Bar", "Cookies", "Gummy Bears", "Ice Tea",
    "Lemonade", "Chocolate Bar", "Potato Skins", "Beef Jerky",
    "Pre tzels", "Almonds", "Trail Mix", "Coconut Water",
    "Herbal Tea", "Root Beer"
]

initial_stock = [5] * len(items)

if "stock" not in st.session_state:
    st.session_state.stock = initial_stock.copy()

if "cart" not in st.session_state:
    st.session_state.cart = []

if "checkout" not in st.session_state:
    st.session_state.checkout = False


def get_total_cost():
    return sum(row["price"] * row["qty"] for row in st.session_state.cart)


def add_to_cart(item_name, new_qty):
    if new_qty <= 0:
        st.warning("Quantity must be at least 1.")
        return

    idx = items.index(item_name)
    current_stock = st.session_state.stock[idx]

    existing_row = None
    for row in st.session_state.cart:
        if row["item"] == item_name:
            existing_row = row
            break

    existing_qty_in_cart = existing_row["qty"] if existing_row else 0
    total_available_for_item = current_stock + existing_qty_in_cart

    if total_available_for_item == 0:
        st.error(f"❗ {item_name} is sold out.")
        return

    if new_qty > total_available_for_item:
        st.error(f"❗ Only {total_available_for_item} {item_name}(s) available.")
        return

    st.session_state.stock[idx] = total_available_for_item - new_qty

    if existing_row:
        existing_row["qty"] = new_qty
        st.success(f"✅ Updated {item_name} quantity to {new_qty}.")
    else:
        st.session_state.cart.append({
            "item": item_name,
            "price": prices_inr[idx],
            "qty": new_qty
        })
        st.success(f"✅ Added {new_qty} {item_name}(s) to cart.")


def reset_all():
    st.session_state.stock = initial_stock.copy()
    st.session_state.cart = []
    st.session_state.checkout = False


def highlight_zero(s):
    return ['background-color: #ff4b4b' if v == 0 else '' for v in s]


with st.sidebar:
    st.title("🧃 Vending Panel")
    st.write("Manage and monitor the vending machine.")

    total_products = len(items)
    total_stock_left = sum(st.session_state.stock)
    cart_items = sum(row["qty"] for row in st.session_state.cart)

    st.metric("Item Types", total_products)
    st.metric("Total Stock Left", total_stock_left)
    st.metric("Items in Cart", cart_items)

    st.markdown("---")
    if st.button("🔄 Reset Machine"):
        reset_all()
        st.success("Machine reset successfully!")

    st.markdown("---")
    with st.expander("ℹ️ How it works"):
        st.write(
            "1. Choose an item and quantity.\n"
            "2. Click **Add / Update Cart**.\n"
            "3. If you enter more than available, it will tell you.\n"
            "4. Proceed to payment.\n"
            "5. Get confirmation and change."
        )

st.markdown(
    "<h1 style='text-align: center;'>Smart Vending Machine 🧃</h1>",
    unsafe_allow_html=True
)

st.write("")
st.write("Select items, add to your cart, and simulate payment in INR.")
st.markdown("---")

st.subheader("🧾 Items Available")

df = pd.DataFrame({
    "Item": items,
    "Price (₹)": prices_inr,
    "Stock": st.session_state.stock,
})
df.index = df.index + 1
df_style = df.style.apply(highlight_zero, subset=["Stock"])

st.dataframe(df_style, use_container_width=True)
st.markdown("---")

st.subheader("🛒 Add Items to Cart")

col_left, col_right = st.columns([2, 1])

with col_left:
    item_selected = st.selectbox("Choose an item:", items)

idx_sel = items.index(item_selected)
current_stock_sel = st.session_state.stock[idx_sel]
existing_row_sel = next((r for r in st.session_state.cart if r["item"] == item_selected), None)
existing_qty_sel = existing_row_sel["qty"] if existing_row_sel else 0
total_available_sel = current_stock_sel + existing_qty_sel

with col_right:
    qty = st.number_input(
        "Quantity (final in cart)",
        min_value=1,
        value=existing_qty_sel if existing_qty_sel > 0 else 1,
        step=1
    )

st.caption(f"Available for **{item_selected}**: {total_available_sel} piece(s).")

if st.button("➕ Add / Update Cart"):
    add_to_cart(item_selected, qty)

st.markdown("---")

st.subheader("📦 Your Cart")

if not st.session_state.cart:
    st.info("Your cart is empty. Add something from the list above.")
else:
    cart_df = pd.DataFrame(st.session_state.cart)
    cart_df["Total (₹)"] = cart_df["price"] * cart_df["qty"]
    cart_df = cart_df.rename(columns={
        "item": "Item",
        "price": "Price (₹)",
        "qty": "Quantity"
    })
    cart_df.index = cart_df.index + 1

    st.table(cart_df)

    total_cost = get_total_cost()
    st.write(f"### 💰 Total cost: ₹{total_cost:.2f}")

    if not st.session_state.checkout:
        if st.button("➡️ Proceed to Payment"):
            st.session_state.checkout = True

st.markdown("---")

if st.session_state.checkout and st.session_state.cart:
    st.subheader("💳 Payment")

    total_cost = get_total_cost()
    st.write(f"Total amount to pay: **₹{total_cost:.2f}**")

    amount = st.number_input(
        "Insert money (₹)",
        min_value=0.0,
        step=10.0,
        value=0.0,
        format="%.2f"
    )

    if st.button("✅ Pay"):
        if amount <= 0:
            st.error("Please insert a positive amount.")
        elif amount < total_cost:
            st.error(f"Insufficient amount. You still need ₹{total_cost - amount:.2f}.")
        else:
            change = amount - total_cost
            st.success(f"Purchase complete! 🎉 Change returned: ₹{change:.2f}")
            st.balloons()
            st.session_state.cart = []
            st.session_state.checkout = False
