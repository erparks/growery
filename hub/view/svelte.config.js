import adapter from '@sveltejs/adapter-static';

export default {
	kit: {
		adapter: adapter({
			// default options are shown. On some platforms
			// these options are set automatically — see below
			pages: "../../hub/backend/static",
			assets: '../../hub/backend/static',
			fallback: undefined,
			precompress: false,
			strict: true,
		}),
		// router: true,
		paths: {
			base: '',
		}
	}
};