const form = document.getElementById("urlForm");
const urlInput = document.getElementById("urlInput");
const result = document.getElementById("result");
const shortUrl = document.getElementById("shortUrl");
const copyButton = document.getElementById("copyButton");
const error = document.getElementById("error");

form.addEventListener("submit", async (event) => {
event.preventDefault();


result.classList.add("hidden");
error.textContent = "";

try {
    const response = await fetch("/shorten", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            original_url: urlInput.value
        })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Something went wrong");
    }

    shortUrl.textContent = data.short_url;
    shortUrl.href = data.short_url;

    result.classList.remove("hidden");

} catch (err) {
    error.textContent = err.message;
}


});

copyButton.addEventListener("click", async () => {
await navigator.clipboard.writeText(shortUrl.textContent);


copyButton.textContent = "Copied!";

setTimeout(() => {
    copyButton.textContent = "Copy";
}, 1500);


});
