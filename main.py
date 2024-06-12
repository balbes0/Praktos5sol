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
    except:
        pass

def check_password_complexity(password):
    if len(password) >= 12 and re.search(r'[A-Z]', password) and re.search(r'[a-z]', password) and re.search(r'[0-9]', password):
        return True
    else:
        return False

def get_public_key(_public_key):
    public_key = Web3.to_checksum_address(_public_key)
    return public_key

def login_sol(public_key, password):
    try:
        checksum_public_key = Web3.to_checksum_address(public_key)
        w3.geth.personal.unlock_account(checksum_public_key, password)
        return True
    except:
        return False
    
def register_sol(password):
    try:
        account = w3.geth.personal.new_account(password)
        give_balance_to_user(account)
        with open('info.txt', 'a', encoding="utf-8") as f:
            f.write('\nПубличный ключ: {}, пароль: {}'.format(account, password))
        return True
    except:
        return False

def createEstate(account, address, square, type):
    try:
        tx_hash = contract.functions.createEstate(address, square, type).transact({
            "from": account
        })
        return(f"Транзакция отправлена: {tx_hash.hex()}")
    except Exception as e:
        error_message = str(e).split(': ')[1].split(',')[0].strip("'")
        return(f"Ошибка при создании недвижимости: {error_message}")


def GetAvailableAdvertisements():
    try:
        toReturn = []
        estates = getEstates()
        ads = contract.functions.getAds().call()
        for ad in ads:
            for estate in estates:
                if ad[2] == estate[5] and estate[4] == "Активный" and ad[6] == 0:
                    if ad[6] == 0:
                        status = "Открыт"
                    else:
                        status = "Закрыт"
                    extended_estate = estate + (ad[1],ad[0],status,)
                    toReturn.append(extended_estate)
        return toReturn
    except Exception as e:
        return(f"{e}")

def getEstates():
    try:
        estates = contract.functions.getEstates().call()
        toReturn = []
        if len(estates) > 0:
            for estate in estates:
                if estate[2] == 0:
                    estate_type = "Дом"
                elif estate[2] == 1:
                    estate_type = "Квартира"
                elif estate[2] == 2:
                    estate_type = "Промышленный объект"
                elif estate[2] == 3:
                    estate_type = "Дача"
                if estate[4] == True:
                    status = "Активный"
                elif estate[4] == False:
                    status = "Неактивный"
                estate_info = (estate[0], estate[1], estate_type, estate[3], status, estate[5])
                toReturn.append(estate_info)
            return toReturn
        else:
            return ("Список недвижимостей пуст",)
    except Exception as e:
        return (f"Ошибка при просмотре недвижимости: {e}",)

def createAd(account, price, estateid):
    try:
        date = int(datetime.now().strftime("%d%m%Y"))
        tx_hash = contract.functions.createAd(price, estateid, date).transact({
            "from": account
        })
        return(f"Транзакция отправлена: {tx_hash.hex()}")
    except Exception as e:
        error_message = str(e).split(': ')[1].split(',')[0].strip("'")
        return(f"Ошибка при создании недвижимости: {error_message}")


def GetMyEstates(account):
    try:
        estates = contract.functions.getEstates().call()
        my_estates = []
        
        for estate in estates:
            if estate[3] == account:
                modified_estate = list(estate)
                if estate[2] == 0:
                    type = "Дом"
                elif estate[2] == 1:
                    type = "Квартира"
                elif estate[2] == 2:
                    type = "Промышленный объект"
                elif estate[2] == 3:
                    type = "Дача"
                modified_estate[2] = type
                if estate[4] == True:
                    status = "Активный"
                elif estate[4] == False:
                    status = "Неактивный"
                modified_estate[4] = status
                my_estates.append(modified_estate)
        
        return my_estates
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def updateEstateStatus(account, id, status):
    try:
        GetMyEstates(account)
        estates = contract.functions.getEstates().call()
        myestatesID = []
        for estate in estates:
            if estate[3] == account:
                myestatesID.append(estate[5])
        if id in myestatesID:
            contract.functions.updateEstateActive(id, status).transact({
                "from": account
            })
            return("Статус недвижимости был успешно изменен!")
        else:
            return("Такой недвижимости не существует или вы не его владелец!")
    except Exception as e:
        error_message = str(e).split(': ')[1].split(',')[0].strip("'")
        return(f"Ошибка при изменени статуса недвижимости: {error_message}")

def GetMyAds(account):
    try:
        ads = contract.functions.getAds().call()
        myAds = []
        if len(ads) > 0:
            for ad in ads:
                if ad[3] == account:
                    modified_ad = list(ad)
                    if ad[4] == "0x0000000000000000000000000000000000000000":
                        modified_ad[4] = "Отсутствует"
                    if ad[6] == 0:
                        modified_ad[6] = "Открыт"
                    elif ad[6] == 1:
                        modified_ad[6] = "Закрыт"
                    myAds.append(modified_ad)
        return myAds
    except:
        return []


def updateAdStatus(account, id, status):
    try:
        myAds = GetMyAds(account)
        myAdsID = [ad[3] for ad in myAds]
        
        if account in myAdsID:
            contract.functions.updateAdType(id, status).transact({"from": account})
            return "Статус объявления был успешно изменен"
        else:
            return "Данных объявлений не существует или вы не его владелец!"
    except Exception as e:
        error_message = str(e).split(': ')[1].split(',')[0].strip("'")
        return f"Ошибка при изменении статуса объявления: {error_message}"

    
def GetBalanceOnContract(account):
    try:
        balance = contract.functions.getBalance().call({
            "from": account
        })
        return(balance)
    except:
        return 0

def deposit(account, amount):
    try:
        tx_hash = contract.functions.deposit().transact({
            "from": account,
            "value": amount
        })
        return(f"Транзакция отправлена: {tx_hash.hex()}, счет: {account}")
    except Exception as e:
        error_message = str(e).split(': ')[1].split(',')[0].strip("'")
        return(f"Ошибка при депозите средств на контракт: {error_message}")

def WithDraw(account, amount):
    try:
        tx_hash = contract.functions.withdraw(amount).transact({
            "from": account
        })
        return(f"Транзакция отправлена: {tx_hash.hex()}")
    except Exception as e:
        error_message = str(e).split(': ')[1].split(',')[0].strip("'")
        return(f"Ошибка при выводе средств: {error_message}")

def GetBalanceOnAccount(account):
    try:
        balance = w3.eth.get_balance(account)
        return(balance)
    except:
        return 0

def BuyEstate(account, id):
    try:
        tx_hash = contract.functions.buyEstate(id).transact({
            "from": account
        })
        return(f"Недвижимость было успешно куплена, транзакция отправлена: {tx_hash.hex()}")
    except Exception as e:
        error_message = str(e).split(': ')[1].split(',')[0].strip("'")
        return(f"Ошибка при покупке недвижимости: {error_message}")