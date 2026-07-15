# =============================================================
# modules/ai_assistant.py - AI Assistant Module (Rule-Based)
# =============================================================
# A simple rule-based AI assistant — NO external API needed.
# It reads data from the database and gives smart suggestions
# based on predefined rules.
#
# Rules covered:
#   - Milk production drop  → suggest nutrition improvement
#   - High temperature      → suggest hydration
#   - Symptoms: "fever"     → suggest calling vet
#   - Symptoms: "cough"     → suggest isolation
#   - Low weight cow        → suggest more nutrition
#   - General farm tips
# =============================================================

from database import get_connection
from config import print_header, print_line


# ---------------------------------------------------------
# Helper: print an AI suggestion box
# ---------------------------------------------------------
def ai_say(message):
    """Prints a nicely formatted AI suggestion."""
    print("\n  ┌─────────────────────────────────────────────┐")
    # Word-wrap the message to fit the box
    words   = message.split()
    line    = "  │  "
    for word in words:
        if len(line) + len(word) + 1 > 48:
            print(f"{line:<49}│")
            line = f"  │  {word} "
        else:
            line += word + " "
    if line.strip() != "│":
        print(f"{line:<49}│")
    print("  └─────────────────────────────────────────────┘\n")


# ---------------------------------------------------------
# Rule Engine: check a symptom string for keywords
# ---------------------------------------------------------
def analyze_symptoms(symptoms: str):
    """
    Rule-based symptom checker.
    Returns a list of suggestions based on keywords found.
    """
    symptoms_lower = symptoms.lower()
    suggestions    = []

    if "fever" in symptoms_lower:
        suggestions.append(
            "FEVER DETECTED: Please contact a veterinarian immediately. "
            "Isolate the cow and monitor temperature every 2 hours."
        )

    if "cough" in symptoms_lower:
        suggestions.append(
            "COUGH DETECTED: Isolate the affected cow from the herd immediately "
            "to prevent spread. Schedule a medical check-up as soon as possible."
        )

    if "diarrhea" in symptoms_lower or "loose stool" in symptoms_lower:
        suggestions.append(
            "DIGESTIVE ISSUE: Ensure clean drinking water. "
            "Reduce concentrate feed temporarily. Consult a vet if it persists."
        )

    if "limping" in symptoms_lower or "lame" in symptoms_lower:
        suggestions.append(
            "LAMENESS DETECTED: Check hooves for injury or infection. "
            "Reduce the cow's movement and apply hoof care treatment."
        )

    if "not eating" in symptoms_lower or "loss of appetite" in symptoms_lower:
        suggestions.append(
            "APPETITE LOSS: Check for dental issues or fever. "
            "Try offering fresh green feed. Consult vet if lasting more than 2 days."
        )

    if not suggestions:
        suggestions.append(
            "No specific issues detected from symptoms. "
            "Monitor the cow closely and consult a vet if condition worsens."
        )

    return suggestions


# ---------------------------------------------------------
# Rule 1: Analyze milk production trend
# ---------------------------------------------------------
def analyze_milk_production():
    """
    Compares last 3 days milk average to the previous 7 days.
    If recent production is lower, suggest nutrition improvement.
    """
    print_header("AI - MILK PRODUCTION ANALYSIS")

    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # Get last 3 days total
        cursor.execute("""
            SELECT AVG(liters) as avg_liters
            FROM milk
            WHERE date >= date('now', '-3 days')
        """)
        recent = cursor.fetchone()['avg_liters'] or 0.0

        # Get previous 7 days total (before last 3 days)
        cursor.execute("""
            SELECT AVG(liters) as avg_liters
            FROM milk
            WHERE date >= date('now', '-10 days')
              AND date <  date('now', '-3 days')
        """)
        previous = cursor.fetchone()['avg_liters'] or 0.0
        conn.close()

        print(f"  Recent avg (last 3 days)    : {recent:.2f} L/session")
        print(f"  Previous avg (last 7 days)  : {previous:.2f} L/session")

        # Apply rule
        if previous > 0 and recent < previous * 0.85:
            drop_pct = ((previous - recent) / previous) * 100
            print(f"\n  ⚠ Milk production dropped by {drop_pct:.1f}%!")
            ai_say(
                "MILK DROP ALERT: Production has decreased significantly. "
                "Recommendations: (1) Increase protein-rich feed such as concentrate. "
                "(2) Ensure adequate water supply. "
                "(3) Check for signs of illness or stress. "
                "(4) Review milking schedule for consistency."
            )
        elif recent == 0 and previous == 0:
            ai_say("Not enough milk data to analyze. Please record more milk entries.")
        else:
            ai_say(
                "Milk production looks stable. Keep maintaining the current "
                "feeding schedule and health checks."
            )

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Rule 2: Check for underweight cows
# ---------------------------------------------------------
def analyze_cow_weights():
    """
    Checks if any active cows are underweight.
    Threshold: below 300 kg for adult cows is flagged.
    """
    print_header("AI - COW WEIGHT ANALYSIS")

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, weight, breed FROM cows WHERE status = 'Active'"
        )
        cows = cursor.fetchall()
        conn.close()

        if not cows:
            print("  No active cows found.")
            return

        underweight = [c for c in cows if c['weight'] < 300]
        healthy     = [c for c in cows if c['weight'] >= 300]

        print(f"  Total active cows: {len(cows)}")
        print(f"  Healthy weight   : {len(healthy)}")
        print(f"  Underweight (<300kg): {len(underweight)}\n")

        if underweight:
            print("  Underweight Cows:")
            for cow in underweight:
                print(f"  → {cow['name']} (ID: {cow['id']}) — {cow['weight']} kg")

            ai_say(
                "UNDERWEIGHT ALERT: Some cows are below the healthy weight threshold. "
                "Recommendations: (1) Increase daily feed quantity, especially hay and concentrate. "
                "(2) Add mineral supplements to their diet. "
                "(3) Schedule a vet check for underlying health issues. "
                "(4) Monitor weight weekly."
            )
        else:
            ai_say("All cows are at a healthy weight. Keep up the good work!")

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Rule 3: Check recent health events
# ---------------------------------------------------------
def analyze_health_events():
    """
    Looks at health records from the last 7 days and gives advice.
    """
    print_header("AI - HEALTH EVENT ANALYSIS")

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT h.*, c.name as cow_name
            FROM health h
            JOIN cows c ON h.cow_id = c.id
            WHERE h.date >= date('now', '-7 days')
            ORDER BY h.date DESC
        """)
        records = cursor.fetchall()
        conn.close()

        if not records:
            print("  No health events in the last 7 days.")
            ai_say("Farm health looks clear this week. Schedule routine vaccinations if due.")
            return

        print(f"  Health events in last 7 days: {len(records)}\n")
        for r in records:
            print(f"  → {r['cow_name']} | {r['record_type']} | {r['date']} | {r['description']}")

        # Check for patterns
        disease_count = sum(1 for r in records if r['record_type'] == "Disease")
        all_descriptions = " ".join(r['description'] for r in records if r['description'])

        if disease_count >= 3:
            ai_say(
                f"HIGH DISEASE ALERT: {disease_count} disease cases in the last 7 days. "
                "This may indicate an outbreak. Recommend immediate herd inspection, "
                "isolation of affected cows, and urgent veterinarian consultation."
            )
        else:
            # Analyze symptom keywords from descriptions
            suggestions = analyze_symptoms(all_descriptions)
            for s in suggestions:
                ai_say(s)

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Rule 4: Symptom checker (manual input)
# ---------------------------------------------------------
def symptom_checker():
    """
    User types symptoms and the AI gives advice.
    """
    print_header("AI - SYMPTOM CHECKER")
    print("  Describe the cow's symptoms (e.g. fever, cough, not eating):")
    symptoms = input("  >> ").strip()

    if not symptoms:
        print("  [!] No symptoms entered.")
        return

    print(f"\n  Analyzing: '{symptoms}'...\n")
    suggestions = analyze_symptoms(symptoms)
    for s in suggestions:
        ai_say(s)


# ---------------------------------------------------------
# Rule 5: General farm tips
# ---------------------------------------------------------
def farm_tips():
    """Displays general best-practice tips for cow farming."""
    print_header("AI - GENERAL FARM TIPS")

    tips = [
        "Feed cows at the same time every day to maintain routine and reduce stress.",
        "Ensure every cow has access to clean, fresh water at all times.",
        "Clean the barn floor daily to prevent hoof diseases and infections.",
        "Vaccinate cows regularly – consult your vet for a schedule.",
        "Record milk production daily to detect drops early.",
        "Weigh cows monthly to monitor nutrition and growth.",
        "Separate sick cows immediately to prevent disease spreading.",
        "Ensure proper ventilation in the barn to avoid respiratory issues.",
        "Check hooves every 2–3 months and trim if necessary.",
        "Maintain a stress-free environment – calm cows produce more milk.",
    ]

    print()
    for i, tip in enumerate(tips, 1):
        print(f"  {i:>2}. {tip}")
    print()


# ---------------------------------------------------------
# AI Assistant Menu
# ---------------------------------------------------------
def ai_menu():
    """Displays the AI Assistant sub-menu."""
    while True:
        print_header("AI ASSISTANT")
        print("  1. Analyze Milk Production")
        print("  2. Analyze Cow Weights")
        print("  3. Analyze Recent Health Events")
        print("  4. Symptom Checker (Enter Symptoms)")
        print("  5. General Farm Tips")
        print("  0. Back to Main Menu")
        print_line()

        choice = input("  Select option: ").strip()

        if   choice == "1": analyze_milk_production()
        elif choice == "2": analyze_cow_weights()
        elif choice == "3": analyze_health_events()
        elif choice == "4": symptom_checker()
        elif choice == "5": farm_tips()
        elif choice == "0": break
        else: print("  [!] Invalid option.")
