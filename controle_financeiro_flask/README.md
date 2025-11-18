# Controle Financeiro Pessoal

Um aplicativo web simples e funcional para gerenciar suas finanças pessoais, desenvolvido com **Python**, **Flask** e **SQLite**.

## 📋 Características

- ✅ **Autenticação de Usuário**: Login e registro simplificados
- ✅ **Gestão de Categorias**: Criar, editar e deletar categorias de transações
- ✅ **Registro de Receitas**: Adicionar receitas com descrição, valor e categoria
- ✅ **Registro de Despesas**: Adicionar despesas com descrição, valor e categoria
- ✅ **Dashboard com Resumo Mensal**: Visualizar totais de receitas, despesas e saldo
- ✅ **Análise por Categoria**: Ver despesas agrupadas por categoria
- ✅ **Interface Responsiva**: Design clean e intuitivo com Bootstrap 5

## 🏗️ Arquitetura

### Tecnologias Utilizadas

- **Backend**: Python 3.x + Flask (micro framework)
- **Banco de Dados**: SQLite
- **Frontend**: HTML5 + CSS3 + JavaScript + Bootstrap 5 CDN
- **ORM**: Flask-SQLAlchemy

### Modelo de Dados

```
Usuario
├── id (PK)
├── nome
├── email (UNIQUE)
├── senha_hash
└── data_criacao

Categoria
├── id (PK)
├── nome
├── usuario_id (FK)
└── data_criacao

Transacao (Base)
├── id (PK)
├── descricao
├── valor
├── data
├── tipo (receita/despesa)
├── usuario_id (FK)
├── categoria_id (FK)
└── Receita (herda de Transacao)
└── Despesa (herda de Transacao)
```

### Estrutura de Pastas

```
controle_financeiro_flask/
├── app/
│   ├── __init__.py          # Inicialização da aplicação Flask
│   ├── models.py            # Modelos do banco de dados
│   └── routes.py            # Rotas e lógica da aplicação
├── templates/
│   ├── base.html            # Template base com navbar e footer
│   ├── login.html           # Página de login
│   ├── registro.html        # Página de registro
│   ├── dashboard.html       # Dashboard com resumo mensal
│   ├── nova_receita.html    # Formulário para nova receita
│   ├── nova_despesa.html    # Formulário para nova despesa
│   ├── categorias.html      # Página de gerenciamento de categorias
│   └── editar_categoria.html # Formulário para editar categoria
├── static/
│   ├── css/
│   │   └── style.css        # Estilos customizados
│   └── js/
│       └── script.js        # Scripts JavaScript
├── app.py                   # Arquivo principal da aplicação
├── requirements.txt         # Dependências do projeto
└── README.md               # Este arquivo
```

## 🚀 Guia de Instalação e Execução

### Pré-requisitos

- **Python 3.7+** instalado
- **pip** (gerenciador de pacotes do Python)
- **Git** (opcional, para clonar o repositório)

### Passo 1: Preparar o Ambiente

#### 1.1 Clonar ou extrair o projeto

Se você tiver o arquivo ZIP, extraia-o em uma pasta de sua escolha:

```bash
unzip controle_financeiro_flask.zip
cd controle_financeiro_flask
```

#### 1.2 Criar um ambiente virtual

Um ambiente virtual isola as dependências do projeto do seu sistema Python global.

**No Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**No macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Você saberá que o ambiente virtual está ativado quando ver `(venv)` no início da linha do terminal.

### Passo 2: Instalar Dependências

Com o ambiente virtual ativado, instale as dependências do projeto:

```bash
pip install -r requirements.txt
```

Este comando instalará:
- **Flask**: Micro framework web
- **Flask-SQLAlchemy**: ORM para gerenciar o banco de dados
- **Werkzeug**: Utilitários de segurança (hash de senhas)

### Passo 3: Executar a Aplicação

Com as dependências instaladas, inicie o servidor Flask:

```bash
python app.py
```

Você deverá ver uma mensagem similar a:

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

### Passo 4: Acessar a Aplicação

Abra seu navegador e acesse:

```
http://localhost:5000
```

Você será redirecionado para a página de login.

## 📖 Como Usar

### 1. Registrar uma Conta

1. Clique em **"Registrar"** na página inicial
2. Preencha os campos:
   - **Nome Completo**: Seu nome
   - **Email**: Um email válido e único
   - **Senha**: Mínimo 6 caracteres
   - **Confirmar Senha**: Repita a senha
3. Clique em **"Registrar"**

### 2. Fazer Login

1. Clique em **"Login"**
2. Preencha:
   - **Email**: O email da sua conta
   - **Senha**: A senha da sua conta
3. Clique em **"Entrar"**

### 3. Criar Categorias

1. Clique em **"Categorias"** na barra de navegação
2. Clique em **"Nova Categoria"**
3. Digite o nome da categoria (ex: Alimentação, Transporte, Salário)
4. Clique em **"Criar Categoria"**

**Nota**: Você precisa criar pelo menos uma categoria antes de registrar transações.

### 4. Registrar Receitas

1. Clique em **"Nova Receita"** na barra de navegação
2. Preencha os campos:
   - **Descrição**: O que é a receita (ex: Salário, Freelance)
   - **Valor**: O valor em reais
   - **Categoria**: Selecione uma categoria
   - **Data**: (Opcional) A data da receita
3. Clique em **"Registrar Receita"**

### 5. Registrar Despesas

1. Clique em **"Nova Despesa"** na barra de navegação
2. Preencha os campos:
   - **Descrição**: O que é a despesa (ex: Supermercado, Gasolina)
   - **Valor**: O valor em reais
   - **Categoria**: Selecione uma categoria
   - **Data**: (Opcional) A data da despesa
3. Clique em **"Registrar Despesa"**

### 6. Visualizar Dashboard

1. Clique em **"Dashboard"** na barra de navegação
2. Você verá:
   - **Total de Receitas do Mês**: Soma de todas as receitas
   - **Total de Despesas do Mês**: Soma de todas as despesas
   - **Saldo Final**: Receitas - Despesas
   - **Despesas por Categoria**: Gráfico de gastos por categoria
   - **Transações do Mês**: Lista de todas as transações

### 7. Gerenciar Transações

- **Deletar Transação**: Clique no botão de lixeira ao lado da transação
- **Editar Categoria**: Clique em "Editar" na página de categorias
- **Deletar Categoria**: Clique em "Deletar" na página de categorias (só é possível se não houver transações)

### 8. Fazer Logout

Clique em **"Sair"** na barra de navegação para desconectar.

## 🔒 Segurança

- **Senhas**: Armazenadas com hash usando `werkzeug.security` (nunca em texto plano)
- **Sessões**: Gerenciadas pelo Flask com chave secreta
- **Autenticação**: Decorador `@login_required` protege rotas
- **Validação**: Todos os formulários são validados no servidor

**⚠️ Importante para Produção**: 
- Altere a `SECRET_KEY` em `app/__init__.py` para uma chave segura e aleatória
- Desative o modo debug (`debug=False`)
- Use um servidor de produção como Gunicorn

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'flask'"

**Solução**: Certifique-se de que o ambiente virtual está ativado e instale as dependências:
```bash
pip install -r requirements.txt
```

### Erro: "Address already in use"

**Solução**: A porta 5000 já está em uso. Você pode:
1. Encerrar a aplicação que está usando a porta
2. Ou modificar a porta em `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use 5001 ou outra porta
```

### Banco de dados não está sendo criado

**Solução**: Certifique-se de que a pasta do projeto tem permissões de escrita. O banco de dados será criado automaticamente na primeira execução.

### Esqueci minha senha

**Solução**: Atualmente, não há função de "Recuperar Senha". Você pode:
1. Criar uma nova conta com outro email
2. Ou deletar manualmente o arquivo `controle_financeiro.db` e criar uma nova conta

## 📝 Funcionalidades Futuras

- [ ] Recuperação de senha por email
- [ ] Exportar dados em CSV/PDF
- [ ] Gráficos mais avançados
- [ ] Orçamentos mensais
- [ ] Metas de poupança
- [ ] Autenticação com OAuth (Google, GitHub)
- [ ] Aplicativo mobile

## 📄 Licença

Este projeto é fornecido como está, sem garantias. Sinta-se livre para usar, modificar e distribuir.

## 👨‍💻 Desenvolvido por

**Seu Nome** - 2024

---

## 📞 Suporte

Se encontrar algum problema ou tiver dúvidas, verifique:

1. Se o Python está instalado: `python --version`
2. Se o ambiente virtual está ativado
3. Se as dependências estão instaladas: `pip list`
4. Se o servidor está rodando corretamente

## 🎓 Aprendizados

Este projeto é excelente para aprender:

- ✅ Estrutura de aplicações Flask
- ✅ Relacionamentos em bancos de dados com SQLAlchemy
- ✅ Autenticação e gerenciamento de sessões
- ✅ Herança de classes em Python (Transacao → Receita/Despesa)
- ✅ Templates Jinja2
- ✅ Validação de formulários
- ✅ Design responsivo com Bootstrap

---

**Divirta-se controlando suas finanças! 💰**
