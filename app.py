from pymongo import MongoClient
import os
from flask import Flask, redirect, url_for, request, render_template

app = Flask(__name__)

global ch_listo, mk_listo, ap_listo, cf_listo
ch_listo, mk_listo, ap_listo, cf_listo = [], [], [], []
client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)
db = client.basketdb
product_names = {
    'CH1': 'Chai',
    'AP1': 'Apples',
    'CF1': 'Coffee',
    'MK1': 'Milk',
    'OM1': 'oatmeal'
}
product_prices = {
    'CH1': 3.11,
    'AP1': 6.00,
    'CF1': 11.23,
    'MK1': 4.75,
    'OM1': 3.69
}
discounts = {
    'BOGO': -product_prices['CF1'],
    'APPL': 4.50 - product_prices['AP1'],
    'CHMK': -product_prices['MK1']
}
product_codes = ['CH1', 'AP1', 'CF1', 'MK1', 'OM1']

@app.route('/')
def basket():
    _items = db.basketdb.find()
    items = [item for item in _items]
    total = sum([float(item["price"]) for item in items])
    return render_template('basket.html', items=items, total=total)

@app.route('/retail', methods=['POST'])
def retail():
    flag = False
    cf_total, ap_total, ch_total, mk_total, om_total = 0, 0, 0, 0, 0
    total, ch_count, ap_count, cf_count, mk_count = 0, 0, 0, 0, 0
    product_code, product, price, quantity, discount_code, discount_amount = request.form['product_code'].upper(), '', 0, int(request.form['quantity']), '', 1
    if product_code in product_codes:
        product = product_names[product_code]
        price = product_prices[product_code]
        if product_code == 'CF1':
            cf_count += 1
            cf_listo.append(cf_count)
            if len(cf_listo) == 1:
                cf_total += quantity * price
            else:
                if len(cf_listo) % 2 == 0:
                    discount_code = 'BOGO'
                    discount_amount = discounts[discount_code]
                    cf_total += quantity * price + (len(cf_listo)/2)*discount_amount
                else:
                    discount_code = 'BOGO'
                    discount_amount = discounts[discount_code]
                    cf_total += quantity * price + ((len(cf_listo)-1)/2)*discount_amount + (len(cf_listo)%2)*discount_amount
        elif product_code == 'AP1':
            ap_count += 1
            ap_listo.append(ap_count)
            if len(ap_listo) >= 3:
                discount_code = 'APPL'
                discount_amount = discounts[discount_code]
                ap_total += quantity * price + len(ap_listo) * discount_amount
            else:
                ap_total += quantity * price
        elif product_code == 'CH1':
            ch_count = ch_count + 1
            ch_listo.append(ch_count)
            if len(ch_listo) > 1:
                flag = True
            if len(mk_listo) == 1 and flag == False:
                discount_code = 'CHMK'
                discount_amount = discounts[discount_code]
                ch_total += price + discount_amount
            else:
                ch_total += quantity * price
        elif product_code == 'MK1':
            mk_count += 1
            mk_listo.append(mk_count)
            if len(mk_listo) > 1:
                flag = True
            if len(ch_listo) == 1 and flag == False:
                discount_code = 'CHMK'
                discount_amount = discounts[discount_code]
                mk_total += price + discount_amount
            else:
                mk_total += quantity * price
        elif product_code == 'OM1':
            om_total += quantity * price
        else:
            return
    else:
        return
    item_doc = {
        'product_code': product_code,
        'product': product,
        'price': price,
        'quantity': quantity,
        'discount_code': discount_code,
        'discount_amount': discount_amount,
        'total': ap_total+ch_total+cf_total+mk_total+om_total,
        'ch_count': ch_count,
        'ap_count': ap_count,
        'cf_count': cf_count,
        'mk_count': mk_count,
        'ap_total': ap_total,
        'ch_total': ch_total,
        'cf_total': cf_total,
        'mk_total': mk_total,
        'om_total': om_total
    }
    db.basketdb.insert_one(item_doc)
    return redirect(url_for('basket'))

@app.route('/delete', methods=['POST'])
def delete():
    del ch_listo[:]
    del mk_listo[:]
    del ap_listo[:]
    del cf_listo[:]
    db.basketdb.delete_many({})
    return redirect(url_for('basket'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
