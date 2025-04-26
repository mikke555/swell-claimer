import questionary
from questionary import Choice

import settings
from data.const import style
from modules.controller import Controller
from modules.logger import logger
from modules.utils import get_accounts, random_sleep, sleep


def get_action() -> str:
    action = questionary.select(
        "Select action",
        choices=[
            Choice("Claim Swell rewards", value="claim_swell"),
            Choice("Check Swell rewards", value="check_swell"),
            Choice("Exit", value="exit"),
        ],
        style=style,
    ).ask()

    if action == "exit" or action is None:
        exit(0)

    return action


def main():
    accounts = get_accounts()
    action = get_action()

    for index, account in enumerate(accounts, start=1):
        controller = Controller(account, action)
        controller.execute()

        if index < len(accounts):
            random_sleep(*settings.SLEEP_BETWEEN_WALLETS)

    logger.success("All done! 🎉")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Cancelled by user")
    # except Exception as e:
    #     logger.error(f"An error occurred: {e}")
