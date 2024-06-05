
<template>
  <main>
    <textarea v-model="specificationsText"></textarea>
    <button @click="onSubmit">Submit</button>
    <img :src="imgSrc"/>
  </main>
</template>

<script>
import { BASE_URL, generate, download } from '@/scripts/api'
export default {
  data() {
    return {
      specificationsText: "",
      imgSrc: ""
    }
  },
  methods: {
    async onSubmit() {
      console.log(this.specificationsText)
      let res = await generate(this.specificationsText, {
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
      if (res?.data?.diagram_file_name) {
        const filename = res?.data?.diagram_file_name;
        this.imgSrc = `${BASE_URL}/downloads/${filename}`
      }
    }
  }
}
</script>