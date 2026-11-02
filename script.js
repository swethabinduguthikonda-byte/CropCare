const leafImage = document.getElementById("leafImage");
const preview = document.getElementById("preview");
const detectButton = document.getElementById("detectButton");
const result = document.getElementById("result");

leafImage.addEventListener("change", function () {
    const file = leafImage.files[0];

    if (file) {
        preview.src = URL.createObjectURL(file);
        preview.style.display = "block";
        result.textContent = "Image uploaded. Ready for AI analysis.";
    }
});

detectButton.addEventListener("click", async function () {
    const file = leafImage.files[0];

    if (!file) {
        result.textContent = "Please upload a crop leaf image first.";
        return;
    }

    detectButton.disabled = true;
    result.innerHTML = "<h3>🌱 AI is analysing your leaf image...</h3>";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Prediction failed.");
        }

        const predictions = (data.top_predictions || [])
            .map(item => `
                <li>${item.label} — ${item.confidence}%</li>
            `).join("");

        result.innerHTML = `
            <h2>🌱 CropCare AI Results</h2>
            <p><strong>${data.message}</strong></p>

            <h3>🌾 Detected Crop</h3>
            <h2>${data.sample_crop}</h2>

            <h3>🔬 Detected Disease</h3>
            <h2>${data.sample_disease}</h2>

            <h3>📊 AI Confidence</h3>
            <h2>${data.confidence ?? "Not available"}${data.confidence != null ? "%" : ""}</h2>

            <h3>💊 Suggested Treatment</h3>
            <p>${data.sample_treatment}</p>

            <h3>Other Possible Predictions</h3>
            <ol>${predictions || "<li>No additional predictions available.</li>"}</ol>

            <p><small>AI predictions are estimates. Please consult an agricultural expert before applying treatment.</small></p>
        `;

    } catch (error) {
        result.textContent = "Error: " + error.message;
    } finally {
        detectButton.disabled = false;
    }
});
