/**
 * Relative time only, e.g. "3 days ago" (no calendar date).
 * @param {string | null | undefined} dateString
 * @returns {string}
 */
export function formatTimeAgo(dateString) {
	if (!dateString) return 'N/A';
	const date = new Date(dateString);
	if (Number.isNaN(date.getTime())) return 'N/A';
	const now = new Date();
	const seconds = Math.floor((now - date) / 1000);

	const timeAgo = (() => {
		const units = [
			{ label: 'week', secs: 60 * 60 * 24 * 7 },
			{ label: 'day', secs: 60 * 60 * 24 },
			{ label: 'hour', secs: 60 * 60 },
			{ label: 'minute', secs: 60 }
		];
		for (const { label, secs } of units) {
			const value = Math.floor(seconds / secs);
			if (value >= 1) {
				return `${value} ${label}${value > 1 ? 's' : ''} ago`;
			}
		}
		return 'just now';
	})();

	return timeAgo;
}
