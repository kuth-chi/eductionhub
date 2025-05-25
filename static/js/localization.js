function isLocalText (text) {
    const localTextRegex = /[\u1780-\u17FF]/;
    const test = localTextRegex.test(text);
    console.log("Localization Test: ", test);
    return test;
}

document.addEventListener("DOMContentLoaded", () => {
    const elements = document.querySelectorAll(".lang-charset");

    elements.forEach((element) => {
        const text = element.textContent || element.innerText;
        if (isLocalText(text)) {
            element.classList.add("font-localization");
        } else {
            element.classList.remove("font-body");
        }
    })
})