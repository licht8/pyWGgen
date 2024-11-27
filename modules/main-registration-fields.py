#!/usr/bin/env python3
# modules/main-registration-fields.py
## Основной модуль для генерации полей пользователя

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
    Создает и возвращает структуру данных пользователя.
    """
    current_time = datetime.now()
    user_record = {
        "username": username,
        "user_id": str(uuid.uuid4()),  # Генерация уникального UUID
        "group": group,
        "tags": ["default-user"],
        "priority": 1,
        "created_at": current_time.isoformat(),
        "expires_at": (current_time + timedelta(days=30)).isoformat(),  # Срок действия 30 дней
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
