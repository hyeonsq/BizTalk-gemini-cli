document.addEventListener('DOMContentLoaded', () => {
    const inputText = document.getElementById('inputText');
    const targetAudience = document.getElementById('targetAudience');
    const convertButton = document.getElementById('convertButton');
    const outputText = document.getElementById('outputText');
    const copyButton = document.getElementById('copyButton');
    const currentCharCount = document.getElementById('currentCharCount');

    const MAX_CHAR_COUNT = 500;
    const API_ENDPOINT = '/api/convert'; // This will be handled by Flask

    // --- Character Counter ---
    inputText.addEventListener('input', () => {
        const currentLength = inputText.value.length;
        currentCharCount.textContent = currentLength;
        if (currentLength > MAX_CHAR_COUNT) {
            inputText.value = inputText.value.substring(0, MAX_CHAR_COUNT);
            currentCharCount.textContent = MAX_CHAR_COUNT;
            // Optionally, provide visual feedback for exceeding limit
        }
    });

    // --- Convert Button Logic ---
    convertButton.addEventListener('click', async () => {
        const textToConvert = inputText.value;
        const audience = targetAudience.value;

        if (!textToConvert.trim()) {
            alert('변환할 내용을 입력해주세요.');
            return;
        }

        convertButton.disabled = true;
        convertButton.textContent = '변환 중...';
        outputText.value = '변환 중입니다...';

        try {
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: textToConvert, audience: audience }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'API 호출 중 오류 발생');
            }

            const data = await response.json();
            outputText.value = data.converted_text;
        } catch (error) {
            console.error('Error during conversion:', error);
            outputText.value = `오류가 발생했습니다: ${error.message}. 잠시 후 다시 시도해주세요.`;
            // FR-05: Display clear error message and potentially a retry button (future enhancement)
        } finally {
            convertButton.disabled = false;
            convertButton.textContent = '변환하기';
        }
    });

    // --- Copy Button Logic ---
    copyButton.addEventListener('click', () => {
        if (outputText.value) {
            navigator.clipboard.writeText(outputText.value).then(() => {
                alert('변환된 텍스트가 복사되었습니다!'); // FR-03: Visual feedback
            }).catch(err => {
                console.error('Failed to copy text: ', err);
                alert('텍스트 복사에 실패했습니다.');
            });
        } else {
            alert('복사할 내용이 없습니다.');
        }
    });

    // Initialize character count on load in case there's pre-filled text
    inputText.dispatchEvent(new Event('input'));
});