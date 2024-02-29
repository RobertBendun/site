document.addEventListener('DOMContentLoaded', () => {
	const prefers_reduced_motion = window.matchMedia('(prefers-reduced-motion: reduce)') === true
															|| window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	if (prefers_reduced_motion) {
		return;
	}

	const letters = 'z'.charCodeAt(0) - 'a'.charCodeAt(0);
	function random_letter() {
		const random = Math.floor(letters * 2 * Math.random());
		const letter = String.fromCharCode((random < letters ? 'a'.charCodeAt(0) : 'A'.charCodeAt(0)) + (random % letters));
		return letter;
	}

	for (const element of document.getElementsByClassName('hover-scramble')) {
		element.addEventListener('mouseenter', () => {
			let i = 0;
			let offset = Math.floor(Math.random() * element.dataset.text.length);

			const interval = setInterval(() => {
				if (i > element.dataset.text.length) {
					clearInterval(interval);
					return;
				}

				let current_text = "";
				for (let j = 0; j < element.dataset.text.length; ++j) {
					if (i > (offset+j)%element.dataset.text.length) {
						current_text += element.dataset.text[j];
					} else {
						current_text += random_letter();
					}
				}

				++i;
				element.textContent = current_text;
			}, 30);
		});
	}
});
