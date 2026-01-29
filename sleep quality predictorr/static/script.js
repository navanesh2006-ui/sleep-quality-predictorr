document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('predictionForm');
    const resetBtn = document.getElementById('resetBtn');
    const stressSlider = document.getElementById('stress_level');
    const stressVal = document.getElementById('stress_val');
    const resultSection = document.getElementById('resultSection');
    const resultIcon = document.getElementById('resultIcon');
    const tipsContainer = document.getElementById('tipsContainer');
    const tipsList = document.getElementById('tipsList');

    // Live update slider value
    stressSlider.oninput = function() {
        stressVal.innerHTML = this.value;
    }

    resetBtn.addEventListener('click', () => {
        form.reset();
        stressVal.innerHTML = stressSlider.value;
        resetResult();
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // collect data
        const formData = {
            sleep_duration: document.getElementById('sleep_duration').value,
            bedtime: document.getElementById('bedtime').value,
            wake_time: document.getElementById('wake_time').value,
            caffeine: document.getElementById('caffeine').value,
            exercise_duration: document.getElementById('exercise_duration').value,
            screen_time: document.getElementById('screen_time').value,
            stress_level: document.getElementById('stress_level').value,
            mood: document.getElementById('mood').value,
            interruptions: document.getElementById('interruptions').value
        };

        // UI indicate loading
        resultSection.style.opacity = '1';
        resultSection.style.cursor = 'default';
        resultSection.innerHTML = `
            <div class="animate-spin h-10 w-10 border-4 border-blue-500 rounded-full border-t-transparent mx-auto mb-4"></div>
            <p class="text-blue-300 font-semibold">Analyzing sleep patterns...</p>
        `;

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                displayResult(data.quality, data.tips);
            } else {
                throw new Error(data.error || 'Prediction failed');
            }
        } catch (error) {
            resultSection.innerHTML = `<p class="text-red-400">Error: ${error.message}</p>`;
        }
    });

    function displayResult(quality, tips) {
        let colorClass = '';
        let icon = '';
        
        switch(quality) {
            case 'Good':
                colorClass = 'result-good';
                icon = '🌟';
                break;
            case 'Average':
                colorClass = 'result-average';
                icon = '😐';
                break;
            case 'Poor':
                colorClass = 'result-poor';
                icon = '⚠️';
                break;
        }

        // Re-construct the result section structure
        resultSection.innerHTML = `
            <div class="fade-in">
                <div class="w-24 h-24 bg-gray-700/50 rounded-full flex items-center justify-center mb-6 text-4xl shadow-inner mx-auto">
                    ${icon}
                </div>
                <h3 class="text-gray-300 text-lg mb-1">Predicted Quality</h3>
                <h2 class="text-4xl font-bold mb-6 ${colorClass}">${quality}</h2>
                
                <div class="text-left bg-gray-800/50 p-4 rounded-xl w-full border border-gray-700">
                    <h4 class="text-sm font-semibold text-purple-300 mb-2">💡 Tips for Improvement:</h4>
                    <ul class="text-sm text-gray-300 space-y-2 list-disc pl-4">
                        ${tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    function resetResult() {
        resultSection.style.opacity = '0.7';
        resultSection.style.cursor = 'not-allowed';
        resultSection.innerHTML = `
            <div class="w-24 h-24 bg-gray-700/50 rounded-full flex items-center justify-center mb-6 text-4xl shadow-inner">
                💤
            </div>
            <h3 class="text-2xl font-bold mb-2">Prediction Awaited...</h3>
            <p class="text-gray-400 mb-6">Enter your daily habits and click predict to see your result.</p>
        `;
    }
});
