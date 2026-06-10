import re
from typing import Optional
from ..models.shipping import ShippingRule


# -----------------------------------------------------------
# Google Places Location Normalizer
# -----------------------------------------------------------
# Google Places often returns location names with suffixes
# that won't match clean admin-configured names.
# This function strips common suffixes to get a clean base name.
#
# Examples:
#   "Bagmati Province"         → "Bagmati"
#   "Kathmandu Metropolitan City" → "Kathmandu"
#   "Lalitpur Sub-Metropolitan" → "Lalitpur"

_GOOGLE_SUFFIXES = [
    r'\s+province$',
    r'\s+metropolitan\s+city$',
    r'\s+sub-?metropolitan\s+city?$',
    r'\s+metropolitan$',
    r'\s+municipality$',
    r'\s+rural\s+municipality$',
    r'\s+urban\s+municipality$',
    r'\s+district$',
]

def get_similarity(s1: str, s2: str) -> float:
    """
    Calculates similarity between two strings (0.0 to 1.0).
    Uses a simple Levenshtein-based similarity score.
    """
    s1, s2 = s1.lower().strip(), s2.lower().strip()
    if s1 == s2: return 1.0
    if not s1 or not s2: return 0.0

    # Basic distance calculation
    rows = len(s1) + 1
    cols = len(s2) + 1
    distance = [[0 for _ in range(cols)] for _ in range(rows)]

    for i in range(1, rows): distance[i][0] = i
    for i in range(1, cols): distance[0][i] = i

    for col in range(1, cols):
        for row in range(1, rows):
            cost = 0 if s1[row-1] == s2[col-1] else 1
            distance[row][col] = min(
                distance[row-1][col] + 1,      # deletion
                distance[row][col-1] + 1,      # insertion
                distance[row-1][col-1] + cost  # substitution
            )
    
    max_len = max(len(s1), len(s2))
    return (max_len - distance[row][col]) / max_len


def normalize_location(name: str, field_name: str = 'province') -> str:
    """
    Smart normalizer that strips suffixes and uses fuzzy canonical matching
    against existing database entries to solve spelling variations.
    """
    if not name:
        return ''
    
    # 1. Clean basic noise
    name = name.strip()
    for suffix in _GOOGLE_SUFFIXES:
        name = re.sub(suffix, '', name, flags=re.IGNORECASE).strip()
    
    # 2. Fuzzy Canonical Matching (The Smart Internal Search)
    # We look at what the ADMIN has already saved in the DB, 
    # and see if the user's input is a 85% match to it.
    try:
        # Get all unique values for this field (province or district) from your Rules
        existing_values = ShippingRule.objects.filter(is_active=True).values_list(field_name, flat=True).distinct()
        
        best_match = name
        highest_score = 0.0
        
        for val in existing_values:
            if not val: continue
            score = get_similarity(name, val)
            if score > highest_score:
                highest_score = score
                best_match = val
        
        # If we find a very close match (80%+ similarity), we auto-correct it.
        # This solves Bagmati vs Bagamati, Kathmandu vs Katmandu, etc.
        if highest_score > 0.8:
            return best_match
            
    except Exception:
        pass # Fallback to cleaned name if DB fails

    return name


# -----------------------------------------------------------
# Hierarchical Shipping Rule Lookup
# -----------------------------------------------------------
def get_rule_for_address(
    province: str = '',
    district: str = '',
    city: str = ''
) -> Optional[ShippingRule]:
    """
    Finds the most applicable active ShippingRule for the given address.
    Applies priority-based hierarchical matching with FUZZY resilience.
    """
    # Normalize and Auto-Correct based on what exists in the DB
    p = normalize_location(province, 'province')
    d = normalize_location(district, 'district')
    c = normalize_location(city, 'city_or_municipality')

    active_rules = ShippingRule.objects.filter(is_active=True).order_by('priority')

    # --- FULL HIERARCHY MATCH (Province + X) ---
    # Most accurate path: Matches exactly what admin set (e.g. Bagmati + Lalitpur)
    
    # 1. Province + District + City
    if p and d and c:
        rule = active_rules.filter(province__iexact=p, district__iexact=d, city_or_municipality__iexact=c).first()
        if rule: return rule

    # 2. Province + District
    if p and d:
        rule = active_rules.filter(province__iexact=p, district__iexact=d, city_or_municipality='').first()
        if rule: return rule

    # 3. Province Only
    if p:
        rule = active_rules.filter(province__iexact=p, district='', city_or_municipality='').first()
        if rule: return rule

    # --- SMART FALLBACK (District ONLY) ---
    # If Province match failed (due to typo/Google variation), but District is identified
    # and we have a unique rule for that District, we use it.
    if d:
        # Search for any rule matching this district, ignoring the province field 
        # to handle spelling mismatches in the province name (e.g. Bagamati vs Bagmati).
        rule = active_rules.filter(district__iexact=d).first()
        if rule:
            return rule

    # --- FINAL FALLBACK (Default Rule) ---
    return active_rules.filter(is_default=True).first()


def get_all_active_rules():
    """Returns all active shipping rules ordered by priority."""
    return ShippingRule.objects.filter(is_active=True).order_by('priority')
