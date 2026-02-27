const formData = new FormData();
formData.append("resume", resumeFile);
formData.append("job_description", jdFile);

fetch("/process_resume", {
  method: "POST",
  body: formData
})
  .then(response => response.json())
  .then(data => {
    console.log(data.score);
    console.log(data.retrieved_tips);
    console.log(data.ai_suggestions);
  });

  // frontend/js/main.js
document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const resumeFile = document.getElementById("resume").files[0];
    const jdFile = document.getElementById("job_description").files[0];

    if (!resumeFile || !jdFile) {
        alert("Please upload both files.");
        return;
    }

    const formData = new FormData();
    formData.append("resume", resumeFile);
    formData.append("job_description", jdFile);

    const resultDiv = document.getElementById("result");
    resultDiv.style.display = "none";

    try {
        const response = await fetch("/process_resume", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        document.getElementById("score").innerText = data.score;
        const tipsList = document.getElementById("tipsList");
        tipsList.innerHTML = "";
        data.retrieved_tips.forEach(tip => {
            const li = document.createElement("li");
            li.innerText = tip;
            tipsList.appendChild(li);
        });
        document.getElementById("aiSuggestions").innerText = data.ai_suggestions;
        resultDiv.style.display = "block";
    } catch (err) {
        alert("Error processing files. Make sure backend is running.");
        console.error(err);
    }
});