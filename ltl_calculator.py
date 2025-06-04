# LTL Charge Calculator - Web Version using Streamlit
import streamlit as st
import base64
from io import BytesIO
from PIL import Image
import requests

st.set_page_config(page_title="Narchin Transport - LTL Freight Calculator", layout="wide")

# --------------------
# Constants
# --------------------
CHINA_RATE = 0.2
BAKU_RATE = 0.3
TBILISI_RATE = 0.35
CHINA_CUSTOM_FEE = 70
KZ_TRANSIT_FEE = 200
LOCAL_HANDLING_FEE = 100

CHINA_CITIES = [
    "Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu",
    "Chongqing", "Tianjin", "Hangzhou", "Nanjing", "Wuhan",
    "Xi'an", "Dongguan", "Suzhou", "Shenyang", "Qingdao",
    "Dalian", "Zhengzhou", "Jinan", "Fuzhou", "Changsha"
]

DESTINATIONS = ["Baku, Azerbaijan", "Tbilisi, Georgia"]

# --------------------
# Calculation Logic
# --------------------
def calculate_charge(length, width, height, weight):
    volume_cbm = (length / 100) * (width / 100) * (height / 100)
    volumetric_weight = volume_cbm * 333
    chargeable_weight = max(weight, volumetric_weight)
    return volume_cbm, volumetric_weight, chargeable_weight

def calculate_total_cost(pallets, destination):
    total_actual_weight = 0
    total_volume_cbm = 0
    total_chargeable_weight = 0

    for pallet in pallets:
        vol, vol_weight, ch_weight = calculate_charge(
            pallet['length'], pallet['width'], pallet['height'], pallet['weight']
        )
        vol *= pallet['quantity']
        vol_weight *= pallet['quantity']
        ch_weight *= pallet['quantity']
        total_volume_cbm += vol
        total_actual_weight += pallet['weight'] * pallet['quantity']
        total_chargeable_weight += ch_weight

    cost_to_horgos = total_chargeable_weight * CHINA_RATE
    cost_from_horgos = total_chargeable_weight * (BAKU_RATE if destination == "Baku, Azerbaijan" else TBILISI_RATE)

    total_cost = cost_to_horgos + cost_from_horgos + CHINA_CUSTOM_FEE + KZ_TRANSIT_FEE + LOCAL_HANDLING_FEE

    return {
        "Total Actual Weight (kg)": round(total_actual_weight, 2),
        "Total Volume (CBM)": round(total_volume_cbm, 2),
        "Chargeable Weight (kg)": round(total_chargeable_weight, 2),
        "Cost China to Horgos (USD)": round(cost_to_horgos, 2),
        "Cost Horgos to Destination (USD)": round(cost_from_horgos, 2),
        "China Customs Fee (USD)": CHINA_CUSTOM_FEE,
        "KZ Transit Fee (USD)": KZ_TRANSIT_FEE,
        "Local Handling Fee (USD)": LOCAL_HANDLING_FEE,
        "Total Cost (USD)": round(total_cost, 2)
    }

# --------------------
# PDF Generator
# --------------------
def generate_invoice(data, origin, destination):
    from fpdf import FPDF
    import tempfile

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add logo
    logo_url = "https://www.narchin.az/images/logo-narchin.png"
    try:
        r = requests.get(logo_url)
        if r.status_code == 200:
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tmp_file.write(r.content)
            tmp_file.close()
            pdf.image(tmp_file.name, x=10, y=8, w=40)
    except Exception as e:
        pass

    pdf.set_fill_color(0, 102, 153)
    pdf.set_text_color(255)
    pdf.cell(200, 10, "Narchin Transport - Freight Invoice", ln=True, align="C", fill=True)
    pdf.set_text_color(0)
    pdf.ln(10)
    pdf.cell(200, 10, f"From: {origin} to {destination}", ln=True)

    for key, val in data.items():
        pdf.cell(200, 10, f"{key}: {val}", ln=True)

    # Footer with website
    pdf.set_y(-20)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(128)
    pdf.cell(0, 10, "Thank you for choosing Narchin Transport | www.narchin.az", ln=True, align="C")

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --------------------
# UI
# --------------------
# Header with logo and color
st.markdown("""
    <style>
    .main-header {
        text-align:center;
        background-color:#006699;
        padding:20px;
        border-radius:10px;
        color:white;
    }
    </style>
    <div class='main-header'>
        <h1>Narchin Transport</h1>
        <h3>LTL Freight Calculator (China → Horgos → Baku/Tbilisi)</h3>
    </div>
""", unsafe_allow_html=True)

with st.form("ltl_form"):
    st.subheader("Shipment Details")
    origin_city = st.selectbox("Pickup City in China", CHINA_CITIES)
    destination_city = st.selectbox("Delivery City", DESTINATIONS)

    st.markdown("### Pallet Details")
    pallet_count = st.number_input("Number of Different Pallet Types", min_value=1, value=1)
    pallets = []

    for i in range(int(pallet_count)):
        st.markdown(f"#### Pallet {i+1}")
        length = st.number_input(f"Length (cm) - Pallet {i+1}", min_value=0.0, value=120.0)
        width = st.number_input(f"Width (cm) - Pallet {i+1}", min_value=0.0, value=80.0)
        height = st.number_input(f"Height (cm) - Pallet {i+1}", min_value=0.0, value=100.0)
        weight = st.number_input(f"Weight per Unit (kg) - Pallet {i+1}", min_value=0.0, value=200.0)
        quantity = st.number_input(f"Number of Units - Pallet {i+1}", min_value=1, value=1)

        pallets.append({
            "length": length,
            "width": width,
            "height": height,
            "weight": weight,
            "quantity": quantity
        })

    submitted = st.form_submit_button("Calculate")

if submitted:
    result = calculate_total_cost(pallets, destination_city)
    st.subheader("Calculation Result")
    for key, value in result.items():
        st.write(f"{key}: {value}")

    invoice_buffer = generate_invoice(result, origin_city, destination_city)
    b64 = base64.b64encode(invoice_buffer.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Narchin_Invoice.pdf">📥 Download Quote as PDF</a>'
    st.markdown(href, unsafe_allow_html=True)
