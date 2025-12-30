function buildQuery(params = {}) {
	const entries = Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '');
	if (entries.length === 0) return '';
	return `?${new URLSearchParams(entries).toString()}`;
}

async function requestJson(url, options = {}) {
	const response = await fetch(url, options);
	let body = null;
	try {
		body = await response.json();
	} catch {
		body = null;
	}

	if (!response.ok) {
		const message =
			(body && (body.error || body.message)) || `Request failed (${response.status})`;
		throw new Error(message);
	}
	return body;
}

export const NoteService = {
	/**
	 * Fetch mixed timeline items for a plant (photos + notes).
	 */
	getTimeline(plantId, { createdFrom, createdTo } = {}) {
		return requestJson(
			`/api/plants/${plantId}/timeline${buildQuery({
				created_from: createdFrom,
				created_to: createdTo
			})}`
		);
	},

	listNotes(plantId, { createdFrom, createdTo, dueFrom, dueTo } = {}) {
		return requestJson(
			`/api/plants/${plantId}/notes${buildQuery({
				created_from: createdFrom,
				created_to: createdTo,
				due_from: dueFrom,
				due_to: dueTo
			})}`
		);
	},

	listAllNotes({ plantId, createdFrom, createdTo, dueFrom, dueTo } = {}) {
		return requestJson(
			`/api/notes${buildQuery({
				plant_id: plantId,
				created_from: createdFrom,
				created_to: createdTo,
				due_from: dueFrom,
				due_to: dueTo
			})}`
		);
	},

	createNote(plantId, { content, dueDate, photoHistoryId } = {}) {
		return requestJson(`/api/plants/${plantId}/notes`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				content,
				due_date: dueDate,
				photo_history_id: photoHistoryId
			})
		});
	},

	createNoteWithImage(
		plantId,
		{ content, dueDate, photoHistoryId, imageFile, imageDate } = {}
	) {
		const formData = new FormData();
		formData.append('content', content ?? '');
		if (dueDate) formData.append('due_date', dueDate);
		if (photoHistoryId !== undefined && photoHistoryId !== null) {
			formData.append('photo_history_id', String(photoHistoryId));
		}
		if (imageDate) formData.append('image_date', imageDate);
		if (imageFile) formData.append('image', imageFile);

		return requestJson(`/api/plants/${plantId}/notes`, {
			method: 'POST',
			body: formData
		});
	},

	updateNote(plantId, noteId, { content, dueDate, clearDueDate, photoHistoryId, clearPhoto } = {}) {
		return requestJson(`/api/plants/${plantId}/notes/${noteId}`, {
			method: 'PATCH',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				content,
				due_date: dueDate,
				clear_due_date: clearDueDate,
				photo_history_id: photoHistoryId,
				clear_photo: clearPhoto
			})
		});
	},

	deleteNote(plantId, noteId) {
		return requestJson(`/api/plants/${plantId}/notes/${noteId}`, {
			method: 'DELETE'
		});
	}
};


