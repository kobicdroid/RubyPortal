import streamlit as st

# 1. Page Config
st.set_page_config(page_title="RSC Portal - Maintenance", page_icon="🚧")

# 2. Main Message
st.title("🚧 Under Maintenance")
st.subheader("We're upgrading your experience!")

st.write("""
The **Ruby Springfield College Portal** is currently undergoing scheduled maintenance 
to serve you better. We are updating our systems and will be back online shortly.
""")

# 3. The Image (Using your suggested style)
st.image("https://images.unsplash.com/photo-1584824486509-112e4181ff6b?q=80&w=500", caption="Improving our digital home...")

st.divider()

# 4. Support Info
st.info("📩 For urgent inquiries, please contact the Admin Office or email us at sumilogics@gmail.com")

st.caption("© 2026 Ruby Springfield College | Technical Team")
