/**
 * Local-time sky gradient + directional shadows (sunrise → sunset arc).
 * Not astronomical precision — tuned for a pleasant greenhouse feel.
 */

function lerp(a, b, t) {
	return a + (b - a) * t;
}

function hexToRgb(hex) {
	const n = hex.replace('#', '');
	return {
		r: parseInt(n.slice(0, 2), 16),
		g: parseInt(n.slice(2, 4), 16),
		b: parseInt(n.slice(4, 6), 16)
	};
}

function lerpColor(hexA, hexB, t) {
	const A = hexToRgb(hexA);
	const B = hexToRgb(hexB);
	const r = Math.round(lerp(A.r, B.r, t));
	const g = Math.round(lerp(A.g, B.g, t));
	const b = Math.round(lerp(A.b, B.b, t));
	return `rgb(${r},${g},${b})`;
}

/** @param {number} h Hour 0–24 with fractional minutes */
function buildSkyGradient(h) {
	// Key palette stops (top → mid → bottom), 168deg matches static CSS
	const nightTop = '#1a2622';
	const nightMid = '#121a17';
	const nightBot = '#0f1613';

	const dawnTop = '#3d4e58';
	const dawnMid = '#2a4a3c';
	const dawnBot = '#e8a078';

	const dayTop = '#2a3834';
	const dayMid = '#1a2622';
	const dayBot = '#141f1c';

	const duskTop = '#2a3550';
	const duskMid = '#4a3545';
	const duskBot = '#d88868';

	// Pre-dawn 4–6: night → dawn
	if (h >= 4 && h < 6) {
		const u = (h - 4) / 2;
		return `linear-gradient(168deg, ${lerpColor(nightTop, dawnTop, u)} 0%, ${lerpColor(nightMid, dawnMid, u)} 44%, ${lerpColor(nightBot, dawnBot, u)} 100%)`;
	}
	// Dawn 6–8: full warm horizon
	if (h >= 6 && h < 8) {
		const u = (h - 6) / 2;
		return `linear-gradient(168deg, ${lerpColor(dawnTop, dayTop, u)} 0%, ${lerpColor(dawnMid, dayMid, u)} 44%, ${lerpColor(dawnBot, lerpColor(dawnBot, dayBot, 0.35), u)} 100%)`;
	}
	// Day 8–16
	if (h >= 8 && h < 16) {
		return `linear-gradient(168deg, ${dayTop} 0%, ${dayMid} 44%, ${dayBot} 100%)`;
	}
	// Dusk 16–19.5: day → sunset
	if (h >= 16 && h < 19.5) {
		const u = (h - 16) / 3.5;
		return `linear-gradient(168deg, ${lerpColor(dayTop, duskTop, u)} 0%, ${lerpColor(dayMid, duskMid, u)} 44%, ${lerpColor(dayBot, duskBot, u)} 100%)`;
	}
	// Late dusk → night 19.5–22
	if (h >= 19.5 && h < 22) {
		const u = (h - 19.5) / 2.5;
		return `linear-gradient(168deg, ${lerpColor(duskTop, nightTop, u)} 0%, ${lerpColor(duskMid, nightMid, u)} 44%, ${lerpColor(duskBot, nightBot, u)} 100%)`;
	}
	// Night 22–4 (wrap)
	return `linear-gradient(168deg, ${nightTop} 0%, ${nightMid} 44%, ${nightBot} 100%)`;
}

/**
 * Sun arc 6:00–18:00: east → overhead → west. Shadow opposite light.
 * @param {number} h
 */
function shadowFromHour(h) {
	if (h >= 6 && h <= 18) {
		const t = ((h - 6) / 12) * Math.PI;
		const x = 16 * Math.cos(t);
		const y = 4 + 11 * (1 - Math.sin(t));
		const lowSun = Math.abs(Math.cos(t));
		/* Tighter blur + higher alpha = darker, sharper cast (sun direction reads more clearly) */
		const blur = 9 + 7 * lowSun;
		const blurLg = 22 + 11 * lowSun;
		const alpha = 0.34 + 0.14 * lowSun;
		const alphaLg = 0.42 + 0.14 * lowSun;
		return { x, y, blur, blurLg, alpha, alphaLg };
	}
	if (h > 18 && h < 22) {
		const u = (h - 18) / 4;
		const day = shadowFromHour(18);
		return {
			x: lerp(day.x, 0, u),
			y: lerp(day.y, 5, u),
			blur: lerp(day.blur, 14, u),
			blurLg: lerp(day.blurLg, 30, u),
			alpha: lerp(day.alpha, 0.34, u),
			alphaLg: lerp(day.alphaLg, 0.4, u)
		};
	}
	if (h >= 4 && h < 6) {
		const u = (h - 4) / 2;
		const dawn = shadowFromHour(6);
		return {
			x: lerp(0, dawn.x, u),
			y: lerp(5, dawn.y, u),
			blur: lerp(14, dawn.blur, u),
			blurLg: lerp(30, dawn.blurLg, u),
			alpha: lerp(0.34, dawn.alpha, u),
			alphaLg: lerp(0.4, dawn.alphaLg, u)
		};
	}
	// default night
	return { x: 0, y: 5, blur: 14, blurLg: 30, alpha: 0.34, alphaLg: 0.4 };
}

/**
 * @param {Date} date
 */
export function computeSunTheme(date) {
	const h = date.getHours() + date.getMinutes() / 60 + date.getSeconds() / 3600;
	const gradient = buildSkyGradient(h);
	const s = shadowFromHour(h);
	const softX = s.x * 1.2;
	const softY = s.y * 2.2;
	/* Crisp inner layer (harder edge) + softer outer layer — reads more like a real cast shadow */
	const crispBlur = Math.max(2, s.blur * 0.28);
	const crispAlpha = Math.min(0.62, s.alpha * 1.35 + 0.08);
	const softCrispBlur = Math.max(4, s.blurLg * 0.22);
	const softCrispAlpha = Math.min(0.55, s.alphaLg * 0.85);
	const shadowCard =
		`${s.x.toFixed(2)}px ${s.y.toFixed(2)}px ${crispBlur.toFixed(1)}px rgba(0, 0, 0, ${crispAlpha.toFixed(3)}), ` +
		`${s.x.toFixed(2)}px ${s.y.toFixed(2)}px ${s.blur.toFixed(1)}px rgba(8, 14, 12, ${s.alpha})`;
	const shadowSoft =
		`${softX.toFixed(2)}px ${softY.toFixed(2)}px ${softCrispBlur.toFixed(1)}px rgba(0, 0, 0, ${softCrispAlpha.toFixed(3)}), ` +
		`${softX.toFixed(2)}px ${softY.toFixed(2)}px ${s.blurLg.toFixed(1)}px rgba(8, 14, 12, ${s.alphaLg})`;
	return { gradient, shadowCard, shadowSoft };
}

/**
 * Apply CSS variables on :root. Call from browser only.
 */
export function applySunTheme() {
	if (typeof document === 'undefined' || typeof window === 'undefined') return;

	const root = document.documentElement;

	if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
		root.style.removeProperty('--sky-gradient');
		root.style.removeProperty('--shadow-card');
		root.style.removeProperty('--shadow-soft');
		return;
	}

	const t = computeSunTheme(new Date());
	root.style.setProperty('--sky-gradient', t.gradient);
	root.style.setProperty('--shadow-card', t.shadowCard);
	root.style.setProperty('--shadow-soft', t.shadowSoft);
}
