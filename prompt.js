document.addEventListener('DOMContentLoaded', () => {
	const prompt = document.querySelector('nav.prompt div[contenteditable]');
	prompt.addEventListener('keydown', (e) => {
		if (e.code === "Enter") {
			e.preventDefault();
			alert("Not implemented yet! Your prompt: " + prompt.textContent);
		}
	});
});
