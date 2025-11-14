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
  /* ReadSmart Design System - 基于 readsmart_3.html */
  --rs-gray-50: #fafafa;
  --rs-gray-100: #f5f5f5;
  --rs-gray-200: #e5e5e5;
  --rs-gray-300: #d4d4d4;
  --rs-gray-400: #a3a3a3;
  --rs-gray-500: #737373;
  --rs-gray-600: #525252;
  --rs-gray-700: #4a4a4a;
  --rs-gray-800: #2d2d2d;
  --rs-gray-900: #1a1a1a;
  --rs-black: #000000;
  --rs-white: #ffffff;
  
  --rs-text-primary: #1a1a1a;
  --rs-text-secondary: #737373;
  --rs-background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
  --rs-card-bg: #ffffff;
  
  --rs-shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
  --rs-shadow-md: 0 4px 16px rgba(0, 0, 0, 0.06), 0 2px 4px rgba(0, 0, 0, 0.08);
  --rs-shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.1), 0 4px 8px rgba(0, 0, 0, 0.12);
  
  --rs-radius-sm: 8px;
  --rs-radius-md: 12px;
  --rs-radius-lg: 16px;
  --rs-radius-xl: 20px;
  --rs-radius-2xl: 24px;
  
  --rs-transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  
  /* 状态颜色 */
  --rs-red-50: #fef2f2;
  --rs-red-700: #b91c1c;
  --rs-yellow-50: #fefce8;
  --rs-yellow-100: #fef9c3;
  --rs-yellow-200: #fef08a;
  --rs-yellow-700: #a16207;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
  color: #1a1a1a;
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

