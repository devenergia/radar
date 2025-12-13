<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Interrupcao {
  ideConjuntoUnidadeConsumidora: number
  ideMunicipio: number
  qtdUCsAtendidas: number
  qtdOcorrenciaProgramada: number
  qtdOcorrenciaNaoProgramada: number
}

const interrupcoes = ref<Interrupcao[]>([])
const loading = ref(false)
const error = ref('')

const fetchInterrupcoes = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch('/api/quantitativointerrupcoesativas', {
      headers: {
        'x-api-key': import.meta.env.VITE_API_KEY || ''
      }
    })

    const data = await response.json()

    if (data.idcStatusRequisicao === 1) {
      interrupcoes.value = data.listaInterrupcoes || []
    } else {
      error.value = data.mensagem || 'Erro ao carregar dados'
    }
  } catch (e) {
    error.value = 'Erro de conexao com a API'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchInterrupcoes()
})
</script>

<template>
  <div class="interrupcoes">
    <h2>Interrupcoes Ativas</h2>

    <button @click="fetchInterrupcoes" :disabled="loading">
      {{ loading ? 'Carregando...' : 'Atualizar' }}
    </button>

    <div v-if="error" class="error">{{ error }}</div>

    <table v-if="interrupcoes.length > 0">
      <thead>
        <tr>
          <th>Conjunto</th>
          <th>Municipio (IBGE)</th>
          <th>UCs Atendidas</th>
          <th>Programadas</th>
          <th>Nao Programadas</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in interrupcoes" :key="`${item.ideConjuntoUnidadeConsumidora}-${item.ideMunicipio}`">
          <td>{{ item.ideConjuntoUnidadeConsumidora }}</td>
          <td>{{ item.ideMunicipio }}</td>
          <td>{{ item.qtdUCsAtendidas }}</td>
          <td>{{ item.qtdOcorrenciaProgramada }}</td>
          <td>{{ item.qtdOcorrenciaNaoProgramada }}</td>
        </tr>
      </tbody>
    </table>

    <p v-else-if="!loading && !error">Nenhuma interrupcao ativa no momento.</p>
  </div>
</template>

<style scoped>
.interrupcoes {
  max-width: 1000px;
  margin: 0 auto;
}

h2 {
  margin-bottom: 1rem;
}

button {
  background: #1a5f2a;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 1rem;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  background: #fee;
  color: #c00;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

table {
  width: 100%;
  background: white;
  border-collapse: collapse;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f5f5f5;
  font-weight: 600;
}

tr:hover {
  background: #f9f9f9;
}
</style>
