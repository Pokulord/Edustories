import './style.css'

const burger = document.getElementById("burger");
const mobileMenu = document.getElementById("mobileMenu");

burger.addEventListener("click", () => {
  mobileMenu.classList.toggle("opacity-0");
  mobileMenu.classList.toggle("pointer-events-none");
});


const fireflyContainer = document.getElementById("fireflies");

function createFirefly() {
  const firefly = document.createElement("div");
  firefly.classList.add("firefly");

  // случайная позиция по ширине
  firefly.style.left = Math.random() * 100 + "vw";
  firefly.style.bottom = "-10px";

  // случайная скорость
  const duration = 10 + Math.random() * 10;
  firefly.style.animationDuration = duration + "s, 3s";

  // случайный размер
  const size = 4 + Math.random() * 4;
  firefly.style.width = size + "px";
  firefly.style.height = size + "px";

  fireflyContainer.appendChild(firefly);

  // удаляем после завершения
  setTimeout(() => {
    firefly.remove();
  }, duration * 1000);
}

// создаём постоянно
setInterval(createFirefly, 800);


document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener("click", function (e) {

    const href = this.getAttribute("href");

    // игнорируем пустой #
    if (href === "#" || href.length <= 1) return;

    const target = document.querySelector(href);

    if (target) {
      e.preventDefault();

      target.scrollIntoView({
        behavior: "smooth"
      });

      // закрываем мобильное меню
      const mobileMenu = document.getElementById("mobileMenu");
      mobileMenu?.classList.add("opacity-0", "pointer-events-none");
    }
  });
});




