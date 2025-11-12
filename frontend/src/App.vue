<template>
  <router-view />
</template>

<script setup>
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  /* Apple Design Colors */
  --apple-blue: #007AFF;
  --apple-gray-1: #F5F5F7;
  --apple-gray-2: #E5E5EA;
  --apple-gray-3: #D1D1D6;
  --apple-gray-4: #8E8E93;
  --apple-gray-5: #636366;
  --apple-gray-6: #48484A;
  --apple-text-primary: #1D1D1F;
  --apple-text-secondary: #86868B;
  --apple-background: #FBFBFD;
  --apple-card-background: rgba(255, 255, 255, 0.8);
  --apple-shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);
  --apple-shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
  --apple-shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.12);
  --apple-border-radius: 12px;
  --apple-border-radius-lg: 16px;
  --apple-transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--apple-background);
  color: var(--apple-text-primary);
  line-height: 1.6;
}

#app {
  min-height: 100vh;
}

/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--apple-gray-1);
}

::-webkit-scrollbar-thumb {
  background: var(--apple-gray-3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--apple-gray-4);
}
</style>

