import random

# Assuming lastNames, lastNameFrequency, and firstNames are defined as per your data

# Helper function to construct a syllable from Jamo indices
def constructFromJamoIndex(indices):
    choseong_base = 0x1100
    jungseong_base = 0x1161
    jongseong_base = 0x11A7  # Note: 0x11A7 is one less than the actual base to account for 0 index

    choseong, jungseong, jongseong = indices
    syllable = chr(0xAC00 + (choseong * 21 * 28) + (jungseong * 28) + jongseong)
    return syllable

# Function to generate all possible syllables based on firstNames data
def generate_valid_syllables(firstNamesData):
    valid_syllables = set()
    for genderData in firstNamesData:
        for setData in genderData:
            choseong_weights, jungseong_weights, jongseong_weights, _ = setData
            for i, cw in enumerate(choseong_weights):
                if cw > 0:
                    for j, jw in enumerate(jungseong_weights):
                        if jw > 0:
                            for k, kw in enumerate(jongseong_weights):
                                if kw > 0:
                                    syllable = constructFromJamoIndex([i, j, k])
                                    valid_syllables.add(syllable)
    return valid_syllables

# Function to check if the first name is valid
def is_valid_first_name(first_name, valid_syllables):
    # Split the first name into syllables
    syllables = list(first_name)
    for syllable in syllables:
        if syllable not in valid_syllables:
            return False
    return True

# Main function to determine if a text is a Korean name
def is_korean_name(name, lastNames, lastNameFrequency, firstNames):
    # Normalize the name by removing spaces
    name = name.strip()

    # Generate a mapping of last name codes to characters
    last_name_chars = [chr(code + 0xAC00) for code in lastNames]
    last_name_set = set(last_name_chars)

    # Generate valid syllables from the firstNames data
    valid_syllables = generate_valid_syllables(firstNames)

    # Try possible splits for the last name (considering one or two syllable last names)
    max_last_name_length = 2  # Adjust based on known last name lengths
    for i in range(1, min(max_last_name_length + 1, len(name))):
        last_name_candidate = name[:i]
        if last_name_candidate in last_name_set:
            first_name_candidate = name[i:]
            if len(first_name_candidate) >= 1 and is_valid_first_name(first_name_candidate, valid_syllables):
                return True
    return False

if __name__ == "__main__":
    from trained_data import Name_Likelihoods
    L_nm = Name_Likelihoods()
    name = "지승현"  # Replace with the name you want to check
    if is_korean_name(name, L_nm.lastNames, L_nm.lastNameFrequency, L_nm.firstNames):
        print(f"{name} is likely a Korean name.")
    else:
        print(f"{name} is unlikely to be a Korean name.")
