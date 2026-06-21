import bcrypt


# Method for Checking Password Strength
# Password should:
# 1. Be 10 charachters in length
# 2. Have Upper and Lowercase letters
# 3. Have digits
# 4. Have special charachter
def password_strength(password):
    score = 0

    length = len(password)
    upper = False
    lower = False
    special = False
    digits = False


    for c in password:
        # Checking for Upper Letters
        if c.isupper():
            upper = True

        # Checking for Lower Letters
        if c.islower():
            lower = True

        # Checking for Special Charachter
        if not c.isalnum():
            special = True

        # Checking for Digits
        if c.isdigit():
            digits = True


    if length >= 10:
        score += 1
        print('Adding length')

    if upper:
        score += 1
        print('Adding upper')

    if lower:
        score += 1
        print('Adding lower')

    if special:
        score += 1
        print('Adding special')

    if digits:
        score += 1
        print('Adding digits')

    return score

# Method for Hashing Passwords
def password_hashing(password, salt=None):
    bytes_password = password.encode()
    generated_values  = {}
    
    if salt == None:
        generated_values['salt'] = bcrypt.gensalt()
    else:
        generated_values['salt'] = salt

    generated_values['hash'] = bcrypt.hashpw(bytes_password, generated_values['salt']) # Hashing Password with Salt
    return generated_values