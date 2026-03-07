# Exemplos de Uso da API ScraperFC

Este documento contém exemplos práticos de como consumir a API.

## 🚀 Quick Start

### 1. Verificar Status

```bash
# Health check
curl http://localhost:8000/health

# Resposta esperada:
{
  "status": "healthy",
  "timestamp": "2026-03-06T10:30:00",
  "database": "healthy",
  "version": "1.0.0"
}
```

### 2. Ver Documentação Interativa

Acesse: http://localhost:8000/docs

## 📊 Exemplos de Consultas

### Esportes

```bash
# Listar todos os esportes
curl http://localhost:8000/sports

# Resposta:
[
  {
    "id": 1,
    "key": "football",
    "name": "Football",
    "created_at": "2026-03-06T10:00:00",
    "updated_at": "2026-03-06T10:00:00"
  }
]
```

### Ligas/Campeonatos

```bash
# Todas as ligas
curl http://localhost:8000/leagues

# Ligas de futebol
curl http://localhost:8000/leagues?sport=football

# Ligas da Inglaterra
curl http://localhost:8000/leagues?country=England

# Liga específica
curl http://localhost:8000/leagues/1
```

### Times

```bash
# Buscar Barcelona
curl "http://localhost:8000/teams/search?q=barcelona"

# Buscar times de futebol com "real"
curl "http://localhost:8000/teams/search?q=real&sport=football"

# Limitar resultados
curl "http://localhost:8000/teams/search?q=united&limit=10"

# Time específico
curl http://localhost:8000/teams/123
```

### Partidas - Jogos de Hoje

```bash
# Todos os jogos de hoje
curl http://localhost:8000/matches/today

# Jogos de hoje filtrados por esporte
curl "http://localhost:8000/matches/today?sport=football"

# Jogos de hoje de uma liga específica
curl "http://localhost:8000/matches/today?league=Premier League"

# Apenas jogos ao vivo
curl "http://localhost:8000/matches/today?status=live"

# Apenas jogos finalizados
curl "http://localhost:8000/matches/today?status=finished"
```

### Partidas - Data Específica

```bash
# Jogos de uma data
curl http://localhost:8000/matches/date/2026-03-10

# Com filtros
curl "http://localhost:8000/matches/date/2026-03-10?sport=football&league=La Liga"
```

### Partidas - Intervalo de Datas

```bash
# Jogos entre 01/03 e 15/03
curl "http://localhost:8000/matches/range?start=2026-03-01&end=2026-03-15"

# Com paginação
curl "http://localhost:8000/matches/range?start=2026-03-01&end=2026-03-15&page=2&page_size=20"

# Filtrado por liga
curl "http://localhost:8000/matches/range?start=2026-03-01&end=2026-03-31&league=Champions"
```

### Partidas - Busca

```bash
# Buscar por time
curl "http://localhost:8000/matches/search?team=flamengo"

# Buscar por liga
curl "http://localhost:8000/matches/search?league=bundesliga"

# Combinar filtros
curl "http://localhost:8000/matches/search?team=barcelona&status=finished&limit=20"

# Partida específica
curl http://localhost:8000/matches/456
```

## 🔄 Sincronização

### Status da Sincronização

```bash
# Ver status atual
curl http://localhost:8000/sync/status

# Resposta:
{
  "is_running": false,
  "last_sync": {
    "id": 42,
    "started_at": "2026-03-06T10:25:00",
    "finished_at": "2026-03-06T10:28:30",
    "status": "completed",
    "source": "sofascore",
    "matches_created": 150,
    "matches_updated": 89,
    "error_message": null,
    "created_at": "2026-03-06T10:25:00"
  },
  "next_scheduled": "2026-03-06T10:33:30"
}
```

### Histórico de Sincronizações

```bash
# Últimas 10 sincronizações
curl http://localhost:8000/sync/history

# Últimas 20
curl "http://localhost:8000/sync/history?limit=20"
```

### Disparar Sincronização Manual

```bash
# Trigger normal (falha se já estiver rodando)
curl -X POST http://localhost:8000/sync/run \
  -H "Content-Type: application/json" \
  -d '{
    "force": false,
    "source": null
  }'

# Forçar sync mesmo se estiver rodando
curl -X POST http://localhost:8000/sync/run \
  -H "Content-Type: application/json" \
  -d '{
    "force": true,
    "source": null
  }'

# Sync de fonte específica
curl -X POST http://localhost:8000/sync/run \
  -H "Content-Type: application/json" \
  -d '{
    "force": false,
    "source": "sofascore"
  }'
```

## 🐍 Exemplos em Python

### Setup

```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
```

### Consultar Jogos de Hoje

```python
def get_today_matches(sport=None, league=None):
    """Retorna jogos de hoje."""
    url = f"{BASE_URL}/matches/today"
    params = {}
    
    if sport:
        params['sport'] = sport
    if league:
        params['league'] = league
    
    response = requests.get(url, params=params)
    return response.json()

# Usar
matches = get_today_matches(sport='football')
for match in matches:
    print(f"{match['home_team']['name']} vs {match['away_team']['name']}")
```

### Buscar Time e Seus Próximos Jogos

```python
def find_team_next_matches(team_name, days_ahead=7):
    """Encontra próximos jogos de um time."""
    # 1. Buscar o time
    search_url = f"{BASE_URL}/teams/search"
    teams = requests.get(search_url, params={'q': team_name, 'limit': 1}).json()
    
    if not teams:
        return None
    
    team = teams[0]
    
    # 2. Buscar próximos jogos
    today = datetime.now().strftime('%Y-%m-%d')
    future = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    matches_url = f"{BASE_URL}/matches/range"
    matches = requests.get(matches_url, params={
        'start': today,
        'end': future,
        'team': team_name
    }).json()
    
    return {
        'team': team,
        'matches': matches
    }

# Usar
result = find_team_next_matches('Barcelona', days_ahead=14)
print(f"Próximos jogos de {result['team']['name']}:")
for match in result['matches']:
    print(f"  {match['match_datetime_utc']}: {match['home_team']['name']} vs {match['away_team']['name']}")
```

### Monitorar Sincronização

```python
import time

def wait_for_sync_completion(timeout=300):
    """Aguarda conclusão da sincronização."""
    start = time.time()
    
    while time.time() - start < timeout:
        status = requests.get(f"{BASE_URL}/sync/status").json()
        
        if not status['is_running']:
            last_sync = status.get('last_sync')
            if last_sync:
                print(f"Sync completado: {last_sync['matches_created']} criados, {last_sync['matches_updated']} atualizados")
                return True
        
        print("Aguardando sincronização...")
        time.sleep(5)
    
    return False

# Trigger e aguardar
requests.post(f"{BASE_URL}/sync/run", json={'force': False})
wait_for_sync_completion()
```

### Obter Estatísticas

```python
def get_stats():
    """Retorna estatísticas gerais."""
    stats = {}
    
    # Total de esportes
    sports = requests.get(f"{BASE_URL}/sports").json()
    stats['sports_count'] = len(sports)
    
    # Total de ligas
    leagues = requests.get(f"{BASE_URL}/leagues").json()
    stats['leagues_count'] = len(leagues)
    
    # Jogos de hoje
    today_matches = requests.get(f"{BASE_URL}/matches/today").json()
    stats['today_matches'] = len(today_matches)
    
    # Status de sync
    sync_status = requests.get(f"{BASE_URL}/sync/status").json()
    stats['sync_running'] = sync_status['is_running']
    stats['last_sync'] = sync_status.get('last_sync', {}).get('finished_at')
    
    return stats

# Usar
stats = get_stats()
print(f"Estatísticas do sistema:")
print(f"  Esportes: {stats['sports_count']}")
print(f"  Ligas: {stats['leagues_count']}")
print(f"  Jogos hoje: {stats['today_matches']}")
print(f"  Última sync: {stats['last_sync']}")
```

## 🌐 Exemplos em JavaScript/Node.js

### Fetch Jogos de Hoje

```javascript
async function getTodayMatches(sport = null, league = null) {
    const params = new URLSearchParams();
    if (sport) params.append('sport', sport);
    if (league) params.append('league', league);
    
    const response = await fetch(`http://localhost:8000/matches/today?${params}`);
    const matches = await response.json();
    
    return matches;
}

// Usar
getTodayMatches('football', 'Premier League')
    .then(matches => {
        matches.forEach(match => {
            console.log(`${match.home_team.name} vs ${match.away_team.name}`);
        });
    });
```

### Webhook Listener (Exemplo de Integração)

```javascript
const express = require('express');
const axios = require('axios');

const app = express();
const API_URL = 'http://localhost:8000';

// Endpoint que consome a API
app.get('/api/today-matches', async (req, res) => {
    try {
        const response = await axios.get(`${API_URL}/matches/today`, {
            params: {
                sport: req.query.sport,
                status: req.query.status
            }
        });
        
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => {
    console.log('Frontend server running on port 3000');
});
```

## 📱 Formato de Resposta

### Match Detail (Completo)

```json
{
  "id": 123,
  "sport_id": 1,
  "league_id": 5,
  "season": "2025/2026",
  "home_team_id": 42,
  "away_team_id": 87,
  "match_datetime_utc": "2026-03-10T20:00:00",
  "status": "scheduled",
  "home_score": null,
  "away_score": null,
  "source_primary": "sofascore",
  "source_external_id": "11234567",
  "last_synced_at": "2026-03-06T10:25:00",
  "created_at": "2026-03-05T15:30:00",
  "updated_at": "2026-03-06T10:25:00",
  "league": {
    "id": 5,
    "sport_id": 1,
    "name": "Premier League",
    "country": "England",
    "canonical_name": "england premier league",
    "created_at": "2026-03-05T10:00:00",
    "updated_at": "2026-03-05T10:00:00"
  },
  "home_team": {
    "id": 42,
    "sport_id": 1,
    "name": "Manchester City",
    "canonical_name": "manchester city",
    "country": "England",
    "created_at": "2026-03-05T10:00:00",
    "updated_at": "2026-03-05T10:00:00"
  },
  "away_team": {
    "id": 87,
    "sport_id": 1,
    "name": "Liverpool",
    "canonical_name": "liverpool",
    "country": "England",
    "created_at": "2026-03-05T10:00:00",
    "updated_at": "2026-03-05T10:00:00"
  }
}
```

## 🔗 Filtros Úteis

### Status da Partida

- `scheduled` - Ainda não começou
- `live` - Em andamento
- `finished` - Finalizada
- `postponed` - Adiada
- `cancelled` - Cancelada

### Esportes Disponíveis

- `football` - Futebol (principal)
- Outros serão adicionados conforme implementação

### Dicas de Performance

1. **Use filtros sempre que possível**
   ```bash
   # Melhor
   curl "http://localhost:8000/matches/today?sport=football&league=Premier"
   
   # Evite
   curl "http://localhost:8000/matches/today"  # Retorna tudo
   ```

2. **Prefira endpoints específicos**
   ```bash
   # Melhor
   curl "http://localhost:8000/matches/date/2026-03-10"
   
   # Evite
   curl "http://localhost:8000/matches/range?start=2026-03-10&end=2026-03-10"
   ```

3. **Use paginação para grandes resultados**
   ```bash
   curl "http://localhost:8000/matches/range?start=2026-03-01&end=2026-03-31&page=1&page_size=50"
   ```

## 🎯 Use Cases Comuns

### 1. Widget de "Jogos de Hoje"

```python
def get_today_widget_data():
    matches = requests.get(f"{BASE_URL}/matches/today", params={
        'sport': 'football',
        'status': 'scheduled'
    }).json()
    
    return sorted(matches, key=lambda x: x['match_datetime_utc'])[:10]
```

### 2. Notificação de Jogos ao Vivo

```python
def get_live_matches():
    return requests.get(f"{BASE_URL}/matches/today", params={
        'status': 'live'
    }).json()
```

### 3. Calendário de Time

```python
def get_team_calendar(team_name, days=30):
    today = datetime.now().strftime('%Y-%m-%d')
    future = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    
    return requests.get(f"{BASE_URL}/matches/range", params={
        'start': today,
        'end': future,
        'team': team_name
    }).json()
```

## 🔧 Troubleshooting

### Erro 404
```bash
# Verificar se a API está rodando
curl http://localhost:8000/health
```

### Erro 500
```bash
# Ver logs
docker logs scraperfc_api -f
```

### Resposta vazia
```bash
# Verificar se houve sincronização
curl http://localhost:8000/sync/status

# Forçar sync
curl -X POST http://localhost:8000/sync/run -H "Content-Type: application/json" -d '{"force": true}'
```

---

Para mais exemplos, acesse a documentação interativa: http://localhost:8000/docs
