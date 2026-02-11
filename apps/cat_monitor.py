import json
from rascan.reader import CANReader

# risk thresholds
RISK_RULES = [
    {'name': 'Over-speed', 'check': lambda s: s.get('Speed', 0) > 120, 'level': 'High'},
    {'name': 'Aggressive throttle', 'check': lambda s: s.get('Throttle', 0) > 80, 'level': 'Medium'},
    {'name': 'Hard braking', 'check': lambda s: s.get('Brake', 0) > 70, 'level': 'Medium'},
    {'name': 'Sharp steering', 'check': lambda s: abs(s.get('Steering', 0)) > 30, 'level': 'Medium'},
    {'name': 'No turn signal while turning', 'check': lambda s: abs(s.get('Steering', 0)) > 10 and not (s.get('Left') or s.get('Right')), 'level': 'Low'},
]

def evaluate_risk(temp_frame):
    """Combine signals and evaluate risks for a full frame."""
    # merge all signals
    signals_combined = {}
    signals_combined.update(temp_frame.get(256, {}))
    signals_combined.update(temp_frame.get(257, {}))
    signals_combined.update(temp_frame.get(258, {}))

    #write raw signals file
    raw_signals_path = 'raw_decoded_signals.json'
    with open(raw_signals_path, 'w') as json_file:
        json.dump(signals_combined , json_file, indent=4)

    risks = []
    for rule in RISK_RULES:
        if rule['name'] == 'No turn signal while turning':
            check_signals = signals_combined.copy()
            if rule['check'](check_signals):
                risks.append({'behavior': rule['name'], 'level': rule['level']})
        else:
            if rule['check'](signals_combined):
                risks.append({'behavior': rule['name'], 'level': rule['level']})

    # Determine overall risk
    if any(r['level'] == 'High' for r in risks):
        overall = 'High'
    elif any(r['level'] == 'Medium' for r in risks):
        overall = 'Medium'
    elif any(r['level'] == 'Low' for r in risks):
        overall = 'Low'
    else:
        overall = 'Safe'

    return {
        'Signals': signals_combined,
        'Risk Level': overall,
        'Risks': risks
    }

def main():
    reader = CANReader("dbc/example.dbc")
    temp_frame = {}  # holds full frame with ids 256, 257, 258

    while True:
        frame = reader.read()
        if frame:
            frame_id = frame['id']
            signals = frame['signals']

            if frame_id in [256, 257, 258]:
                temp_frame[frame_id] = signals

            # Once we have all 3 messages, evaluate
            if all(k in temp_frame for k in [256, 257, 258]):
                result = evaluate_risk(temp_frame)
                #writes latest frame to file 
                categorized_path = 'categorized_data.json'
                with open(categorized_path, 'w') as json_file:
                    json.dump(result , json_file, indent=4)
                print(json.dumps(result, indent=4))
                temp_frame = {}  # reset for next frame

if __name__ == "__main__":
    main()