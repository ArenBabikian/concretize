import "./assets/shared-styles.css"

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())

router.beforeEach((to, from, next) => {
    console.log(to);
    document.title = `${to?.meta?.title} | Concretize` || "Concretize";
    next();
})

app.use(router)

app.mount('#app')
