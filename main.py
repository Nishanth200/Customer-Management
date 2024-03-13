import requests
from flask import Flask, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customer.db'
db = SQLAlchemy(app)
#URL = 'http://127.0.0.1:5000/'


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/', methods=['POST', 'GET'])
def put_data():
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            if not name or not email:
                raise ValueError("Name and email are required fields.")

            myobj = {'name': name, 'email': email}
            x = requests.post(url=request.url_root + 'customers', json=myobj)
            x.raise_for_status()  # Check for HTTP errors in the response
            m = x.json()['message']
            return render_template('index.html', message=m)
        else:
            return render_template('index.html')
    except requests.RequestException as e:
        return render_template('error.html', error=str(e))


@app.route('/printcus', methods=['POST', 'GET'])
def print_customers():
    try:
        if request.method == 'GET':
            x = requests.get(request.url_root + 'customers')
            x.raise_for_status()

            customers = x.json().get('users', [])
            return render_template('customer.html', customers=customers)
        else:
            return render_template('customer.html', customers=[])
    except requests.RequestException as e:
        return render_template('error.html', error=str(e))


@app.route('/delete_customer', methods=['POST'])
def delete_c():
    try:
        data = request.form
        customer_id = data.get('id')
        if not customer_id:
            raise ValueError("Failed to delete customer: No customer ID provided.")

        response = requests.delete(url=request.url_root + f'customers/{customer_id}')
        response.raise_for_status()
        return redirect('/')
    except requests.RequestException as e:
        return render_template('error.html', error=f"Failed to delete customer")
    except Exception as e:
        return render_template('error.html', error=f"Failed to delete customer")


@app.route('/update_data', methods=['GET', 'POST'])
def update_data():
    try:
        data = request.form
        id = data.get('id')
        name = data.get('name')
        email = data.get('email')

        response = requests.put(url=request.url_root + f'customers/{id}', json={'name': name, 'email': email})
        response.raise_for_status()
        return redirect('/')
    except requests.RequestException as e:
        return render_template('error.html', error=f"Failed to Update customer")


@app.route('/get_customer', methods=['GET', 'POST'])
def get_c():
    try:
        customer_id = request.form.get('id')
        if request.method == 'POST' and customer_id:
            response = requests.get(request.url_root + f'customers/{customer_id}')
            response.raise_for_status()

            customer_data = {
                'id': response.json().get('customer', {}).get('id', ''),
                'email': response.json().get('customer', {}).get('email', ''),
                'name': response.json().get('customer', {}).get('name', '')
            }
            return render_template('index.html', customer=customer_data)
        else:
            return render_template('index.html', customer={'id': '', 'email': '', 'name': ''})
    except requests.RequestException as e:
        return render_template('error.html', error=str(e))


@app.route('/customers', methods=['POST'])
def create_customers():
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'email' not in data:
            raise ValueError("Invalid data. Name and email are required fields.")

        new_customer = Customer(name=data['name'], email=data['email'])
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({'message': 'Customer created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/customers', methods=['GET'])
def get_all_customers():
    try:
        customers = Customer.query.all()
        customers_list = [{'id': customer.id, 'name': customer.name, 'email': customer.email} for customer in customers]
        return jsonify({'users': customers_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        customer_data = {'id': customer.id, 'name': customer.name, 'email': customer.email}
        return jsonify({'customer': customer_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()

        if not data or 'name' not in data or 'email' not in data:
            raise ValueError("Invalid data. Name and email are required fields.")

        customer.name = data['name']
        customer.email = data['email']

        db.session.commit()
        return jsonify({'message': 'Customer data Updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': "Customer deleted successfully"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
