"""
Tanglish Robustness Analyzer & Perturbation Generator.
Generates controlled, semantically-preserving Tanglish variations (spelling, transliteration,
synonyms, character repetition, punctuation, and script variations) and evaluates dual-model
prediction stability and inter-model agreement under linguistic stress.
"""

import re
from typing import Dict, Any, List, Tuple

# 1. Phonetic & Orthographic Transliteration Maps
PHONETIC_SPELLING_MAP = {
    "aagudhu": ["agudhu", "aaguthu", "aagiduthu"],
    "aagum": ["agum", "aakum", "aagumm"],
    "pannuthu": ["panuthu", "pannudhu", "panudhu"],
    "kudicha": ["kuditsha", "kudichaa", "kudithal"],
    "varudho": ["varutho", "varuthu", "varuthoo"],
    "ungalu": ["ungal", "ungada"],
    "ungaluku": ["ungallukku", "ungalukku", "ungalku"],
    "panranga": ["panraanga", "pannuraanga", "pandranga"],
    "panna": ["pana", "pannaa", "seyya"],
    "irundha": ["iruntha", "irundhaa"],
    "kitta": ["kitte", "kittai"],
    "parthu": ["paarthu", "paathu"],
    "vanggunga": ["vaangunga", "vangunga", "vaangikonga"],
    "potu": ["pottu", "potuu"],
    "intha": ["indha", "inda"],
    "inga": ["ingey", "ingae"],
    "unga": ["ungaloda", "ungada"],
    "solranga": ["solluranga", "solraanga"],
    "vandhu": ["vanthu", "vandhoo"],
    "namma": ["nama", "nammaloda"],
    "pannalam": ["panlaam", "pannalaam"],
    "maari": ["maadhiri", "madhiri", "maatiri"],
    "thoonguna": ["thunguna", "thongina"],
    "milikkum": ["kidaikkum", "varum"],
    "pannuvanga": ["panuvaanga", "pannuvaanga"],
    "nala": ["naala", "naley"],
    "rays": ["kathir", "rays"],
    "stop": ["nirutha", "stop"]
}

# 2. Semantic Synonym Substitutions (Meaning Preserving)
LEXICAL_SYNONYMS = {
    "die aagudhu": "sethudhu",
    "die aagum": "sethupoidum",
    "kill pannuthu": "destroy pannuthu",
    "share pannunga": "forward pannunga",
    "share aagura": "viral aagura",
    "message": "msg",
    "immediately": "urgent ah",
    "kudicha": "drink panna",
    "solranga": "pesuranga",
    "bro": "brooo",
    "cure aayidum": "kunamaayidum",
    "birds": "birds ellam",
    "sparrows": "kuruvi ellam",
    "link": "link ah"
}

# 3. Abbreviations
ABBREVIATIONS = {
    "message": "msg",
    "government": "govt",
    "please": "pls",
    "because": "bcoz",
    "whatsapp": "whtsapp",
    "year": "yr",
    "hours": "hrs",
    "minutes": "mins",
    "number": "no."
}

def generate_tanglish_variants(text: str) -> List[Dict[str, str]]:
    """
    Generates 6-10 semantically consistent variations across 7 perturbation categories.
    """
    variants: List[Dict[str, str]] = []
    seen = {text.strip().lower()}

    def add_variant(v_text: str, v_type: str, desc: str):
        cleaned = v_text.strip()
        cleaned_key = cleaned.lower()
        if cleaned_key not in seen and len(cleaned) > 10:
            seen.add(cleaned_key)
            variants.append({
                "type": v_type,
                "description": desc,
                "text": cleaned
            })

    # --- VARIATION 1: Phonetic Spelling Variation ---
    words = text.split()
    v1_words = []
    replaced_v1 = False
    for w in words:
        punct = ""
        clean_w = w.strip(".,!?\"'()[]{}").lower()
        if clean_w in PHONETIC_SPELLING_MAP:
            alt = PHONETIC_SPELLING_MAP[clean_w][0]
            v1_words.append(alt)
            replaced_v1 = True
        else:
            v1_words.append(w)
    if replaced_v1:
        add_variant(" ".join(v1_words), "Spelling Variation", "Common phonetic Romanized Tamil spelling variation")

    # --- VARIATION 2: Transliteration Vowel / Consonant Shift ---
    v2_text = text
    # Convert 'aa' -> 'a' or 'a' -> 'aa', 'dh' -> 'th', 'ee' -> 'i'
    if "nala" in v2_text.lower():
        v2_text = re.sub(r"\bnala\b", "naala", v2_text, flags=re.IGNORECASE)
    elif "naala" in v2_text.lower():
        v2_text = re.sub(r"\bnaala\b", "nala", v2_text, flags=re.IGNORECASE)

    if "aagudhu" in v2_text.lower():
        v2_text = re.sub(r"\baagudhu\b", "aaguthu", v2_text, flags=re.IGNORECASE)
    elif "aaguthu" in v2_text.lower():
        v2_text = re.sub(r"\baaguthu\b", "aagudhu", v2_text, flags=re.IGNORECASE)

    if "irundha" in v2_text.lower():
        v2_text = re.sub(r"\birundha\b", "iruntha", v2_text, flags=re.IGNORECASE)
    if "ungaluku" in v2_text.lower():
        v2_text = re.sub(r"\bungaluku\b", "ungallukku", v2_text, flags=re.IGNORECASE)
    if "solranga" in v2_text.lower():
        v2_text = re.sub(r"\bsolranga\b", "solluranga", v2_text, flags=re.IGNORECASE)

    if v2_text != text:
        add_variant(v2_text, "Transliteration Variation", "Vowel length (naala/nala) & dental consonant (dhu/thu) shift")
    else:
        # Fallback transliteration
        v2_mod = re.sub(r"\b(la|ah|ku)\b", r"\1\1", text, flags=re.IGNORECASE)
        if v2_mod != text:
            add_variant(v2_mod, "Transliteration Variation", "Enclitic suffix lengthening (la -> lala / ah -> ahh)")

    # --- VARIATION 3: Lexical Synonym Substitution ---
    v3_text = text
    replaced_v3 = False
    for k, v in LEXICAL_SYNONYMS.items():
        if k in v3_text.lower():
            v3_text = re.sub(re.escape(k), v, v3_text, flags=re.IGNORECASE)
            replaced_v3 = True
            break
    if replaced_v3:
        add_variant(v3_text, "Lexical Substitution", "Semantically equivalent Tanglish spoken synonym swap")

    # --- VARIATION 4: Repeated-Character Emphasis (Social Slang) ---
    v4_words = []
    elongated = False
    for w in words:
        clean_w = w.strip(".,!?\"'()[]{}").lower()
        if clean_w in ["die", "urgent", "free", "bro", "immediately", "kill", "cure", "stop"] and not elongated:
            # e.g., die -> dieee, bro -> brooo
            v4_words.append(w + (w[-1] * 2))
            elongated = True
        else:
            v4_words.append(w)
    if elongated:
        add_variant(" ".join(v4_words), "Character Elongation", "Social media emphatic character repetition (slang tone)")
    else:
        # Elongate first verb or last word
        if len(words) > 3:
            v4_mod = words[:]
            v4_mod[-2] = v4_mod[-2] + v4_mod[-2][-1] * 2
            add_variant(" ".join(v4_mod), "Character Elongation", "Chat emphasis repetition on penultimate predicate token")

    # --- VARIATION 5: Punctuation & Casing Perturbation ---
    clean_p = text.rstrip(".!? ")
    v5_text = f"{clean_p}!! Urgent forward!!"
    add_variant(v5_text, "Punctuation Perturbation", "Sensational exclamation marks and urgency tags")

    # --- VARIATION 6: Capitalization Emphasis ---
    v6_words = []
    caps_count = 0
    for w in words:
        clean_w = w.strip(".,!?\"'()[]{}").lower()
        if clean_w in ["5g", "tower", "radiation", "kill", "die", "cancer", "free", "urgent", "secret", "fake", "link", "covid"] and caps_count < 2:
            v6_words.append(w.upper())
            caps_count += 1
        else:
            v6_words.append(w)
    if caps_count > 0:
        add_variant(" ".join(v6_words), "Capitalization Variation", "Uppercase emphasis on key semantic subject/predicate")

    # --- VARIATION 7: Chat Abbreviation ---
    v7_text = text
    replaced_v7 = False
    for full_w, abbr in ABBREVIATIONS.items():
        if re.search(rf"\b{full_w}\b", v7_text, flags=re.IGNORECASE):
            v7_text = re.sub(rf"\b{full_w}\b", abbr, v7_text, flags=re.IGNORECASE)
            replaced_v7 = True
    if replaced_v7:
        add_variant(v7_text, "Common Abbreviation", "Colloquial chat messaging abbreviations (msg, govt, whtsapp)")

    # --- VARIATION 8: Secondary Transliteration / Spacing ---
    v8_words = []
    for w in words:
        clean_w = w.strip(".,!?\"'()[]{}").lower()
        if clean_w in PHONETIC_SPELLING_MAP and len(PHONETIC_SPELLING_MAP[clean_w]) > 1:
            alt2 = PHONETIC_SPELLING_MAP[clean_w][1]
            v8_words.append(alt2)
        else:
            v8_words.append(w)
    v8_text = " ".join(v8_words)
    if v8_text != text:
        add_variant(v8_text, "Transliteration Dialect", "Secondary Romanized colloquial Tanglish spelling pattern")

    # Ensure we have at least 5 variants
    if len(variants) < 5:
        add_variant(f"Forwarded: {text}", "Framing Variation", "WhatsApp forwarding preamble")
        add_variant(f"{text} Pls verify and share.", "Call-to-Action Variation", "Standard conversational sharing appendix")

    return variants[:8]

def run_robustness_experiment(
    original_text: str,
    original_muril_res: Dict[str, Any],
    original_indic_res: Dict[str, Any],
    predict_fn
) -> Dict[str, Any]:
    """
    Executes the perturbation experiment:
    1. Generates 6-8 natural Tanglish variations
    2. Runs both MuRIL and IndicBERT on every variant
    3. Analyzes stability, confidence shift, and inter-model agreement
    """
    orig_m_label = original_muril_res["label_name"]
    orig_i_label = original_indic_res["label_name"]
    orig_m_conf = original_muril_res["confidence"]
    orig_i_conf = original_indic_res["confidence"]
    orig_agreement = (orig_m_label == orig_i_label)

    variants = generate_tanglish_variants(original_text)
    
    variant_results: List[Dict[str, Any]] = []
    
    muril_stable_count = 0
    indic_stable_count = 0
    agreement_count = 0
    
    m_conf_drops = []
    i_conf_drops = []

    # Original row for the table
    variant_results.append({
        "variant_id": 0,
        "type": "Original Input",
        "description": "Baseline reference text provided by user",
        "text": original_text,
        "muril_label": orig_m_label,
        "muril_conf": orig_m_conf,
        "indic_label": orig_i_label,
        "indic_conf": orig_i_conf,
        "agreement": orig_agreement,
        "muril_stable": True,
        "indic_stable": True,
        "overall_stable": True,
        "muril_shift": 0.0,
        "indic_shift": 0.0
    })

    for idx, v in enumerate(variants, 1):
        res = predict_fn(v["text"])
        m_res = res["muril_results"]
        i_res = res["indic_results"]

        m_label = m_res["label_name"]
        m_conf = m_res["confidence"]
        i_label = i_res["label_name"]
        i_conf = i_res["confidence"]

        # Stability relative to baseline
        m_stable = (m_label == orig_m_label)
        i_stable = (i_label == orig_i_label)
        agreement = (m_label == i_label)

        if m_stable:
            muril_stable_count += 1
        if i_stable:
            indic_stable_count += 1
        if agreement:
            agreement_count += 1

        m_shift = round(m_conf - orig_m_conf, 1)
        i_shift = round(i_conf - orig_i_conf, 1)

        m_conf_drops.append(orig_m_conf - m_conf)
        i_conf_drops.append(orig_i_conf - i_conf)

        variant_results.append({
            "variant_id": idx,
            "type": v["type"],
            "description": v["description"],
            "text": v["text"],
            "muril_label": m_label,
            "muril_conf": m_conf,
            "indic_label": i_label,
            "indic_conf": i_conf,
            "agreement": agreement,
            "muril_stable": m_stable,
            "indic_stable": i_stable,
            "overall_stable": (m_stable and i_stable),
            "muril_shift": m_shift,
            "indic_shift": i_shift
        })

    total_variants = len(variants)
    
    # Metrics
    muril_stability_pct = round((muril_stable_count / total_variants) * 100, 1) if total_variants > 0 else 100.0
    indic_stability_pct = round((indic_stable_count / total_variants) * 100, 1) if total_variants > 0 else 100.0
    agreement_rate_pct = round((agreement_count / total_variants) * 100, 1) if total_variants > 0 else 100.0
    
    # Combined Robustness Score: Average of both models' stability rates
    robustness_score = round((muril_stability_pct + indic_stability_pct) / 2.0, 1)

    avg_m_shift = round(float(sum(abs(d) for d in m_conf_drops) / max(1, len(m_conf_drops))), 1)
    avg_i_shift = round(float(sum(abs(d) for d in i_conf_drops) / max(1, len(i_conf_drops))), 1)
    max_m_drop = round(max(0.0, max(m_conf_drops, default=0.0)), 1)
    max_i_drop = round(max(0.0, max(i_conf_drops, default=0.0)), 1)

    # Identify most sensitive and most stable variations
    # Exclude original row (id: 0)
    tested_rows = variant_results[1:]
    
    # Most sensitive: max total drop or flip
    sorted_by_sensitivity = sorted(
        tested_rows,
        key=lambda r: (not r["overall_stable"], abs(r["muril_shift"]) + abs(r["indic_shift"])),
        reverse=True
    )
    most_sensitive = sorted_by_sensitivity[0] if sorted_by_sensitivity else None

    # Most stable: minimal shift and overall stable
    sorted_by_stability = sorted(
        tested_rows,
        key=lambda r: (r["overall_stable"], -(abs(r["muril_shift"]) + abs(r["indic_shift"]))),
        reverse=True
    )
    most_stable = sorted_by_stability[0] if sorted_by_stability else None

    # Research observation synthesis
    if muril_stability_pct > indic_stability_pct:
        more_robust_model = "Google MuRIL"
        robust_reason = (
            f"Google MuRIL maintained higher stability ({muril_stability_pct}%) across Tanglish "
            f"variations compared to IndicBERT ({indic_stability_pct}%). This empirical divergence aligns "
            f"with MuRIL's specialized romanized and transliterated Indic pre-training corpus, "
            f"which exhibits lower subword token fragmentation."
        )
    elif indic_stability_pct > muril_stability_pct:
        more_robust_model = "IndicBERT"
        robust_reason = (
            f"IndicBERT maintained higher stability ({indic_stability_pct}%) than MuRIL ({muril_stability_pct}%) "
            f"on this particular lexical pattern."
        )
    else:
        more_robust_model = "Tie (MuRIL & IndicBERT)"
        robust_reason = (
            f"Both Google MuRIL and IndicBERT demonstrated equivalent stability ({muril_stability_pct}%) "
            f"across all generated Tanglish perturbations."
        )

    return {
        "robustness_score": robustness_score,
        "total_variants_tested": total_variants,
        "muril_stability_pct": muril_stability_pct,
        "indic_stability_pct": indic_stability_pct,
        "agreement_rate_pct": agreement_rate_pct,
        "disagreement_count": total_variants - agreement_count,
        "more_robust_model": more_robust_model,
        "research_observation": robust_reason,
        "muril_metrics": {
            "stable_count": muril_stable_count,
            "stability_pct": muril_stability_pct,
            "avg_conf_shift": avg_m_shift,
            "max_conf_drop": max_m_drop
        },
        "indic_metrics": {
            "stable_count": indic_stable_count,
            "stability_pct": indic_stability_pct,
            "avg_conf_shift": avg_i_shift,
            "max_conf_drop": max_i_drop
        },
        "most_sensitive_variation": {
            "type": most_sensitive["type"],
            "text": most_sensitive["text"],
            "muril_shift": most_sensitive["muril_shift"],
            "indic_shift": most_sensitive["indic_shift"]
        } if most_sensitive else None,
        "most_stable_variation": {
            "type": most_stable["type"],
            "text": most_stable["text"]
        } if most_stable else None,
        "variants_table": variant_results
    }
