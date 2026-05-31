def calculate_risk_flags(input_dict):
    flags = []

    duration_weeks = input_dict.get('duration_weeks', 0)
    material_grade = input_dict.get('material_grade', '')
    project_type = input_dict.get('project_type', '')
    location_tier = input_dict.get('location_tier', '')
    size_sqft = input_dict.get('size_sqft', 0)
    num_floors = input_dict.get('num_floors', 0)

    # Rule 1: Long duration → schedule risk
    if duration_weeks > 52:
        flags.append({
            'flag': 'Schedule Risk',
            'severity': 'High',
            'description': f'Project duration of {duration_weeks} weeks exceeds 1 year.',
            'mitigation': 'Break project into phases. Set monthly milestone reviews.'
        })

    # Rule 2: Budget materials on Commercial → quality risk
    if material_grade == 'Budget' and project_type == 'Commercial':
        flags.append({
            'flag': 'Quality Risk',
            'severity': 'High',
            'description': 'Budget materials on a Commercial project risk regulatory non-compliance.',
            'mitigation': 'Upgrade to Standard grade. Budget materials fail BIS commercial standards.'
        })

    # Rule 3: Tier1 city → labor escalation risk
    if location_tier == 'Tier1':
        flags.append({
            'flag': 'Labor Escalation Risk',
            'severity': 'Medium',
            'description': 'Tier1 cities like Mumbai and Delhi have high labor cost volatility.',
            'mitigation': 'Lock in labor contracts early. Add 15% labor cost buffer to budget.'
        })

    # Rule 4: Large project → complexity risk
    if size_sqft > 50000:
        flags.append({
            'flag': 'Complexity Risk',
            'severity': 'Medium',
            'description': f'Project size of {size_sqft:,} sqft requires advanced project management.',
            'mitigation': 'Assign dedicated project manager. Use phased construction approach.'
        })

    # Rule 5: High rise → structural risk (India specific)
    if num_floors > 10:
        flags.append({
            'flag': 'Structural Risk',
            'severity': 'High',
            'description': f'{num_floors} floor structure requires NBC 2016 compliance and soil testing.',
            'mitigation': 'Engage structural consultant. Conduct geotechnical survey before foundation.'
        })

    # Rule 6: No flags → healthy project
    if not flags:
        flags.append({
            'flag': 'No Significant Risks',
            'severity': 'Low',
            'description': 'Project parameters are within normal operational range.',
            'mitigation': 'Standard monitoring recommended.'
        })

    return flags


if __name__ == '__main__':
    # Test 1: High risk commercial project
    test1 = {
        'project_type': 'Commercial',
        'location_tier': 'Tier1',
        'size_sqft': 75000,
        'num_floors': 15,
        'material_grade': 'Budget',
        'duration_weeks': 60
    }
    print("Test 1 - High Risk Commercial:")
    for flag in calculate_risk_flags(test1):
        print(f"  [{flag['severity']}] {flag['flag']}: {flag['description']}")

    print()

    # Test 2: Low risk residential project
    test2 = {
        'project_type': 'Residential',
        'location_tier': 'Tier2',
        'size_sqft': 2000,
        'num_floors': 2,
        'material_grade': 'Standard',
        'duration_weeks': 20
    }
    print("Test 2 - Low Risk Residential:")
    for flag in calculate_risk_flags(test2):
        print(f"  [{flag['severity']}] {flag['flag']}: {flag['description']}")