document.addEventListener("DOMContentLoaded", () => {
    setInterval(() => {
        let star = document.createElement("div");
        star.classList.add("shooting-star");
        document.body.appendChild(star);
        setTimeout(() => star.remove(), 2000);
    }, 5000);
});
