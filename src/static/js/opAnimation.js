const normalContents = document.getElementById("mainContents");
setTimeout(() => {
    normalContents.style.opacity = 1;
}, 4000);

const text = "Do you love?\nOffical Site";
const opAnimationText = document.getElementById("opAnimationText");
const lines = text.split('\n');
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