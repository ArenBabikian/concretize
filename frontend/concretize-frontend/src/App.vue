<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <div class="wrapper">
      <nav>
        <div class="nav-bar">
          <div class="wordmark-wrap">
          <i class="concretize-logo"></i>
          <div class="wordmark">Concretize</div>
          </div>
          <RouterLink to="/" class="no-underline nav-element">Home</RouterLink>
        </div>
      </nav>
    </div>
  </header>

  <RouterView class="content-wrapper" />
</template>

<style scoped>
.nav-bar {
  font-family: var(--font-sans);
  font-size: var(--text-size-big);
  background-color: var(--color-accent);
  position: fixed;
  top: 0;
  width: 100%;
  height: var(--navbar-height);
  display: flex;
  flex-direction:row;
  box-shadow: grey 0px 2px 3px;
}

.wordmark {
  align-content: center;
  color: var(--color-gray-text);
  font-family: var(--font-serif);
  margin-top: -6px;
}

.nav-element {
  color: var(--color-light-text);
  transition: 0.2s;
  align-content: center;
  padding-left: 0.5em;
  padding-right: 0.5em;
}

.nav-element:hover {
  background-color: hsl(from var(--color-accent) h s calc(l + 10));
}
.content-wrapper {
  margin-top: calc(var(--navbar-height) + 5px);
}
.wordmark-wrap {
  display: flex;
  background-color: var(--color-light-text);
  padding-right: 7px;
}
</style>
