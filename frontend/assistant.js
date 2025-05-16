document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const uploadBox = document.getElementById('uploadBox');
    const fileInput = document.getElementById('fileInput');
    const uploadedFile = document.getElementById('uploadedFile');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFile = document.getElementById('removeFile');
    const noResumeMessage = document.getElementById('noResumeMessage');
    const resumeUploadedContent = document.getElementById('resumeUploadedContent');
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const starterQuestions = document.querySelectorAll('.starter-question');
    
    let currentResumeId = null;
    let isProcessing = false;

    // Event Listeners
    uploadBox.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileUpload);
    removeFile.addEventListener('click', handleRemoveFile);
    sendButton.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendMessage();
    });
    
    starterQuestions.forEach(question => {
        question.addEventListener('click', function() {
            const questionText = this.getAttribute('data-question');
            askQuestion(questionText);
        });
    });

    // Functions
    function handleFileUpload(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            const fileSizeMB = (file.size / (1024*1024)).toFixed(1);
            
            // Display file info
            fileName.textContent = file.name;
            fileSize.textContent = `${fileSizeMB} MB`;
            uploadBox.style.display = 'none';
            uploadedFile.style.display = 'flex';
            noResumeMessage.style.display = 'none';
            resumeUploadedContent.style.display = 'block';
            
            // Upload to server
            uploadResume(file);
        }
    }

    function handleRemoveFile(e) {
        e.stopPropagation();
        fileInput.value = '';
        uploadBox.style.display = 'block';
        uploadedFile.style.display = 'none';
        noResumeMessage.style.display = 'flex';
        resumeUploadedContent.style.display = 'none';
        userInput.disabled = true;
        sendButton.disabled = true;
        currentResumeId = null;
        addMessage('ai', 'Your resume has been removed. Upload a new resume to continue.');
    }

    async function uploadResume(file) {
        const formData = new FormData();
        formData.append('resume', file);
        
        try {
            const response = await fetch('http://127.0.0.1:8000/api/assistant/', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status) {
                currentResumeId = data.data.resume_id;
                userInput.disabled = false;
                sendButton.disabled = false;
                addMessage('ai', data.data.message);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Upload error:', error);
            addMessage('ai', 'Error uploading resume. Please try again.');
            handleRemoveFile({ stopPropagation: () => {} });
        }
    }

    async function handleSendMessage() {
        const message = userInput.value.trim();
        if (!message || isProcessing) return;
        
        askQuestion(message);
        userInput.value = '';
    }

    async function askQuestion(question) {
        if (!currentResumeId || isProcessing) return;
        
        isProcessing = true;
        addMessage('user', question);
        
        try {
            const response = await fetch('http://127.0.0.1:8000/api/assistant/', {
                method: 'POST',
            //     headers: {
            //     'Content-Type': 'application/json',
            //     'X-CSRFToken': getCookie('csrftoken'),
            // },
               headers: {
        'Content-Type': 'application/json',
        // 'X-CSRFToken': getCookie('csrftoken'), // Uncomment if CSRF protection is enabled
    },
                body: JSON.stringify({
                    message: question,
                    resume_id: currentResumeId
                })
            });
            
            const data = await response.json();
            
            if (data.status) {
                addMessage('ai', data.data.response);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Chat error:', error);
            addMessage('ai', 'Sorry, I encountered an error. Please try again.');
        } finally {
            isProcessing = false;
        }
    }

    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.innerHTML = `<p>${text}</p>`;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}