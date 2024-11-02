import random

# Assume trainedDataMatrix is already defined as per your provided data
# We need to define resolveToJamoIndex and other helper functions

# Helper function to expand compressed arrays (Run-Length Decoding)
def expand_array(compressed_array):
    expanded = []
    for value in compressed_array:
        if value >= 0:
            expanded.append(value)
        else:
            expanded.extend([0] * abs(value))
    return expanded

# Function to resolve a syllable to Jamo indices
def resolveToJamoIndex(syllable):
    # Hangul syllables range from U+AC00 to U+D7A3
    base_code = ord(syllable) - 0xAC00
    if 0 <= base_code <= (0xD7A3 - 0xAC00):
        choseong = base_code // (21 * 28)
        jungseong = (base_code % (21 * 28)) // 28
        jongseong = base_code % 28
        return [choseong, jungseong, jongseong]
    else:
        # Not a Hangul syllable
        return None

# Function to calculate the probability of a Jamo index using the trained data
def calculate_probability(trainedDataMatrix, set_index, jamo_indices):
    probabilities = []

    # Expand the compressed arrays
    trained_data_set = trainedDataMatrix[set_index]
    counts_0 = expand_array(trained_data_set[0])
    counts_1 = expand_array(trained_data_set[1])
    counts_2 = expand_array(trained_data_set[2])
    counts_3 = expand_array(trained_data_set[3])

    # Calculate probabilities for each Jamo index
    # Choseong
    total_0 = sum(counts_0)
    prob_choseong = counts_0[jamo_indices[0]] / total_0 if total_0 > 0 else 0

    # Jungseong given Choseong
    index_1 = jamo_indices[0] * 21 + jamo_indices[1]
    total_1 = sum(counts_1)
    prob_jungseong = counts_1[index_1] / total_1 if total_1 > 0 else 0

    # Jongseong given Jungseong and Choseong
    index_2 = jamo_indices[1] * 28 + jamo_indices[2]
    index_3 = jamo_indices[0] * 28 + jamo_indices[2]
    count_2 = counts_2[index_2] if index_2 < len(counts_2) else 0
    count_3 = counts_3[index_3] if index_3 < len(counts_3) else 0
    total_2 = sum(counts_2)
    total_3 = sum(counts_3)
    prob_jongseong = ((count_2 / total_2 if total_2 > 0 else 0) *
                      (count_3 / total_3 if total_3 > 0 else 0))

    # Overall probability for the syllable
    overall_prob = prob_choseong * prob_jungseong * prob_jongseong
    return overall_prob

# Function to classify if a given text is likely a Korean name
def classify_name(name, trainedDataMatrix, lastNames, lastNameFrequency):
    # Check if the name is at least two characters (Surname + Given name)
    if len(name) < 2:
        return False

    # Split the name into surname and given name
    surname = name[0]
    given_name = name[1:]

    # Process surname
    surname_code = ord(surname) - 0xAC00
    is_valid_surname = surname_code in [code - 0xAC00 for code in lastNames]
    if not is_valid_surname:
        return False

    # Process given name syllables
    syllables = list(given_name)
    if len(syllables) != 2:
        # The model is trained on two-syllable given names
        return False

    probs = []
    for i, syllable in enumerate(syllables):
        jamo_indices = resolveToJamoIndex(syllable)
        if not jamo_indices:
            return False  # Invalid syllable

        # For the first syllable, use set 0; for the second, use set 1
        syllable_prob = calculate_probability(trainedDataMatrix, i, jamo_indices)
        probs.append(syllable_prob)

    # Calculate the overall probability
    overall_prob = probs[0] * probs[1]

    # Define a threshold for classification
    # Since probabilities can be very small, you may need to adjust this
    threshold = 1e-12  # Adjust based on experimentation

    return overall_prob > threshold

# Example usage:

# Assuming trainedDataMatrix, lastNames, and lastNameFrequency are defined as per your data

# Let's define trainedDataMatrix by expanding the compressed arrays
def expand_trained_data(firstNames):
    trainedDataMatrix = [[], []]
    for set_index in range(2):  # Male and Female
        trained_set = []
        for array_index in range(4):  # Four arrays per set
            compressed_array = firstNames[set_index][0][array_index]
            expanded_array = expand_array(compressed_array)
            trained_set.append(expanded_array)
        trainedDataMatrix[set_index].append(trained_set)
    return trainedDataMatrix

# For simplicity, let's assume we are only using male names (set_index = 0)
trainedDataMatrix = []
for set_index in range(2):
    trained_set = []
    for syllable_index in range(2):  # First and second syllables
        syllable_data = []
        for array_index in range(4):
            compressed_array = firstNames[set_index][syllable_index][array_index]
            expanded_array = expand_array(compressed_array)
            syllable_data.append(expanded_array)
        trained_set.append(syllable_data)
    trainedDataMatrix.append(trained_set)

# Now we can classify a given name
name = '김철수'  # Example name
is_likely_korean_name = classify_name(name, trainedDataMatrix[0], lastNames, lastNameFrequency)
print(f"The name '{name}' is likely a Korean name: {is_likely_korean_name}")

