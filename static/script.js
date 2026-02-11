let currentQuestion = null;

async function fetchQuestion() {
    const domain = document.getElementById('domain-select').value;
    const loader = document.getElementById('loading');
    const card = document.getElementById('question-card');
    
    // UI Reset
    card.classList.add('hidden');
    loader.classList.remove('hidden');
    document.getElementById('result-area').classList.add('hidden');
    
    try {
        const response = await fetch('/generate_question', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ domain: domain })
        });
        
        const data = await response.json();
        
        if(data.error) throw new Error(data.error);
        
        currentQuestion = data;
        renderQuestion(data);
        
    } catch (error) {
        alert("System Error: " + error.message);
    } finally {
        loader.classList.add('hidden');
        card.classList.remove('hidden');
    }
}

function renderQuestion(data) {
    document.getElementById('q-text').textContent = data.question;
    const container = document.getElementById('options-container');
    container.innerHTML = '';
    
    data.options.forEach((opt, index) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        // Check if options are objects or strings, handling mostly string list
        btn.textContent = opt; 
        btn.onclick = () => checkAnswer(index, btn);
        container.appendChild(btn);
    });
}

function checkAnswer(selectedIndex, btnElement) {
    const options = ['A', 'B', 'C', 'D'];
    const selectedLetter = options[selectedIndex];
    const correctLetter = currentQuestion.correct_answer;
    
    const allBtns = document.querySelectorAll('.option-btn');
    allBtns.forEach(b => b.disabled = true); // Lock answers
    
    const resultArea = document.getElementById('result-area');
    const verdict = document.getElementById('verdict');
    const explanation = document.getElementById('explanation');
    
    resultArea.classList.remove('hidden');
    explanation.textContent = "Analysis: " + currentQuestion.explanation;
    
    if (selectedLetter === correctLetter) {
        btnElement.classList.add('correct');
        verdict.textContent = "ACCESS GRANTED // CORRECT";
        verdict.style.color = "var(--success)";
    } else {
        btnElement.classList.add('wrong');
        verdict.textContent = "ACCESS DENIED // INCORRECT";
        verdict.style.color = "var(--danger)";
        
        // Highlight correct answer
        const correctIndex = options.indexOf(correctLetter);
        if(correctIndex !== -1) allBtns[correctIndex].classList.add('correct');
    }
}
