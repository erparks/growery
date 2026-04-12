/**
 * Variable microcopy with optional time-of-day flavor.
 * Phase ranges align with hub/view/src/lib/sunTheme.js (sky gradient buckets).
 *
 * Phases (local time, fractional hours):
 * - night:    22:00–04:00
 * - predawn:  04:00–06:00  (pre-dawn transition in sunTheme)
 * - dawn:     06:00–08:00
 * - day:      08:00–16:00
 * - dusk:     16:00–19:30
 * - late:     19:30–22:00  (late dusk → night in sunTheme)
 */

/** @typedef {'night'|'predawn'|'dawn'|'day'|'dusk'|'late'} DayPhase */

/**
 * @param {Date} date
 * @returns {DayPhase}
 */
export function getDayPhase(date) {
	const h = date.getHours() + date.getMinutes() / 60 + date.getSeconds() / 3600;
	if (h >= 22 || h < 4) return 'night';
	if (h < 6) return 'predawn';
	if (h < 8) return 'dawn';
	if (h < 16) return 'day';
	if (h < 19.5) return 'dusk';
	if (h < 22) return 'late';
	return 'night';
}

/**
 * @template T
 * @param {T[]} arr
 * @returns {T}
 */
export function pickRandom(arr) {
	if (!arr.length) throw new Error('pickRandom: empty array');
	return arr[Math.floor(Math.random() * arr.length)];
}

/**
 * @param {Partial<Record<DayPhase, string[]>> & { neutral?: string[] }} pools
 * @param {DayPhase} phase
 * @returns {string}
 */
export function pickFromPools(pools, phase) {
	const phaseList = pools[phase];
	if (phaseList && phaseList.length) return pickRandom(phaseList);
	const neutral = pools.neutral;
	if (neutral && neutral.length) return pickRandom(neutral);
	const first = Object.values(pools).find((v) => Array.isArray(v) && v.length);
	if (first && first.length) return pickRandom(first);
	return '';
}

const HOME_TAGLINE = {
	night: [
		'The greenhouse is quiet. Your plants are still here.',
		'Night outside—warmth in here.',
		'City lights out there; leaves in here.'
	],
	predawn: [
		'Almost light. Worth a look at the bench.',
		'The glass is still cool; morning comes soon.'
	],
	dawn: [
		'First light on the glass.',
		'Morning in the greenhouse.',
		'The day opens slowly—like a new leaf.'
	],
	day: [
		'Your plants, in order.',
		'Still air and steady growth.',
		'Light through the panes, leaves below.'
	],
	dusk: [
		'Gold on the glass—good time to look.',
		'Evening settling in the house.',
		'Sun going down; the bench still glows.'
	],
	late: [
		'Late—only the grow-lights and you.',
		'Almost night. One more check?',
		'The room cools; the leaves don’t mind.'
	],
	neutral: [
		'Your plants, in order.',
		'A quiet bench, well kept.',
		'Growery—nothing fancy, just growth.'
	]
};

const TIMELINE_TITLE = {
	night: ['Moments (night)', 'Photos & notes', 'The log'],
	predawn: ['Moments', 'Images & notes', 'Growth log'],
	dawn: ['Moments', 'Images & notes', 'What happened'],
	day: ['Images & notes', 'Moments', 'The timeline'],
	dusk: ['Images & notes', 'Moments', 'Light and memory'],
	late: ['Images & notes', 'Moments', 'The day’s record'],
	neutral: ['Images & notes', 'Moments']
};

const TIMELINE_LOADING = {
	night: ['Gathering the timeline…', 'Loading moments…', 'Pulling up the log…'],
	predawn: ['Gathering the timeline…', 'Almost there…'],
	dawn: ['Gathering the timeline…', 'Loading your moments…'],
	day: ['Loading timeline…', 'Gathering moments…'],
	dusk: ['Loading the day’s story…', 'Gathering moments…'],
	late: ['Loading timeline…', 'Almost there…'],
	neutral: ['Loading timeline…', 'Gathering moments…']
};

const TIMELINE_EMPTY = {
	night: [
		'Nothing here yet—add a photo when the light feels right.',
		'Empty bench in the log. A photo would warm it up.',
		'No moments yet. Night’s a fine time to start.'
	],
	predawn: [
		'Nothing here yet—dawn’s a good time for a first picture.',
		'The log is waiting. One photo opens the story.'
	],
	dawn: [
		'Nothing here yet—morning light loves a first photo.',
		'Start with a picture; the timeline grows from there.'
	],
	day: [
		'Nothing here yet—add a photo when you’re ready.',
		'No images or notes yet. Your first moment goes here.',
		'An empty log. Fill it leaf by leaf.'
	],
	dusk: [
		'Nothing here yet—golden hour’s kind to plants.',
		'The timeline’s empty. Evening’s a good time to begin.'
	],
	late: [
		'Nothing here yet—still time tonight for a first shot.',
		'The log is empty. One photo is enough to start.'
	],
	neutral: [
		'No images or notes yet for this plant.',
		'Nothing here yet—add a photo or a note.',
		'Start the story with a photo or a line.'
	]
};

/** Short labels (2–3 words) for the timeline header buttons */
const TIMELINE_UPLOAD_LABEL = {
	neutral: ['Upload', 'Add photos', 'Images'],
	day: ['Upload', 'Add photos'],
	dusk: ['Upload', 'Golden hour'],
	late: ['Upload', 'One more shot'],
	night: ['Upload', 'Add photos']
};

const TIMELINE_ADD_NOTE_LABEL = {
	neutral: ['Add note', 'Note', 'Journal'],
	day: ['Add note', 'Note'],
	dawn: ['Note', 'Morning note'],
	night: ['Add note', 'Note']
};

const FAB_ARIA = {
	night: ['Add a new plant', 'Bring another plant to the bench', 'Start a new plant'],
	predawn: ['Add a new plant', 'Add another to the collection'],
	dawn: ['Add a new plant', 'New plant—morning', 'Add a plant'],
	day: ['Add a new plant', 'Add another plant', 'New plant'],
	dusk: ['Add a new plant', 'Add a plant before dark'],
	late: ['Add a new plant', 'One more plant for the night'],
	neutral: ['Add a new plant']
};

const ADD_PLANT_SUB = {
	neutral: [
		'Name it, then watch it grow.',
		'A nickname and a species—that’s enough to begin.',
		'Every bench starts with one pot.',
		'Give it a name; the rest comes with time.'
	],
	day: ['Name it, then watch it grow.', 'Daylight’s good for a new label.'],
	dawn: ['Name it—morning’s a fine time to begin.'],
	dusk: ['Name it before the light fades.', 'Evening’s fine for a new arrival.']
};

const ADD_NOTE_SUB = {
	night: [
		'Night notes stick—say what you noticed.',
		'Quiet hour; good for a line about {nickname}.',
		'The glass is dark; your words still land.'
	],
	predawn: ['Early—jot what you’ll forget by breakfast.', 'A line for {nickname} before the day runs away.'],
	dawn: ['Morning light, fresh words for {nickname}.', 'Say what changed overnight.'],
	day: ['What did you notice today?', 'A note for {nickname}—short is fine.'],
	dusk: ['Evening check-in for {nickname}.', 'Golden hour—worth a sentence.'],
	late: ['Still time to note something about {nickname}.', 'Before bed—a line for the log.'],
	neutral: ['What changed? What did you do?', 'A few words for the record.', 'Notes keep the story honest.']
};

const PLANT_LOADING = {
	night: ['Opening the bench…', 'Finding your plant…', 'Loading…'],
	predawn: ['Almost there…', 'Gathering your plant…'],
	dawn: ['Good morning—loading…', 'Opening the bench…'],
	day: ['Loading plant…', 'One moment…'],
	dusk: ['Loading…', 'Gathering details…'],
	late: ['Loading…', 'Almost there…'],
	neutral: ['Loading plant data…', 'One moment…']
};

/**
 * @param {string} key
 * @param {Date} [date]
 * @param {{ nickname?: string }} [ctx]
 * @returns {string}
 */
export function pickMicrocopy(key, date = new Date(), ctx = {}) {
	const phase = getDayPhase(date);
	switch (key) {
		case 'homeTagline':
			return pickFromPools(HOME_TAGLINE, phase);
		case 'timelineSectionTitle':
			return pickFromPools(TIMELINE_TITLE, phase);
		case 'timelineLoading':
			return pickFromPools(TIMELINE_LOADING, phase);
		case 'timelineEmpty':
			return pickFromPools(TIMELINE_EMPTY, phase);
		case 'timelineUploadLabel':
			return pickFromPools(TIMELINE_UPLOAD_LABEL, phase);
		case 'timelineAddNoteLabel':
			return pickFromPools(TIMELINE_ADD_NOTE_LABEL, phase);
		case 'fabAria':
			return pickFromPools(FAB_ARIA, phase);
		case 'addPlantSubtitle':
			return pickFromPools(ADD_PLANT_SUB, phase);
		case 'addNoteSubtitle': {
			const raw = pickFromPools(ADD_NOTE_SUB, phase);
			const nick = ctx.nickname?.trim() || 'this plant';
			return raw.replace(/\{nickname\}/g, nick);
		}
		case 'plantLoading':
			return pickFromPools(PLANT_LOADING, phase);
		default:
			return '';
	}
}
