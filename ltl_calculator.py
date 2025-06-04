import streamlit as st
from fpdf import FPDF
from io import BytesIO
import math

# ------------------ CONFIGURATION ------------------
CHINA_CITIES = [
    "Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu",
    "Tianjin", "Hangzhou", "Wuhan", "Chongqing", "Nanjing",
    "Xi'an", "Suzhou", "Shenyang", "Qingdao", "Dalian",
    "Zhengzhou", "Jinan", "Changsha", "Kunming", "Harbin"
]

DESTINATIONS = {
    "Baku, Azerbaijan": 0.3,
    "Tbilisi, Georgia": 0.35
}

CHINA_TO_HORGOS_RATE = 0.2
CHINA_CUSTOMS_FEE = 70
KZ_TRANSIT_FEE = 200
LOCAL_HANDLING_FEE = 100

def calculate_chargeable_weight(length, width, height, weight):
    volume_cbm = (length * width * height) / 1000000
    chargeable_weight = max(weight, volume_cbm * 333)
    return weight, volume_cbm, chargeable_weight

def calculate_total(pallets, origin_city, destination, insurance_rate, cargo_value):
    total_weight = 0
    total_volume = 0
    total_chargeable_weight = 0

    for pallet in pallets:
        weight, volume, chargeable_weight = calculate_chargeable_weight(
            pallet["length"], pallet["width"], pallet["height"], pallet["weight"]
        )
        total_weight += weight
        total_volume += volume
        total_chargeable_weight += chargeable_weight

    cost_china_to_horgos = total_chargeable_weight * CHINA_TO_HORGOS_RATE
    cost_horgos_to_dest = total_chargeable_weight * DESTINATIONS[destination]
    insurance_cost = (insurance_rate / 100) * cargo_value

    total_cost = (
        cost_china_to_horgos +
        cost_horgos_to_dest +
        CHINA_CUSTOMS_FEE +
        KZ_TRANSIT_FEE +
        LOCAL_HANDLING_FEE +
        insurance_cost
    )

    return {
        "Total Actual Weight (kg)": round(total_weight, 2),
        "Total Volume (CBM)": round(total_volume, 2),
        "Chargeable Weight (kg)": round(total_chargeable_weight, 2),
        f"Cost {origin_city} to Horgos (USD)": round(cost_china_to_horgos, 2),
        f"Cost Horgos to {destination} (USD)": round(cost_horgos_to_dest, 2),
        "China Customs Fee (USD)": CHINA_CUSTOMS_FEE,
        "KZ Transit Fee (USD)": KZ_TRANSIT_FEE,
        "Local Handling Fee (USD)": LOCAL_HANDLING_FEE,
        "Insurance Cost (USD)": round(insurance_cost, 2),
        "Total Cost (USD)": round(total_cost, 2)
    }

def generate_invoice(result, origin_city, destination, stackable, insurance_rate, cargo_value, company_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_text_color(0, 80, 180)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Narchin Transport | Harbin Zohor", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="LTL Freight Calculator (China -> Horgos -> Baku/Tbilisi)", ln=True, align='C')
    pdf.ln(10)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Origin City: {origin_city}", ln=True)
    pdf.cell(200, 10, f"Destination City: {destination}", ln=True)
    pdf.cell(200, 10, f"Stackable: {'Yes' if stackable else 'No'}", ln=True)
    pdf.cell(200, 10, f"Insurance Rate: {insurance_rate}%", ln=True)
    pdf.cell(200, 10, f"Cargo Value: {cargo_value} USD", ln=True)
    pdf.ln(10)

    for key, value in result.items():
        pdf.cell(200, 10, f"{key}: {value}", ln=True)

    buffer = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1', 'replace')
    buffer.write(pdf_output)
    buffer.seek(0)
    return buffer

# ------------------ STREAMLIT APP ------------------
st.set_page_config(page_title="LTL Freight Calculator", layout="centered")
st.title("LTL Freight Calculator")
st.subheader("Narchin Transport | Harbin Zohor")

if "step" not in st.session_state:
    st.session_state.step = 0

if "num_pallets" not in st.session_state:
    st.session_state.num_pallets = 1

if "pallets" not in st.session_state:
    st.session_state.pallets = [{} for _ in range(1)]

if "calculation_result" not in st.session_state:
    st.session_state.calculation_result = {}

if "invoice_buffer" not in st.session_state:
    st.session_state.invoice_buffer = None

def reset_all():
    st.session_state.step = 0
    st.session_state.num_pallets = 1
    st.session_state.pallets = [{} for _ in range(1)]
    st.session_state.calculation_result = {}
    st.session_state.invoice_buffer = None

if st.button("Start Over"):
    reset_all()

if st.session_state.step == 0:
    st.session_state.num_pallets = st.number_input("Number of Pallets", min_value=1, max_value=50, value=st.session_state.num_pallets)
    if len(st.session_state.pallets) != st.session_state.num_pallets:
        for i in range(st.session_state.num_pallets):
            if i >= len(st.session_state.pallets):
                st.session_state.pallets.append({})
    if st.button("Next: Enter Pallet Details"):
        st.session_state.step = 1

if st.session_state.step == 1:
    st.write("### Enter Details for Each Pallet")
    for i in range(st.session_state.num_pallets):
        with st.expander(f"Pallet {i+1}", expanded=True):
            length = st.number_input(f"Length (cm) - Pallet {i+1}", min_value=1, key=f"length_{i}")
            width = st.number_input(f"Width (cm) - Pallet {i+1}", min_value=1, key=f"width_{i}")
            height = st.number_input(f"Height (cm) - Pallet {i+1}", min_value=1, key=f"height_{i}")
            weight = st.number_input(f"Weight (kg) - Pallet {i+1}", min_value=1.0, key=f"weight_{i}")
            st.session_state.pallets[i] = {"length": length, "width": width, "height": height, "weight": weight}

    origin_city = st.selectbox("Pickup City in China", CHINA_CITIES)
    destination_city = st.selectbox("Delivery City", list(DESTINATIONS.keys()))
    stackable = st.checkbox("Are the goods stackable?", value=True)
    insurance_rate = st.number_input("Insurance Rate (%)", min_value=0.0, value=2.0)
    cargo_value = st.number_input("Total Cargo Value (USD)", min_value=0.0, value=1000.0)

    if st.button("Calculate Freight Cost"):
        result = calculate_total(st.session_state.pallets, origin_city, destination_city, insurance_rate, cargo_value)
        st.session_state.calculation_result = result
        st.session_state.invoice_buffer = generate_invoice(result, origin_city, destination_city, stackable, insurance_rate, cargo_value, "")
        st.session_state.step = 2

if st.session_state.step == 2:
    st.write("## Freight Cost Calculation Result")
    for key, value in st.session_state.calculation_result.items():
        st.write(f"**{key}:** {value}")

    st.download_button(
        label="📄 Download Invoice (PDF)",
        data=st.session_state.invoice_buffer,
        file_name="ltl_invoice.pdf",
        mime="application/pdf"
    )
