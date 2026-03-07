# ⚙️ Variáveis de Ambiente para Coolify

## 📋 COPIE E COLE ESTAS VARIÁVEIS NO COOLIFY

### ✅ CONFIGURAÇÃO MÍNIMA RECOMENDADA

```env
APP_ENV=production
APP_NAME=ScraperFC API
PORT=8000
LOG_LEVEL=INFO

# Database - OPÇÃO 1 (Mais simples - RECOMENDADO)
DATABASE_URL=postgresql://postgres:1zqGQjBi6rCNi06zw2Gl5aLG90qrQep8@db.safet1ps.supabase.co:5432/postgres

# Sync
SYNC_INTERVAL_MINUTES=5
HISTORY_DAYS_PAST=30
HISTORY_DAYS_FUTURE=30

# Providers
ENABLE_SOFASCORE=true
ENABLE_FBREF=false

# CORS (ajuste conforme necessário)
CORS_ORIGINS=*
```

---

## 📋 CONFIGURAÇÃO COMPLETA (Todas as variáveis)

Caso a opção acima não funcione ou você queira mais controle, use esta configuração completa:

```env
# Application
APP_NAME=ScraperFC API
APP_ENV=production
APP_VERSION=1.0.0
PORT=8000
LOG_LEVEL=INFO

# Database - OPÇÃO 1: URL Completa (RECOMENDADO)
DATABASE_URL=postgresql://postgres:1zqGQjBi6rCNi06zw2Gl5aLG90qrQep8@db.safet1ps.supabase.co:5432/postgres

# Database - OPÇÃO 2: Componentes Separados (fallback automático se DATABASE_URL falhar)
SUPABASE_URL=https://supabase.safet1ps.com.br
SUPABASE_DB_HOST=db.safet1ps.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=1zqGQjBi6rCNi06zw2Gl5aLG90qrQep8

# Database Pool
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# CORS
CORS_ORIGINS=*

# Sync Configuration
SYNC_INTERVAL_MINUTES=5
HISTORY_DAYS_PAST=30
HISTORY_DAYS_FUTURE=30
DEFAULT_TIMEZONE=UTC

# Provider Settings
ENABLE_SOFASCORE=true
ENABLE_FBREF=false
FBREF_WAIT_TIME=6

# Retry Settings
MAX_RETRIES=3
RETRY_BACKOFF_SECONDS=2
```

---

## 🚀 INSTRUÇÕES DE CONFIGURAÇÃO NO COOLIFY

### 1. Acesse seu serviço no Coolify

### 2. Vá em "Environment Variables" ou "Configuration"

### 3. Cole as variáveis usando um dos formatos:

#### OPÇÃO A: Formato Key-Value (Recomendado)
Adicione cada variável separadamente:

| Chave | Valor |
|-------|-------|
| `APP_ENV` | `production` |
| `PORT` | `8000` |
| `DATABASE_URL` | `postgresql://postgres:1zqGQjBi6rCNi06zw2Gl5aLG90qrQep8@db.safet1ps.supabase.co:5432/postgres` |
| `SYNC_INTERVAL_MINUTES` | `5` |
| `ENABLE_SOFASCORE` | `true` |
| `CORS_ORIGINS` | `*` |
| `LOG_LEVEL` | `INFO` |

#### OPÇÃO B: Formato Bulk (se Coolify permitir)
Cole todo o bloco de uma vez no editor de texto:

```
APP_ENV=production
PORT=8000
LOG_LEVEL=INFO
DATABASE_URL=postgresql://postgres:1zqGQjBi6rCNi06zw2Gl5aLG90qrQep8@db.safet1ps.supabase.co:5432/postgres
SYNC_INTERVAL_MINUTES=5
ENABLE_SOFASCORE=true
CORS_ORIGINS=*
```

---

## ⚠️ ATENÇÃO - IMPORTANTE!

### DATABASE_URL
A variável **DATABASE_URL** é a MAIS IMPORTANTE. Certifique-se de que está correta.

**Formato**: `postgresql://USUARIO:SENHA@HOST:PORTA/DATABASE`

**Sua configuração**:
```
postgresql://postgres:1zqGQjBi6rCNi06zw2Gl5aLG90qrQep8@db.safet1ps.supabase.co:5432/postgres
```

### Se o host do banco for diferente
Caso `db.safet1ps.supabase.co` não funcione, tente:
- `db.supabase.safet1ps.com.br`
- Verifique no painel do Supabase qual é o host correto do PostgreSQL
- Normalmente está em: **Settings > Database > Connection String**

---

## 🔍 COMO VERIFICAR NO SUPABASE

1. Acesse seu projeto Supabase
2. Vá em **Settings** → **Database**
3. Procure por **Connection String** ou **Direct Connection**
4. Copie o host correto e substitua se necessário

O formato típico do Supabase é:
```
db.{PROJETO}.supabase.co
```

---

## 🎯 ORDEM DE CONFIGURAÇÃO NO COOLIFY

1. **Configure as variáveis de ambiente** (acima)
2. **Configure o repositório Git**
3. **Configure o Branch** (main)
4. **Configure o Build**:
   - Build Type: Dockerfile
   - Dockerfile: `Dockerfile` (na raiz)
5. **Configure o Port**: 8000
6. **Configure o Health Check**: `/health`
7. **Deploy!**

---

## ✅ CHECKLIST PÓS-DEPLOY

Após o deploy, verifique:

```bash
# 1. Health check (substitua pela URL do seu deploy)
curl https://seu-dominio.com/health

# Resposta esperada:
# {"status":"healthy","timestamp":"...","database":"healthy","version":"1.0.0"}

# 2. Documentação da API
https://seu-dominio.com/docs

# 3. Status da sync
curl https://seu-dominio.com/sync/status

# 4. Disparar primeira sync
curl -X POST https://seu-dominio.com/sync/run -H "Content-Type: application/json" -d '{"force":true}'
```

---

## 🔧 TROUBLESHOOTING

### Problema: Erro de conexão com banco
**Solução**: Verifique se o host está correto. Teste diferentes formatos:
- `db.safet1ps.supabase.co`
- `db.supabase.safet1ps.com.br`

### Problema: Port binding error
**Solução**: Certifique-se que a variável `PORT=8000` está configurada

### Problema: Health check falha
**Solução**: 
1. Verifique os logs do container
2. Confirme que DATABASE_URL está correto
3. Teste a conexão com o banco localmente

---

## 📞 VARIÁVEIS POR CATEGORIA

### ESSENCIAIS (Obrigatórias)
```env
APP_ENV=production
PORT=8000
DATABASE_URL=postgresql://postgres:1zqGQjBi6rCNi06zw2Gl5aLG90qrQep8@db.safet1ps.supabase.co:5432/postgres
```

### SYNC (Recomendadas)
```env
SYNC_INTERVAL_MINUTES=5
HISTORY_DAYS_PAST=30
HISTORY_DAYS_FUTURE=30
ENABLE_SOFASCORE=true
```

### OPCIONAIS (Defaults funcionam)
```env
LOG_LEVEL=INFO
CORS_ORIGINS=*
ENABLE_FBREF=false
DB_POOL_SIZE=10
MAX_RETRIES=3
```

---

## 🎉 RESUMO RÁPIDO

**Mínimo para funcionar:**
1. `DATABASE_URL` (com suas credenciais)
2. `PORT=8000`
3. `APP_ENV=production`

**Recomendado adicionar:**
4. `SYNC_INTERVAL_MINUTES=5`
5. `ENABLE_SOFASCORE=true`
6. `LOG_LEVEL=INFO`

---

**Suas credenciais já estão configuradas no arquivo .env local!**
**No Coolify, use as variáveis acima. ✅**
