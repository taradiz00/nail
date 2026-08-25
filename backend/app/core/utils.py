def normalize_phone(phone: str) -> str:
    phone = phone.strip().replace(" ", "").replace("-", "")

    if phone.startswith("0098"):
        phone = "+98" + phone[4:]

    elif phone.startswith("98"):
        phone = "+" + phone

    elif phone.startswith("0"):
        phone = "+98" + phone[1:]

    if not phone.startswith("+98"):
        raise ValueError("Invalid phone number")

    return phone