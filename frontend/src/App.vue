<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <header class="app-header">
      <h1>RADAR</h1>
      <span>Roraima Energia - Monitoramento ANEEL</span>
    </header>

    <main class="app-main">
      <RouterView />
    </main>

    <footer class="app-footer">
      <p>RADAR - Sistema de Integracao com ANEEL</p>
    </footer>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: #1a5f2a;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.app-header h1 {
  font-size: 1.5rem;
}

.app-header span {
  font-size: 0.9rem;
  opacity: 0.9;
}

.app-main {
  flex: 1;
  padding: 2rem;
  background: #f5f5f5;
}

.app-footer {
  background: #333;
  color: white;
  padding: 1rem;
  text-align: center;
  font-size: 0.85rem;
}
</style>
