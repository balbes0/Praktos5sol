from flask import Flask, request, render_template, url_for, redirect, session, flash
from main import *

app = Flask(__name__)
app.secret_key = 'key_key_key'

@app.route('/index')
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        public_key = request.form.get('public_key')
        password = request.form.get('password')
        result = login_sol(public_key, password)
        if result == True:
            session['public_key'] = public_key
            return redirect(url_for("main", public_key=public_key))
        elif result == False:
            error = "Неправильный публичный ключ или пароль."
            return render_template("login.html", error=error)
    else:
        return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        if password == confirm_password:
            if check_password_complexity(password):
                result = register_sol(password)
                if result == True:
                    correct = "Регистрация проведена успешно! Данные записаны в файл"
                    return render_template("login.html", correct=correct)
                else:
                    error = "Ошибка при регистрации!"
                    return render_template("register.html", error=error)
            else:
                error = "Пароль не соответствует требования безопасности!"
                return render_template("register.html", error=error)
        elif password != confirm_password:
            error = "Первый пароль не равен второму!"
            return render_template("register.html", error=error)
    else:
        return render_template("register.html")

@app.route('/main/<public_key>', methods=['GET', 'POST'])
def main(public_key):
    public_key = session.get('public_key')
    if not public_key:
        return redirect(url_for('index'))
    
    myad = []
    notmyad = []
    list = get_available_advertisements()
    for ad in list:
        if ad[3] == public_key:
            myad.append(ad)
        else:
            notmyad.append(ad)
    balance = get_balance_on_contract(public_key)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'buy_estate':
            ad_id = int(request.form.get('ad_id'))
            result = buy_estate(public_key, ad_id)
            return render_template("main.html", public_key=public_key, balance=balance, notmyad=notmyad, myad=myad, message=result)
        if action == 'edit_ad':
            ad_id = int(request.form.get('ad_id'))
            return redirect(url_for('edit_ad', ID_AD=ad_id))
        if action == 'edit_estate':
            estate_id = int(request.form.get('estate_id'))
            return redirect(url_for('edit_estate', ID_ESTATE=estate_id))
        
    return render_template("main.html", public_key=public_key, balance=balance, notmyad=notmyad, myad=myad)

@app.route('/wallet', methods=['GET', 'POST'])
def wallet():
    public_key = session.get('public_key')
    if not public_key:
        return redirect(url_for('index'))
    
    balance_account = get_balance_on_account(public_key)
    balance_contract = get_balance_on_contract(public_key)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'back':
            return redirect(url_for('main', public_key=public_key))
        if action == 'withdraw':
            amount = int(request.form.get('withdraw_amount'))
            result = withdraw(public_key, amount)
            balance_account = get_balance_on_account(public_key)
            balance_contract = get_balance_on_contract(public_key)
            return render_template("wallet.html", message=result, balance_account=balance_account, balance_contract=balance_contract)
        if action == 'deposit':
            amount = int(request.form.get('deposit_amount'))
            result = deposit(public_key, amount)
            balance_account = get_balance_on_account(public_key)
            balance_contract = get_balance_on_contract(public_key)
            return render_template("wallet.html", message=result, balance_account=balance_account, balance_contract=balance_contract)

    return render_template("wallet.html", balance_account=balance_account, balance_contract=balance_contract)

@app.route('/create_estate', methods=['GET', 'POST'])
def create_estate():
    public_key = session.get('public_key')
    if not public_key:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'back':
            return redirect(url_for('main', public_key=public_key))
        if action == 'create_real_estate':
            address = request.form.get('address')
            street_num = int(request.form.get('street_number'))
            type = request.form.get('property_type')
            if type == "House":
                type_index = 0
            elif type == "Flat":
                type_index = 1
            elif type == "Loft":
                type_index = 2
            elif type == "Dacha":
                type_index = 3
        result = create_estate_main(public_key, address, street_num, type_index)
        return render_template("create_estate.html", message=result)
    return render_template("create_estate.html")

@app.route('/create_ad', methods=['GET', 'POST'])
def create_ad():
    public_key = session.get('public_key')
    if not public_key:
        return redirect(url_for('index'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'back':
            return redirect(url_for('main', public_key=public_key))
        if action == 'create_ad':
            price = int(request.form.get('price'))
            estate_id = int(request.form.get('estate_id'))
            result = create_ad_main(public_key, price, estate_id)
            return render_template("create_ad.html", message=result)
    return render_template("create_ad.html")

@app.route('/edit_ad', methods=['GET', 'POST'])
def edit_ad():
    public_key = session.get('public_key')
    if not public_key:
        return redirect(url_for('index'))
    
    ID_AD = request.args.get('ID_AD')

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'back':
            return redirect(url_for('main', public_key=public_key))
        if action == 'edit_ad':
            id_ad = int(request.form.get('id_ad'))
            type = request.form.get('property_type')
            if type == "Opened":
                status = 0
            elif type == "Closed":
                status = 1

            result = update_ad_status(public_key, id_ad, status)
            return render_template("edit_ad.html", message=result)
    return render_template("edit_ad.html", ID_AD=ID_AD)

@app.route('/edit_estate', methods=['GET', 'POST'])
def edit_estate():
    public_key = session.get('public_key')
    if not public_key:
        return redirect(url_for('index'))
    
    ID_ESTATE = request.args.get('ID_ESTATE')

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'back':
            return redirect(url_for('main', public_key=public_key))
        if action == 'edit_estate':
            id_estate = int(request.form.get('id_estate'))
            type = request.form.get('property_type')
            if type == "Opened":
                status = True
            elif type == "Closed":
                status = False

            result = update_estate_status(public_key, id_estate, status)
            return render_template("edit_estate.html", message=result)
    return render_template("edit_estate.html", ID_ESTATE=ID_ESTATE)

@app.route('/my_ads', methods=['GET', 'POST'])
def my_ads():
    public_key = session.get('public_key')
    if not public_key:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'back':
            return redirect(url_for('main', public_key=public_key))
        
    myads = get_my_ads(public_key)

    return render_template("my_ads.html", myads=myads)

@app.route('/my_estates', methods=['GET', 'POST'])
def my_estates():
    public_key = session.get('public_key')
    if not public_key:
        return redirect(url_for('index'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'back':
            return redirect(url_for('main', public_key=public_key))

    my_estates = get_my_estates(public_key)

    return render_template("my_estates.html", myestates=my_estates)



if __name__ == '__main__':
    app.run(debug=True)