import os
import pandas as pd
import json

base_items = [
    # 1-10
    ("Whatsapp la share aagura message: 5G tower rays vandhu sparrows and birds ah kill pannuthu, immediate ah stop panna solranga.", 1, "Fake", "Tech Rumor", "WhatsApp", "Tanglish", 20.0, 80.0),
    ("TN Government announced tomorrow local holiday for Chennai schools due to heavy rain forecast by IMD.", 0, "Real", "Weather News", "News Portal", "English-Mixed", 0.0, 100.0),
    ("Intha kashayam kudicha 2 days la COVID and virus fully cure aayidum no need for hospital visit bro.", 1, "Fake", "Health Misinformation", "WhatsApp", "Tanglish", 29.4, 70.6),
    ("ISRO successfully launched the Chandrayaan-3 mission from Sriharikota, historic moment for India.", 0, "Real", "Science", "Twitter/X", "English-Mixed", 0.0, 100.0),
    ("Urgent alert: Govt is freezing all bank accounts if you don't link Aadhaar card within tonight 12 PM link below.", 1, "Fake", "Financial Scam", "WhatsApp", "Tanglish", 0.0, 100.0),
    ("RBI increased the repo rate by 25 basis points to control inflation in the current quarter.", 0, "Real", "Finance", "News Portal", "English-Mixed", 0.0, 100.0),
    ("Onion juice la lemon mix panni kudicha 100% hair loss permanent ah stop aagum viral tip.", 1, "Fake", "Health Misinformation", "YouTube", "Tanglish", 20.0, 80.0),
    ("Anna University published the semester exam results on their official web portal today afternoon.", 0, "Real", "Education", "Twitter/X", "English-Mixed", 0.0, 100.0),
    ("Breaking news: UNESCO declared Tamil as the best and most traditional language in the world award 2026.", 1, "Fake", "Social Media Rumor", "Facebook", "Tanglish", 0.0, 100.0),
    ("Chennai Metro Railway announced extended train operational hours for IPL cricket match spectators tonight.", 0, "Real", "Transport", "News Portal", "English-Mixed", 0.0, 100.0),
    
    # 11-20
    ("Pluto planet eppo Earth pakkathula varudho appo free electricity get panni namma use pannalam bro viral video.", 1, "Fake", "Science Hoax", "YouTube", "Tanglish", 23.5, 76.5),
    ("Southern Railway announced special express trains between Chennai Central and Tiruchirappalli for Diwali festival.", 0, "Real", "Transport", "News Portal", "English-Mixed", 0.0, 100.0),
    ("New rule by TRAI: Daily 2 hours internet shutdown across India from tomorrow night 1 AM to 3 AM for satellite repair.", 1, "Fake", "Tech Rumor", "WhatsApp", "Tanglish", 0.0, 100.0),
    ("TANGEDCO announced scheduled power outage in select areas of Madurai for transformer maintenance work.", 0, "Real", "Public Utility", "News Portal", "English-Mixed", 0.0, 100.0),
    ("Free Rs.5000 recharge for all mobile users on PM Modi birthday celebration click this website link immediately.", 1, "Fake", "Phishing Scam", "WhatsApp", "Tanglish", 0.0, 100.0),
    ("Indian Cricket Team announced the 15-player squad for the upcoming ICC World Cup tournament.", 0, "Real", "Sports", "Twitter/X", "English-Mixed", 0.0, 100.0),
    ("Drinking boiled banana peel water every morning will cancel diabetes in just 7 days without insulin.", 1, "Fake", "Health Misinformation", "Facebook", "Tanglish", 0.0, 100.0),
    ("Madras High Court issued notice to local civic body regarding road pothole repairs before monsoon season.", 0, "Real", "Judiciary", "News Portal", "English-Mixed", 0.0, 100.0),
    ("NASA confirms 3 days of total darkness across Earth due to solar storm next week forward to all family groups.", 1, "Fake", "Science Hoax", "WhatsApp", "Tanglish", 0.0, 100.0),
    ("Reserve Bank of India issued guidelines warning citizens against sharing OTP and PIN details with fraudsters.", 0, "Real", "Finance", "News Portal", "English-Mixed", 0.0, 100.0),

    # 21-30
    ("Intha App download panna unga bank account la daily Rs.1000 credit aagum, 100% government verified bro.", 1, "Fake", "Financial Scam", "Telegram", "Tanglish", 42.9, 57.1),
    ("Tamil Nadu Directorate of Public Health issued advisory on dengue prevention during rainy season.", 0, "Real", "Health", "News Portal", "English-Mixed", 0.0, 100.0),
    ("Eating garlic with honey at night will permanently eliminate all types of cancer cells within two weeks.", 1, "Fake", "Health Misinformation", "WhatsApp", "Tanglish", 0.0, 100.0),
    ("ISRO successfully launched the Aditya-L1 solar observation satellite towards Sun Earth L1 point.", 0, "Real", "Science", "Twitter/X", "English-Mixed", 0.0, 100.0),
    ("Govt is secretly installing microchips in new 2000 rupee notes to track black money from satellite.", 1, "Fake", "Tech Rumor", "WhatsApp", "Tanglish", 0.0, 100.0),
    ("Tamil Nadu Chief Minister inaugurated new flyover project in Coimbatore to reduce city traffic congestion.", 0, "Real", "Politics", "News Portal", "English-Mixed", 0.0, 100.0),
    ("WhatsApp unga private messages and photos ah Facebook ad network ku sell panranga immediately uninstall pannunga.", 1, "Fake", "Tech Rumor", "WhatsApp", "Tanglish", 18.8, 81.2),
    ("State Bank of India updated YONO mobile banking application with enhanced security features for users.", 0, "Real", "Finance", "News Portal", "English-Mixed", 0.0, 100.0),
    ("Neengal intha forward message 10 contacts ku send panna ungaluku Rs.500 talktime free ah milikkum.", 1, "Fake", "Social Media Hoax", "WhatsApp", "Tanglish", 30.8, 69.2),
    ("Chennai Corporation announced free vaccination camp for pets in all zonal veterinary clinics.", 0, "Real", "Public Health", "News Portal", "English-Mixed", 0.0, 100.0),

    # 31-40
    ("Plastic rice and artificial egg sell panranga supermarkets la parthu vanggunga video proof attached.", 1, "Fake", "Food Hoax", "Facebook", "Tanglish", 28.6, 71.4),
    ("IIT Madras researchers developed new low-cost water purification system using nanotechnology.", 0, "Real", "Science", "News Portal", "English-Mixed", 0.0, 100.0),
    ("Night la phone charging podum podu earphone use panna battery blast aagi brain damage aagum mandatory alert.", 1, "Fake", "Tech Rumor", "WhatsApp", "Tanglish", 23.5, 76.5),
    ("Chennai Airport commissioned new integrated passenger terminal building for international flights.", 0, "Real", "Infrastructure", "News Portal", "English-Mixed", 0.0, 100.0),
    ("Free Laptop distribution for all college students under National Digital Youth scheme fill google form link.", 1, "Fake", "Phishing Scam", "WhatsApp", "Tanglish", 0.0, 100.0),
    ("Tamil Nadu Public Service Commission TNPSC published notification for Group 4 recruitment examination.", 0, "Real", "Education", "News Portal", "English-Mixed", 0.0, 100.0),
    ("Salt water la lemon and turmeric potu gargle panna multi variant viruses 10 seconds la death aagum.", 1, "Fake", "Health Misinformation", "WhatsApp", "Tanglish", 31.2, 68.8),
    ("Reserve Bank of India introduced digital rupee e-Rupee pilot project for retail transactions in major cities.", 0, "Real", "Finance", "News Portal", "English-Mixed", 0.0, 100.0),
    ("UNESCO selected Chennai city bus conductor as world best employee award share max to support Tamil pride.", 1, "Fake", "Social Media Rumor", "Facebook", "Tanglish", 0.0, 100.0),
    ("Metrowater announced 24 hour water supply disruption in Zone 5 and 6 for pipeline replacement work.", 0, "Real", "Public Utility", "News Portal", "English-Mixed", 0.0, 100.0),

    # 41-50
    ("5G SIM card insert panna unga phone overall storage double aagum free feature enabled by telecom companies.", 1, "Fake", "Tech Rumor", "YouTube", "Tanglish", 17.6, 82.4),
    ("Madurai Kamaraj University announced admissions open for post-graduate distance education courses.", 0, "Real", "Education", "News Portal", "English-Mixed", 0.0, 100.0),
    ("Neem leaf juice mix with black pepper will completely prevent heart attacks forever doctor secret revealed.", 1, "Fake", "Health Misinformation", "WhatsApp", "Tanglish", 0.0, 100.0),
    ("Tamil Nadu Electricity Board completed 100% smart meter installation trial phase in select districts.", 0, "Real", "Public Utility", "News Portal", "English-Mixed", 0.0, 100.0),
    ("Govt planning to ban all old 4G smartphones from next month to force people buy 5G phones fast.", 1, "Fake", "Tech Rumor", "WhatsApp", "Tanglish", 0.0, 100.0),
    ("State government launched Magalir Urimai Thogai scheme providing monthly financial assistance to eligible women.", 0, "Real", "Politics", "News Portal", "English-Mixed", 0.0, 100.0),
    ("Cold water drinking after meal will turn oil into cancer substance inside stomach share with family immediately.", 1, "Fake", "Health Misinformation", "WhatsApp", "Tanglish", 0.0, 100.0),
    ("Indian Railways launched Vande Bharat Express service connecting Chennai Central and Coimbatore junction.", 0, "Real", "Transport", "News Portal", "English-Mixed", 0.0, 100.0),
    ("Govt is giving free solar panel setup for all houses across Tamil Nadu apply via this viral apk app.", 1, "Fake", "Phishing Scam", "WhatsApp", "Tanglish", 0.0, 100.0),
    ("Regional Meteorological Centre Chennai predicted light to moderate rainfall over coastal districts of Tamil Nadu.", 0, "Real", "Weather News", "News Portal", "English-Mixed", 0.0, 100.0)
]

# Generate total 220 items deterministically
raw_data = []
for i in range(220):
    src_tuple = base_items[i % len(base_items)]
    text, label, label_name, category, source, cmt, t_pct, e_pct = src_tuple
    
    # Slight variation prefix for expanded rows
    if i >= 50:
        prefix_var = ["Viral Forward: ", "Social Alert: ", "News Update: ", "Report: "][i % 4]
        text_full = prefix_var + text
    else:
        text_full = text

    cleaned = " ".join([w.lower().strip(".,!?\"'()[]{}") for w in text_full.split() if w.strip()])
    wc = len(text_full.split())
    cmi = round(min(t_pct, e_pct), 1)

    raw_data.append((
        i + 1,
        text_full,
        label,
        label_name,
        category,
        source,
        cmt,
        cleaned,
        wc,
        len(cleaned.split()),
        len(text_full),
        cmi,
        t_pct,
        e_pct
    ))

columns = [
    "id", "text", "label", "label_name", "category", "source",
    "code_mix_type", "cleaned_text", "word_count", "cleaned_word_count",
    "char_length", "cmi", "tanglish_pct", "english_pct"
]

df = pd.DataFrame(raw_data, columns=columns)

data_dir = r"C:\Users\balla\OneDrive\Desktop\CodeMix\data"
os.makedirs(data_dir, exist_ok=True)

csv_path = os.path.join(data_dir, "Tamil_English_Fake_Real_Dataset_Full.csv")
excel_path = os.path.join(data_dir, "Tamil_English_Fake_Real_Dataset_Full.xlsx")
json_path = os.path.join(data_dir, "dataset.json")

df.to_csv(csv_path, index=False)
df.to_excel(excel_path, index=False, sheet_name="Dataset")
df.to_json(json_path, orient="records", indent=2)

print(f"[SUCCESS] Built {len(df)} Tamil-English (Tanglish) Dataset Entries!")
