<template>
  <div class="upload-container">
    <h1>Selecionar Imagem</h1>
    
    <input type="file" accept="image/*" @change="onFileChange" />

    <div v-if="previewUrl" class="preview">
      <h2>Pré-visualização:</h2>
      <img :src="previewUrl" alt="Imagem selecionada" />
      <button @click="uploadImage">Enviar Imagem</button>
    </div>

    <div v-if="prediction">
      <h3>Predição:</h3>
      <p>{{ prediction }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImageUploader',
  data() {
    return {
      selectedFile: null,
      previewUrl: null,
      prediction: null,
    };
  },
  methods: {
    onFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
        this.previewUrl = URL.createObjectURL(file);
        console.log("🖼️ Arquivo selecionado:", file);
      } else {
        console.warn("⚠️ Nenhum arquivo foi selecionado.");
      }
    },
    async uploadImage() {
      if (!this.selectedFile) {
        console.warn("⚠️ Nenhum arquivo selecionado para upload.");
        return;
      }

      console.log("📤 Enviando imagem para o backend...");

      const formData = new FormData();
      formData.append('file', this.selectedFile);

      try {
        const response = await fetch('https://neoplasms-classifier.onrender.com/predict', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error("❌ Erro da API:", response.status, errorText);
          return;
        }

        const data = await response.json();
        console.log("✅ Resposta da API:", data);
        this.prediction = data.prediction;
      } catch (error) {
        console.error("❌ Erro ao enviar imagem:", error);
      }
    }
  }
};
</script>


<style scoped>
.upload-container {
  max-width: 400px;
  margin: auto;
  text-align: center;
  padding: 20px;
  border: 2px dashed #ccc;
  border-radius: 8px;
}

.preview img {
  max-width: 100%;
  margin-top: 10px;
  border-radius: 4px;
}
</style>
