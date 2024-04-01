
function open_details_element_when_hash_matches() {
	if (location.hash) {
		/** @type {HtmlDetailsElement} */
		const details = document.querySelector(`details${location.hash}`);
		if (details) {
			details.open = true;
		}
	}
}

window.addEventListener('hashchange', open_details_element_when_hash_matches);
document.addEventListener('DOMContentLoaded', open_details_element_when_hash_matches);
