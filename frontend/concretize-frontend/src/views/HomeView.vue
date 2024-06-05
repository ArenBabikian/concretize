
<template>
  <main>
    <div class="wrapper">
      <div class="input-area">
        <textarea v-model="specificationsText" class="input-text block"></textarea>
        <button @click="onSubmit" class="submit-button block" :disabled="waiting">{{ buttonText }}</button>
      </div>
      <div class="img-display">
        <img :src="imgSrc" class="res-img"/>
        <div class="placeholder-text center-text" v-if="showPlaceholder">
          Your image will appear here
        </div>
      </div>

    </div>
  </main>
</template>

<script>
import { BASE_URL, generate, download } from '@/scripts/api'
export default {
  data() {
    return {
      specificationsText: "",
      imgSrc: "",
      waiting: false
    }
  },
  computed: {
    showPlaceholder() {
      return this.imgSrc.length == 0;
    },
    buttonText() {
      if (this.waiting) {
        return "Loading...";
      } 
      return "Submit";
    }
  },
  methods: {
    async onSubmit() {
      this.waiting = true;
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
      this.waiting = false;
    }
  }
}
</script>

<style scoped>
.wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  width: 100%;
  margin-top: 10px;
}
.input-text {
  height: 70vh;
  width: 100%;
  resize: none;
}

.center-text {
  width: 100%;
  text-align: center;
  margin-top: 30vh;
}
.submit-button {
  margin-top: 5px;
  float: right;
  position: relative;
  left: 5px; 
}
.res-img {
  width: min(48vw, 100%);
  float:right;
}
</style>