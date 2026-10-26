# Dataset expansion generator
import json
import re
import os
import pandas as pd

TAMIL_WORDS = {
    'la', 'ah', 'bro', 'pannuthu', 'pannunga', 'kudicha', 'iruku', 'vandhu', 'solranga', 
    'aayidum', 'illai', 'dhan', 'mattum', 'enna', 'oru', 'unga', 'namma', 'panna', 
    'paravuthu', 'paathutu', 'sollidunga', 'seithu', 'adhu', 'idhu', 'konjam', 'eppadi',
    'appadi', 'romba', 'kooda', 'ippo', 'eppo', 'paatha', 'theriyala', 'vandhuruku',
    'tharanum', 'vaanganum', 'podanum', 'keta', 'sonna', 'pesranga', 'varuthu', 'poidum',
    'aachu', 'aagathu', 'kedaikum', 'solli', 'seiyunga', 'anupunga', 'share', 'forward',
    'kudunga', 'irukku', 'pola', 'seri', 'illana', 'kandippa', 'ungalukku', 'namakku',
    'ellarum', 'intha', 'andha', 'makkal', 'thambi', 'akko', 'anna', 'amma', 'appa',
    'kuda', 'vandha', 'poga', 'solla', 'parunga', 'namba', 'nambathinga', 'viral', 'msg'
}

def clean_text(text: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
    return re.sub(r'\s+', ' ', cleaned).strip()

def calculate_cmi(text: str):
    words = re.findall(r'[a-zA-Z]+', text.lower())
    if not words:
        return 0.0, 0.0, 100.0, 'English'
    tamil_count = sum(1 for w in words if w in TAMIL_WORDS)
    eng_count = len(words) - tamil_count
    total = len(words)
    cmi = round(min(tamil_count, eng_count) / total * 100, 1)
    ta_pct = round(tamil_count / total * 100, 1)
    en_pct = round(100.0 - ta_pct, 1)
    mix_type = 'Tanglish' if ta_pct >= 15 else ('English-Mixed' if ta_pct > 0 else 'English')
    return cmi, ta_pct, en_pct, mix_type
