import { STORAGE_KEYS } from '#lib/config.js';
import { listLearners, type Learner } from './api.js';

function readStoredId(): string | null {
	try {
		return localStorage.getItem(STORAGE_KEYS.activeLearner);
	} catch {
		return null;
	}
}

function writeStoredId(id: string | null): void {
	try {
		if (id === null) localStorage.removeItem(STORAGE_KEYS.activeLearner);
		else localStorage.setItem(STORAGE_KEYS.activeLearner, id);
	} catch {
		// Storage can be unavailable (private mode). The choice then lasts for this visit only.
	}
}

/**
 * The account's learner profiles and which one is learning right now.
 * `list` is null until the first load finishes.
 */
class LearnerState {
	list = $state<Learner[] | null>(null);
	activeId = $state<string | null>(null);
	loadFailed = $state(false);
	#loading: Promise<void> | null = null;

	get active(): Learner | null {
		return this.list?.find((learner) => learner.id === this.activeId) ?? null;
	}

	/** Loads once per sign-in. Pass `force` to fetch again. */
	load(force = false): Promise<void> {
		if (this.#loading && !force) return this.#loading;

		this.#loading = (async () => {
			this.loadFailed = false;

			try {
				const list = await listLearners();
				const stored = this.activeId ?? readStoredId();

				this.list = list;
				// A stored choice from another account, or an archived learner, is dropped.
				this.activeId = list.some((learner) => learner.id === stored) ? stored : null;

				// With one learner there is nothing to pick.
				if (this.activeId === null && list.length === 1) this.choose(list[0].id);
			} catch {
				this.loadFailed = true;
				this.#loading = null;
			}
		})();

		return this.#loading;
	}

	choose(id: string): void {
		this.activeId = id;
		writeStoredId(id);
	}

	add(learner: Learner): void {
		this.list = [...(this.list ?? []), learner];
		this.choose(learner.id);
	}

	/** Called on sign-out so the next account starts clean. */
	reset(): void {
		this.list = null;
		this.activeId = null;
		this.loadFailed = false;
		this.#loading = null;
		writeStoredId(null);
	}
}

export const learners = new LearnerState();
