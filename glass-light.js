document.addEventListener('DOMContentLoaded', () => {
	const prefers_reduced_motion = window.matchMedia('(prefers-reduced-motion: reduce)') === true
															|| window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	if (prefers_reduced_motion) {
		return;
	}

	for (const el of document.getElementsByClassName("glass")) {
		const element = el;
		element.addEventListener('mousemove', (e) => {
			const rect = element.getBoundingClientRect();
			const x = e.clientX - rect.left;
			const y = e.clientY - rect.top;

			element.style.setProperty("--mouse-x", `${x}px`);
			element.style.setProperty("--mouse-y", `${y}px`);
		});
	}
});
