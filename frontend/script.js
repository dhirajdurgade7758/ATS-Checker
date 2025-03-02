document.addEventListener("DOMContentLoaded", function () {
    // Theme Toggle
    const themeToggle = document.getElementById("themeToggle");
    const body = document.body;
    let isDarkMode = false;

    themeToggle.addEventListener("click", () => {
        isDarkMode = !isDarkMode;
        body.setAttribute("data-theme", isDarkMode ? "dark" : "light");
        themeToggle.innerHTML = isDarkMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });

    // Fetch Job Descriptions
    fetch("http://127.0.0.1:8000/api/jobs/")
        .then(response => response.json())
        .then(data => {
            const jobSelect = document.getElementById("jobDescription");
            jobSelect.innerHTML = '<option value="">Select a Job Description</option>';
            data.data.forEach(job => {
                jobSelect.innerHTML += `<option value="${job.job_description}">${job.job_title}</option>`;
            });
        })
        .catch(error => console.error("Error fetching job descriptions:", error));

    // File Upload Preview
    document.getElementById("resumeFile").addEventListener("change", function () {
        const filePreview = document.getElementById("filePreview");
        if (this.files[0]) {
            filePreview.textContent = `Uploaded: ${this.files[0].name}`;
        } else {
            filePreview.textContent = "";
        }
    });

    // Analyze Resume
    document.getElementById("resumeForm").addEventListener("submit", function (event) {
        event.preventDefault();
        
        const jobDescription = document.getElementById("jobDescription").value;
        const resumeFile = document.getElementById("resumeFile").files[0];
        if (!jobDescription || !resumeFile) {
            alert("Please select a job and upload a resume.");
            return;
        }
        
        const formData = new FormData();
        formData.append("resume", resumeFile);
        formData.append("job_description", jobDescription);
        
        document.getElementById("loadingSpinner").style.display = "block";
        document.getElementById("result").style.display = "none";
        
        fetch("http://127.0.0.1:8000/api/resume/", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("loadingSpinner").style.display = "none";
            if (data.status) {
                document.getElementById("message").textContent = data.message;
                const rankScore = document.getElementById("rankScore");
                if (data.data.rank >= 80) {
                    rankScore.textContent = `${data.data.rank}% - Great match!`;
                } else if (data.data.rank >= 50) {
                    rankScore.textContent = `${data.data.rank}% - Good match!`;
                } else {
                    rankScore.textContent = `${data.data.rank}% - Needs improvement.`;
                }
                document.getElementById("rankProgress").style.width = `${data.data.rank}%`;
                document.getElementById("experience").textContent = `${data.data.total_experience || 0} years`;

                // Display skills as tags
                const skillsContainer = document.getElementById("skills");
                skillsContainer.innerHTML = data.data.skills.length > 0
                    ? data.data.skills.map(skill => `<div class="tag">${skill}</div>`).join("")
                    : '<div class="empty-state">No skills found.</div>';

                // Display project categories as tags
                const projectsContainer = document.getElementById("projects");
                projectsContainer.innerHTML = data.data.project_category.length > 0
                    ? data.data.project_category.map(category => `<div class="tag">${category}</div>`).join("")
                    : '<div class="empty-state">No project categories found.</div>';

                document.getElementById("result").style.display = "block";

                // Confetti for high rank
                if (data.data.rank > 90) {
                    confetti({
                        particleCount: 100,
                        spread: 70,
                        origin: { y: 0.6 },
                    });
                }
            } else {
                alert("Error analyzing resume.");
            }
        })
        .catch(error => {
            console.error("Error analyzing resume:", error);
            document.getElementById("loadingSpinner").style.display = "none";
            alert("An error occurred while analyzing the resume.");
        });
    });

    // Clear Analysis
    document.getElementById("clearButton").addEventListener("click", function () {
        document.getElementById("resumeForm").reset();
        document.getElementById("result").style.display = "none";
        document.getElementById("rankScore").textContent = "";
        document.getElementById("rankProgress").style.width = "0";
        document.getElementById("experience").textContent = "0 years";
        document.getElementById("skills").innerHTML = '<div class="empty-state">No skills found.</div>';
        document.getElementById("projects").innerHTML = '<div class="empty-state">No project categories found.</div>';
        document.getElementById("filePreview").textContent = "";
    });
});