# Deploy no PythonAnywhere — App Financeiro

## 1. Preparar os arquivos

No seu computador, abra o terminal no diretório do app:

```bash
cd C:\Users\User\Documents\app-financeiro
```

Crie um arquivo `.gitignore`:

```bash
venv/
__pycache__/
*.pyc
instance/
.env
```

(Opcional) Suba para o GitHub:

```bash
git init
git add .
git commit -m "App Financeiro completo"
# cria um repositório no GitHub e depois:
git remote add origin https://github.com/SEU_USUARIO/app-financeiro.git
git push -u origin main
```

---

## 2. Criar conta no PythonAnywhere

Acesse [pythonanywhere.com](https://www.pythonanywhere.com) e crie uma conta **Free** (ou paga, se quiser domínio personalizado).

---

## 3. Upload dos arquivos

### Opção A — Via GitHub (recomendado)

No console Bash do PythonAnywhere:

```bash
git clone https://github.com/SEU_USUARIO/app-financeiro.git
```

### Opção B — Upload direto

1. Clique em **Files** > **Upload a file**
2. Faça upload de cada arquivo da pasta `app-financeiro/` mantendo a estrutura:

```
/home/SEU_USUARIO/app-financeiro/
├── run.py
├── config.py
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── transacoes.py
│   │   ├── categorias.py
│   │   ├── contas_fixas.py
│   │   ├── orcamentos.py
│   │   ├── relatorios.py
│   │   ├── cartoes.py
│   │   └── parcelamentos.py
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── transacoes.html
│       ├── categorias.html
│       ├── contas_fixas.html
│       ├── orcamentos.html
│       ├── relatorios.html
│       ├── cartoes.html
│       └── parcelamentos.html
```

> **Importante:** Crie a pasta `instance/` vazia dentro de `app-financeiro/`.

---

## 4. Criar virtualenv e instalar dependências

No console Bash do PythonAnywhere:

```bash
cd ~/app-financeiro
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 5. Configurar variável de ambiente SECRET_KEY

No mesmo console:

```bash
echo "export SECRET_KEY='$(python3 -c 'import secrets; print(secrets.token_hex(32))')'" >> ~/.bashrc
source ~/.bashrc
```

Ou defina no arquivo de ativação da venv:

```bash
echo "export SECRET_KEY='$(python3 -c 'import secrets; print(secrets.token_hex(32))')'" >> ~/app-financeiro/venv/bin/activate
```

---

## 6. Configurar o Web App no PythonAnywhere

### 6.1. Criar o Web App

1. Vá em **Web** > **Add a new web app**
2. Clique em **Next** > **Manual configuration** > **Python 3.12** > **Next**

### 6.2. Configurar o arquivo WSGI

Em **Web**, clique no link do arquivo WSGI (algo como `/var/www/SEU_USUARIO_pythonanywhere_com_wsgi.py`).

Substitua TODO o conteúdo por:

```python
import sys
import os

# Caminho do projeto
path = '/home/SEU_USUARIO/app-financeiro'
if path not in sys.path:
    sys.path.insert(0, path)

# Ativar virtualenv
activate_this = os.path.join(path, 'venv', 'bin', 'activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})

# Forçar ambiente de produção
os.environ['FLASK_ENV'] = 'production'

# Importar o app
from app import create_app
application = create_app('production')
```

> ⚠️ Substitua `SEU_USUARIO` pelo seu nome de usuário no PythonAnywhere.

### 6.3. Configurar arquivos estáticos

Em **Web** > **Static files**, adicione:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/SEU_USUARIO/app-financeiro/app/static/` |

### 6.4. Configurar o banco de dados

O SQLite será criado automaticamente em `app-financeiro/instance/financas.db`.

**Importante:** No PythonAnywhere Free, o SQLite é reiniciado periodicamente. Para não perder dados:
- Faça backup manual pelo console: `cp ~/app-financeiro/instance/financas.db ~/backup-financas.db`
- Melhor ainda: use **MySQL** do PythonAnywhere (veja seção extra abaixo)

---

## 7. Reload e testar

1. Em **Web**, clique no botão **Reload**
2. Acesse `https://SEU_USUARIO.pythonanywhere.com`
3. Pronto! 🎉

---

## 8. Troubleshooting

### Erro 500 — Internal Server Error

Veja os logs:

- **Web** > **Error log** — mostra erros do Python
- **Web** > **Server log** — mostra erros do servidor

### Erro "No module named 'app'"

- Verifique se o `sys.path` no WSGI está apontando para o diretório correto

### Erro de permissão no SQLite

O PythonAnywhere pode reclamar se o diretório `instance/` não existir:

```bash
mkdir -p ~/app-financeiro/instance
```

### Banco corrompido ou resetado

No Free tier, o SQLite não é persistente. Veja abaixo como migrar para MySQL.

---

## 9. (Opcional) Migrar para MySQL do PythonAnywhere

A conta Free vem com MySQL incluso. Para usar:

### 9.1. Criar banco MySQL

1. Vá em **Databases** > **MySQL**
2. Defina a senha do MySQL
3. Anote o nome do banco: `SEU_USUARIO$financas`

### 9.2. Instalar conector

```bash
cd ~/app-financeiro
source venv/bin/activate
pip install pymysql
```

### 9.3. Atualizar variável de ambiente

```bash
echo "export DATABASE_URL='mysql+pymysql://SEU_USUARIO:SENHA@SEU_USUARIO.mysql.pythonanywhere-services.com/SEU_USUARIO\$financas'" >> ~/app-financeiro/venv/bin/activate
```

### 9.4. Atualizar o WSGI

No arquivo WSGI, adicione antes de criar o app:

```python
os.environ['DATABASE_URL'] = 'mysql+pymysql://SEU_USUARIO:SENHA@SEU_USUARIO.mysql.pythonanywhere-services.com/SEU_USUARIO$financas'
```

---

## 10. Comandos úteis (console Bash)

```bash
# Ver logs em tempo real
tail -f /var/log/SEU_USUARIO.error.log

# Reiniciar o app pelo terminal
touch /var/www/SEU_USUARIO_pythonanywhere_com_wsgi.py

# Backup do banco
cp ~/app-financeiro/instance/financas.db ~/backups/$(date +%Y%m%d_%H%M)_financas.db

# Acessar banco SQLite
cd ~/app-financeiro
source venv/bin/activate
python -c "from app import create_app; app = create_app(); from app import db; print('OK')"
```
