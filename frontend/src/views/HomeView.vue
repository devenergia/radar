<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

interface ApiStatus {
  name: string
  status: string
  endpoint: string
  prazo: string
}

const apis = ref<ApiStatus[]>([
  {
    name: 'API 1 - Interrupcoes Ativas',
    status: 'Em desenvolvimento',
    endpoint: '/quantitativointerrupcoesativas',
    prazo: 'Prioritario'
  },
  {
    name: 'API 2 - Dados Demanda',
    status: 'Placeholder',
    endpoint: '/dadosdemanda',
    prazo: 'Abril/2026'
  },
  {
    name: 'API 3 - Demandas Diversas',
    status: 'Placeholder',
    endpoint: '/quantitativodemandasdiversas',
    prazo: 'Maio/2026'
  },
  {
    name: 'API 4 - Tempo Real',
    status: 'Aguardando ANEEL',
    endpoint: 'A definir',
    prazo: '60 dias apos instrucoes'
  }
])
</script>

<template>
  <div class="home">
    <h2>Dashboard RADAR</h2>

    <div class="cards">
      <div
        v-for="api in apis"
        :key="api.name"
        class="card"
        :class="{ active: api.status === 'Em desenvolvimento' }"
      >
        <h3>{{ api.name }}</h3>
        <p class="endpoint">{{ api.endpoint }}</p>
        <p class="status">{{ api.status }}</p>
        <p class="prazo">Prazo: {{ api.prazo }}</p>
      </div>
    </div>

    <nav class="nav-links">
      <router-link to="/interrupcoes">Ver Interrupcoes</router-link>
      <router-link to="/demandas">Ver Demandas</router-link>
    </nav>
  </div>
</template>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  margin-bottom: 2rem;
  color: #333;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border-left: 4px solid #ccc;
}

.card.active {
  border-left-color: #1a5f2a;
}

.card h3 {
  margin-bottom: 0.5rem;
  color: #333;
}

.card .endpoint {
  font-family: monospace;
  background: #f5f5f5;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.card .status {
  color: #666;
  font-size: 0.9rem;
}

.card .prazo {
  color: #1a5f2a;
  font-weight: 500;
  margin-top: 0.5rem;
}

.nav-links {
  display: flex;
  gap: 1rem;
}

.nav-links a {
  background: #1a5f2a;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
}

.nav-links a:hover {
  background: #145222;
}
</style>
