# Sistema de Estacionamento

API REST desenvolvida com Django e Django REST Framework para cadastrar clientes
e veículos, registrar entradas e saídas e acompanhar vagas e cobranças.

## Requisitos

- Python 3.10 ou superior
- Pip

## Como executar

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

O servidor fica disponível em `http://127.0.0.1:8000/`. A documentação
interativa da API está em `/swagger/`.

Crie vagas pelo endpoint de vagas ou pelo Django Admin (`/admin/`). Para criar
um administrador, execute `python manage.py createsuperuser`.

## Endpoints

| Método | Endpoint | Ação |
| --- | --- | --- |
| `GET`, `POST` | `/api/customers/` | Listar e cadastrar clientes |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/customers/{id}/` | Consultar e editar cliente |
| `GET`, `POST` | `/api/vehicles/` | Listar e cadastrar veículos |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/vehicles/{id}/` | Consultar e editar veículo |
| `GET`, `POST` | `/api/spots/` | Listar e cadastrar vagas |
| `GET`, `POST` | `/api/parking-sessions/` | Consultar sessões e registrar entrada |
| `POST` | `/api/parking-sessions/{id}/checkout/` | Registrar saída e calcular cobrança |
| `GET` | `/api/summary/` | Consultar totais, ocupação e receita |

Para registrar uma entrada, envie o ID do veículo. O sistema seleciona
automaticamente a primeira vaga disponível e não permite uma segunda entrada
para o mesmo veículo enquanto ele ainda estiver estacionado.

```json
{
  "vehicle": 1
}
```

Na saída, o valor é calculado individualmente usando a tarifa horária definida
em `PARKING_HOURLY_RATE` no `config/settings.py`. Cada hora iniciada é cobrada
por inteiro, com cobrança mínima de uma hora. A sessão guarda a tarifa usada,
o horário de entrada e saída, a duração e o valor cobrado.

Os campos abaixo são exemplos de cadastro:

```json
{
  "name": "Maria Silva",
  "phone_number": "11999999999",
  "email": "maria@example.com"
}
```

```json
{
  "customer": 1,
  "plate": "ABC1D23",
  "make": "Fiat",
  "model": "Argo",
  "color": "Prata"
}
```

Cadastre cada vaga enviando seu número:

```json
{
  "number": 1
}
```

Execute os testes com:

```bash
python manage.py test
```

Configure o pre-commit localmente para rodar os checks antes de cada commit:

```bash
python -m pip install -r requirements.txt
pre-commit install
pre-commit run --all-files
```
