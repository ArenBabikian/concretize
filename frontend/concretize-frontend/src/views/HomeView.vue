
<template>
  <main>
    <textarea v-model="specificationsText"></textarea>
    <button @click="onSubmit">Submit</button>
  </main>
</template>

<script>
import { generate } from '@/scripts/api'
export default {
  data() {
    return {
      specificationsText: ""
    }
  },
  methods: {
    async onSubmit() {
      console.log(this.specificationsText)
      res = await generate(this.specificationsText, {
        approach: "mhs",
        aggregation_strategy: "actors",
        algorithm_name: "nsga2",
        restart_time: -1,
        history: "none",
        num_of_runs: 10,
        timeout: 60,
        zoom_diagram: true
      })
      console.log(res)
    }
  }
}
</script>