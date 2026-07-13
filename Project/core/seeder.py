"""
Development Demo Seeder
=======================
Seeds realistic demo accounts (Patients, Doctors, Administrator) with sample health
data ONLY when running in development mode. Strictly excluded from production.
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import (
    User, Role, Vitals, Medication, MedicalCondition, Allergy, Vaccination,
    Appointment, DoctorVisit, FamilyMedicalHistory, HealthGoal, EmergencyContact, MedicalDocument
)
from app.security.password import hash_password

logger = logging.getLogger("app.core.seeder")


def seed_development_demo_accounts(db: Session):
    """
    Seeds demo accounts if they do not already exist in the development database.
    """
    logger.info("Checking and seeding development-only demo accounts...")

    # Ensure roles exist
    roles = {}
    for r_name in ["Patient", "Doctor", "Administrator", "user", "admin"]:
        role = db.query(Role).filter(Role.name == r_name).first()
        if not role:
            role = Role(name=r_name, description=f"{r_name} privileges")
            db.add(role)
            db.commit()
            db.refresh(role)
        roles[r_name] = role

    # 1. Administrator
    admin_email = "admin@healthvault.pro"
    if not db.query(User).filter(User.email == admin_email).first():
        admin = User(
            email=admin_email,
            password_hash=hash_password("DemoAdmin123!"),
            first_name="System",
            last_name="Administrator",
            is_active=True,
            is_verified=True,
            roles=[roles["Administrator"]],
            blood_group="N/A"
        )
        db.add(admin)
        logger.info(f"Seeded Admin account: {admin_email}")

    # 2. Doctors (Two Domains: Urology and Neurology - Demo Healthcare Network Visakhapatnam)
    dr1_email = "dr.rohan@healthvault.pro"
    dr1 = db.query(User).filter(User.email == dr1_email).first()
    if not dr1:
        dr1 = User(
            email=dr1_email,
            password_hash=hash_password("DemoDoctor123!"),
            first_name="Rohan",
            last_name="Sharma",
            phone_number="+91-891-2888888",
            is_active=True,
            is_verified=True,
            roles=[roles["Doctor"]],
            blood_group="O+",
            primary_care_physician="Self (Urology Specialist, Demo Healthcare Network Vizag)"
        )
        db.add(dr1)
        logger.info(f"Seeded Urology Doctor account: {dr1_email}")

    dr2_email = "dr.priya@healthvault.pro"
    dr2 = db.query(User).filter(User.email == dr2_email).first()
    if not dr2:
        dr2 = User(
            email=dr2_email,
            password_hash=hash_password("DemoDoctor123!"),
            first_name="Priya",
            last_name="Menon",
            phone_number="+91-891-2777777",
            is_active=True,
            is_verified=True,
            roles=[roles["Doctor"]],
            blood_group="A+",
            primary_care_physician="Self (Neurology Specialist, Demo Healthcare Network Vizag)"
        )
        db.add(dr2)
        logger.info(f"Seeded Neurology Doctor account: {dr2_email}")

    db.commit()

    now = datetime.utcnow()

    # 3. Patient 1: Recovered Emergency Urological Patient (Spoorthi Verma)
    spoorthi_email = "spoorthi.verma@healthvault.pro"
    spoorthi = db.query(User).filter(User.email == spoorthi_email).first()
    if not spoorthi:
        spoorthi = User(
            email=spoorthi_email,
            password_hash=hash_password("DemoPatient123!"),
            first_name="Spoorthi",
            last_name="Verma",
            date_of_birth="1988-04-15",
            gender="Female",
            phone_number="+91-891-2567890",
            is_active=True,
            is_verified=True,
            roles=[roles["Patient"]],
            blood_group="A+",
            organ_donor_status="Yes",
            insurance_provider="Demo Health Premier Vizag #884920",
            primary_care_physician="Dr. Rohan Sharma (Urology Specialist)",
            pcp_contact="+91-891-2888888"
        )
        db.add(spoorthi)
        db.commit()
        db.refresh(spoorthi)
        logger.info(f"Seeded Urological Patient account: {spoorthi_email}")

        # Vitals over time for Spoorthi (Recovering stably after lithotripsy emergency)
        vitals_data_spoorthi = [
            {"sys": 118, "dia": 76, "wt": 68.5, "sug": 88, "pulse": 68, "spo2": 99, "days": 90},
            {"sys": 120, "dia": 78, "wt": 68.3, "sug": 90, "pulse": 70, "spo2": 99, "days": 60},
            {"sys": 122, "dia": 78, "wt": 68.1, "sug": 92, "pulse": 71, "spo2": 98, "days": 30},
            {"sys": 120, "dia": 76, "wt": 68.0, "sug": 89, "pulse": 69, "spo2": 99, "days": 14},
            {"sys": 121, "dia": 77, "wt": 67.9, "sug": 91, "pulse": 70, "spo2": 98, "days": 5},
            {"sys": 119, "dia": 76, "wt": 67.8, "sug": 90, "pulse": 68, "spo2": 99, "days": 1},
        ]
        for vd in vitals_data_spoorthi:
            db.add(Vitals(
                user_id=spoorthi.id,
                recorded_at=now - timedelta(days=vd["days"]),
                systolic_bp=vd["sys"],
                diastolic_bp=vd["dia"],
                weight_kg=vd["wt"],
                height_cm=168.0,
                blood_sugar_mgdl=vd["sug"],
                pulse_bpm=vd["pulse"],
                oxygen_saturation=vd["spo2"],
                temperature_c=36.6
            ))

        # Medications / Tablets for Spoorthi (Urological calculus recovery)
        db.add(Medication(
            user_id=spoorthi.id,
            name="Tamsulosin (Urological Calculus Relief)",
            dosage="0.4mg",
            frequency="Night ✔",
            start_date="2025-01-10",
            status="Active",
            adherence_rate=98.0
        ))
        db.add(Medication(
            user_id=spoorthi.id,
            name="Potassium Citrate (Stone Prevention)",
            dosage="10 mEq",
            frequency="Afternoon ✔",
            start_date="2025-02-01",
            status="Active",
            adherence_rate=95.0
        ))
        db.add(Medication(
            user_id=spoorthi.id,
            name="Vitamin D3 Complex",
            dosage="1000 IU",
            frequency="Morning ✔",
            start_date="2025-01-15",
            status="Active",
            adherence_rate=92.0
        ))

        # Medical Conditions
        db.add(MedicalCondition(
            user_id=spoorthi.id,
            name="Recovered Acute Nephrolithiasis (Renal Calculus - Post Lithotripsy)",
            diagnosed_date="2024-10-15",
            status="Active",
            notes="PAST EMERGENCY: Evaluated at Demo Healthcare Network (Urology Wing, Visakhapatnam) for calculus colic. Successful clearance. Currently recovered stably."
        ))
        db.add(MedicalCondition(
            user_id=spoorthi.id,
            name="Mild Essential Hypertension (Controlled)",
            diagnosed_date="2025-01-10",
            status="Active",
            notes="Monitoring vitals routinely at Demo Healthcare Network (Diagnostic Wing, Visakhapatnam). Normal parameters observed."
        ))

        # Allergies
        db.add(Allergy(
            user_id=spoorthi.id,
            allergen="Sulfa Antibiotics",
            reaction="Mild localized skin rash and itching",
            severity="Mild"
        ))

        # Medical Reports / Documents (Vizag Hospital Network)
        db.add(MedicalDocument(
            user_id=spoorthi.id,
            title="Emergency Urology KUB Ultrasound Scan (Demo Healthcare Network).pdf",
            description="Diagnostic ultrasound showing complete clearance of renal calculus post-lithotripsy.",
            file_path="/reports/spoorthi/kub_ultrasound_vizag.pdf",
            mime_type="application/pdf",
            file_size=3400000,
            document_type="Ultrasound"
        ))
        db.add(MedicalDocument(
            user_id=spoorthi.id,
            title="Post-Lithotripsy Renal Function & Electrolyte Panel.pdf",
            description="Normal serum creatinine and glomerular filtration rate (eGFR) confirmed.",
            file_path="/reports/spoorthi/renal_panel_2025.pdf",
            mime_type="application/pdf",
            file_size=1450000,
            document_type="Lab Report"
        ))
        db.add(MedicalDocument(
            user_id=spoorthi.id,
            title="Annual Routine Comprehensive Blood Chemistry (Demo Diagnostic Center).pdf",
            description="Preventive metabolic wellness screening performed at Demo Healthcare Network.",
            file_path="/reports/spoorthi/chemistry_panel_2025.pdf",
            mime_type="application/pdf",
            file_size=1250000,
            document_type="Lab Report"
        ))

        # Appointments for Spoorthi (5 Total across Vizag Hospitals)
        db.add(Appointment(
            user_id=spoorthi.id,
            doctor_name="Dr. Rohan Sharma",
            specialty="Urology",
            appointment_date=now + timedelta(days=4, hours=10),
            status="Confirmed",
            location="Urology Wing, Demo Healthcare Network, Visakhapatnam",
            notes="Annual urological ultrasound check and renal stone prevention dietary review."
        ))
        db.add(Appointment(
            user_id=spoorthi.id,
            doctor_name="Dr. Priya Menon",
            specialty="Neurology",
            appointment_date=now - timedelta(days=15),
            status="Completed",
            location="Neurology Wing, Demo Healthcare Network, Visakhapatnam",
            notes="Preventive headache screening and neurological wellness check - normal."
        ))
        db.add(Appointment(
            user_id=spoorthi.id,
            doctor_name="Dr. Rohan Sharma",
            specialty="Urology",
            appointment_date=now - timedelta(days=45),
            status="Completed",
            location="Urology Center, Demo Healthcare Network, Visakhapatnam",
            notes="Quarterly post-lithotripsy renal function follow-up check."
        ))
        db.add(Appointment(
            user_id=spoorthi.id,
            doctor_name="Dr. Priya Menon",
            specialty="Neurology",
            appointment_date=now - timedelta(days=90),
            status="Completed",
            location="Specialty Clinic, Demo Healthcare Network, Visakhapatnam",
            notes="Baseline neurological reflex screening."
        ))
        db.add(Appointment(
            user_id=spoorthi.id,
            doctor_name="Dr. Rohan Sharma",
            specialty="Urology",
            appointment_date=now - timedelta(days=30),
            status="Follow-up",
            location="Urology Wing, Demo Healthcare Network, Visakhapatnam",
            notes="Post-ultrasound status review without repeat consultation fee."
        ))

        db.commit()
        logger.info(f"Seeded clinical records and appointments for Urological Patient: {spoorthi_email}")

    # 4. Patient 2: Active Emergency Patient of Neurologist (Ramesh Rao)
    ramesh_email = "ramesh.rao@healthvault.pro"
    ramesh = db.query(User).filter(User.email == ramesh_email).first()
    if not ramesh:
        ramesh = User(
            email=ramesh_email,
            password_hash=hash_password("DemoPatient123!"),
            first_name="Ramesh (Emergency)",
            last_name="Rao",
            date_of_birth="1992-08-20",
            gender="Male",
            phone_number="+91-9848123456",
            is_active=True,
            is_verified=True,
            roles=[roles["Patient"]],
            blood_group="O-",
            organ_donor_status="No",
            insurance_provider="Demo Emergency Gold Vizag #99182",
            primary_care_physician="Dr. Priya Menon (Neurology)",
            pcp_contact="+91-891-2777777"
        )
        db.add(ramesh)
        db.commit()
        db.refresh(ramesh)
        logger.info(f"Seeded Emergency Patient account: {ramesh_email}")

        # Emergency Contact with QR Code Authorization (Vizag Emergency Medical Center)
        db.add(EmergencyContact(
            user_id=ramesh.id,
            name="Sunitha Rao (Wife & Legal Guardian)",
            relationship="Spouse & Legal Guardian",
            phone_number="+91-9848654321",
            email="sunitha.rao@healthvault.pro",
            blood_group="O-",
            notes="ACTIVE EMERGENCY AUTHORIZATION: Emergency QR Code containing encrypted emergency medical information for authorized healthcare personnel at Demo Healthcare Network, Visakhapatnam."
        ))

        # Vitals over time for Ramesh (Showing Critical Spikes & Abnormal Readings requiring emergency neuro intervention)
        vitals_data_ramesh = [
            {"sys": 138, "dia": 88, "wt": 82.0, "sug": 140, "pulse": 88, "spo2": 96, "days": 30},
            {"sys": 145, "dia": 92, "wt": 81.8, "sug": 180, "pulse": 94, "spo2": 95, "days": 20},
            {"sys": 168, "dia": 104, "wt": 81.5, "sug": 285, "pulse": 118, "spo2": 92, "days": 10},
            {"sys": 156, "dia": 98, "wt": 81.2, "sug": 210, "pulse": 105, "spo2": 94, "days": 5},
            {"sys": 142, "dia": 90, "wt": 81.0, "sug": 155, "pulse": 90, "spo2": 96, "days": 2},
            {"sys": 135, "dia": 86, "wt": 80.8, "sug": 135, "pulse": 84, "spo2": 97, "days": 1},
        ]
        for vd in vitals_data_ramesh:
            db.add(Vitals(
                user_id=ramesh.id,
                recorded_at=now - timedelta(days=vd["days"]),
                systolic_bp=vd["sys"],
                diastolic_bp=vd["dia"],
                weight_kg=vd["wt"],
                height_cm=178.0,
                blood_sugar_mgdl=vd["sug"],
                pulse_bpm=vd["pulse"],
                oxygen_saturation=vd["spo2"],
                temperature_c=38.5 if vd["sys"] >= 160 else 37.0
            ))

        # Medications / Tablets for Ramesh
        db.add(Medication(
            user_id=ramesh.id,
            name="Levetiracetam (Anti-Seizure Prophylaxis)",
            dosage="500mg",
            frequency="Morning ✔, Night ✔",
            start_date="2025-01-01",
            status="Active",
            adherence_rate=82.0
        ))
        db.add(Medication(
            user_id=ramesh.id,
            name="Insulin Glargine (Glucose Control)",
            dosage="20 Units",
            frequency="Night ✔",
            start_date="2025-01-15",
            status="Active",
            adherence_rate=75.0
        ))
        db.add(Medication(
            user_id=ramesh.id,
            name="Topiramate (Neurological Prophylaxis)",
            dosage="50mg",
            frequency="Morning ✔",
            start_date="2025-02-01",
            status="Active",
            adherence_rate=88.0
        ))
        db.add(Medication(
            user_id=ramesh.id,
            name="Diazepam (Emergency Rescue Nasal Spray)",
            dosage="5mg",
            frequency="Missed Dose Logged - Alert!",
            start_date="2025-01-01",
            status="Active",
            adherence_rate=65.0
        ))

        # Medical Conditions (Active Emergency Risk under Dr. Priya Menon)
        db.add(MedicalCondition(
            user_id=ramesh.id,
            name="Acute Neurological Spikes & Monitoring (ACTIVE EMERGENCY)",
            diagnosed_date="2024-11-10",
            status="Active",
            notes="ACTIVE EMERGENCY: Currently under intensive acute neurological monitoring by Dr. Priya Menon at Demo Healthcare Network (Neurology Center, Visakhapatnam). Emergency QR Code containing encrypted emergency medical information enabled for authorized healthcare personnel."
        ))
        db.add(MedicalCondition(
            user_id=ramesh.id,
            name="Type 1 Diabetes Mellitus (Uncontrolled Hyperglycemic Spikes)",
            diagnosed_date="2023-05-20",
            status="Active",
            notes="Monitored for metabolic risk during vitals spikes at Demo Healthcare Network, Visakhapatnam."
        ))
        db.add(MedicalCondition(
            user_id=ramesh.id,
            name="Past Urological Screening & Stone Clearance",
            diagnosed_date="2024-02-15",
            status="Active",
            notes="Evaluated by Dr. Rohan Sharma (Urology) - normal renal clearance confirmed."
        ))

        # Allergies (Critical Emergency Warnings)
        db.add(Allergy(
            user_id=ramesh.id,
            allergen="Penicillin",
            reaction="Severe Anaphylaxis and Airway Swelling",
            severity="Severe"
        ))
        db.add(Allergy(
            user_id=ramesh.id,
            allergen="Morphine",
            reaction="Acute Respiratory Depression",
            severity="Severe"
        ))
        db.add(Allergy(
            user_id=ramesh.id,
            allergen="Peanuts & Tree Nuts",
            reaction="Severe Hives and Facial Swelling",
            severity="Severe"
        ))

        # Medical Reports / Documents (Vizag Emergency Network)
        db.add(MedicalDocument(
            user_id=ramesh.id,
            title="Neurological Clinical Scan Evaluation (Demo Healthcare Network).pdf",
            description="Clinical scan evaluating neurological spike abnormalities during acute emergency episode.",
            file_path="/reports/ramesh/neuro_scan_vizag_emergency.pdf",
            mime_type="application/pdf",
            file_size=14500000,
            document_type="MRI"
        ))
        db.add(MedicalDocument(
            user_id=ramesh.id,
            title="Neurological Rhythm & Spike Analysis Report (Dr. Priya Menon).pdf",
            description="Continuous electroencephalogram report documenting neurological rhythm activity.",
            file_path="/reports/ramesh/eeg_seizure_vizag.pdf",
            mime_type="application/pdf",
            file_size=4200000,
            document_type="Lab Report"
        ))
        db.add(MedicalDocument(
            user_id=ramesh.id,
            title="Emergency Room Blood Gas & Electrolytes Panel (Demo Emergency Network).pdf",
            description="Acute emergency admission metabolic panel during hyperglycemia spike.",
            file_path="/reports/ramesh/er_electrolytes_vizag.pdf",
            mime_type="application/pdf",
            file_size=1800000,
            document_type="Lab Report"
        ))
        db.add(MedicalDocument(
            user_id=ramesh.id,
            title="Continuous Patient EHR Session Log & Vitals Trend.pdf",
            description="Continuous clinical monitoring log from Demo Healthcare Network, Visakhapatnam.",
            file_path="/reports/ramesh/neuro_telemetry_vizag.pdf",
            mime_type="application/pdf",
            file_size=3100000,
            document_type="Lab Report"
        ))

        # Appointments for Ramesh (5 Total across Vizag Hospitals)
        db.add(Appointment(
            user_id=ramesh.id,
            doctor_name="Dr. Priya Menon",
            specialty="Neurology",
            appointment_date=now + timedelta(days=1, hours=14),
            status="Confirmed",
            location="Neurology Center, Demo Healthcare Network, Visakhapatnam",
            notes="Urgent clinical follow-up review and dosage titration."
        ))
        db.add(Appointment(
            user_id=ramesh.id,
            doctor_name="Dr. Priya Menon",
            specialty="Neurology",
            appointment_date=now - timedelta(days=10),
            status="Completed",
            location="Specialty Clinic, Demo Healthcare Network, Visakhapatnam",
            notes="Emergency acute stabilization and neurology evaluation."
        ))
        db.add(Appointment(
            user_id=ramesh.id,
            doctor_name="Dr. Rohan Sharma",
            specialty="Urology",
            appointment_date=now - timedelta(days=20),
            status="Completed",
            location="Urology Wing, Demo Healthcare Network, Visakhapatnam",
            notes="Routine renal clearance screening - normal parameters confirmed."
        ))
        db.add(Appointment(
            user_id=ramesh.id,
            doctor_name="Dr. Priya Menon",
            specialty="Neurology",
            appointment_date=now - timedelta(days=40),
            status="Cancelled",
            location="Diagnostic Wing, Demo Healthcare Network, Visakhapatnam",
            notes="Cancelled: Patient hospitalized during scheduled routine check."
        ))
        db.add(Appointment(
            user_id=ramesh.id,
            doctor_name="Dr. Priya Menon",
            specialty="Neurology",
            appointment_date=now - timedelta(days=60),
            status="Follow-up",
            location="Neurology Center, Demo Healthcare Network, Visakhapatnam",
            notes="Post-hospitalization status review without repeat consultation fee."
        ))
        # Additional historical appointments with other doctors for Spoorthi and Ramesh
        other_specialists = [
            ("Dr. Anjali Rao", "Cardiology", "Cardiology Clinic, Demo Healthcare Network, Visakhapatnam", "Routine cardiac stress evaluation - normal EKGs."),
            ("Dr. Sneha Reddy", "General Medicine", "General Medicine Wing, Demo Healthcare Network, Visakhapatnam", "Annual wellness checkup and preventive metabolic panel."),
            ("Dr. Vikram Mehta", "Orthopedics", "Orthopedics Center, Demo Healthcare Network, Visakhapatnam", "Joint mobility evaluation and vitamin D supplementation review."),
            ("Dr. Arvind Patel", "Pulmonology", "Respiratory Wing, Demo Healthcare Network, Visakhapatnam", "Seasonal allergy and pulmonary function screening."),
            ("Dr. Meera Nair", "Dermatology", "Skin & Laser Center, Demo Healthcare Network, Visakhapatnam", "Routine dermatological screening and topical care.")
        ]
        for idx, (doc_name, spec, loc, note) in enumerate(other_specialists):
            db.add(Appointment(
                user_id=spoorthi.id,
                doctor_name=doc_name,
                specialty=spec,
                appointment_date=now - timedelta(days=120 + idx*25),
                status="Completed",
                location=loc,
                notes=note
            ))
            db.add(Appointment(
                user_id=ramesh.id,
                doctor_name=doc_name,
                specialty=spec,
                appointment_date=now - timedelta(days=110 + idx*30),
                status="Completed",
                location=loc,
                notes=f"Emergency clearance consultation with {doc_name} during metabolic evaluation."
            ))

        db.commit()
        logger.info(f"Seeded emergency records and appointments for Emergency Patient: {ramesh_email}")

    # 5. Bulk Enterprise Seeding: 10 Specialists and 25 Diverse Patients (handling lots of people, not 2-5)
    specialist_data = [
        ("dr.anjali@healthvault.pro", "Anjali", "Rao", "Cardiology", "O+"),
        ("dr.vikram@healthvault.pro", "Vikram", "Mehta", "Orthopedics", "B+"),
        ("dr.sneha@healthvault.pro", "Sneha", "Reddy", "General Medicine", "A+"),
        ("dr.arvind@healthvault.pro", "Arvind", "Patel", "Pulmonology", "AB+"),
        ("dr.meera@healthvault.pro", "Meera", "Nair", "Dermatology", "O-"),
        ("dr.rajesh@healthvault.pro", "Rajesh", "Gupta", "Nephrology", "B-"),
        ("dr.kavitha@healthvault.pro", "Kavitha", "S.", "Pediatrics", "A-"),
        ("dr.suresh.v@healthvault.pro", "Suresh", "V.", "Oncology", "O+"),
        ("dr.deepa@healthvault.pro", "Deepa", "M.", "Psychiatry", "AB-"),
        ("dr.amit@healthvault.pro", "Amit", "K.", "Gastroenterology", "B+")
    ]
    for email, fn, ln, spec, blood in specialist_data:
        if not db.query(User).filter(User.email == email).first():
            doc_user = User(
                email=email,
                password_hash=hash_password("DemoDoctor123!"),
                first_name=fn,
                last_name=ln,
                phone_number=f"+91-891-288{len(email):04d}",
                is_active=True,
                is_verified=True,
                roles=[roles["Doctor"]],
                blood_group=blood,
                primary_care_physician=f"Self ({spec} Specialist, Demo Healthcare Network Vizag)"
            )
            db.add(doc_user)
    db.commit()

    patient_names = [
        ("Sandeep", "Patnaik", "sandeep.patnaik@email.com", "O+", "Active"),
        ("Anitha", "Verma", "anitha.verma@email.com", "A+", "Active"),
        ("Ravi", "Kumar", "ravi.kumar@email.com", "B+", "Active"),
        ("Madhavi", "S.", "madhavi.s@email.com", "AB+", "Active"),
        ("Venkatesh", "K.", "venkatesh.k@email.com", "O-", "Active"),
        ("Aditya", "Rao", "aditya.rao@email.com", "A-", "Active"),
        ("Pooja", "Sharma", "pooja.sharma@email.com", "B-", "Active"),
        ("Kiran", "Kumar", "kiran.kumar@email.com", "O+", "Active"),
        ("Lakshmi", "N.", "lakshmi.n@email.com", "A+", "Active"),
        ("Rahul", "V.", "rahul.v@email.com", "B+", "Active"),
        ("Divya", "M.", "divya.m@email.com", "AB+", "Active"),
        ("Sanjay", "P.", "sanjay.p@email.com", "O-", "Active"),
        ("Anita", "R.", "anita.r@email.com", "A-", "Active"),
        ("Suresh", "B.", "suresh.b@email.com", "O+", "Active"),
        ("Bhavani", "K.", "bhavani.k@email.com", "B+", "Active"),
        ("Karthik", "S.", "karthik.s@email.com", "A+", "Active"),
        ("Neha", "G.", "neha.g@email.com", "O+", "Active"),
        ("Manoj", "D.", "manoj.d@email.com", "AB+", "Active"),
        ("Pradeep", "T.", "pradeep.t@email.com", "B-", "Active"),
        ("Sunitha", "M.", "sunitha.m@email.com", "O-", "Active"),
        ("Harish", "R.", "harish.r@email.com", "A+", "Active"),
        ("Geetha", "L.", "geetha.l@email.com", "B+", "Active"),
        ("Vijay", "N.", "vijay.n@email.com", "O+", "Active"),
        ("Swathi", "P.", "swathi.p@email.com", "A-", "Active"),
        ("Rakesh", "M.", "rakesh.m@email.com", "AB-", "Active")
    ]
    
    # Get all doctors for assignment
    all_docs = db.query(User).filter(User.roles.any(Role.name == "Doctor")).all()
    if not all_docs:
        all_docs = [dr1, dr2]

    for idx, (fn, ln, email, bg, status_str) in enumerate(patient_names):
        p_user = db.query(User).filter(User.email == email).first()
        if not p_user:
            assigned_doc = all_docs[idx % len(all_docs)] if all_docs else None
            doc_name_str = f"Dr. {assigned_doc.first_name} {assigned_doc.last_name}" if assigned_doc else "Dr. Rohan Sharma"
            p_user = User(
                email=email,
                password_hash=hash_password("DemoPatient123!"),
                first_name=fn,
                last_name=ln,
                date_of_birth=f"19{80 + (idx % 20)}-0{(idx % 9) + 1}-15",
                gender="Male" if idx % 2 == 0 else "Female",
                phone_number=f"+91-9848{idx:06d}",
                is_active=True,
                is_verified=True,
                roles=[roles["Patient"]],
                blood_group=bg,
                primary_care_physician=f"{doc_name_str} (Specialist)",
                pcp_contact="+91-891-2888888"
            )
            db.add(p_user)
            db.commit()
            db.refresh(p_user)

            # Add vitals (BP, Sugar, O2 Saturation levels)
            db.add(Vitals(
                user_id=p_user.id,
                recorded_at=now - timedelta(days=idx),
                systolic_bp=115 + (idx % 25),
                diastolic_bp=75 + (idx % 15),
                weight_kg=65.0 + (idx % 20),
                height_cm=170.0,
                blood_sugar_mgdl=88 + (idx % 40),
                pulse_bpm=68 + (idx % 20),
                oxygen_saturation=97 + (idx % 3),
                temperature_c=36.6
            ))

            # Add appointments: both historical completed and upcoming scheduled with various doctors
            for a_idx, doc in enumerate(all_docs[:3]):
                d_name = f"Dr. {doc.first_name} {doc.last_name}"
                db.add(Appointment(
                    user_id=p_user.id,
                    doctor_name=d_name,
                    specialty="Specialty Care",
                    appointment_date=now - timedelta(days=(a_idx + 1) * 20 + idx),
                    status="Completed",
                    location="Demo Healthcare Network, Visakhapatnam",
                    notes="Historical outpatient checkup and vitals review."
                ))
            # Upcoming scheduled appointment for Dr. Rohan or Dr. Priya
            target_doc = dr1 if idx % 2 == 0 else dr2
            if target_doc:
                db.add(Appointment(
                    user_id=p_user.id,
                    doctor_name=f"Dr. {target_doc.first_name} {target_doc.last_name}",
                    specialty="Urology" if idx % 2 == 0 else "Neurology",
                    appointment_date=now + timedelta(days=(idx % 7) + 1, hours=(idx % 8) + 9),
                    status="Confirmed",
                    location="Demo Healthcare Network, Visakhapatnam",
                    notes="Scheduled follow-up consultation and treatment review."
                ))

    db.commit()
    logger.info("Bulk enterprise seeding completed: 10 Specialists and 25 Patients with extensive appointment histories.")
