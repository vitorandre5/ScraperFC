# ⚡ Quick Start - ScraperFC API

## 1️⃣ Configuração Inicial (5 minutos)

### Opção A: Docker Compose (Recomendado)

```bash
# Clone e configure
git clone <seu-repo>
cd ScraperFC
cp .env.example .env

# Edite o .env com suas credenciais Supabase:
# SUPABASE_DB_HOST=db.xxxxx.supabase.co
# SUPABASE_DB_USER=postgres.xxxxx
# SUPABASE_DB_PASSWORD=sua_senha

# Inicie os serviços
docker-compose up -d

# Verifique
curl http://localhost:8000/health
```

### Opção B: Python Local

```bash
# Clone e configure
git clone <seu-repo>
cd ScraperFC

# Crie virtualenv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale dependências
pip install -e .

# Configure ambiente
cp .env.example .env
# Edite .env com suas credenciais

# Inicie
python -m uvicorn app.main:app --reload --port 8000
```

## 2️⃣ Primeira Sincronização

```bash
# Dispare a primeira sync manualmente
curl -X POST http://localhost:8000/sync/run \
  -H "Content-Type: application/json" \
  -d '{"force": true}'

# Acompanhe o status (aguarde 2-5 minutos)
curl http://localhost:8000/sync/status

# Quando completed, você terá dados!
```

## 3️⃣ Primeiras Consultas

```bash
# Esportes disponíveis
curl http://localhost:8000/sports

# Ligas disponíveis
curl http://localhost:8000/leagues

# Jogos de hoje
curl http://localhost:8000/matches/today

# Documentação interativa
open http://localhost:8000/docs
```

## 4️⃣ Deploy no Coolify

### No Coolify:

1. **Novo Serviço > Dockerfile**
   - Repository: seu Git repo
   - Branch: main
   - Build Pack: Dockerfile

2. **Environment Variables**
   ```
   APP_ENV=production
   PORT=8000
   DATABASE_URL=postgresql://user:pass@host:5432/db
   SYNC_INTERVAL_MINUTES=5
   ENABLE_SOFASCORE=true
   ```

3. **Deploy**
   - Coolify vai detectar o Dockerfile
   - Build automático
   - Deploy com health check

4. **Verificar**
   ```bash
   curl https://seu-dominio.com/health
   ```

## 5️⃣ Integração Frontend (Exemplo React)

```jsx
import { useEffect, useState } from 'react';

function TodayMatches() {
  const [matches, setMatches] = useState([]);
  
  useEffect(() => {
    fetch('http://localhost:8000/matches/today?sport=football')
      .then(res => res.json())
      .then(data => setMatches(data));
  }, []);
  
  return (
    <div>
      <h1>Jogos de Hoje</h1>
      {matches.map(match => (
        <div key={match.id}>
          {match.home_team.name} vs {match.away_team.name}
          <br />
          {new Date(match.match_datetime_utc).toLocaleString()}
          <br />
          Status: {match.status}
        </div>
      ))}
    </div>
  );
}
```

## 6️⃣ Principais Endpoints

```bash
# Status do sistema
GET /health

# Listar esportes
GET /sports

# Ligar ligas
GET /leagues?sport=football

# Buscar times
GET /teams/search?q=barcelona

# Jogos de hoje
GET /matches/today

# Jogos de uma data
GET /matches/date/2026-03-10

# Intervalo de datas
GET /matches/range?start=2026-03-01&end=2026-03-15

# Buscar por time
GET /matches/search?team=flamengo

# Status da sync
GET /sync/status

# Disparar sync manual
POST /sync/run
```

## 7️⃣ Monitoramento

```bash
# Health check
curl http://localhost:8000/health

# Status da sincronização
curl http://localhost:8000/sync/status

# Histórico de syncs
curl http://localhost:8000/sync/history

# Logs (Docker)
docker logs scraperfc_api -f

# Logs (sem Docker)
# Veja no terminal onde rodou uvicorn
```

## 8️⃣ Troubleshooting Rápido

### Problema: API não inicia
```bash
# Verificar .env
cat .env

# Testar conexão com banco
psql $DATABASE_URL
```

### Problema: Sem jogos retornados
```bash
# Verificar última sync
curl http://localhost:8000/sync/status

# Forçar nova sync
curl -X POST http://localhost:8000/sync/run -H "Content-Type: application/json" -d '{"force": true}'

# Aguardar alguns minutos e verificar
curl http://localhost:8000/matches/today
```

### Problema: Erro 500
```bash
# Ver logs
docker logs scraperfc_api --tail 100

# Verificar banco
curl http://localhost:8000/health
```

## 9️⃣ Customizações Comuns

### Mudar intervalo de sync
```env
# .env
SYNC_INTERVAL_MINUTES=10  # Padrão é 5
```

### Desabilitar Sofascore
```env
# .env
ENABLE_SOFASCORE=false
```

### Aumentar janela de histórico
```env
# .env
HISTORY_DAYS_PAST=60
HISTORY_DAYS_FUTURE=60
```

### Logs mais detalhados
```env
# .env
LOG_LEVEL=DEBUG
```

## 🔟 Arquivos Importantes

```
.env              # Suas configurações
README_API.md     # Documentação completa
API_EXAMPLES.md   # Exemplos de uso
docker-compose.yml # Dev local
Dockerfile        # Produção
/docs             # Swagger UI em /docs
```

## ✅ Checklist de Deploy

- [ ] .env configurado com credenciais reais
- [ ] DATABASE_URL válido
- [ ] Banco de dados Supabase criado
- [ ] Docker rodando (se usar compose)
- [ ] Porta 8000 disponível
- [ ] Primeira sync executada
- [ ] /health retornando "healthy"
- [ ] /docs acessível
- [ ] CORS configurado (se necessário)

## 📞 Ajuda

- **Documentação API**: http://localhost:8000/docs
- **README Completo**: README_API.md
- **Exemplos**: API_EXAMPLES.md
- **Resumo Técnico**: IMPLEMENTATION_SUMMARY.md

## 🎯 Casos de Uso Rápidos

### Widget de Jogos
```bash
curl "http://localhost:8000/matches/today?sport=football&status=scheduled" | jq
```

### Jogos Ao Vivo
```bash
curl "http://localhost:8000/matches/today?status=live" | jq
```

### Próximos Jogos do Time
```bash
curl "http://localhost:8000/matches/search?team=barcelona&status=scheduled" | jq
```

### Resultados Recentes
```bash
curl "http://localhost:8000/matches/search?team=real madrid&status=finished&limit=5" | jq
```

---

**Tudo pronto!** 🚀

A API está sincronizando automaticamente a cada 5 minutos e pronta para ser consumida por qualquer frontend ou sistema.
