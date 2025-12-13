<script setup lang="ts">
// Placeholder - API 2 e 3 ainda nao implementadas
</script>

<template>
  <div class="demandas">
    <h2>Demandas</h2>

    <div class="placeholder">
      <h3>Em desenvolvimento</h3>
      <p>As APIs de demandas estao em desenvolvimento e serao disponibilizadas em breve.</p>

      <ul>
        <li>
          <strong>API 2 - Dados de Demanda:</strong>
          Consulta de dados de uma demanda especifica por protocolo.
          <br><em>Prazo: Abril/2026</em>
        </li>
        <li>
          <strong>API 3 - Demandas Diversas:</strong>
          Quantitativo agregado de demandas por canal, tipologia e status.
          <br><em>Prazo: Maio/2026</em>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.demandas {
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  margin-bottom: 1rem;
}

.placeholder {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.placeholder h3 {
  color: #1a5f2a;
  margin-bottom: 1rem;
}

.placeholder ul {
  margin-top: 1rem;
  padding-left: 1.5rem;
}

.placeholder li {
  margin-bottom: 1rem;
  line-height: 1.6;
}

.placeholder em {
  color: #666;
}
</style>
