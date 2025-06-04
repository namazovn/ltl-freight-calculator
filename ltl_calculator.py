# LTL Charge Calculator - Web Version using Streamlit
import streamlit as st

def calculate_ltl_charge(length_cm, width_cm, height_cm, actual_weight_kg, num_units,
                          rate_per_kg=0.5, transit_fees=200, insurance_rate=0.003, cargo_value=0):
    total_actual_weight = actual_weight_kg * num_units
    volume_cbm_per_unit = (length_cm / 100) * (width_cm / 100) * (height_cm / 100)
    total_volume_cbm = volume_cbm_per_unit * num_units
    volumetric_weight = total_volume_cbm * 333
    chargeable_weight = max(total_actual_weight, volumetric_weight)
    freight_cost = chargeable_weight * rate_per_kg
    insurance_cost = insurance_rate * cargo_value if cargo_value > 0 else 0
    total_cost = freight_cost + transit_fees + insurance_cost

    return {
        'Total Actual Weight (kg)': round(total_actual_weight, 2),
        'Total Volume (CBM)': round(total_volume_cbm, 2),
        'Volumetric Weight (kg)': round(volumetric_weight, 2),
        'Chargeable Weight (kg)': round(chargeable_weight, 2),
        'Freight Cost (USD)': round(freight_cost, 2),
        'Transit Fees (USD)': round(transit_fees, 2),
        'Insurance Cost (USD)': round(insurance_cost, 2),
        'Total Cost (USD)': round(total_cost, 2)
    }

st.title("LTL Freight Calculator (China → Kazakhstan → Azerbaijan)")

with st.form("ltl_form"):
    length_cm = st.number_input("Length (cm)", min_value=0.0, value=120.0)
    width_cm = st.number_input("Width (cm)", min_value=0.0, value=80.0)
    height_cm = st.number_input("Height (cm)", min_value=0.0, value=100.0)
    actual_weight_kg = st.number_input("Weight per Unit (kg)", min_value=0.0, value=200.0)
    num_units = st.number_input("Number of Units", min_value=1, value=3)
    rate_per_kg = st.number_input("Rate per kg (USD)", min_value=0.0, value=0.5)
    transit_fees = st.number_input("Transit Fees (USD)", min_value=0.0, value=200.0)
    insurance_rate = st.number_input("Insurance Rate (e.g. 0.003)", min_value=0.0, value=0.003)
    cargo_value = st.number_input("Cargo Value (USD)", min_value=0.0, value=10000.0)

    submitted = st.form_submit_button("Calculate")

if submitted:
    result = calculate_ltl_charge(length_cm, width_cm, height_cm, actual_weight_kg, num_units,
                                   rate_per_kg, transit_fees, insurance_rate, cargo_value)
    st.subheader("Calculation Result")
    for key, value in result.items():
        st.write(f"{key}: {value}")
