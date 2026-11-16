// Fails the build when the app gets heavier than agreed.
//
// Run after `npm run build`:  npm run check:bundle
//
// What it checks, on the files that will actually be deployed:
//   1. Public pages (landing, privacy, offline) ship no JavaScript at all.
//   2. No app page needs more JavaScript on first load than the budget below.
//   3. The stylesheet stays within its budget.
//
// Sizes are gzipped, which is close to what a phone downloads. If a check
// fails, look for a new dependency or a missing dynamic import before raising
// a budget, and say why in the pull request when you do raise one.
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { gzipSync } from 'node:zlib';

const OUTPUT_DIR = '.svelte-kit/cloudflare';

/** Budgets in kilobytes, gzipped. */
const BUDGET = {
	firstLoadJsPerPage: 90,
	css: 12
};

/** Pages that must work without JavaScript. */
const NO_SCRIPT_PAGES = ['index.html', 'privasi.html', 'offline.html'];

if (!existsSync(OUTPUT_DIR)) {
	console.error(`Nothing to check: ${OUTPUT_DIR} does not exist. Run "npm run build" first.`);
	process.exit(1);
}

/** @param {string} dir @returns {string[]} */
function walk(dir) {
	return readdirSync(dir).flatMap((name) => {
		const path = join(dir, name);
		return statSync(path).isDirectory() ? walk(path) : [path];
	});
}

/** @type {Map<string, number>} */
const gzipCache = new Map();

/** @param {string} path @returns {number} Size in bytes after gzip. */
function gzipSize(path) {
	let size = gzipCache.get(path);
	if (size === undefined) {
		size = gzipSync(readFileSync(path), { level: 9 }).length;
		gzipCache.set(path, size);
	}
	return size;
}

/** @param {number} bytes */
const kb = (bytes) => `${(bytes / 1024).toFixed(1)} kB`;

const files = walk(OUTPUT_DIR);
const pages = files.filter((path) => path.endsWith('.html'));
const problems = [];

// 1. Public pages ship no JavaScript.
for (const name of NO_SCRIPT_PAGES) {
	const path = join(OUTPUT_DIR, name);
	if (!existsSync(path)) {
		problems.push(`${name} is missing from the build output.`);
	} else if (/<script[\s>]/i.test(readFileSync(path, 'utf8'))) {
		problems.push(`${name} contains a <script> tag. Public pages must ship no JavaScript.`);
	}
}

// 2. First-load JavaScript for each app page: the scripts its HTML asks the
//    browser to fetch straight away (preloaded modules and the start script).
const scriptReference = /["'(](\/_app\/immutable\/[^"')]+\.js)["')]/g;

const firstLoads = pages
	.filter((path) => !NO_SCRIPT_PAGES.includes(relative(OUTPUT_DIR, path)))
	.map((path) => {
		const html = readFileSync(path, 'utf8');
		const scripts = new Set([...html.matchAll(scriptReference)].map((match) => match[1]));
		const bytes = [...scripts].reduce((sum, src) => sum + gzipSize(join(OUTPUT_DIR, src)), 0);
		return { page: `/${relative(OUTPUT_DIR, path).replace(/\.html$/, '')}`, bytes };
	})
	.sort((a, b) => b.bytes - a.bytes);

for (const { page, bytes } of firstLoads) {
	if (bytes > BUDGET.firstLoadJsPerPage * 1024) {
		problems.push(
			`${page} needs ${kb(bytes)} of JavaScript on first load. The budget is ${BUDGET.firstLoadJsPerPage} kB.`
		);
	}
}

// 3. Stylesheets.
const cssBytes = files
	.filter((path) => path.endsWith('.css'))
	.reduce((sum, path) => sum + gzipSize(path), 0);

if (cssBytes > BUDGET.css * 1024) {
	problems.push(`The stylesheets add up to ${kb(cssBytes)}. The budget is ${BUDGET.css} kB.`);
}

// Report.
const allJsBytes = files
	.filter((path) => path.includes('/_app/immutable/') && path.endsWith('.js'))
	.reduce((sum, path) => sum + gzipSize(path), 0);

console.log('First-load JavaScript per app page (gzipped):');
for (const { page, bytes } of firstLoads) {
	console.log(`  ${kb(bytes).padStart(9)}  ${page}`);
}
console.log(`\nBudget per page: ${BUDGET.firstLoadJsPerPage} kB`);
console.log(`Stylesheets:     ${kb(cssBytes)} of ${BUDGET.css} kB`);
console.log(`All app JavaScript, every page together: ${kb(allJsBytes)}`);

if (problems.length > 0) {
	console.error('\nBundle check failed:');
	for (const problem of problems) console.error(`  - ${problem}`);
	process.exit(1);
}

console.log('\nBundle check passed.');
