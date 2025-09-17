from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Inicializar a aplicação

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Utilizador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Utilizador {self.nome}>'


# Modelo Cliente
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nif = db.Column(db.String(20), unique=True, nullable=False)
    morada = db.Column(db.String(200), nullable=False)
    aniversario = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<Cliente {self.nome}>'


# Modelo Produto
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    preco = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Produto {self.nome} - €{self.preco}>'


# Criar base de dados
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return redirect(url_for('login'))


# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    nome = request.form.get('utilizador')
    senha = request.form.get('password')

    utilizador = Utilizador.query.filter_by(nome=nome).first()

    if utilizador and utilizador.verificar_senha(senha):
        return redirect(url_for('dashboard'))
    else:
        erro = "Utilizador ou password incorretos"
        return render_template('index.html', erro=erro)


# Rota do dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dasboard.html')


# Rota para cadastrar cliente
@app.route('/cadastro', methods=['POST'])
def cadastro():
    data = request.get_json()

    try:
        novo_cliente = Cliente(
            nome=data['nome'],
            nif=data['nif'],
            morada=data['morada'],
            aniversario=datetime.strptime(data['aniversario'], '%Y-%m-%d').date()
        )
        db.session.add(novo_cliente)
        db.session.commit()
        return jsonify({'mensagem': 'Cliente cadastrado com sucesso!'}), 201

    except Exception as e:
        return jsonify({'erro': str(e)}), 400


# Rota para listar clientes
@app.route('/clientes', methods=['GET'])
def listar_clientes():
    clientes = Cliente.query.all()
    resultado = [
        {
            'id': c.id,
            'nome': c.nome,
            'nif': c.nif,
            'morada': c.morada,
            'aniversario': c.aniversario.strftime('%Y-%m-%d')
        } for c in clientes
    ]
    return jsonify(resultado)


# Rota para inserir produto
@app.route('/inserir_preco', methods=['POST'])
def inserir_preco():
    data = request.get_json()

    nome = data.get('nome')
    categoria = data.get('categoria')
    preco = data.get('preco')

    if not nome or not categoria or preco is None:
        return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400

    novo_produto = Produto(nome=nome, categoria=categoria, preco=preco)
    db.session.add(novo_produto)
    db.session.commit()

    return jsonify({'mensagem': 'Produto inserido com sucesso!', 'item': {
        'nome': nome,
        'categoria': categoria,
        'preco': preco
    }}), 201


# Rota para listar produtos
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    produtos = Produto.query.all()
    resultado = [
        {
            'id': p.id,
            'nome': p.nome,
            'categoria': p.categoria,
            'preco': p.preco
        } for p in produtos
    ]
    return jsonify(resultado)


@app.route('/produtos_html')
def produtos_html():
    produtos = Produto.query.all()
    return render_template('produtos.html', produtos=produtos)


@app.route('/servicos_html')
def servicos_html():
    # Aqui podes criar uma lista fixa ou usar um modelo de base de dados
    servicos = [
        {'nome': 'Instalação de Climatização', 'descricao': 'Serviço completo com garantia.'},
        {'nome': 'Manutenção Preventiva', 'descricao': 'Evite avarias com inspeções regulares.'}
    ]
    return render_template('servicos.html', servicos=servicos)


# Iniciar servidor
if __name__ == '__main__':
    app.run(debug=True)
