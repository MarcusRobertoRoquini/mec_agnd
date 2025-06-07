const frases = [
  "Seu tempo vale ouro",
  "Agende com facilidade",
  "Cuide do seu carro com quem entende",
  "Oficina inteligente, cliente satisfeito",
  "Serviço de qualidade, no seu tempo",
  "Organize, agende, resolva",
  "Tecnologia e confiança para seu veículo"
];
 
let index = 0;
const textSpan = document.getElementById("rotatingText");
 
// Inicia com opacidade 1
textSpan.textContent = frases[index];
 
setInterval(() => {
  // Fade out
  textSpan.style.opacity = 0;
 
  // Aguarda o fade-out antes de trocar o texto
  setTimeout(() => {
    index = (index + 1) % frases.length;
    textSpan.textContent = frases[index];
   
    // Fade in
    textSpan.style.opacity = 1;
  }, 500); // Tempo do fade-out
}, 4000); // Troca a cada 4 segundos
 