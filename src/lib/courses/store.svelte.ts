import { SvelteSet } from 'svelte/reactivity';
import type { PlanId } from '#lib/content/site.js';
import { loadCatalog, loadCompleted } from './api.js';
import type { Level } from './catalog.js';

/**
 * The levels and the active learner's finished lessons, loaded once and
 * shared by the home, level and lesson screens.
 */
class CourseState {
	catalog = $state<Level[] | null>(null);
	completed = new SvelteSet<string>();
	loadFailed = $state(false);

	// Everyone is on the free plan until payments arrive (Milestone 2).
	// The database enforces the same rule in private.account_plan().
	readonly plan: PlanId = 'percuma';

	#learnerId: string | null = null;
	#loading: Promise<void> | null = null;

	/** Loads for this learner. Calling again for the same learner does nothing. */
	load(learnerId: string, force = false): Promise<void> {
		if (this.#loading && this.#learnerId === learnerId && !force) return this.#loading;
		this.#learnerId = learnerId;

		this.#loading = (async () => {
			this.loadFailed = false;
			try {
				const [catalog, completed] = await Promise.all([loadCatalog(), loadCompleted(learnerId)]);
				if (this.#learnerId !== learnerId) return;
				this.catalog = catalog;
				this.completed.clear();
				for (const id of completed) this.completed.add(id);
			} catch {
				if (this.#learnerId === learnerId) this.loadFailed = true;
			}
		})();

		return this.#loading;
	}

	markCompleted(lessonId: string): void {
		this.completed.add(lessonId);
	}

	reset(): void {
		this.catalog = null;
		this.completed.clear();
		this.loadFailed = false;
		this.#learnerId = null;
		this.#loading = null;
	}
}

export const courses = new CourseState();
