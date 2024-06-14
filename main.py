from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract_info import abi, address_contract
import re
from datetime import datetime

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract = w3.eth.contract(address=address_contract, abi=abi)

start_capital = "0xEd16A0890751E5B6A54b9Ba4D4A3Bcde6EF2c775"

def give_balance_to_user(public_key):
    try:
        w3.eth.send_transaction({'to': public_key, 'from': start_capital, 'value': w3.to_wei(10, 'ether')})
    except Exception as e:
        print(f"Ошибка при переводе баланса: {e}")

def check_password_complexity(password):
    return len(password) >= 12 and re.search(r'[A-Z]', password) and re.search(r'[a-z]', password) and re.search(r'[0-9]', password)

def get_public_key(_public_key):
    return Web3.to_checksum_address(_public_key)

def login_sol(public_key, password):
    try:
        checksum_public_key = Web3.to_checksum_address(public_key)
        w3.geth.personal.unlock_account(checksum_public_key, password)
        return True
    except Exception as e:
        print(f"Login error: {e}")
        return False

def register_sol(password):
    try:
        account = w3.geth.personal.new_account(password)
        give_balance_to_user(account)
        with open('info.txt', 'a', encoding="utf-8") as f:
            f.write(f'\nПубличный ключ: {account}, пароль: {password}')
        return True
    except Exception as e:
        print(f"Ошибка при регистрации: {e}")
        return False

def create_estate_main(account, address, square, type):
    try:
        tx_hash = contract.functions.createEstate(address, square, type).transact({"from": account})
        return f"Транзакция отправлена: {tx_hash.hex()}"
    except Exception as e:
        error_message = str(e).split(': ')[1].split(',')[0].strip("'")
        return f"Ошибка при создании недвижимости: {error_message}"

def get_estates():
    try:
        estates = contract.functions.getEstates().call()
        estate_types = ["Дом", "Квартира", "Промышленный объект", "Дача"]
        statuses = ["Неактивный", "Активный"]
        to_return = [(estate[0], estate[1], estate_types[estate[2]], estate[3], statuses[estate[4]], estate[5]) for estate in estates]
        return to_return if to_return else ["Список недвижимостей пуст"]
    except Exception as e:
        return [f"Ошибка при просмотре недвижимости: {e}"]

def get_available_advertisements():
    try:
        ads = contract.functions.getAds().call()
        estates = get_estates()
        available_ads = []
        for ad in ads:
            for estate in estates:
                if ad[2] == estate[5] and estate[4] == "Активный" and ad[6] == 0:
                    status = "Открыт" if ad[6] == 0 else "Закрыт"
                    extended_estate = estate + (ad[1], ad[0], status)
                    available_ads.append(extended_estate)
        return available_ads
    except Exception as e:
        print(f"Ошибка при получении доступных объявлений.: {e}")
        return []

def create_ad_main(account, price, estateid):
    try:
        date = int(datetime.now().strftime("%d%m%Y"))
        tx_hash = contract.functions.createAd(price, estateid, date).transact({"from": account})
        return f"Транзакция отправлена: {tx_hash.hex()}"
    except Exception as e:
        error_message = str(e).split(': ')[1].split(',')[0].strip("'")
        return f"Ошибка при создании недвижимости: {error_message}"

def get_my_estates(account):
    try:
        estates = contract.functions.getEstates().call()
        estate_types = ["Дом", "Квартира", "Промышленный объект", "Дача"]
        statuses = ["Неактивный", "Активный"]
        my_estates = [list(estate) for estate in estates if estate[3] == account]
        for estate in my_estates:
            estate[2] = estate_types[estate[2]]
            estate[4] = statuses[estate[4]]
        return my_estates
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []

def update_estate_status(account, id, status):
    try:
        my_estates = get_my_estates(account)
        my_estate_ids = [estate[5] for estate in my_estates]
        if id in my_estate_ids:
            contract.functions.updateEstateActive(id, status).transact({"from": account})
            return "Статус недвижимости был успешно изменен!"
        else:
            return "Такой недвижимости не существует или вы не его владелец!"
    except Exception as e:
        error_message = str(e).split(': ')[1].split(',')[0].strip("'")
        return f"Ошибка при изменении статуса недвижимости: {error_message}"

def get_my_ads(account):
    try:
        ads = contract.functions.getAds().call()
        ad_statuses = ["Открыт", "Закрыт"]
        my_ads = [list(ad) for ad in ads if ad[3] == account]
        for ad in my_ads:
            ad[4] = "Отсутствует" if ad[4] == "0x0000000000000000000000000000000000000000" else ad[4]
            ad[6] = ad_statuses[ad[6]]
        return my_ads
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []

def update_ad_status(account, id, status):
    try:
        my_ads = get_my_ads(account)
        my_ad_ids = [ad[0] for ad in my_ads]
        if id in my_ad_ids:
            contract.functions.updateAdType(id, status).transact({"from": account})
            return "Статус объявления был успешно изменен"
        else:
            return "Данных объявлений не существует или вы не его владелец!"
    except Exception as e:
        error_message = str(e).split(': ')[1].split(',')[0].strip("'")
        return f"Ошибка при изменении статуса объявления: {error_message}"

def get_balance_on_contract(account):
    try:
        return contract.functions.getBalance().call({"from": account})
    except Exception as e:
        print(f"Ошибка получения баланса: {e}")
        return 0

def deposit(account, amount):
    try:
        tx_hash = contract.functions.deposit().transact({"from": account, "value": amount})
        return f"Транзакция отправлена: {tx_hash.hex()}, счет: {account}"
    except Exception as e:
        error_message = str(e).split(': ')[1].split(',')[0].strip("'")
        return f"Ошибка при депозите средств на контракт: {error_message}"

def withdraw(account, amount):
    try:
        tx_hash = contract.functions.withdraw(amount).transact({"from": account})
        return f"Транзакция отправлена: {tx_hash.hex()}"
    except Exception as e:
        error_message = str(e).split(': ')[1].split(',')[0].strip("'")
        return f"Ошибка при выводе средств: {error_message}"

def get_balance_on_account(account):
    try:
        return w3.eth.get_balance(account)
    except Exception as e:
        print(f"Ошибка получения баланса: {e}")
        return 0

def buy_estate(account, id):
    try:
        tx_hash = contract.functions.buyEstate(id).transact({"from": account})
        return f"Недвижимость была успешно куплена, транзакция отправлена: {tx_hash.hex()}"
    except Exception as e:
        error_message = str(e).split(': ')[1].split(',')[0].strip("'")
        return f"Ошибка при покупке недвижимости: {error_message}"
