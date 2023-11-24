import secrets


def generate_coupon_code(length=8):
    # Generate a random hex string with the specified length
    coupon_code = secrets.token_hex(length // 2)

    # Format the code to be uppercase and return it
    return coupon_code.upper()
