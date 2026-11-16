/** Chrome and Android fire this when the app can be installed. It is not in the DOM typings yet. */
interface BeforeInstallPromptEvent extends Event {
	prompt(): Promise<void>;
	readonly userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

/**
 * Tracks whether the app can be installed to the home screen.
 * Android offers a prompt; iPhone has no prompt, so we show instructions instead.
 */
class InstallState {
	canPrompt = $state(false);
	installed = $state(false);
	isIos = $state(false);
	#event: BeforeInstallPromptEvent | null = null;
	#started = false;

	/** Must run early: the browser fires `beforeinstallprompt` soon after load. */
	start(): void {
		if (this.#started || typeof window === 'undefined') return;
		this.#started = true;

		const iosStandalone = (navigator as Navigator & { standalone?: boolean }).standalone === true;
		this.installed = iosStandalone || window.matchMedia('(display-mode: standalone)').matches;
		this.isIos = /iphone|ipad|ipod/i.test(navigator.userAgent);

		window.addEventListener('beforeinstallprompt', (event) => {
			event.preventDefault();
			this.#event = event as BeforeInstallPromptEvent;
			this.canPrompt = true;
		});

		window.addEventListener('appinstalled', () => {
			this.installed = true;
			this.canPrompt = false;
			this.#event = null;
		});
	}

	async prompt(): Promise<void> {
		const event = this.#event;
		if (!event) return;

		await event.prompt();
		await event.userChoice;

		// A prompt event can be used once.
		this.#event = null;
		this.canPrompt = false;
	}
}

export const install = new InstallState();
