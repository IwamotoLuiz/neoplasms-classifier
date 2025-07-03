<template>
  <div class="upload-container">
    <h2>Selecionar Imagem</h2>
    <div class="file-input-wrapper">
      <label for="file-upload" class="custom-file-upload">
        Escolher arquivo
      </label>
      <input id="file-upload" type="file" @change="onFileSelected" accept="image/*">
      <span class="file-name">{{ selectedFileName || 'Nenhum arquivo selecionado' }}</span>
    </div>

    <div v-if="imageUrl" class="preview-section">
      <h3>Pré-visualização:</h3>
      <img :src="imageUrl" alt="Image preview" class="image-preview">
    </div>

    <button @click="uploadImage" class="upload-button" :disabled="!imageUrl || isLoading">
      Enviar Imagem
    </button>

    <div class="prediction-result">
      <h3>Resultado da Predição:</h3>
      <p v-if="isLoading" class="loading-message">Carregando...</p>
      <p v-else-if="prediction" :class="predictionClass">{{ prediction }}</p>
      <p v-else class="initial-message">Envie uma imagem para obter a predição.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImageUploader',
  data() {
    return {
      selectedFile: null,
      imageUrl: null,
      selectedFileName: '',
      prediction: null,
      isLoading: false, // NOVO: Variável para controlar o estado de carregamento
    };
  },
  computed: {
    // Propriedade computada para determinar a classe CSS da predição
    predictionClass() {
      if (this.prediction) {
        // Converte a predição para minúsculas e remove espaços para comparação robusta
        const lowerCasePrediction = this.prediction.toLowerCase().trim();

        // Ajuste estes termos para o que sua API realmente retorna para cada tipo
        if (lowerCasePrediction.includes('maligno') || lowerCasePrediction.includes('cancer') || lowerCasePrediction.includes('melanoma')) {
          return 'malignant-prediction';
        } else if (lowerCasePrediction.includes('benigno') || lowerCasePrediction.includes('saudavel')) {
          return 'benign-prediction';
        } else if (lowerCasePrediction.startsWith('erro:')) { // Se for uma mensagem de erro
          return 'error-message';
        }
      }
      return ''; // Retorna vazio se não houver predição ou se não corresponder
    }
  },
  methods: {
    onFileSelected(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
        this.selectedFileName = file.name;
        this.imageUrl = URL.createObjectURL(file);
        this.prediction = null; // Limpa qualquer predição anterior
        this.isLoading = false; // Garante que não esteja no estado de carregamento ao selecionar um novo arquivo
        console.log("🖼️ Arquivo selecionado:", file.name);
      } else {
        this.selectedFile = null;
        this.selectedFileName = '';
        this.imageUrl = null;
        this.prediction = null;
        this.isLoading = false;
        console.warn("⚠️ Nenhum arquivo foi selecionado.");
      }
    },
    async uploadImage() {
      if (!this.selectedFile) {
        console.warn("⚠️ Nenhum arquivo selecionado para upload.");
        return;
      }

      this.isLoading = true; // Inicia o estado de carregamento
      this.prediction = null; // Limpa a predição anterior para que "Carregando..." apareça

      console.log("📤 Enviando imagem para o backend...");

      const formData = new FormData();
      formData.append('file', this.selectedFile);

      // Defina o URL da sua API (local ou remota)
      const apiUrl = 'https://neoplasms-classifier.onrender.com/predict'; // OU 'http://127.0.0.1:8000/predict';

      try {
        const response = await fetch(apiUrl, {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error("❌ Erro da API:", response.status, errorText);
          this.prediction = `Erro: ${response.status} - ${errorText}`; // Exibe erro HTTP no frontend
          return;
        }

        const data = await response.json();
        console.log("✅ Resposta da API:", data);

        // Verifica o formato da resposta da API antes de atribuir
        if (data && data.prediction) {
          this.prediction = data.prediction;
        } else {
          this.prediction = "Formato de resposta inesperado da API.";
          console.warn("Formato de resposta inesperado:", data);
        }

      } catch (error) {
        console.error("❌ Erro ao enviar imagem ou processar resposta:", error);
        this.prediction = `Erro ao conectar com a API: ${error.message}`; // Exibe erros de rede/conexão
      } finally {
        this.isLoading = false; // Finaliza o estado de carregamento (sempre executa)
      }
    }
  }
};
</script>

<style scoped>
.upload-container {
  max-width: 500px;
  margin: 40px auto;
  text-align: center;
  padding: 30px;
  border: 2px dashed #444;
  border-radius: 12px;
  background-color: #2a2a2a;
  color: #e0e0e0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
}

h2 {
  color: #ffffff;
  margin-bottom: 25px;
  font-size: 2em;
}

h3 {
  color: #bbbbbb;
  margin-top: 30px;
  margin-bottom: 15px;
  font-size: 1.5em;
}

.file-input-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
}

.custom-file-upload {
  border: 1px solid #007bff;
  display: inline-block;
  padding: 10px 20px;
  cursor: pointer;
  background-color: #007bff;
  color: white;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.custom-file-upload:hover {
  background-color: #0056b3;
}

input[type="file"] {
  display: none;
}

.file-name {
  color: #ccc;
  font-style: italic;
}

.preview-section {
  margin-top: 20px;
}

.image-preview {
  max-width: 100%;
  height: auto;
  border: 1px solid #555;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  display: block;
  margin: 0 auto 30px auto;
}

.upload-button {
  background-color: rgb(236, 236, 236);
  color: black;
  padding: 12px 25px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1em;
  transition: background-color 0.3s ease;
  margin-bottom: 20px;
}

.upload-button:hover {
  background-color: rgb(201, 204, 204);
}

.upload-button:disabled {
  background-color: #6c757d; /* Cor quando desabilitado */
  cursor: not-allowed;
  opacity: 0.7; /* Suaviza a aparência quando desabilitado */
}

/* Estilos para a seção de resultado da predição */
.prediction-result {
  margin-top: 25px;
  padding: 15px;
  border: 1px solid #007bff;
  border-radius: 8px;
  background-color: #333;
  color: #f5f5f5;
  font-size: 1.2em;
  font-weight: bold;
  text-align: center;
  word-wrap: break-word;
  min-height: 50px; /* Garante que a caixa não encolha demais */
  display: flex; /* Para centralizar o conteúdo verticalmente */
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.prediction-result h3 {
  margin-top: 0;
  color: #fff;
  font-size: 1.3em;
}

.prediction-result p {
  margin-bottom: 0;
  font-size: 25px;
  /* A cor padrão é removida pois será definida pelas classes específicas */
}

/* NOVAS CLASSES PARA CORES CONDICIONAIS E ESTADOS */
.malignant-prediction {
  color: #ff4444; /* Vermelho vibrante para maligno */
  font-weight: bold;
}

.benign-prediction {
  color: #44cc44; /* Verde suave para benigno */
  font-weight: bold;
}

.loading-message {
  color: #ffd700; /* Dourado/Amarelo para mensagem de carregamento */
  font-style: italic;
  animation: pulse 1.5s infinite alternate; /* Animação simples de pulsação */
}

.error-message {
  color: #ffbb00; /* Laranja para mensagens de erro */
  font-weight: bold;
}

.initial-message {
    color: #999; /* Cor mais suave para a mensagem inicial */
    font-style: italic;
    font-size: 0.9em; /* Um pouco menor para a mensagem inicial */
}

/* Animação de pulsação para o texto de carregamento */
@keyframes pulse {
  0% { opacity: 0.1; }
  100% { opacity: 1; }
}

/* Global styles (sempre no final do seu style block) */
:global(body) {
  background-color: #121212;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  margin: 0;
  padding: 0;
  height: 100%;
  box-sizing: border-box;
}
</style>