from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import pandas as pd
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini Pro API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load the Gemini Pro model
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Initialize SQLite database for Doctor Recommendation Chatbot
def initialize_database():
    # Connect to the SQLite database
    conn = sqlite3.connect("doctor_recommendations.db")
    cursor = conn.cursor()

    # Drop the existing doctors table if it exists (to avoid schema mismatches)
    cursor.execute("DROP TABLE IF EXISTS doctors")

    # Recreate the doctors table with the correct columns
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id INTEGER PRIMARY KEY,
        doctor_identity_number TEXT NOT NULL,
        doctor_name TEXT NOT NULL,
        symptom_name TEXT NOT NULL,
        specialization TEXT NOT NULL,
        contact TEXT NOT NULL,
        email TEXT NOT NULL,
        hospital_name TEXT NOT NULL,
        hospital_location TEXT NOT NULL
    )
    ''')

    # Add sample data if the table is empty (preventing duplicates)
    cursor.execute("SELECT COUNT(*) FROM doctors")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO doctors (doctor_identity_number, doctor_name, symptom_name, specialization, contact, email, hospital_name, hospital_location) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            ('8751','Dr. Arjun Rao', 'blurred vision, eye pain, redness, floaters, cataracts, glaucoma, dry eyes, double vision, sensitivity to light, eye infections', 'Ophthalmologist', '9199210246', 'dr.arjun.rao@hospital.com', 'Apollo BGS Hospitals', 'Adichunchanagiri Road\nMysuru, Karnataka 570023\nIndia'),
            ('8986','Dr. B. C. Roy', 'fever, cough, ear infections, abdominal pain, diarrhea, rashes, growth delays, asthma, colic, vaccination side effects', 'Pediatrician', '9578974941', 'dr.b.c.roy@hospital.com', 'KLE Hospital', 'Nehru Nagar\nBelagavi, Karnataka 590010\nIndia'),
            ('4854', 'Dr. S. K. Sarin', 'blurred vision, eye pain, redness, floaters, cataracts, glaucoma, dry eyes, double vision, sensitivity to light, eye infections', 'Ophthalmologist', '9716140332', 'dr.s.k.sarin@hospital.com', 'KMC Hospital', 'Ambedkar Circle\nMangalore, Karnataka 575001\nIndia'),
            ('9654','Dr. Randeep Guleria', 'headaches, dizziness, seizures, memory loss, numbness, paralysis, tremors, migraines, muscle weakness, cognitive disorders', 'Neurologist', '9615202590', 'dr.randeep.guleria@hospital.com', 'KLE Hospital', 'Nehru Nagar\nBelagavi, Karnataka 590010\nIndia'),
            ('8726','Dr. Kavita Patil', 'acne, eczema, psoriasis, skin rashes, warts, fungal infections, rosacea, skin cancer, sunburn, dermatitis', 'Dermatologist', '9581928767', 'dr.kavita.patil@hospital.com', 'BGS Gleneagles Global Hospital', 'Kengeri\nBengaluru, Karnataka 560060\nIndia'),
            ('2145','Dr. Sudhansu Bhattacharyya', 'pre-surgery evaluations, pain management, anesthesia reactions, chronic pain, nerve blocks, sedation for procedures, post-surgical pain, regional anesthesia', 'Anesthesiologist', '9323550063', 'dr.sudhansu.bhattacharyya@hospital.com', 'Vinayaka Hospital', 'Vinoba Nagar\nShivamogga, Karnataka 577204\nIndia'),
            ('8759', 'Dr. Sudhansu Bhattacharyya', 'lumps, unexplained weight loss, persistent fatigue, abnormal bleeding, chronic pain, swelling, skin changes, difficulty swallowing, persistent cough, night sweats, frequent infections, anemia, persistent indigestion, abnormal test results, swollen lymph nodes', 'Oncologist', '9928159343', 'dr..sudhansu.bhattacharyya@hospital.com', 'KLE Hospital', 'Nehru Nagar\nBelagavi, Karnataka 590010\nIndia') ,
            ('6932', 'Dr. Randeep Guleria', 'anemia, fatigue, pale skin, easy bruising, excessive bleeding, blood clots, swollen lymph nodes, infections, low platelet count, bone marrow problems, leukemia, sickle cell disease, thalassemia, bleeding disorders, iron deficiency', 'Hematologist', '9934724094', 'dr..randeep.guleria@hospital.com', 'St. John’s Medical College and Hospital', 'Sarjapur Road\nBengaluru, Karnataka 560034\nIndia') ,
            ('9508', 'Dr. Padmavati Sivaramakrishna Iyer', 'pain management needs, pre-surgery assessments, post-surgery recovery, chronic pain issues, numbness for surgery, sedation, monitoring during operations, spinal anesthesia, epidurals, critical care, pain relief during labor, nerve blocks, emergency pain relief, breathing support, anesthesia for dental procedures', 'Anesthesiologist', '9814157131', 'dr..padmavati.sivaramakrishna.iyer@hospital.com', 'Manipal Hospital', 'HAL Old Airport Road\nBengaluru, Karnataka 560017\nIndia') ,
            ('4099', 'Dr. Sunita Naik', 'severe headaches, brain tumors, dizziness, seizures, memory loss, numbness or tingling, paralysis, tremors, migraines, muscle weakness, speech difficulties, cognitive problems, movement disorders, difficulty walking, stroke symptoms', 'Neurologist', '9259351330', 'dr..sunita.naik@hospital.com', 'Karnataka Institute of Medical Sciences', 'PB Road\nHubballi, Karnataka 580022\nIndia') ,
            ('9644', 'Dr. Ravi Kumar', 'acne, skin rashes, dry skin, eczema, psoriasis, moles, skin discoloration, warts, hair loss, dandruff, nail problems, skin allergies, skin infections, wrinkles, scars', 'Dermatologist', '9317727739', 'dr..ravi.kumar@hospital.com', 'Adichunchanagiri Institute of Medical Sciences', 'B.G. Nagara\nMandya, Karnataka 571448\nIndia') ,
            ('2945', 'Dr. Prashant Sharma', 'severe headaches, brain tumors, dizziness, seizures, memory loss, numbness or tingling, paralysis, tremors, migraines, muscle weakness, speech difficulties, cognitive problems, movement disorders, difficulty walking, stroke symptoms', 'Neurologist', '9206422665', 'dr..prashant.sharma@hospital.com', 'Kasturba Medical College and Hospital', 'Tiger Circle Road\nManipal, Karnataka 576104\nIndia') ,
            ('7521', 'Dr. Anjali Kulkarni', 'lumps, unexplained weight loss, persistent fatigue, abnormal bleeding, chronic pain, swelling, skin changes, difficulty swallowing, persistent cough, night sweats, frequent infections, anemia, persistent indigestion, abnormal test results, swollen lymph nodes', 'Oncologist', '9296574973', 'dr..anjali.kulkarni@hospital.com', 'Shimoga Institute of Medical Sciences', 'Sagar Road\nShivamogga, Karnataka 577201\nIndia') ,
            ('5396', 'Dr. Kavita Patil', 'joint pain, broken bones, arthritis, back pain, sports injuries, sprains, ligament tears, bone deformities, dislocations, scoliosis, knee pain, hip pain, tendon injuries, carpal tunnel syndrome, shoulder stiffness', 'Orthopedic Surgeon', '9724548735', 'dr..kavita.patil@hospital.com', 'St. John’s Medical College and Hospital', 'Sarjapur Road\nBengaluru, Karnataka 560034\nIndia') ,
            ('2526', 'Dr. Sunita Naik', 'anxiety, depression, mood swings, stress, insomnia, panic attacks, phobias, PTSD, OCD, bipolar disorder, hallucinations, suicidal thoughts, eating disorders, personality disorders, anger issues', 'Psychiatrist', '9627847122', 'dr..sunita.naik@hospital.com', 'Adichunchanagiri Institute of Medical Sciences', 'B.G. Nagara\nMandya, Karnataka 571448\nIndia') ,
            ('7940', 'Dr. P. Raghuram', 'swelling in legs or feet, blood in urine, foamy urine, high blood pressure, kidney stones, fatigue, nausea, frequent urination at night, chronic kidney disease, difficulty concentrating, decreased appetite, back pain near kidneys, electrolyte imbalance, kidney infections, dialysis needs', 'Nephrologist', '9321746455', 'dr..p..raghuram@hospital.com', 'BGS Gleneagles Global Hospital', 'Kengeri\nBengaluru, Karnataka 560060\nIndia') ,
            ('6228', 'Dr. B. C. Roy', 'toothache, gum bleeding, cavities, bad breath, sensitivity to hot or cold, oral infections, jaw pain, wisdom teeth issues, teeth cleaning, braces, mouth ulcers, dry mouth, broken teeth, missing teeth, tooth decay', 'Dentist', '9360237664', 'dr..b..c..roy@hospital.com', 'Chigateri District Hospital', 'Near Davangere University\nDavangere, Karnataka 577002\nIndia') ,
            ('1113', 'Dr. Meena Menon', 'mobility issues, memory loss, frequent falls, arthritis, chronic diseases, osteoporosis, frailty, depression in the elderly, hearing problems, visual impairments, medication management, dementia, sleep issues, urinary incontinence, cardiovascular diseases', 'Geriatrician', '9670921971', 'dr..meena.menon@hospital.com', 'S. S. Institute of Medical Sciences', 'NH-4 Bypass\nDavangere, Karnataka 577005\nIndia') ,
            ('2914', 'Dr. Shalini Desai', 'frequent urination, excessive thirst, weight gain, weight loss, hair thinning, fatigue, hormonal imbalances, slow growth, irregular periods, diabetes symptoms, thyroid problems, infertility, osteoporosis, excessive sweating, adrenal issues', 'Endocrinologist', '9849110349', 'dr..shalini.desai@hospital.com', 'SDM College of Medical Sciences & Hospital', 'Manjushree Nagar\nDharwad, Karnataka 580009\nIndia') ,
            ('5554', 'Dr. Shalini Desai', 'lumps, unexplained weight loss, persistent fatigue, abnormal bleeding, chronic pain, swelling, skin changes, difficulty swallowing, persistent cough, night sweats, frequent infections, anemia, persistent indigestion, abnormal test results, swollen lymph nodes', 'Oncologist', '9891174632', 'dr..shalini.desai@hospital.com', 'Manipal Hospital', 'HAL Old Airport Road\nBengaluru, Karnataka 560017\nIndia') ,
            ('8820', 'Dr. P. Raghuram', 'frequent urination, excessive thirst, weight gain, weight loss, hair thinning, fatigue, hormonal imbalances, slow growth, irregular periods, diabetes symptoms, thyroid problems, infertility, osteoporosis, excessive sweating, adrenal issues', 'Endocrinologist', '9813306359', 'dr..p..raghuram@hospital.com', 'S. S. Institute of Medical Sciences', 'NH-4 Bypass\nDavangere, Karnataka 577005\nIndia') ,
            ('9319', 'Dr. Randeep Guleria', 'anxiety, depression, mood swings, stress, insomnia, panic attacks, phobias, PTSD, OCD, bipolar disorder, hallucinations, suicidal thoughts, eating disorders, personality disorders, anger issues', 'Psychiatrist', '9502150609', 'dr..randeep.guleria@hospital.com', 'KMC Hospital', 'Ambedkar Circle\nMangalore, Karnataka 575001\nIndia') ,
            ('1979', 'Dr. Vikas Iyer', 'swelling in legs or feet, blood in urine, foamy urine, high blood pressure, kidney stones, fatigue, nausea, frequent urination at night, chronic kidney disease, difficulty concentrating, decreased appetite, back pain near kidneys, electrolyte imbalance, kidney infections, dialysis needs', 'Nephrologist', '9193514898', 'dr..vikas.iyer@hospital.com', 'St. John’s Medical College and Hospital', 'Sarjapur Road\nBengaluru, Karnataka 560034\nIndia') ,
            ('8785', 'Dr. Devi Prasad Shetty', 'irregular periods, pelvic pain, vaginal discharge, urinary infections, infertility, pregnancy care, menopause symptoms, hormonal imbalances, breast lumps, painful periods, endometriosis, PCOS, abnormal bleeding, pelvic infections, sexual health concerns', 'Gynecologist', '9698076194', 'dr..devi.prasad.shetty@hospital.com', 'SDM College of Medical Sciences & Hospital', 'Manjushree Nagar\nDharwad, Karnataka 580009\nIndia') ,
            ('1732', 'Dr. Mahesh Gowda', 'fractures, internal injuries, tumors, abnormal growths, infections, lung conditions, heart conditions, brain abnormalities, gastrointestinal issues, spinal problems, cancer screening, bone density issues, unexplained pain, swollen organs, imaging needs', 'Radiologist', '9137575205', 'dr..mahesh.gowda@hospital.com', 'Sparsh Hospital', 'Infantry Road\nBengaluru, Karnataka 560001\nIndia') ,
            ('7384', 'Dr. Sudhansu Bhattacharyya', 'blurry vision, eye pain, red eyes, dry eyes, watery eyes, sensitivity to light, floaters, double vision, loss of vision, eyelid problems, cataracts, glaucoma, macular degeneration, eye injuries, eye infections', 'Ophthalmologist', '9229888356', 'dr..sudhansu.bhattacharyya@hospital.com', 'Manipal Hospital', 'HAL Old Airport Road\nBengaluru, Karnataka 560017\nIndia') ,
            ('6642', 'Dr. P. Raghuram', 'stomach pain, bloating, heartburn, indigestion, constipation, diarrhea, blood in stool, acid reflux, difficulty swallowing, nausea, vomiting, gas issues, ulcers, liver problems, gallstones', 'Gastroenterologist', '9861564938', 'dr..p..raghuram@hospital.com', 'Apollo BGS Hospitals', 'Adichunchanagiri Road\nMysuru, Karnataka 570023\nIndia') ,
            ('3822', 'Dr. Vandana Shiva', 'anxiety, depression, mood swings, stress, insomnia, panic attacks, phobias, PTSD, OCD, bipolar disorder, hallucinations, suicidal thoughts, eating disorders, personality disorders, anger issues', 'Psychiatrist', '9671063273', 'dr..vandana.shiva@hospital.com', 'Dr. TMA Pai Hospital', 'Udupi-Manipal Highway\nManipal, Karnataka 576104\nIndia') ,
            ('8497', 'Dr. S. K. Sarin', 'scars, burns, deformities, nose reshaping, breast reconstruction, facial reconstruction, cleft lip or palate, cosmetic issues, skin grafting, excess skin removal, liposuction, wrinkles, hand injuries, ear reshaping, facial asymmetry', 'Plastic Surgeon', '9132284452', 'dr..s..k..sarin@hospital.com', 'KMC Hospital', 'Ambedkar Circle\nMangalore, Karnataka 575001\nIndia') ,
            ('9618', 'Dr. S. K. Sarin', 'fractures, internal injuries, tumors, abnormal growths, infections, lung conditions, heart conditions, brain abnormalities, gastrointestinal issues, spinal problems, cancer screening, bone density issues, unexplained pain, swollen organs, imaging needs', 'Radiologist', '9986645240', 'dr..s..k..sarin@hospital.com', 'SDM College of Medical Sciences & Hospital', 'Manjushree Nagar\nDharwad, Karnataka 580009\nIndia') ,
            ('6504', 'Dr. Ravi Kumar', 'urinary tract infections, difficulty urinating, blood in urine, kidney stones, incontinence, prostate problems, pain during urination, frequent urination, bladder control issues, male infertility, testicular pain, urinary retention, urinary infections, pelvic pain, erectile dysfunction', 'Urologist', '9584011240', 'dr..ravi.kumar@hospital.com', 'Kasturba Medical College and Hospital', 'Tiger Circle Road\nManipal, Karnataka 576104\nIndia') ,
            ('7742', 'Dr. Arjun Rao', 'ear pain, hearing loss, nasal congestion, throat pain, sinus infections, balance issues, snoring, voice problems, tonsillitis, tinnitus, allergies, deviated septum, speech difficulties, chronic cough, ear infections', 'ENT Specialist', '9322422401', 'dr..arjun.rao@hospital.com', 'Vinayaka Hospital', 'Vinoba Nagar\nShivamogga, Karnataka 577204\nIndia') ,
            ('4451', 'Dr. B. C. Roy', 'blurry vision, eye pain, red eyes, dry eyes, watery eyes, sensitivity to light, floaters, double vision, loss of vision, eyelid problems, cataracts, glaucoma, macular degeneration, eye injuries, eye infections', 'Ophthalmologist', '9699510358', 'dr..b..c..roy@hospital.com', 'St. John’s Medical College and Hospital', 'Sarjapur Road\nBengaluru, Karnataka 560034\nIndia') ,
            ('9768', 'Dr. Swati Piramal', 'chest pain, breathlessness, fatigue, irregular heartbeats, high blood pressure, dizziness, fainting, chest tightness, heart failure, swollen ankles or feet, palpitations, heart attack symptoms, angina, heart murmurs, hypertension', 'Cardiologist', '9445850741', 'dr..swati.piramal@hospital.com', 'Karnataka Institute of Medical Sciences', 'PB Road\nHubballi, Karnataka 580022\nIndia') ,
            ('8105', 'Dr. Ravi Kumar', 'mobility issues, memory loss, frequent falls, arthritis, chronic diseases, osteoporosis, frailty, depression in the elderly, hearing problems, visual impairments, medication management, dementia, sleep issues, urinary incontinence, cardiovascular diseases', 'Geriatrician', '9763247613', 'dr..ravi.kumar@hospital.com', 'JSS Hospital', 'MG Road\nMysuru, Karnataka 570004\nIndia') ,
            ('5922', 'Dr. Shanta V.', 'fever, body aches, colds, cough, flu, stomach pain, headaches, fatigue, minor injuries, allergies, infections, high blood pressure, diabetes symptoms, general weakness, preventive health care', 'General Physician', '9496737848', 'dr..shanta.v.@hospital.com', 'Chigateri District Hospital', 'Near Davangere University\nDavangere, Karnataka 577002\nIndia') ,
            ('4316', 'Dr. Arun Kurian Thomas', 'toothache, gum bleeding, cavities, bad breath, sensitivity to hot or cold, oral infections, jaw pain, wisdom teeth issues, teeth cleaning, braces, mouth ulcers, dry mouth, broken teeth, missing teeth, tooth decay', 'Dentist', '9487681484', 'dr..arun.kurian.thomas@hospital.com', 'Karnataka Institute of Medical Sciences', 'PB Road\nHubballi, Karnataka 580022\nIndia') ,
            ('6450', 'Dr. Randeep Guleria', 'anemia, fatigue, pale skin, easy bruising, excessive bleeding, blood clots, swollen lymph nodes, infections, low platelet count, bone marrow problems, leukemia, sickle cell disease, thalassemia, bleeding disorders, iron deficiency', 'Hematologist', '9224256755', 'dr..randeep.guleria@hospital.com', 'KMC Hospital', 'Ambedkar Circle\nMangalore, Karnataka 575001\nIndia') ,
            ('1543', 'Dr. Vikas Iyer', 'frequent urination, excessive thirst, weight gain, weight loss, hair thinning, fatigue, hormonal imbalances, slow growth, irregular periods, diabetes symptoms, thyroid problems, infertility, osteoporosis, excessive sweating, adrenal issues', 'Endocrinologist', '9481052055', 'dr..vikas.iyer@hospital.com', 'KMC Hospital', 'Ambedkar Circle\nMangalore, Karnataka 575001\nIndia') ,
            ('5454', 'Dr. Mahesh Gowda', 'irregular periods, pelvic pain, vaginal discharge, urinary infections, infertility, pregnancy care, menopause symptoms, hormonal imbalances, breast lumps, painful periods, endometriosis, PCOS, abnormal bleeding, pelvic infections, sexual health concerns', 'Gynecologist', '9703823771', 'dr..mahesh.gowda@hospital.com', 'BGS Gleneagles Global Hospital', 'Kengeri\nBengaluru, Karnataka 560060\nIndia') ,
            ('1310', 'Dr. Prathap C. Reddy', 'frequent urination, excessive thirst, weight gain, weight loss, hair thinning, fatigue, hormonal imbalances, slow growth, irregular periods, diabetes symptoms, thyroid problems, infertility, osteoporosis, excessive sweating, adrenal issues', 'Endocrinologist', '9684627028', 'dr..prathap.c..reddy@hospital.com', 'SDM College of Medical Sciences & Hospital', 'Manjushree Nagar\nDharwad, Karnataka 580009\nIndia') ,
            ('7771', 'Dr. Vikas Iyer', 'fever in children, ear infections, cough, colds, flu, developmental delays, skin rashes, stomach pain, vomiting, diarrhea, asthma symptoms, behavioral issues, vaccination needs, growth concerns, allergies in children', 'Pediatrician', '9351394042', 'dr..vikas.iyer@hospital.com', 'Shimoga Institute of Medical Sciences', 'Sagar Road\nShivamogga, Karnataka 577201\nIndia') ,
            ('5751', 'Dr. Randeep Guleria', 'anemia, fatigue, pale skin, easy bruising, excessive bleeding, blood clots, swollen lymph nodes, infections, low platelet count, bone marrow problems, leukemia, sickle cell disease, thalassemia, bleeding disorders, iron deficiency', 'Hematologist', '9287453912', 'dr..randeep.guleria@hospital.com', 'Apollo BGS Hospitals', 'Adichunchanagiri Road\nMysuru, Karnataka 570023\nIndia') ,
            ('6143', 'Dr. Mahesh Gowda', 'anxiety, depression, mood swings, stress, insomnia, panic attacks, phobias, PTSD, OCD, bipolar disorder, hallucinations, suicidal thoughts, eating disorders, personality disorders, anger issues', 'Psychiatrist', '9742261971', 'dr..mahesh.gowda@hospital.com', 'Shimoga Institute of Medical Sciences', 'Sagar Road\nShivamogga, Karnataka 577201\nIndia') ,
            ('3068', 'Dr. Prashant Sharma', 'frequent infections, allergic reactions, autoimmune diseases, asthma, eczema, hay fever, hives, immunodeficiency disorders, food allergies, swelling after insect bites, recurrent colds, chronic sinus infections, fatigue from weak immunity, unusual infections, vaccine-related issues', 'Immunologist', '9734185306', 'dr..prashant.sharma@hospital.com', 'JSS Hospital', 'MG Road\nMysuru, Karnataka 570004\nIndia') ,
            ('5332', 'Dr. B. C. Roy', 'stomach pain, bloating, heartburn, indigestion, constipation, diarrhea, blood in stool, acid reflux, difficulty swallowing, nausea, vomiting, gas issues, ulcers, liver problems, gallstones', 'Gastroenterologist', '9134479258', 'dr..b..c..roy@hospital.com', 'SDM College of Medical Sciences & Hospital', 'Manjushree Nagar\nDharwad, Karnataka 580009\nIndia') ,
            ('6666', 'Dr. Gagandeep Kang', 'frequent urination, excessive thirst, weight gain, weight loss, hair thinning, fatigue, hormonal imbalances, slow growth, irregular periods, diabetes symptoms, thyroid problems, infertility, osteoporosis, excessive sweating, adrenal issues', 'Endocrinologist', '9119667947', 'dr..gagandeep.kang@hospital.com', 'S. S. Institute of Medical Sciences', 'NH-4 Bypass\nDavangere, Karnataka 577005\nIndia') ,
            ('1215', 'Dr. Shanta V.', 'chest pain, breathlessness, fatigue, irregular heartbeats, high blood pressure, dizziness, fainting, chest tightness, heart failure, swollen ankles or feet, palpitations, heart attack symptoms, angina, heart murmurs, hypertension', 'Cardiologist', '9965284651', 'dr..shanta.v.@hospital.com', 'Kasturba Medical College and Hospital', 'Tiger Circle Road\nManipal, Karnataka 576104\nIndia') ,
            ('8694', 'Dr. Balamurali Ambati', 'frequent infections, allergic reactions, autoimmune diseases, asthma, eczema, hay fever, hives, immunodeficiency disorders, food allergies, swelling after insect bites, recurrent colds, chronic sinus infections, fatigue from weak immunity, unusual infections, vaccine-related issues', 'Immunologist', '9408535485', 'dr..balamurali.ambati@hospital.com', 'S. S. Institute of Medical Sciences', 'NH-4 Bypass\nDavangere, Karnataka 577005\nIndia') ,
            ('4387', 'Dr. Naresh Trehan', 'irregular periods, pelvic pain, vaginal discharge, urinary infections, infertility, pregnancy care, menopause symptoms, hormonal imbalances, breast lumps, painful periods, endometriosis, PCOS, abnormal bleeding, pelvic infections, sexual health concerns', 'Gynecologist', '9113486746', 'dr..naresh.trehan@hospital.com', 'Kasturba Medical College and Hospital', 'Tiger Circle Road\nManipal, Karnataka 576104\nIndia') ,
            ('9512', 'Dr. Naresh Trehan', 'severe headaches, brain tumors, dizziness, seizures, memory loss, numbness or tingling, paralysis, tremors, migraines, muscle weakness, speech difficulties, cognitive problems, movement disorders, difficulty walking, stroke symptoms', 'Neurologist', '9491742959', 'dr..naresh.trehan@hospital.com', 'KLE Hospital', 'Nehru Nagar\nBelagavi, Karnataka 590010\nIndia') ,
            ('5961', 'Dr. Vikas Iyer', 'lumps, unexplained weight loss, persistent fatigue, abnormal bleeding, chronic pain, swelling, skin changes, difficulty swallowing, persistent cough, night sweats, frequent infections, anemia, persistent indigestion, abnormal test results, swollen lymph nodes', 'Oncologist', '9138440484', 'dr..vikas.iyer@hospital.com', 'Shimoga Institute of Medical Sciences', 'Sagar Road\nShivamogga, Karnataka 577201\nIndia') ,
            ('5124', 'Dr. Mahesh Gowda', 'scars, burns, deformities, nose reshaping, breast reconstruction, facial reconstruction, cleft lip or palate, cosmetic issues, skin grafting, excess skin removal, liposuction, wrinkles, hand injuries, ear reshaping, facial asymmetry', 'Plastic Surgeon', '9587902258', 'dr..mahesh.gowda@hospital.com', 'Manipal Hospital', 'HAL Old Airport Road\nBengaluru, Karnataka 560017\nIndia') ,
            ('2015', 'Dr. Sudhansu Bhattacharyya', 'frequent infections, allergic reactions, autoimmune diseases, asthma, eczema, hay fever, hives, immunodeficiency disorders, food allergies, swelling after insect bites, recurrent colds, chronic sinus infections, fatigue from weak immunity, unusual infections, vaccine-related issues', 'Immunologist', '9359263609', 'dr..sudhansu.bhattacharyya@hospital.com', 'S. S. Institute of Medical Sciences', 'NH-4 Bypass\nDavangere, Karnataka 577005\nIndia') ,
            ('2856', 'Dr. Priya Shetty', 'anxiety, depression, mood swings, stress, insomnia, panic attacks, phobias, PTSD, OCD, bipolar disorder, hallucinations, suicidal thoughts, eating disorders, personality disorders, anger issues', 'Psychiatrist', '9876906057', 'dr..priya.shetty@hospital.com', 'Adichunchanagiri Institute of Medical Sciences', 'B.G. Nagara\nMandya, Karnataka 571448\nIndia') ,
            ('8247', 'Dr. Sudhansu Bhattacharyya', 'anxiety, depression, mood swings, stress, insomnia, panic attacks, phobias, PTSD, OCD, bipolar disorder, hallucinations, suicidal thoughts, eating disorders, personality disorders, anger issues', 'Psychiatrist', '9741042445', 'dr..sudhansu.bhattacharyya@hospital.com', 'SDM College of Medical Sciences & Hospital', 'Manjushree Nagar\nDharwad, Karnataka 580009\nIndia') ,
            ('2441', 'Dr. Arun Kurian Thomas', 'stomach pain, bloating, heartburn, indigestion, constipation, diarrhea, blood in stool, acid reflux, difficulty swallowing, nausea, vomiting, gas issues, ulcers, liver problems, gallstones', 'Gastroenterologist', '9527400907', 'dr..arun.kurian.thomas@hospital.com', 'Manipal Hospital', 'HAL Old Airport Road\nBengaluru, Karnataka 560017\nIndia') ,
            ('5570', 'Dr. Anjali Kulkarni', 'lumps, unexplained weight loss, persistent fatigue, abnormal bleeding, chronic pain, swelling, skin changes, difficulty swallowing, persistent cough, night sweats, frequent infections, anemia, persistent indigestion, abnormal test results, swollen lymph nodes', 'Oncologist', '9882580570', 'dr..anjali.kulkarni@hospital.com', 'Karnataka Institute of Medical Sciences', 'PB Road\nHubballi, Karnataka 580022\nIndia') ,
            ('5387', 'Dr. Naresh Trehan', 'fever in children, ear infections, cough, colds, flu, developmental delays, skin rashes, stomach pain, vomiting, diarrhea, asthma symptoms, behavioral issues, vaccination needs, growth concerns, allergies in children', 'Pediatrician', '9915853768', 'dr..naresh.trehan@hospital.com', 'Kasturba Medical College and Hospital', 'Tiger Circle Road\nManipal, Karnataka 576104\nIndia') ,
            ('3693', 'Dr. Ravi Kumar', 'scars, burns, deformities, nose reshaping, breast reconstruction, facial reconstruction, cleft lip or palate, cosmetic issues, skin grafting, excess skin removal, liposuction, wrinkles, hand injuries, ear reshaping, facial asymmetry', 'Plastic Surgeon', '9890297957', 'dr..ravi.kumar@hospital.com', 'Victoria Hospital', 'K.R. Market\nBengaluru, Karnataka 560002\nIndia') ,
            ('5215', 'Dr. K. K. Aggarwal', 'stomach pain, bloating, heartburn, indigestion, constipation, diarrhea, blood in stool, acid reflux, difficulty swallowing, nausea, vomiting, gas issues, ulcers, liver problems, gallstones', 'Gastroenterologist', '9731815574', 'dr..k..k..aggarwal@hospital.com', 'Kasturba Medical College and Hospital', 'Tiger Circle Road\nManipal, Karnataka 576104\nIndia') ,
            ('3509', 'Dr. Meena Menon', 'chest pain, breathlessness, fatigue, irregular heartbeats, high blood pressure, dizziness, fainting, chest tightness, heart failure, swollen ankles or feet, palpitations, heart attack symptoms, angina, heart murmurs, hypertension', 'Cardiologist', '9322435374', 'dr..meena.menon@hospital.com', 'Kasturba Medical College and Hospital', 'Tiger Circle Road\nManipal, Karnataka 576104\nIndia') ,
            ('1839', 'Dr. Vikas Iyer', 'blurry vision, eye pain, red eyes, dry eyes, watery eyes, sensitivity to light, floaters, double vision, loss of vision, eyelid problems, cataracts, glaucoma, macular degeneration, eye injuries, eye infections', 'Ophthalmologist', '9160928835', 'dr..vikas.iyer@hospital.com', 'SDM College of Medical Sciences & Hospital', 'Manjushree Nagar\nDharwad, Karnataka 580009\nIndia') ,
            ('7520', 'Dr. Vandana Shiva', 'severe headaches, brain tumors, dizziness, seizures, memory loss, numbness or tingling, paralysis, tremors, migraines, muscle weakness, speech difficulties, cognitive problems, movement disorders, difficulty walking, stroke symptoms', 'Neurologist', '9974120478', 'dr..vandana.shiva@hospital.com', 'Dr. TMA Pai Hospital', 'Udupi-Manipal Highway\nManipal, Karnataka 576104\nIndia') ,
            ('8465', 'Dr. Devi Prasad Shetty', 'mobility issues, memory loss, frequent falls, arthritis, chronic diseases, osteoporosis, frailty, depression in the elderly, hearing problems, visual impairments, medication management, dementia, sleep issues, urinary incontinence, cardiovascular diseases', 'Geriatrician', '9121788329', 'dr..devi.prasad.shetty@hospital.com', 'BGS Gleneagles Global Hospital', 'Kengeri\nBengaluru, Karnataka 560060\nIndia') ,
            ('1282', 'Dr. Meena Menon', 'swelling in legs or feet, blood in urine, foamy urine, high blood pressure, kidney stones, fatigue, nausea, frequent urination at night, chronic kidney disease, difficulty concentrating, decreased appetite, back pain near kidneys, electrolyte imbalance, kidney infections, dialysis needs', 'Nephrologist', '9104669969', 'dr..meena.menon@hospital.com', 'BGS Gleneagles Global Hospital', 'Kengeri\nBengaluru, Karnataka 560060\nIndia') ,
            ('6873', 'Dr. Gagandeep Kang', 'irregular periods, pelvic pain, vaginal discharge, urinary infections, infertility, pregnancy care, menopause symptoms, hormonal imbalances, breast lumps, painful periods, endometriosis, PCOS, abnormal bleeding, pelvic infections, sexual health concerns', 'Gynecologist', '9707027229', 'dr..gagandeep.kang@hospital.com', 'JSS Hospital', 'MG Road\nMysuru, Karnataka 570004\nIndia') ,
            ('6459', 'Dr. Meena Menon', 'irregular periods, pelvic pain, vaginal discharge, urinary infections, infertility, pregnancy care, menopause symptoms, hormonal imbalances, breast lumps, painful periods, endometriosis, PCOS, abnormal bleeding, pelvic infections, sexual health concerns', 'Gynecologist', '9341026093', 'dr..meena.menon@hospital.com', 'Adichunchanagiri Institute of Medical Sciences', 'B.G. Nagara\nMandya, Karnataka 571448\nIndia') ,
            ('4845', 'Dr. Padmavati Sivaramakrishna Iyer', 'chest pain, breathlessness, fatigue, irregular heartbeats, high blood pressure, dizziness, fainting, chest tightness, heart failure, swollen ankles or feet, palpitations, heart attack symptoms, angina, heart murmurs, hypertension', 'Cardiologist', '9825555847', 'dr..padmavati.sivaramakrishna.iyer@hospital.com', 'Manipal Hospital', 'HAL Old Airport Road\nBengaluru, Karnataka 560017\nIndia') ,
            ('9133', 'Dr. Ashok Seth', 'fractures, internal injuries, tumors, abnormal growths, infections, lung conditions, heart conditions, brain abnormalities, gastrointestinal issues, spinal problems, cancer screening, bone density issues, unexplained pain, swollen organs, imaging needs', 'Radiologist', '9217571147', 'dr..ashok.seth@hospital.com', 'Sparsh Hospital', 'Infantry Road\nBengaluru, Karnataka 560001\nIndia') ,
            ('2956', 'Dr. Swati Piramal', 'stomach pain, bloating, heartburn, indigestion, constipation, diarrhea, blood in stool, acid reflux, difficulty swallowing, nausea, vomiting, gas issues, ulcers, liver problems, gallstones', 'Gastroenterologist', '9130100352', 'dr..swati.piramal@hospital.com', 'St. John’s Medical College and Hospital', 'Sarjapur Road\nBengaluru, Karnataka 560034\nIndia') ,
            ('1157', 'Dr. A. Velumani', 'urinary tract infections, difficulty urinating, blood in urine, kidney stones, incontinence, prostate problems, pain during urination, frequent urination, bladder control issues, male infertility, testicular pain, urinary retention, urinary infections, pelvic pain, erectile dysfunction', 'Urologist', '9741956937', 'dr..a..velumani@hospital.com', 'Chigateri District Hospital', 'Near Davangere University\nDavangere, Karnataka 577002\nIndia') ,
            ('7130', 'Dr. P. Raghuram', 'blurry vision, eye pain, red eyes, dry eyes, watery eyes, sensitivity to light, floaters, double vision, loss of vision, eyelid problems, cataracts, glaucoma, macular degeneration, eye injuries, eye infections', 'Ophthalmologist', '9400596022', 'dr..p..raghuram@hospital.com', 'Vinayaka Hospital', 'Vinoba Nagar\nShivamogga, Karnataka 577204\nIndia') ,
            ('2567', 'Dr. Shalini Desai', 'irregular periods, pelvic pain, vaginal discharge, urinary infections, infertility, pregnancy care, menopause symptoms, hormonal imbalances, breast lumps, painful periods, endometriosis, PCOS, abnormal bleeding, pelvic infections, sexual health concerns', 'Gynecologist', '9464191481', 'dr..shalini.desai@hospital.com', 'Victoria Hospital', 'K.R. Market\nBengaluru, Karnataka 560002\nIndia') ,
            ('7374', 'Dr. Prashant Sharma', 'lumps, unexplained weight loss, persistent fatigue, abnormal bleeding, chronic pain, swelling, skin changes, difficulty swallowing, persistent cough, night sweats, frequent infections, anemia, persistent indigestion, abnormal test results, swollen lymph nodes', 'Oncologist', '9751688915', 'dr..prashant.sharma@hospital.com', 'Sparsh Hospital', 'Infantry Road\nBengaluru, Karnataka 560001\nIndia') ,
            ('9716', 'Dr. Sameer Reddy', 'anemia, fatigue, pale skin, easy bruising, excessive bleeding, blood clots, swollen lymph nodes, infections, low platelet count, bone marrow problems, leukemia, sickle cell disease, thalassemia, bleeding disorders, iron deficiency', 'Hematologist', '9264940383', 'dr..sameer.reddy@hospital.com', 'Apollo BGS Hospitals', 'Adichunchanagiri Road\nMysuru, Karnataka 570023\nIndia') ,
            ('4255', 'Dr. Padmavati Sivaramakrishna Iyer', 'toothache, gum bleeding, cavities, bad breath, sensitivity to hot or cold, oral infections, jaw pain, wisdom teeth issues, teeth cleaning, braces, mouth ulcers, dry mouth, broken teeth, missing teeth, tooth decay', 'Dentist', '9459447833', 'dr..padmavati.sivaramakrishna.iyer@hospital.com', 'Father Muller Medical College Hospital', 'Kankanady\nMangalore, Karnataka 575002\nIndia') ,
            ('9727', 'Dr. B. C. Roy', 'fractures, internal injuries, tumors, abnormal growths, infections, lung conditions, heart conditions, brain abnormalities, gastrointestinal issues, spinal problems, cancer screening, bone density issues, unexplained pain, swollen organs, imaging needs', 'Radiologist', '9440025273', 'dr..b..c..roy@hospital.com', 'Narayana Health City', 'Bommasandra Industrial Area\nBengaluru, Karnataka 560099\nIndia') ,
            ('4306', 'Dr. S. K. Sarin', 'stomach pain, bloating, heartburn, indigestion, constipation, diarrhea, blood in stool, acid reflux, difficulty swallowing, nausea, vomiting, gas issues, ulcers, liver problems, gallstones', 'Gastroenterologist', '9477725482', 'dr..s..k..sarin@hospital.com', 'Victoria Hospital', 'K.R. Market\nBengaluru, Karnataka 560002\nIndia') ,
            ('8524', 'Dr. Sunita Naik', 'toothache, gum bleeding, cavities, bad breath, sensitivity to hot or cold, oral infections, jaw pain, wisdom teeth issues, teeth cleaning, braces, mouth ulcers, dry mouth, broken teeth, missing teeth, tooth decay', 'Dentist', '9514532483', 'dr..sunita.naik@hospital.com', 'JSS Hospital', 'MG Road\nMysuru, Karnataka 570004\nIndia') ,
            ('6557', 'Dr. Arun Kurian Thomas', 'fever in children, ear infections, cough, colds, flu, developmental delays, skin rashes, stomach pain, vomiting, diarrhea, asthma symptoms, behavioral issues, vaccination needs, growth concerns, allergies in children', 'Pediatrician', '9939250434', 'dr..arun.kurian.thomas@hospital.com', 'BGS Gleneagles Global Hospital', 'Kengeri\nBengaluru, Karnataka 560060\nIndia') ,
            ('4691', 'Dr. Anjali Kulkarni', 'fractures, internal injuries, tumors, abnormal growths, infections, lung conditions, heart conditions, brain abnormalities, gastrointestinal issues, spinal problems, cancer screening, bone density issues, unexplained pain, swollen organs, imaging needs', 'Radiologist', '9896937708', 'dr..anjali.kulkarni@hospital.com', 'Apollo BGS Hospitals', 'Adichunchanagiri Road\nMysuru, Karnataka 570023\nIndia') ,
            ('5224', 'Dr. Ravi Kumar', 'blurry vision, eye pain, red eyes, dry eyes, watery eyes, sensitivity to light, floaters, double vision, loss of vision, eyelid problems, cataracts, glaucoma, macular degeneration, eye injuries, eye infections', 'Ophthalmologist', '9904675880', 'dr..ravi.kumar@hospital.com', 'SDM College of Medical Sciences & Hospital', 'Manjushree Nagar\nDharwad, Karnataka 580009\nIndia') ,
            ('3721', 'Dr. Sudhansu Bhattacharyya', 'disease diagnosis, biopsy analysis, abnormal blood test results, cancer detection, infections, chronic diseases, tissue analysis, organ dysfunction, laboratory testing issues, unexplained symptoms, genetic disorders, disease progression monitoring, infections in organs, rare conditions, tumor evaluation', 'Pathologist', '9811240486', 'dr..sudhansu.bhattacharyya@hospital.com', 'St. John’s Medical College and Hospital', 'Sarjapur Road\nBengaluru, Karnataka 560034\nIndia') ,
            ('1858', 'Dr. Vandana Shiva', 'scars, burns, deformities, nose reshaping, breast reconstruction, facial reconstruction, cleft lip or palate, cosmetic issues, skin grafting, excess skin removal, liposuction, wrinkles, hand injuries, ear reshaping, facial asymmetry', 'Plastic Surgeon', '9667691344', 'dr..vandana.shiva@hospital.com', 'Chigateri District Hospital', 'Near Davangere University\nDavangere, Karnataka 577002\nIndia') ,
            ('5110', 'Dr. Arun Kurian Thomas', 'disease diagnosis, biopsy analysis, abnormal blood test results, cancer detection, infections, chronic diseases, tissue analysis, organ dysfunction, laboratory testing issues, unexplained symptoms, genetic disorders, disease progression monitoring, infections in organs, rare conditions, tumor evaluation', 'Pathologist', '9802495417', 'dr..arun.kurian.thomas@hospital.com', 'BGS Gleneagles Global Hospital', 'Kengeri\nBengaluru, Karnataka 560060\nIndia') ,
            ('2317', 'Dr. Ashok Seth', 'scars, burns, deformities, nose reshaping, breast reconstruction, facial reconstruction, cleft lip or palate, cosmetic issues, skin grafting, excess skin removal, liposuction, wrinkles, hand injuries, ear reshaping, facial asymmetry', 'Plastic Surgeon', '9561708435', 'dr..ashok.seth@hospital.com', 'KMC Hospital', 'Ambedkar Circle\nMangalore, Karnataka 575001\nIndia') ,
            ('9066', 'Dr. Vandana Shiva', 'anxiety, depression, mood swings, stress, insomnia, panic attacks, phobias, PTSD, OCD, bipolar disorder, hallucinations, suicidal thoughts, eating disorders, personality disorders, anger issues', 'Psychiatrist', '9598754363', 'dr..vandana.shiva@hospital.com', 'S. S. Institute of Medical Sciences', 'NH-4 Bypass\nDavangere, Karnataka 577005\nIndia') ,
            ('6790', 'Dr. Devi Prasad Shetty', 'frequent infections, allergic reactions, autoimmune diseases, asthma, eczema, hay fever, hives, immunodeficiency disorders, food allergies, swelling after insect bites, recurrent colds, chronic sinus infections, fatigue from weak immunity, unusual infections, vaccine-related issues', 'Immunologist', '9978232120', 'dr..devi.prasad.shetty@hospital.com', 'BGS Gleneagles Global Hospital', 'Kengeri\nBengaluru, Karnataka 560060\nIndia') ,
            ('5592', 'Dr. Anjali Kulkarni', 'frequent infections, allergic reactions, autoimmune diseases, asthma, eczema, hay fever, hives, immunodeficiency disorders, food allergies, swelling after insect bites, recurrent colds, chronic sinus infections, fatigue from weak immunity, unusual infections, vaccine-related issues', 'Immunologist', '9140883809', 'dr..anjali.kulkarni@hospital.com', 'KLE Hospital', 'Nehru Nagar\nBelagavi, Karnataka 590010\nIndia') ,
            ('3616', 'Dr. Priya Shetty', 'fractures, internal injuries, tumors, abnormal growths, infections, lung conditions, heart conditions, brain abnormalities, gastrointestinal issues, spinal problems, cancer screening, bone density issues, unexplained pain, swollen organs, imaging needs', 'Radiologist', '9306520697', 'dr..priya.shetty@hospital.com', 'KLE Hospital', 'Nehru Nagar\nBelagavi, Karnataka 590010\nIndia') ,
            ('1652', 'Dr. S. K. Sarin', 'mobility issues, memory loss, frequent falls, arthritis, chronic diseases, osteoporosis, frailty, depression in the elderly, hearing problems, visual impairments, medication management, dementia, sleep issues, urinary incontinence, cardiovascular diseases', 'Geriatrician', '9102328045', 'dr..s..k..sarin@hospital.com', 'Chigateri District Hospital', 'Near Davangere University\nDavangere, Karnataka 577002\nIndia') ,
            ('4933', 'Dr. Anjali Kulkarni', 'joint pain, stiffness, swelling, fatigue, arthritis, lupus, gout, back pain, connective tissue disorders, autoimmune diseases, fibromyalgia, joint inflammation, muscle weakness, chronic pain, swollen fingers or toes', 'Rheumatologist', '9548852545', 'dr..anjali.kulkarni@hospital.com', 'Adichunchanagiri Institute of Medical Sciences', 'B.G. Nagara\nMandya, Karnataka 571448\nIndia') ,
            ('6582', 'Dr. Padmavati Sivaramakrishna Iyer', 'joint pain, broken bones, arthritis, back pain, sports injuries, sprains, ligament tears, bone deformities, dislocations, scoliosis, knee pain, hip pain, tendon injuries, carpal tunnel syndrome, shoulder stiffness', 'Orthopedic Surgeon', '9312193299', 'dr..padmavati.sivaramakrishna.iyer@hospital.com', 'Kasturba Medical College and Hospital', 'Tiger Circle Road\nManipal, Karnataka 576104\nIndia') ,
            ('1895', 'Dr. Arun Kurian Thomas', 'anxiety, depression, mood swings, stress, insomnia, panic attacks, phobias, PTSD, OCD, bipolar disorder, hallucinations, suicidal thoughts, eating disorders, personality disorders, anger issues', 'Psychiatrist', '9515281476', 'dr..arun.kurian.thomas@hospital.com', 'Karnataka Institute of Medical Sciences', 'PB Road\nHubballi, Karnataka 580022\nIndia') ,
            ('8280', 'Dr. Meena Menon', 'joint pain, stiffness, swelling, fatigue, arthritis, lupus, gout, back pain, connective tissue disorders, autoimmune diseases, fibromyalgia, joint inflammation, muscle weakness, chronic pain, swollen fingers or toes', 'Rheumatologist', '9167457670', 'dr..meena.menon@hospital.com', 'Sparsh Hospital', 'Infantry Road\nBengaluru, Karnataka 560001\nIndia') ,
            ('6808', 'Dr. Naresh Trehan', 'scars, burns, deformities, nose reshaping, breast reconstruction, facial reconstruction, cleft lip or palate, cosmetic issues, skin grafting, excess skin removal, liposuction, wrinkles, hand injuries, ear reshaping, facial asymmetry', 'Plastic Surgeon', '9959184524', 'dr..naresh.trehan@hospital.com', 'Sparsh Hospital', 'Infantry Road\nBengaluru, Karnataka 560001\nIndia') ,
            ('7191', 'Dr. Arun Kurian Thomas', 'lumps, unexplained weight loss, persistent fatigue, abnormal bleeding, chronic pain, swelling, skin changes, difficulty swallowing, persistent cough, night sweats, frequent infections, anemia, persistent indigestion, abnormal test results, swollen lymph nodes', 'Oncologist', '9872681122', 'dr..arun.kurian.thomas@hospital.com', 'Manipal Hospital', 'HAL Old Airport Road\nBengaluru, Karnataka 560017\nIndia') ,
            ('6596', 'Dr. Shanta V.', 'chest pain, breathlessness, fatigue, irregular heartbeats, high blood pressure, dizziness, fainting, chest tightness, heart failure, swollen ankles or feet, palpitations, heart attack symptoms, angina, heart murmurs, hypertension', 'Cardiologist', '9789398020', 'dr..shanta.v.@hospital.com', 'KMC Hospital', 'Ambedkar Circle\nMangalore, Karnataka 575001\nIndia') ,
            ('1065', 'Dr. Mammen Chandy', 'anemia, fatigue, pale skin, easy bruising, excessive bleeding, blood clots, swollen lymph nodes, infections, low platelet count, bone marrow problems, leukemia, sickle cell disease, thalassemia, bleeding disorders, iron deficiency', 'Hematologist', '9633665455', 'dr..mammen.chandy@hospital.com', 'St. John’s Medical College and Hospital', 'Sarjapur Road\nBengaluru, Karnataka 560034\nIndia') ,
            ('5293', 'Dr. Sudhansu Bhattacharyya', 'anxiety, depression, mood swings, stress, insomnia, panic attacks, phobias, PTSD, OCD, bipolar disorder, hallucinations, suicidal thoughts, eating disorders, personality disorders, anger issues', 'Psychiatrist', '9257520037', 'dr..sudhansu.bhattacharyya@hospital.com', 'Karnataka Institute of Medical Sciences', 'PB Road\nHubballi, Karnataka 580022\nIndia') ,
            ('1707', 'Dr. Vikas Iyer', 'chest pain, breathlessness, fatigue, irregular heartbeats, high blood pressure, dizziness, fainting, chest tightness, heart failure, swollen ankles or feet, palpitations, heart attack symptoms, angina, heart murmurs, hypertension', 'Cardiologist', '9893696256', 'dr..vikas.iyer@hospital.com', 'Father Muller Medical College Hospital', 'Kankanady\nMangalore, Karnataka 575002\nIndia') ,
            ('1030', 'Dr. Naresh Trehan', 'blurry vision, eye pain, red eyes, dry eyes, watery eyes, sensitivity to light, floaters, double vision, loss of vision, eyelid problems, cataracts, glaucoma, macular degeneration, eye injuries, eye infections', 'Ophthalmologist', '9837012381', 'dr..naresh.trehan@hospital.com', 'SDM College of Medical Sciences & Hospital', 'Manjushree Nagar\nDharwad, Karnataka 580009\nIndia') ,
            ('3675', 'Dr. Randeep Guleria', 'scars, burns, deformities, nose reshaping, breast reconstruction, facial reconstruction, cleft lip or palate, cosmetic issues, skin grafting, excess skin removal, liposuction, wrinkles, hand injuries, ear reshaping, facial asymmetry', 'Plastic Surgeon', '9518041382', 'dr..randeep.guleria@hospital.com', 'Vinayaka Hospital', 'Vinoba Nagar\nShivamogga, Karnataka 577204\nIndia') ,
            ('8411', 'Dr. P. Raghuram', 'anemia, fatigue, pale skin, easy bruising, excessive bleeding, blood clots, swollen lymph nodes, infections, low platelet count, bone marrow problems, leukemia, sickle cell disease, thalassemia, bleeding disorders, iron deficiency', 'Hematologist', '9117008516', 'dr..p..raghuram@hospital.com', 'JSS Hospital', 'MG Road\nMysuru, Karnataka 570004\nIndia') ,
            ('2768', 'Dr. Anjali Kulkarni', 'swelling in legs or feet, blood in urine, foamy urine, high blood pressure, kidney stones, fatigue, nausea, frequent urination at night, chronic kidney disease, difficulty concentrating, decreased appetite, back pain near kidneys, electrolyte imbalance, kidney infections, dialysis needs', 'Nephrologist', '9328333372', 'dr..anjali.kulkarni@hospital.com', 'St. John’s Medical College and Hospital', 'Sarjapur Road\nBengaluru, Karnataka 560034\nIndia') 
        ])
        conn.commit()
    conn.close()

# Query the database for doctor details based on symptoms
def query_database(symptoms):
    conn = sqlite3.connect("doctor_recommendations.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT doctor_identity_number, doctor_name, specialization, contact, email, hospital_name, hospital_location FROM doctors WHERE symptom_name LIKE ?",
        ('%' + symptoms + '%',)
    )
    result = cursor.fetchall()
    conn.close()
    return result if result else None

# Get response from Gemini Pro
def get_gemini_response(question, doctor_details=None):
    if doctor_details:
        # Doctor recommendation-specific response
        context = (
            f"You are a doctor recommendation chatbot. "
            f"Based on the input '{question}', the following doctors are suitable for the symptoms:\n"
        )
        # Add doctor details to the context
        for doctor in doctor_details:
            context += (
                f"Doctor Identity Number: {doctor[0]}, Name: {doctor[1]}, Specialization: {doctor[2]}, "
                f"Contact: {doctor[3]}, Email: {doctor[4]}, Hospital: {doctor[5]}, Location: {doctor[6]}\n\n"
            )
        context += "Please provide a summary of the doctor details and why these doctors are suitable."
    else:
        # General question-answering
        context = (
            f"You are an intelligent chatbot. "
            f"Answer the user's question '{question}' in under 200 words."
        )
    response = chat.send_message(context, stream=True)
    return response

# Initialize the Streamlit app
st.set_page_config(page_title="Chatbot Application", layout="wide")
st.sidebar.title("MediBot Menu")

# Sidebar for navigation
menu_option = st.sidebar.selectbox("Choose a Chatbot:", ["Doctor Recommendation Chatbot", "Q&A Chatbot", "Find Doctors by Specialization"])

# Initialize the database for doctor recommendations
initialize_database()

# Manage chat history in session state
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Doctor Recommendation Chatbot Section
if menu_option == "Doctor Recommendation Chatbot":
    st.header("Doctor Recommendation Chatbot")
    user_input = st.text_input("Enter your symptoms:", key="doctor_input")
    submit_button = st.button("Get Recommendation")

    if submit_button and user_input:
        # Query the database for doctor details
        doctor_details = query_database(user_input)
        if doctor_details:
            st.subheader("Matching Doctors:")
            doctor_df = pd.DataFrame(
                doctor_details,
                columns=[
                    "Doctor Identity Number",
                    "Doctor Name",
                    "Specialization",
                    "Contact",
                    "Email",
                    "Hospital Name",
                    "Hospital Location",
                ],
            )
            st.dataframe(doctor_df)

            response = get_gemini_response(user_input, doctor_details)
            bot_response = "".join(chunk.text for chunk in response)

            st.session_state["chat_history"].append(("You", user_input))
            st.session_state["chat_history"].append(("Bot", bot_response))

            st.subheader("Response Summary:")
            st.write(bot_response)
        else:
            st.error("Sorry, no matching doctors found in our database.")

# Normal Question and Answer Chatbot Section
elif menu_option == "Q&A Chatbot":
    st.header("Question and Answer Chatbot")
    user_input = st.text_input("Ask a question:", key="qa_input")
    submit_button = st.button("Get Answer")

    if submit_button and user_input:
        response = get_gemini_response(user_input)
        bot_response = "".join(chunk.text for chunk in response)

        st.session_state["chat_history"].append(("You", user_input))
        st.session_state["chat_history"].append(("Bot", bot_response))

        st.subheader("Response:")
        st.write(bot_response)

# Find Doctors by Specialization Section
elif menu_option == "Find Doctors by Specialization":
    st.header("Find Doctors by Specialization")
    conn = sqlite3.connect("doctor_recommendations.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT specialization FROM doctors")
    specializations = [row[0] for row in cursor.fetchall()]
    conn.close()

    specialization = st.selectbox("Select a specialization:", specializations)
    find_button = st.button("Find Doctors")

    if find_button and specialization:
        conn = sqlite3.connect("doctor_recommendations.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT doctor_identity_number, doctor_name, symptom_name, contact, email, hospital_name, hospital_location FROM doctors WHERE specialization = ?",
            (specialization,)
        )
        specialization_doctors = cursor.fetchall()
        conn.close()

        if specialization_doctors:
            st.subheader(f"Doctors specializing in {specialization}:")
            specialization_df = pd.DataFrame(
                specialization_doctors,
                columns=[
                    "Doctor Identity Number",
                    "Doctor Name",
                    "Symptoms Treated",
                    "Contact",
                    "Email",
                    "Hospital Name",
                    "Hospital Location",
                ],
            )
            st.dataframe(specialization_df)
        else:
            st.error(f"No doctors found for specialization: {specialization}.")

# Display Chat History
st.sidebar.subheader("Chat History")
for role, text in st.session_state["chat_history"]:
    st.sidebar.write(f"{role}: {text}")
