// Seleciona todos os slides
const slides = Array.from(document.querySelectorAll(".slide"));
let indiceAtual = 0;

function mostrarSlide(i) {
  slides.forEach((slide, idx) => {
    slide.classList.toggle("active", idx === i);
  });
}

// Mostra o primeiro slide
if (slides.length > 0) {
  mostrarSlide(0);
}

// Troca automático a cada 15 segundos
setInterval(() => {
  if (slides.length === 0) return;
  indiceAtual = (indiceAtual + 1) % slides.length;
  mostrarSlide(indiceAtual);
}, 15000);
