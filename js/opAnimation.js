const normalContents = document.getElementById("mainContents");
setTimeout(() => {
    normalContents.style.opacity = 1;
}, 4000);

const text = "Do you love?\nLove UnOffical Site";
const opAnimationText = document.getElementById("opAnimationText");
const lines = text.split('\n'); // 改行で分ける
lines.forEach(line => {
    const lineElement = document.createElement('div');
    opAnimationText.appendChild(lineElement);

    for (let i = 0; i < line.length; i++) {
        const span = document.createElement("span");
        span.textContent = line[i];
        lineElement.appendChild(span);
    }
    const spans = lineElement.querySelectorAll("span");
    spans.forEach((span, index) => {
        span.style.animationDelay = `${index * 0.15}s`;
    });
});