#!/usr/bin/env python3
# modules/main_registration_fields.py
## Main module for generating user fields

import uuid
from datetime import datetime, timedelta

def create_user_record(
    username,
    address,
    public_key,
    preshared_key,
    qr_code_path,
    email="N/A",
    telegram_id="N/A",
    referral_id=None,
    coupon_id=None,
    group="guest",
    subscription_plan="free",
    payment_method="N/A",
    preferred_language="en"
):
    """
    Creates and returns a user data structure.

    Args:
        username (str): The username of the user.
        address (str): The user's allowed IP address.
        public_key (str): The user's public key.
        preshared_key (str): The pre-shared key for the user.
        qr_code_path (str): Path to the user's QR code.
        email (str, optional): User's email address. Defaults to "N/A".
        telegram_id (str, optional): User's Telegram ID. Defaults to "N/A".
        referral_id (str, optional): Referral ID. Defaults to None.
        coupon_id (str, optional): Coupon ID. Defaults to None.
        group (str, optional): User group. Defaults to "guest".
        subscription_plan (str, optional): Subscription plan. Defaults to "free".
        payment_method (str, optional): Payment method. Defaults to "N/A".
        preferred_language (str, optional): Preferred language. Defaults to "en".

    Returns:
        dict: A dictionary representing the user's data structure.
    """
    current_time = datetime.now()
    user_record = {
        "username": username,
        "user_id": str(uuid.uuid4()),  # Generate a unique UUID
        "group": group,
        "tags": ["default-user"],
        "priority": 1,
        "created_at": current_time.isoformat(),
        "expires_at": (current_time + timedelta(days=30)).isoformat(),  # Validity period: 30 days
        "auto_suspend_date": (current_time + timedelta(days=30)).isoformat(),
        "auto_delete_date": (current_time + timedelta(days=30)).isoformat(),
        "last_config_update": current_time.isoformat(),
        "status": "active",
        "blocked_reason": "N/A",
        "renewal_requested": False,
        "allowed_ips": address,
        "allowed_ips_custom": address,
        "dns_custom": "1.1.1.1,8.8.8.8",
        "public_key": public_key,
        "preshared_key": preshared_key,
        "endpoint": "N/A",
        "last_handshake": "N/A",
        "uploaded": "N/A",
        "downloaded": "N/A",
        "transfer": "0.0 KiB received, 0.0 KiB sent",
        "total_transfer": "0.0 KiB",
        "data_limit": "100.0 GB",
        "data_used": "0.0 KiB",
        "qr_code_path": qr_code_path,
        "email": email,
        "telegram_id": telegram_id,
        "contact_method": "telegram",
        "referral_id": referral_id,
        "coupon_id": coupon_id,
        "referral_earnings": "0.00 USD",
        "referral_count": 0,
        "referral_bonus": "0%",
        "subscription_plan": subscription_plan,
        "subscription_price": "0.00 USD",
        "payment_method": payment_method,
        "last_payment_date": "N/A",
        "next_payment_date": "N/A",
        "payment_status": "inactive",
        "total_spent": "0.00 USD",
        "auto_renew": False,
        "transaction_history": [],
        "preferred_language": preferred_language,
        "admin_notes": "N/A",
        "user_notes": "N/A",
        "ip_history": []
    }
    return user_record
