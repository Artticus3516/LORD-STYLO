 const toggleLoading = (button, isLoading, originalText = 'Process') => {
        const buttonTextSpan = button.querySelector('.button-text');
        const loadingSpinnerDiv = button.querySelector('.loading-spinner');

        if (isLoading) {
            buttonTextSpan.style.display = 'none';
            loadingSpinnerDiv.style.display = 'block';
            if (!loadingSpinnerDiv.querySelector('svg')) {
                 loadingSpinnerDiv.innerHTML = `<svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                     <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                     <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                 </svg>`;
            }
            buttonTextSpan.innerText = 'Loading...';
        } else {
            buttonTextSpan.style.display = 'block';
            loadingSpinnerDiv.style.display = 'none';
            buttonTextSpan.innerText = originalText;
        }
    };

    async function sendDataToBackend(button, actionType, modalKeyword = '') {
        const studyMaterial = document.getElementById('studyMaterialText').value;
        const concept = document.getElementById('conceptInput').value;
        const subject = document.getElementById('subjectSelect').value;
        const sclass = document.getElementById('classSelect').value;

        const responseContainerDiv = document.getElementById('genresp');
        const responseTextDiv = document.getElementById('responseText');
        const flashcardContainerDiv = document.getElementById('flashcardContainer');
        const errorMessageDiv = document.getElementById('errorMessage');
        const errorTextP = document.getElementById('errorText');
        const responseTitle = document.getElementById('responseTitle');

        responseTextDiv.innerHTML = '';
        flashcardContainerDiv.innerHTML = '';
        responseContainerDiv.classList.add('hidden');
        errorMessageDiv.classList.add('hidden');
        errorTextP.innerText = '';

        if (!studyMaterial.trim() && !concept.trim() && !modalKeyword.trim()) {
            document.getElementById('keywordModalOverlay').classList.remove('hidden');
            return;
        }

        toggleLoading(button, true, button.dataset.originalText);

        try {
            const response = await fetch('https://lord-stylo-by-artticus.onrender.com/api/process', {
                method: "POST",
                headers: {
                    'Content-Type': "application/json"
                },
                body: JSON.stringify({
                    'action_type': actionType,
                    'study_material': studyMaterial,
                    'concept': concept,
                    'subject': subject,
                    'class': sclass,
                    'modal_keyword': modalKeyword
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error("Backend error:", errorData);
                errorMessageDiv.classList.remove('hidden');
                errorTextP.innerText = errorData.error || `Failed to process request (Status: ${response.status}).`;
                return;
            }

            const data = await response.json();
            console.log("Full response data from backend:", data);


            responseContainerDiv.classList.remove('hidden');
            document.getElementById('downloadPdfButton').classList.remove('hidden');

            if (actionType === 'flashcards' && data.flashcards && Array.isArray(data.flashcards)) {
                responseTitle.innerText = 'Flashcards:';
                flashcardContainerDiv.innerHTML = '';
                data.flashcards.forEach(card => {
                    const cardElement = document.createElement('div');
                    cardElement.className = 'bg-slate-600 p-4 rounded-lg border border-slate-500 shadow-md mb-4';
                    cardElement.innerHTML = `
                        <h3 class="text-xl font-semibold text-blue-300 mb-2">Q: ${marked.parse(card.question || '')}</h3>
                        <p class="text-slate-200 mt-2">A: ${marked.parse(card.answer || '')}</p>
                    `;
                    flashcardContainerDiv.appendChild(cardElement);
                });
                responseTextDiv.style.display = 'none';
                flashcardContainerDiv.style.display = 'grid';
            } else if (data.explanation) {
                responseTitle.innerText = button.dataset.originalText || 'AI Output:';
                responseTextDiv.innerHTML = marked.parse(data.explanation);
                responseTextDiv.style.display = 'block';
                flashcardContainerDiv.style.display = 'none';
            } else {
                responseTitle.innerText = 'AI Output:';
                responseTextDiv.innerHTML = marked.parse(JSON.stringify(data, null, 2));
                responseTextDiv.style.display = 'block';
                flashcardContainerDiv.style.display = 'none';
            }

        }
        catch (error) {
            console.error("Error during fetch or processing:", error);
            errorMessageDiv.classList.remove('hidden');
            errorTextP.innerText = `An unexpected error occurred: ${error.message}. Please try again.`;
        } finally {
            toggleLoading(button, false, button.dataset.originalText);
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        const actionButtons = document.querySelectorAll('.action-button');
        const studyMaterialTextarea = document.getElementById('studyMaterialText');
        const conceptInput = document.getElementById('conceptInput');
        const keywordInput = document.getElementById('keywordInput');
        const keywordModalOverlay = document.getElementById('keywordModalOverlay');
        const cancelKeywordButton = document.getElementById('cancelKeywordButton');
        const confirmKeywordButton = document.getElementById('confirmKeywordButton');

        let currentActionButton = null;

        actionButtons.forEach(button => {

            button.dataset.originalText = button.querySelector('.button-text').innerText;

            button.addEventListener('click', () => {
                const actionType = button.dataset.action;
                const studyMaterial = studyMaterialTextarea.value.trim();
                const concept = conceptInput.value.trim();

                if (!studyMaterial && !concept) {
                    keywordModalOverlay.classList.remove('hidden');
                    currentActionButton = button;
                } else {
                    sendDataToBackend(button, actionType, '');
                }
            });
        });

        cancelKeywordButton.addEventListener('click', () => {
            keywordModalOverlay.classList.add('hidden');
            if (currentActionButton) {
                toggleLoading(currentActionButton, false, currentActionButton.dataset.originalText);
                currentActionButton = null;
            }
        });

        confirmKeywordButton.addEventListener('click', () => {
            const modalKeyword = keywordInput.value.trim();
            if (!modalKeyword) {
                alert('Please enter a keyword or cancel.');
                return;
            }
            keywordModalOverlay.classList.add('hidden');
            if (currentActionButton) {
                sendDataToBackend(currentActionButton, currentActionButton.dataset.action, modalKeyword);
                currentActionButton = null;
            }
        });

        const fileInput = document.getElementById('fileInput');
        const loadFileButton = document.getElementById('loadFileButton');
        const urlInput = document.getElementById('urlInput');
        const loadUrlButton = document.getElementById('loadUrlButton');
        const fileWarning = document.getElementById('fileWarning');
        const urlWarning = document.getElementById('urlWarning');

        fileInput.addEventListener('change', () => {
            const file = fileInput.files[0];
            if (file && file.type === 'application/pdf') {
                fileWarning.classList.remove('hidden');
            } else {
                fileWarning.classList.add('hidden');
            }
        });
        urlInput.addEventListener('input', () => {
            if (urlInput.value.trim() !== '') {
                urlWarning.classList.remove('hidden');
            } else {
                urlWarning.classList.add('hidden');
            }
        });


        loadFileButton.addEventListener('click', () => {
            const file = fileInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (file.type === 'text/plain') {
                        studyMaterialTextarea.value = e.target.result;
                    } else if (file.type === 'application/pdf') {
                        alert("PDF files can't be directly parsed for text here client-side. Please copy-paste text from the PDF into the text area. Only .txt files can be loaded directly.");
                    }
                };
                reader.readAsText(file);
            } else {
                alert("Please select a file to load.");
            }
        });

        loadUrlButton.addEventListener('click', async () => {
            const url = urlInput.value.trim();
            if (!url) {
                alert("Please enter a URL.");
                return;
            }

            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                const text = await response.text();
                studyMaterialTextarea.value = text;
            } catch (error) {
                console.error("Error loading URL:", error);
                alert(`Failed to load content from URL: ${error.message}. This is often due to CORS policy. Please copy-paste the content instead.`);
            }
        });

        const downloadPdfButton = document.getElementById('downloadPdfButton');
        downloadPdfButton.addEventListener('click', () => {
            const element = document.getElementById('genresp');
            if (element.classList.contains('hidden')) {
                alert("Generate some notes first!");
                return;
            }
            html2pdf().from(element).save('Lord_Stylo_Notes.pdf');
        });
    });