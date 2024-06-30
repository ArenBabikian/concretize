<script setup>
import { VAceEditor } from 'vue3-ace-editor';
import './ace/mode-concretize'; // Load the language definition file used below
</script>

<!-- TODOs for the UI:
 1. make the "Generate scenarios" button les wide, and centered on the left column
 2. fix the position of the error log at the bottom of the screen, and the status bar right on top of it
 3. Add simulate "Download" and "Simulate" buttons at the bottom of the left part
 4. Change the initial contenbt of the editor + add documentation for the tool usage.
 5. Alow the user to abort a scenario generation run at any stage.
 6. handle the case where no models are generated.
-->

<template>
  <main>
    <div class="wrapper">
      <div class="input-area">
        <v-ace-editor
          id="editor"
          v-model:value="specificationsText"
          class="input-text block"
        />
        <!-- <button @click="onSubmit" class="submit-button block" :disabled="waiting">{{ buttonText }}</button> -->
        <!-- <div v-if="error" class="diagnostics">Could not generate image</div> -->
        <div class="diagnostics center-text" :style="{backgroundColor: diagnostic[1]}">{{ diagnostic[0] }}</div>
        <!-- <div class="diagnostics">{{ diagnostic }}</div> -->

        <!-- <textarea class="console" ref="resultsConsole" disabled v-model="consoleText"></textarea> -->
        <div class="console" ref="resultsConsole" disabled >{{ consoleText }}</div>
      </div>
      <div class="img-display">
        <button @click="onSubmit" class="submit-button" :disabled="waiting">{{ buttonText }}</button>
        <img :src="imgSrc" class="res-img"/>
        <div class="placeholder-text center-text" v-if="showPlaceholder">
          Your image will appear here
        </div>
        <div class="resultsNav" v-if="!showPlaceholder">
          <button @click="goToPrev" class="round-button" :disabled="page <= 0"><i class="bi bi-caret-left"></i></button>
          <div class="notification-text">{{ page + 1 }}/{{ fileNames.length }}</div>
          <button @click="onSimulate(fileNames[page])" :disabled="waiting"> Simulate </button>
          <button @click="goToNext" class="round-button" :disabled="page >= fileNames.length - 1"><i class="bi bi-caret-right"></i></button>
        </div>
      </div>

    </div>
  </main>
</template>

<script>
import { BASE_URL, generate, simulate } from '@/scripts/api'
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
        return "Running...";
      } 
      return "Generate scenarios";
    },
    diagnostic() {
      if (this.waiting) {
        return ["Status: Running...", "var(--color-gray-text)"];
      } 
      if (! this.error) {
        return ["Status: Ready", "green"];
      } else {
        return ["Status: Error", "red"];
      }
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
    consoleText(newTxt) {
      // Automatically scrolls console to bottom on update
      // this.$nextTick(() => {
      //   this.$refs.resultsConsole.scrollTop = this.$refs.resultsConsole.scrollHeight;
      // });
    }
  },
  mounted() {
    var editor = ace.edit("editor");
    editor.session.setMode("ace/mode/concretize")
  },
  methods: {
    async onSimulate(filename) {
      this.waiting = true;
      this.consoleText = "";
      const res = await simulate(filename);
      if (res?.data?.message) {
        this.consoleText = res.data.message + '\n';
      } 
      if (res?.data?.error){
        this.consoleText = (res?.data?.error || "Unknown error occurred") + '\n';
      }
      this.waiting = false;

    },
    async onSubmit() {
      this.waiting = true;
      this.consoleText = "";
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
      if (res?.data?.diagram_file_names) {
        this.page = 0; //if update occurs, number of pages may change
        this.fileNames = res?.data?.diagram_file_names;
        // this.consoleText = "";
      } else if (res?.data?.error) {
        // this.consoleText += `${res?.data?.error}\n`;
        this.consoleText = `${res?.data?.error}\n`;
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
  height: 70vh;
  margin: 5px 0;
  padding: 0 5px;
  font-size: var(--text-size-small);
  font-family: var(--font-mono);
}

.center-text {
  width: 100%;
  text-align: center;
  margin-top: 30vh;
}
.submit-button {
  display: block;
  margin: 5px;
  float: right;
  position: static;
  left: 5px; 
}

.console {
  height: 14vh;
  padding: 0 5px;
  background-color: var(--color-dark-text);
  color: var(--color-light-text);
  font-family: var(--font-mono);
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.diagnostics {
  height: 2vh;
  margin: 5px 0;
  background-color: var(--color-dark-text);
  color: var(--color-light-text);
  font-family: var(--font-mono);
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.res-img {
  width: min(30vw, 100%);
  margin: 10px;
  align-self:center;
  display: block;
}
.img-display {
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg);
}

.resultsNav {
  display: flex;
  justify-content: space-around;
}
</style>