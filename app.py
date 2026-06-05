import pandas as pd
import os
import pickle
import sqlite3
import random
from datetime import datetime

import streamlit as st
from streamlit_option_menu import option_menu

from reportlab.platypus import (
    SimpleDocTemplate,
    Spacer,
    Paragraph,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib import enums

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Multiple Disease Prediction and Advisory Platform",
    layout="wide",
    page_icon="🩺"
)

working_dir = os.path.dirname(
    os.path.abspath(__file__)
)

# ---------- REPORT ID ----------

def generate_report_id():

    random_number = random.randint(
        10000,
        99999
    )

    return (
        f"MDPAP-"
        f"{datetime.now().year}-"
        f"{random_number}"
    )

# ---------- DATABASE ----------

DB_PATH = "health_predictions.db"


def create_database():

    conn = sqlite3.connect(
        DB_PATH
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS
        prediction_history (

            id INTEGER
            PRIMARY KEY AUTOINCREMENT,

            patient_age INTEGER,

            disease TEXT,

            prediction TEXT,

            risk_score REAL,

            risk_level TEXT,

            important_inputs TEXT,

            created_at TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def save_prediction(
    patient_age,
    disease,
    prediction,
    risk_score,
    risk_level,
    important_inputs
):

    conn = sqlite3.connect(
        DB_PATH
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO prediction_history
        (
            patient_age,
            disease,
            prediction,
            risk_score,
            risk_level,
            important_inputs,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            patient_age,
            disease,
            prediction,
            risk_score,
            risk_level,
            important_inputs,
            datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            )
        )
    )

    conn.commit()
    conn.close()


# create db automatically
create_database()

# ---------- LOAD MODELS ----------
diabetes_model = pickle.load(
    open(
        f"{working_dir}/saved_models/diabetes_model.sav",
        "rb"
    )
)

heart_disease_model = pickle.load(
    open(
        f"{working_dir}/saved_models/heart_disease_model.sav",
        "rb"
    )
)

parkinsons_model = pickle.load(
    open(
        f"{working_dir}/saved_models/parkinsons_model.sav",
        "rb"
    )
)

kidney_model = pickle.load(
    open(
        f"{working_dir}/saved_models/kidney_model.sav",
        "rb"
    )
)

# ---------- CUSTOM CSS ----------
st.markdown(
    """
<style>

/* spacing */
.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
}

/* app title */
.main-title{
    text-align:center;
    font-size:42px;
    font-weight:800;
    margin-bottom:6px;
}

.main-subtitle{
    text-align:center;
    font-size:16px;
    color:#9ca3af;
    margin-bottom:25px;
}

/* result cards */
.result-card{
    border-radius:18px;
    padding:22px;
    margin-top:20px;
    border:1px solid rgba(255,255,255,0.1);
    background:rgba(255,255,255,0.04);
    box-shadow:0 8px 20px rgba(0,0,0,0.12);
}

.result-title{
    font-size:24px;
    font-weight:700;
    margin-bottom:10px;
}

.metric-box{
    border-radius:14px;
    padding:14px;
    text-align:center;
    background:rgba(255,255,255,0.05);
    margin-top:10px;
}

.metric-value{
    font-size:24px;
    font-weight:700;
}

.metric-label{
    font-size:14px;
    opacity:0.8;
}

.low-risk{
    color:#22c55e;
}

.medium-risk{
    color:#f59e0b;
}

.high-risk{
    color:#ef4444;
}

.stButton > button{
    width:100%;
    border-radius:12px;
    height:48px;
    font-size:16px;
    font-weight:600;
}

</style>
""",
    unsafe_allow_html=True
)


# ---------- HELPER FUNCTIONS ----------

def get_risk_level(score):

    if score < 35:
        return "🟢 Low Risk"

    elif score < 70:
        return "🟡 Moderate Risk"

    else:
        return "🔴 High Risk"


def get_specialist(disease):

    specialists = {
        "Diabetes":
            "Endocrinologist / Diabetologist",

        "Heart":
            "Cardiologist",

        "Parkinsons":
            "Neurologist",

        "Kidney":
            "Nephrologist"
    }

    return specialists.get(
        disease,
        "General Physician"
    )


def show_result(text, is_disease):

    if is_disease:
        st.error(text)

    else:
        st.success(text)


def show_result_card(
    disease_name,
    prediction_text,
    risk_score,
    specialist,
    factors,
    advisory
):

    risk_level = get_risk_level(
        risk_score
    )

    st.markdown(
        f"""
        <div class="result-card">

        <div class="result-title">
        {prediction_text}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="metric-box">
            <div class="metric-value">
            {round(risk_score,2)}%
            </div>
            <div class="metric-label">
            Risk Score
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-box">
            <div class="metric-value">
            {risk_level}
            </div>
            <div class="metric-label">
            Risk Level
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-box">
            <div class="metric-value">
            👨‍⚕️
            </div>
            <div class="metric-label">
            {specialist}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        "### 🔍 Main Influencing Factors"
    )

    for factor in factors:
        st.markdown(
            f"• {factor}"
        )

    st.markdown(
        "### 🩺 Health Advisory"
    )

    for tip in advisory:
        st.markdown(
            f"• {tip}"
        )



# ---------- PROFESSIONAL PDF REPORT ----------

def generate_medical_report(

    disease_name,

    patient_name,
    patient_gender,
    patient_phone,
    patient_email,

    age,

    prediction_text,
    risk_score,
    risk_level,

    important_inputs,

    factors,
    specialist,
    advisory
):

    report_id = generate_report_id()

    file_name = (
        f"{disease_name}_"
        f"Report_"
        f"{report_id}.pdf"
    )

    doc = SimpleDocTemplate(
        file_name
    )

    styles = (
        getSampleStyleSheet()
    )

    # ---------- CUSTOM STYLES ----------

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=20,
        alignment=enums.TA_CENTER,
        spaceAfter=10
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=14,
        alignment=enums.TA_CENTER,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["BodyText"],
        fontSize=11,
        leading=18
    )

    green_style = ParagraphStyle(
        "GreenStyle",
        parent=normal_style,
        textColor=colors.green
    )

    red_style = ParagraphStyle(
        "RedStyle",
        parent=normal_style,
        textColor=colors.red
    )

    orange_style = ParagraphStyle(
        "OrangeStyle",
        parent=normal_style,
        textColor=colors.orange
    )

    story = []

    # ---------- HEADER ----------

    story.append(
        Paragraph(
            "MULTIPLE DISEASE "
            "PREDICTION AND "
            "ADVISORY PLATFORM",
            title_style
        )
    )

    story.append(
        Paragraph(
            "AI-POWERED MEDICAL REPORT",
            heading_style
        )
    )

    story.append(
        Spacer(1, 15)
    )

    # ---------- PATIENT DETAILS ----------

    story.append(
        Paragraph(
            "PATIENT INFORMATION",
            heading_style
        )
    )

    patient_data = [
        ["Patient Name", patient_name],
        ["Age", str(age)],
        ["Gender", patient_gender],
        ["Phone", patient_phone or "N/A"],
        ["Email", patient_email or "N/A"],
        ["Report ID", report_id],
        [
            "Date & Time",
            datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            )
        ]
    ]

    table = Table(
        patient_data,
        colWidths=[150, 250]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica")
        ])
    )

    story.append(table)

    story.append(
        Spacer(1, 15)
    )

    # ---------- RESULT ----------

    story.append(
        Paragraph(
            f"{disease_name.upper()} "
            f"SCREENING RESULT",
            heading_style
        )
    )

    result_style = (
        red_style
        if "Detected"
        in prediction_text
        else green_style
    )

    story.append(
        Paragraph(
            prediction_text.upper(),
            result_style
        )
    )

    # ---------- RISK SCORE ----------

    if risk_score >= 70:
        risk_style = red_style

    elif risk_score >= 35:
        risk_style = orange_style

    else:
        risk_style = green_style

    story.append(
        Paragraph(
            f"Risk Score: "
            f"{round(risk_score,2)}%",
            risk_style
        )
    )

    story.append(
        Paragraph(
            f"Risk Level: "
            f"{risk_level}",
            normal_style
        )
    )

    story.append(
        Spacer(1, 10)
    )

    # ---------- INPUTS ----------

    story.append(
        Paragraph(
            "IMPORTANT CLINICAL INPUTS",
            heading_style
        )
    )

    for key, value in important_inputs.items():

        story.append(
            Paragraph(
                f"{key}: {value}",
                normal_style
            )
        )

    story.append(
        Spacer(1, 10)
    )

    # ---------- FACTORS ----------

    story.append(
        Paragraph(
            "MAIN INFLUENCING FACTORS",
            heading_style
        )
    )

    for factor in factors:

        story.append(
            Paragraph(
                factor,
                normal_style
            )
        )

    story.append(
        Spacer(1, 10)
    )

    # ---------- SPECIALIST ----------

    story.append(
        Paragraph(
            "RECOMMENDED SPECIALIST",
            heading_style
        )
    )

    story.append(
        Paragraph(
            specialist,
            normal_style
        )
    )

    story.append(
        Spacer(1, 10)
    )

    # ---------- ADVISORY ----------

    story.append(
        Paragraph(
            "HEALTH ADVISORY",
            heading_style
        )
    )

    for tip in advisory:

        story.append(
            Paragraph(
                tip,
                normal_style
            )
        )

    story.append(
        Spacer(1, 15)
    )

    # ---------- DISCLAIMER ----------

    story.append(
        Paragraph(
            "DISCLAIMER",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "This report is generated "
            "using Machine Learning "
            "for educational screening "
            "purposes only. Please "
            "consult a qualified doctor "
            "for proper diagnosis and "
            "treatment.",
            normal_style
        )
    )

    doc.build(story)

    return file_name

# ---------- APP HEADER ----------

st.markdown(
    """
    <div style="
        text-align:center;
        padding:15px;
        border-radius:18px;
        background:linear-gradient(
            135deg,
            rgba(239,68,68,0.15),
            rgba(59,130,246,0.12)
        );
        margin-bottom:20px;
    ">

    <h1 style="
        margin-bottom:5px;
        font-size:42px;
        font-weight:800;
    ">
        🩺 Multiple Disease Prediction
        & Advisory Platform
    </h1>

    <p style="
        font-size:16px;
        opacity:0.85;
        margin-top:0;
    ">
        AI-powered healthcare screening
        for early disease risk detection
    </p>

    </div>
    """,
    unsafe_allow_html=True
)

# ---------- PATIENT DETAILS ----------

st.sidebar.markdown(
    """
    ## 👤 Patient Details

    Please fill patient information
    before prediction.
    """
)

patient_name = (
    st.sidebar.text_input(
        "Patient Name *"
    )
)

patient_gender = (
    st.sidebar.selectbox(
        "Gender *",
        [
            "Select Gender",
            "Male",
            "Female",
            "Other"
        ]
    )
)

patient_phone = (
    st.sidebar.text_input(
        "Phone (Optional)"
    )
)

patient_email = (
    st.sidebar.text_input(
        "Email (Optional)"
    )
)

st.sidebar.info(
    "Please enter patient details "
    "before using disease prediction "
    "or downloading reports."
)

patient_details_complete = (

    patient_name.strip() != ""

    and

    patient_gender
    != "Select Gender"
)

# ---------- MENU ----------

selected = option_menu(
    menu_title=None,
    options=[
        "Diabetes Prediction",
        "Heart Disease Prediction",
        "Parkinsons Prediction",
        "Kidney Disease Prediction"
    ],
    icons=[
        "activity",
        "heart",
        "person",
        "droplet-half"
    ],
    orientation="horizontal",
)

# ---------- ADMIN ACCESS ----------

st.sidebar.markdown("---")

with st.sidebar.expander(
    "🔒 Admin Access"
):

    admin_login = (
        st.checkbox(
            "Enable Admin Login"
        )
    )

    admin_authenticated = False

    if admin_login:

        admin_password = (
            st.text_input(
                "Admin Password",
                type="password"
            )
        )

        if admin_password == "leo2000":

            admin_authenticated = True

            st.success(
                "Admin Access Granted"
            )

        elif admin_password != "":

            st.error(
                "Incorrect Password"
            )

# ---------- VALIDATION ----------

if (
    not patient_details_complete
    and
    not admin_authenticated
):

    st.warning(
        "Please enter Patient Name "
        "and Gender in sidebar "
        "to continue."
    )

    st.stop()


# ===================== DIABETES PREDICTION PAGE =====================

if selected == "Diabetes Prediction":

    st.title("Diabetes Prediction")

    st.caption(
        "AI-powered diabetes risk screening "
        "using important medical indicators."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        Glucose = st.number_input(
            "Glucose (GLU)",
            min_value=0,
            max_value=300,
            value=100,
            key="diabetes_glucose"
        )

    with col2:
        BMI = st.number_input(
            "Body Mass Index (BMI)",
            min_value=0.0,
            max_value=70.0,
            value=25.0,
            step=0.1,
            key="diabetes_bmi"
        )

    with col3:
        Age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=30,
            key="diabetes_age"
        )

    with col1:
        DiabetesPedigreeFunction = st.number_input(
            "Diabetes Pedigree Function",
            min_value=0.0,
            max_value=3.0,
            value=0.5,
            step=0.001,
            key="diabetes_dpf"
        )

    with col2:
        Insulin = st.number_input(
            "Insulin",
            min_value=0.0,
            max_value=900.0,
            value=80.0,
            key="diabetes_insulin"
        )

    with col3:
        BloodPressure = st.number_input(
            "Blood Pressure",
            min_value=0,
            max_value=200,
            value=80,
            key="diabetes_bp"
        )

    FamilyHistoryLabel = st.radio(
        "Family History of Diabetes",
        ("No", "Yes"),
        key="diabetes_family"
    )

    FamilyHistory = (
        1 if FamilyHistoryLabel == "Yes"
        else 0
    )

    st.write("")

    if st.button(
        "Get Diabetes Test Result",
        key="diabetes_predict"
    ):

        user_input = [
            Glucose,
            BMI,
            Age,
            DiabetesPedigreeFunction,
            Insulin,
            BloodPressure
        ]

        diabetes_prediction = (
            diabetes_model.predict(
                [user_input]
            )
        )

        diabetes_probability = (
            diabetes_model.predict_proba(
                [user_input]
            )[0][1]
        )

        risk_score = (
            diabetes_probability * 100
        )

        risk_level = (
            get_risk_level(
                risk_score
            )
        )

        factors = []

        if Glucose > 140:
            factors.append(
                "High Glucose Level"
            )

        if BMI > 30:
            factors.append(
                "High BMI"
            )

        if Insulin > 276:
            factors.append(
                "High Insulin Level"
            )

        if BloodPressure > 120:
            factors.append(
                "High Blood Pressure"
            )

        if FamilyHistory == 1:
            factors.append(
                "Family History of Diabetes"
            )

        if len(factors) == 0:
            factors = [
                "Healthy metabolic indicators",
                "No major diabetes risk signs"
            ]

        if diabetes_prediction[0] == 1:

            prediction_text = (
                "DIABETES RISK DETECTED"
            )

            advisory = [
                "Consult an endocrinologist",
                "Reduce sugar intake",
                "Exercise regularly",
                "Monitor glucose levels"
            ]

        else:

            prediction_text = (
                "NO SIGNIFICANT "
                "DIABETES RISK"
            )

            advisory = [
                "Maintain healthy diet",
                "Exercise regularly",
                "Maintain healthy weight",
                "Continue regular checkups"
            ]

        specialist = get_specialist(
            "Diabetes"
        )

        show_result_card(
            disease_name="Diabetes",
            prediction_text=prediction_text,
            risk_score=risk_score,
            specialist=specialist,
            factors=factors,
            advisory=advisory
        )

        save_prediction(
            patient_age=Age,
            disease="Diabetes",
            prediction=prediction_text,
            risk_score=round(
                risk_score,
                2
            ),
            risk_level=risk_level,
            important_inputs=
            f"""
            Glucose={Glucose},
            BMI={BMI},
            Insulin={Insulin},
            BloodPressure={BloodPressure}
            """
        )

        # ---------- REPORT ----------

        if patient_name.strip() == "":

            st.error(
                "Please enter "
                "patient name "
                "to download report."
            )

        else:

            pdf_file = (
                generate_medical_report(

                    disease_name=
                    "Diabetes",

                    patient_name=
                    patient_name,

                    patient_gender=
                    patient_gender,

                    patient_phone=
                    patient_phone,

                    patient_email=
                    patient_email,

                    age=
                    Age,

                    prediction_text=
                    prediction_text,

                    risk_score=
                    risk_score,

                    risk_level=
                    risk_level,

                    important_inputs={

                        "Glucose":
                        Glucose,

                        "BMI":
                        BMI,

                        "Insulin":
                        Insulin,

                        "Blood Pressure":
                        BloodPressure,

                        "Family History":
                        FamilyHistoryLabel
                    },

                    factors=
                    factors,

                    specialist=
                    specialist,

                    advisory=
                    advisory
                )
            )

            with open(
                pdf_file,
                "rb"
            ) as file:

                st.download_button(

                    label=
                    "Download Health Report",

                    data=
                    file,

                    file_name=
                    pdf_file,

                    mime=
                    "application/pdf"
                )
        
# ===================== HEART DISEASE PREDICTION PAGE =====================

if selected == "Heart Disease Prediction":

    st.title("Heart Disease Prediction")

    st.caption(
        "AI-powered early heart disease "
        "risk screening using clinical indicators."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input(
            "Age",
            min_value=18,
            max_value=100,
            value=40,
            key="heart_age"
        )

    with col2:
        sex_label = st.radio(
            "Gender",
            ("Male", "Female"),
            key="heart_gender"
        )

        sex = (
            1 if sex_label == "Male"
            else 0
        )

    with col3:
        cp_label = st.selectbox(
            "Chest Pain Type",
            (
                "Typical Angina",
                "Atypical Angina",
                "Non-anginal Pain",
                "Asymptomatic"
            ),
            key="heart_cp"
        )

        cp_map = {
            "Typical Angina": 0,
            "Atypical Angina": 1,
            "Non-anginal Pain": 2,
            "Asymptomatic": 3
        }

        cp = cp_map[
            cp_label
        ]

    with col1:
        trestbps = st.number_input(
            "Blood Pressure",
            min_value=80,
            max_value=220,
            value=120,
            key="heart_bp"
        )

    with col2:
        chol = st.number_input(
            "Cholesterol",
            min_value=100,
            max_value=600,
            value=200,
            key="heart_chol"
        )

    with col3:
        thalach = st.number_input(
            "Maximum Heart Rate",
            min_value=60,
            max_value=220,
            value=150,
            key="heart_thalach"
        )

    with col1:
        exang_label = st.radio(
            "Exercise-Induced Chest Pain",
            ("No", "Yes"),
            key="heart_exang"
        )

        exang = (
            1 if exang_label == "Yes"
            else 0
        )

    with col2:
        oldpeak = st.number_input(
            "ECG Change (Oldpeak)",
            min_value=0.0,
            max_value=6.5,
            value=1.0,
            step=0.1,
            key="heart_oldpeak"
        )

    with col3:
        slope_label = st.selectbox(
            "ECG Pattern",
            (
                "Upsloping",
                "Flat",
                "Downsloping"
            ),
            key="heart_slope"
        )

        slope_map = {
            "Upsloping": 0,
            "Flat": 1,
            "Downsloping": 2
        }

        slope = slope_map[
            slope_label
        ]

    with col1:
        ca = st.number_input(
            "Major Blood Vessels",
            min_value=0,
            max_value=4,
            value=0,
            key="heart_ca"
        )

    with col2:
        thal_label = st.selectbox(
            "Thallium Test",
            (
                "Normal",
                "Fixed Defect",
                "Reversible Defect"
            ),
            key="heart_thal"
        )

        thal_map = {
            "Normal": 1,
            "Fixed Defect": 2,
            "Reversible Defect": 3
        }

        thal = thal_map[
            thal_label
        ]

    st.write("")

    if st.button(
        "Get Heart Disease Result",
        key="heart_predict"
    ):

        user_input = [
            age,
            sex,
            cp,
            trestbps,
            chol,
            thalach,
            exang,
            oldpeak,
            slope,
            ca,
            thal
        ]

        heart_prediction = (
            heart_disease_model.predict(
                [user_input]
            )
        )

        heart_probability = (
            heart_disease_model
            .predict_proba(
                [user_input]
            )[0]
        )

        risk_score = (
            heart_probability[0]
            * 100
        )

        risk_level = (
            get_risk_level(
                risk_score
            )
        )

        factors = []

        if chol >= 240:
            factors.append(
                "High Cholesterol"
            )

        if trestbps >= 140:
            factors.append(
                "High Blood Pressure"
            )

        if cp == 3:
            factors.append(
                "Asymptomatic Chest Pain"
            )

        if oldpeak >= 2:
            factors.append(
                "Abnormal ECG Changes"
            )

        if exang == 1:
            factors.append(
                "Exercise-Induced Chest Pain"
            )

        if ca >= 2:
            factors.append(
                "Multiple Blood Vessels Affected"
            )

        if len(factors) == 0:
            factors = [
                "Healthy cardiovascular profile",
                "Normal heart indicators"
            ]

        if heart_prediction[0] == 0:

            prediction_text = (
                "HEART DISEASE "
                "RISK DETECTED"
            )

            advisory = [
                "Consult a cardiologist",
                "Reduce oily food",
                "Monitor BP regularly",
                "Avoid smoking and stress"
            ]

        else:

            prediction_text = (
                "NO SIGNIFICANT "
                "HEART DISEASE RISK"
            )

            advisory = [
                "Maintain healthy diet",
                "Exercise regularly",
                "Avoid smoking",
                "Continue routine checkups"
            ]

        specialist = get_specialist(
            "Heart"
        )

        show_result_card(
            disease_name="Heart",
            prediction_text=prediction_text,
            risk_score=risk_score,
            specialist=specialist,
            factors=factors,
            advisory=advisory
        )

        save_prediction(
            patient_age=age,
            disease="Heart",
            prediction=prediction_text,
            risk_score=round(
                risk_score,
                2
            ),
            risk_level=risk_level,
            important_inputs=
            f"""
            BP={trestbps},
            Cholesterol={chol},
            OldPeak={oldpeak},
            CA={ca}
            """
        )

        pdf_file = (
            generate_medical_report(

                disease_name=
                "Heart",

                patient_name=
                patient_name,

                patient_gender=
                patient_gender,

                patient_phone=
                patient_phone,

                patient_email=
                patient_email,

                age=
                age,

                prediction_text=
                prediction_text,

                risk_score=
                risk_score,

                risk_level=
                risk_level,

                important_inputs={

                    "Blood Pressure":
                    trestbps,

                    "Cholesterol":
                    chol,

                    "Heart Rate":
                    thalach,

                    "ECG Change":
                    oldpeak,

                    "Chest Pain":
                    cp_label
                },

                factors=
                factors,

                specialist=
                specialist,

                advisory=
                advisory
            )
        )

        with open(
            pdf_file,
            "rb"
        ) as file:

            st.download_button(

                label=
                "Download Health Report",

                data=
                file,

                file_name=
                pdf_file,

                mime=
                "application/pdf"
            )
# ===================== PARKINSON'S PREDICTION PAGE =====================

if selected == "Parkinsons Prediction":

    st.title("Parkinson's Disease Prediction")

    st.caption(
        "AI-powered Parkinson's risk screening "
        "using voice pattern analysis."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        Fo = st.number_input(
            "Average Vocal Frequency (Fo)",
            min_value=70.0,
            max_value=300.0,
            step=0.1,
            key="park_fo"
        )

    with col2:
        Fhi = st.number_input(
            "Highest Vocal Frequency (Fhi)",
            min_value=80.0,
            max_value=600.0,
            step=0.1,
            key="park_fhi"
        )

    with col3:
        Flo = st.number_input(
            "Lowest Vocal Frequency (Flo)",
            min_value=50.0,
            max_value=260.0,
            step=0.1,
            key="park_flo"
        )

    with col1:
        Jitter_percent = st.number_input(
            "Voice Instability (Jitter %)",
            min_value=0.001,
            max_value=0.03,
            step=0.001,
            format="%.4f",
            key="park_jitter"
        )

    with col2:
        Shimmer = st.number_input(
            "Voice Amplitude Variation",
            min_value=0.01,
            max_value=0.2,
            step=0.001,
            key="park_shimmer"
        )

    with col3:
        HNR = st.number_input(
            "Harmonics-to-Noise Ratio",
            min_value=5.0,
            max_value=45.0,
            step=0.1,
            key="park_hnr"
        )

    with col1:
        RPDE = st.number_input(
            "Voice Pattern Recurrence",
            min_value=0.1,
            max_value=1.0,
            step=0.01,
            key="park_rpde"
        )

    with col2:
        DFA = st.number_input(
            "Signal Stability (DFA)",
            min_value=0.4,
            max_value=1.5,
            step=0.01,
            key="park_dfa"
        )

    st.write("")

    if st.button(
        "Get Parkinson's Result",
        key="park_predict"
    ):

        user_input = [
            Fo,
            Fhi,
            Flo,
            Jitter_percent,
            Shimmer,
            HNR,
            RPDE,
            DFA
        ]

        park_prediction = (
            parkinsons_model.predict(
                [user_input]
            )
        )

        park_probability = (
            parkinsons_model.predict_proba(
                [user_input]
            )[0][1]
        )

        risk_score = (
            park_probability * 100
        )

        risk_level = (
            get_risk_level(
                risk_score
            )
        )

        factors = []

        if Jitter_percent > 0.01:
            factors.append(
                "High Voice Instability"
            )

        if Shimmer > 0.05:
            factors.append(
                "Voice Amplitude Variation"
            )

        if HNR < 20:
            factors.append(
                "Low Voice Signal Quality"
            )

        if RPDE > 0.5:
            factors.append(
                "Irregular Voice Pattern"
            )

        if DFA > 0.8:
            factors.append(
                "Abnormal Signal Stability"
            )

        if len(factors) == 0:
            factors = [
                "Healthy voice characteristics",
                "No major Parkinson's indicators"
            ]

        if park_prediction[0] == 1:

            prediction_text = (
                "PARKINSON'S "
                "RISK DETECTED"
            )

            advisory = [
                "Consult a neurologist",
                "Do regular physical exercise",
                "Monitor movement changes",
                "Seek medical evaluation"
            ]

        else:

            prediction_text = (
                "NO SIGNIFICANT "
                "PARKINSON'S RISK"
            )

            advisory = [
                "Stay physically active",
                "Maintain healthy sleep",
                "Keep brain engaged",
                "Continue healthy lifestyle"
            ]

        specialist = get_specialist(
            "Parkinsons"
        )

        show_result_card(
            disease_name="Parkinsons",
            prediction_text=prediction_text,
            risk_score=risk_score,
            specialist=specialist,
            factors=factors,
            advisory=advisory
        )

        save_prediction(
            patient_age=0,
            disease="Parkinsons",
            prediction=prediction_text,
            risk_score=round(
                risk_score,
                2
            ),
            risk_level=risk_level,
            important_inputs=
            f"""
            Jitter={Jitter_percent},
            Shimmer={Shimmer},
            HNR={HNR},
            RPDE={RPDE},
            DFA={DFA}
            """
        )

        pdf_file = (
            generate_medical_report(

                disease_name=
                "Parkinsons",

                patient_name=
                patient_name,

                patient_gender=
                patient_gender,

                patient_phone=
                patient_phone,

                patient_email=
                patient_email,

                age=
                "N/A",

                prediction_text=
                prediction_text,

                risk_score=
                risk_score,

                risk_level=
                risk_level,

                important_inputs={

                    "Jitter %":
                    Jitter_percent,

                    "Shimmer":
                    Shimmer,

                    "HNR":
                    HNR,

                    "RPDE":
                    RPDE,

                    "DFA":
                    DFA
                },

                factors=
                factors,

                specialist=
                specialist,

                advisory=
                advisory
            )
        )

        with open(
            pdf_file,
            "rb"
        ) as file:

            st.download_button(

                label=
                "Download Health Report",

                data=
                file,

                file_name=
                pdf_file,

                mime=
                "application/pdf"
            )

# ===================== KIDNEY DISEASE PREDICTION PAGE =====================

if selected == "Kidney Disease Prediction":

    st.title("Kidney Disease Prediction")

    st.caption(
        "AI-powered kidney disease risk screening "
        "using clinical indicators."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        k_age = st.number_input(
            "Age",
            min_value=1,
            max_value=100,
            value=40,
            key="kidney_age"
        )

    with col2:
        k_bp = st.number_input(
            "Blood Pressure",
            min_value=50.0,
            max_value=200.0,
            value=80.0,
            key="kidney_bp"
        )

    with col3:
        k_sg = st.number_input(
            "Specific Gravity",
            min_value=1.005,
            max_value=1.025,
            value=1.015,
            step=0.001,
            format="%.3f",
            key="kidney_sg"
        )

    with col1:
        k_al = st.number_input(
            "Albumin",
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=1.0,
            key="kidney_al"
        )

    with col2:
        k_bgr = st.number_input(
            "Blood Glucose Random",
            min_value=50.0,
            max_value=500.0,
            value=120.0,
            key="kidney_bgr"
        )

    with col3:
        k_bu = st.number_input(
            "Blood Urea",
            min_value=1.0,
            max_value=400.0,
            value=40.0,
            key="kidney_bu"
        )

    with col1:
        k_sc = st.number_input(
            "Serum Creatinine",
            min_value=0.4,
            max_value=15.0,
            value=1.2,
            key="kidney_sc"
        )

    with col2:
        k_hemo = st.number_input(
            "Hemoglobin",
            min_value=3.0,
            max_value=20.0,
            value=13.0,
            key="kidney_hemo"
        )

    with col3:
        k_wc = st.number_input(
            "White Blood Cell Count",
            min_value=2000,
            max_value=25000,
            value=8000,
            key="kidney_wc"
        )

    with col1:
        k_htn_label = st.radio(
            "Hypertension",
            ("No", "Yes"),
            key="kidney_htn"
        )

        k_htn = (
            1 if k_htn_label == "Yes"
            else 0
        )

    with col2:
        k_dm_label = st.radio(
            "Diabetes",
            ("No", "Yes"),
            key="kidney_dm"
        )

        k_dm = (
            1 if k_dm_label == "Yes"
            else 0
        )

    with col3:
        k_ane_label = st.radio(
            "Anemia",
            ("No", "Yes"),
            key="kidney_ane"
        )

        k_ane = (
            1 if k_ane_label == "Yes"
            else 0
        )

    st.write("")

    if st.button(
        "Get Kidney Disease Result",
        key="kidney_predict"
    ):

        user_input = [
            k_age,
            k_bp,
            k_sg,
            k_al,
            k_bgr,
            k_bu,
            k_sc,
            k_hemo,
            k_wc,
            k_htn,
            k_dm,
            k_ane
        ]

        kidney_prediction = (
            kidney_model.predict(
                [user_input]
            )
        )

        kidney_probability = (
            kidney_model.predict_proba(
                [user_input]
            )[0][1]
        )

        risk_score = (
            kidney_probability * 100
        )

        risk_level = (
            get_risk_level(
                risk_score
            )
        )

        factors = []

        if k_al >= 3:
            factors.append(
                "High Albumin Level"
            )

        if k_sc >= 2:
            factors.append(
                "High Creatinine"
            )

        if k_bu >= 80:
            factors.append(
                "High Blood Urea"
            )

        if k_htn == 1:
            factors.append(
                "Hypertension"
            )

        if k_dm == 1:
            factors.append(
                "Diabetes"
            )

        if k_ane == 1:
            factors.append(
                "Anemia"
            )

        if len(factors) == 0:
            factors = [
                "Healthy kidney indicators",
                "No major kidney risk signs"
            ]

        if kidney_prediction[0] == 1:

            prediction_text = (
                "KIDNEY DISEASE "
                "RISK DETECTED"
            )

            advisory = [
                "Consult a nephrologist",
                "Drink adequate water",
                "Reduce salt intake",
                "Monitor BP and sugar"
            ]

        else:

            prediction_text = (
                "NO SIGNIFICANT "
                "KIDNEY DISEASE RISK"
            )

            advisory = [
                "Maintain hydration",
                "Avoid excess painkillers",
                "Maintain healthy BP",
                "Continue checkups"
            ]

        specialist = get_specialist(
            "Kidney"
        )

        show_result_card(
            disease_name="Kidney",
            prediction_text=prediction_text,
            risk_score=risk_score,
            specialist=specialist,
            factors=factors,
            advisory=advisory
        )

        save_prediction(
            patient_age=k_age,
            disease="Kidney",
            prediction=prediction_text,
            risk_score=round(
                risk_score,
                2
            ),
            risk_level=risk_level,
            important_inputs=
            f"""
            BP={k_bp},
            Albumin={k_al},
            Creatinine={k_sc},
            BloodUrea={k_bu}
            """
        )

        pdf_file = (
            generate_medical_report(

                disease_name=
                "Kidney",

                patient_name=
                patient_name,

                patient_gender=
                patient_gender,

                patient_phone=
                patient_phone,

                patient_email=
                patient_email,

                age=
                k_age,

                prediction_text=
                prediction_text,

                risk_score=
                risk_score,

                risk_level=
                risk_level,

                important_inputs={

                    "Blood Pressure":
                    k_bp,

                    "Albumin":
                    k_al,

                    "Creatinine":
                    k_sc,

                    "Blood Urea":
                    k_bu,

                    "Diabetes":
                    k_dm_label
                },

                factors=
                factors,

                specialist=
                specialist,

                advisory=
                advisory
            )
        )

        with open(
            pdf_file,
            "rb"
        ) as file:

            st.download_button(

                label=
                "Download Health Report",

                data=
                file,

                file_name=
                pdf_file,

                mime=
                "application/pdf"
            )

# ===================== PREDICTION HISTORY =====================

# ===================== PREDICTION HISTORY =====================

if admin_authenticated:

    st.markdown("---")

    st.title(
        "Admin Dashboard"
    )

    st.caption(
        "Admin-only patient "
        "prediction database."
    )

    conn = sqlite3.connect(
        DB_PATH
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
        created_at,
        disease,
        prediction,
        risk_score,
        risk_level,
        patient_age,
        important_inputs

        FROM prediction_history

        ORDER BY id DESC
        """
    )

    data = cursor.fetchall()

    conn.close()

    if len(data) == 0:

        st.info(
            "No prediction history found."
        )

    else:

        history_df = pd.DataFrame(

            data,

            columns=[

                "Date & Time",
                "Disease",
                "Prediction",
                "Risk Score (%)",
                "Risk Level",
                "Age",
                "Important Inputs"
            ]
        )

        st.subheader(
            "Prediction History"
        )

        st.dataframe(
            history_df,
            use_container_width=True
        )

        csv = (
            history_df
            .to_csv(
                index=False
            )
            .encode("utf-8")
        )

        st.download_button(

            label=
            "Export Data for Retraining",

            data=
            csv,

            file_name=
            "prediction_history.csv",

            mime=
            "text/csv"
        )


# ---------- FOOTER ----------

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        padding:10px;
        opacity:0.85;
        font-size:14px;
    ">

    ⚠️ This platform is only for
    educational screening and awareness.
    Always consult a qualified doctor
    for diagnosis and treatment.

    </div>
    """,
    unsafe_allow_html=True
)
