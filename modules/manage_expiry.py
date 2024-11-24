import argparse
from modules.account_expiry import check_expiry, extend_expiry, reset_expiry

def main():
    parser = argparse.ArgumentParser(
        description="Скрипт для управления сроком действия VPN аккаунтов WireGuard"
    )

    subparsers = parser.add_subparsers(dest="action", help="Доступные команды")

    check_parser = subparsers.add_parser("check", help="Проверить, истек ли срок действия аккаунта")
    check_parser.add_argument("nickname", type=str, help="Имя пользователя для проверки")

    extend_parser = subparsers.add_parser("extend", help="Продлить срок действия аккаунта")
    extend_parser.add_argument("nickname", type=str, help="Имя пользователя для продления")
    extend_parser.add_argument("days", type=int, help="Количество дней для продления срока действия")

    reset_parser = subparsers.add_parser("reset", help="Сбросить срок действия аккаунта")
    reset_parser.add_argument("nickname", type=str, help="Имя пользователя для сброса срока")
    reset_parser.add_argument(
        "--days", type=int, default=30,
        help="Новый срок действия в днях (по умолчанию 30 дней)"
    )

    args = parser.parse_args()

    try:
        if args.action == "check":
            result = check_expiry(args.nickname)
            if result["status"] == "expired":
                print(f"Срок действия аккаунта пользователя {args.nickname} истек.")
            else:
                print(f"Аккаунт пользователя {args.nickname} еще действителен. {result['remaining_time']}")

        elif args.action == "extend":
            extend_expiry(args.nickname, args.days)

        elif args.action == "reset":
            reset_expiry(args.nickname, args.days)

        else:
            parser.print_help()

    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
