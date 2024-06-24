<script setup>
import { VAceEditor } from 'vue3-ace-editor';
import './ace/mode-concretize'; // Load the language definition file used below
</script>

<template>
  <main>
    <div class="wrapper">
      <div class="input-area">
        <v-ace-editor
          id="editor"
          v-model:value="specificationsText"
          class="input-text block"
        />
        <button @click="onSubmit" class="submit-button block" :disabled="waiting">{{ buttonText }}</button>
        <div v-if="error" class="notification-text">Could not generate image</div>
        <textarea class="console" ref="resultsConsole" disabled v-model="consoleText"></textarea>
      </div>
      <div class="img-display">
        <img :src="imgSrc" class="res-img"/>
        <div class="placeholder-text center-text" v-if="showPlaceholder">
          Your image will appear here
        </div>
        <div class="resultsNav" v-if="!showPlaceholder">
          <button @click="goToPrev" class="round-button" :disabled="page <= 0"><i class="bi bi-caret-left"></i></button>
          <span class="notification-text">{{ page + 1 }}/{{ fileNames.length }}</span>
          <button @click="goToNext" class="round-button" :disabled="page >= fileNames.length - 1"><i class="bi bi-caret-right"></i></button>
        </div>
      </div>

    </div>
  </main>
</template>

<script>
import { BASE_URL, generate, download } from '@/scripts/api'
import { DEFAULT_PARAMS } from '@/assets/strings';
window.onload = function () {
  var editor = ace.edit("editor");
  editor.session.setMode("ace/mode/concretize")
}

export default {
  data() {
    return {
      specificationsText: DEFAULT_PARAMS,
      waiting: false,
      consoleText: "",
      error: false,
      fileNames: [],
      page: 0
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
    },
    imgSrc() {
      if (this.fileNames.length) {
        return `${BASE_URL}/downloads/${this.fileNames[this.page]}`;
      } else {
        return "";
      }
    }
  },
  watch: {
    specificationsText() {
      // Exit error state if user has changed the text
      this.error = false;
    },
    consoleText() {
      // Automatically scrolls console to bottom on update
      this.$nextTick(() => {
        this.$refs.resultsConsole.scrollTop = this.$refs.resultsConsole.scrollHeight;
      });
    }
  },
  mounted() {
    var editor = ace.edit("editor");
    editor.session.setMode("ace/mode/concretize")
  },
  methods: {
    async onSubmit() {
      this.waiting = true;
      let res = await generate(this.specificationsText, {
        // approach: "mhs",
        // aggregation_strategy: "actors",
        // algorithm_name: "nsga2",
        // restart_time: -1,
        // history: "none",
        // num_of_mhs_runs: 10,
        // num_of_scenarios: 1,
        // color_scheme: "default",
        // hide_actors: false,
        // show_maneuvers: true,
        // show_exact_paths: true,
        // timeout: 60,
        // zoom_diagram: true
      })
      console.log(res)
      if (res?.data?.diagram_file_names) {
        this.page = 0; //if update occurs, number of pages may change
        this.fileNames = res?.data?.diagram_file_names;
        
      } else if (res?.data?.error) {
        this.consoleText += `${res?.data?.error}\n`;
        this.error = true;
      }
      
      this.waiting = false;
    },
    goToPrev() {
      if (this.page > 0) {
        this.page -= 1;
      }
    },
    goToNext() {
      if (this.page < this.fileNames.length - 1) {
        this.page += 1;
      }
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
  height: 60vh;
  width: 100%;
  resize: none;
  font-size: var(--text-size-small);
  font-family: var(--font-mono);
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

.console {
  height: 20vh;
  width: 100%;
  margin-top: 5px;
  background-color: var(--color-dark-text);
  color: var(--color-light-text);
  font-family: var(--font-mono);
  overflow: auto;
}

.res-img {
  width: min(40vw, 100%);
  align-self:center;
  display: block;
}
.img-display {
  display: flex;
  flex-direction: column;
}

.resultsNav {
  display: flex;
  justify-content: space-around;
}
</style>