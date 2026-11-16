<script lang="ts">
	import { submitQuiz, type Question, type QuizResult } from '#lib/courses/api.js';
	import { m } from '#lib/paraglide/messages.js';
	import Notice from './Notice.svelte';

	// The answers are marked in the database, which never sends the right
	// answers to the browser before the learner submits.
	let {
		learnerId,
		lessonId,
		questions,
		onpassed
	}: {
		learnerId: string;
		lessonId: string;
		questions: Question[];
		onpassed: () => void;
	} = $props();

	/** The chosen option for each question, by question order. Empty until answered. */
	let chosen = $state<number[]>([]);
	let result = $state<QuizResult | null>(null);
	let sending = $state(false);
	let problem = $state<'unanswered' | 'failed' | null>(null);

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		const answers = questions.map((_, index) => chosen[index]);
		if (answers.some((answer) => answer === undefined)) {
			problem = 'unanswered';
			return;
		}

		problem = null;
		sending = true;
		try {
			result = await submitQuiz(learnerId, lessonId, answers);
			if (result.passed) onpassed();
		} catch {
			problem = 'failed';
		}
		sending = false;
	}

	function retry() {
		chosen = [];
		result = null;
	}
</script>

<section class="mt-8" aria-labelledby="quiz-title">
	<h2 id="quiz-title" class="text-xl font-bold">{m.quiz_title()}</h2>
	<p class="mt-1 text-ink-soft">{m.quiz_lead()}</p>

	<form onsubmit={submit} class="mt-4 space-y-5">
		{#each questions as question, index (question.id)}
			<fieldset class="card" disabled={result !== null}>
				<legend class="float-left mb-3 w-full font-semibold">
					{index + 1}. {question.prompt}
				</legend>
				<div class="clear-both grid gap-2">
					{#each question.options as option, optionIndex (optionIndex)}
						{@const isCorrect = result?.correct[index] === optionIndex}
						{@const isWrongPick = result !== null && chosen[index] === optionIndex && !isCorrect}
						<label
							class={[
								'flex min-h-12 cursor-pointer items-center gap-3 rounded-xl border px-3 py-2',
								isCorrect
									? 'border-brand-500 bg-brand-50'
									: isWrongPick
										? 'border-red-300 bg-red-50'
										: 'border-sand-200'
							]}
						>
							<input
								type="radio"
								name="q-{question.id}"
								value={optionIndex}
								bind:group={chosen[index]}
								class="size-5"
							/>
							<span class="flex-1">{option}</span>
							{#if isCorrect}
								<span class="text-sm font-medium text-brand-800">{m.quiz_correct_answer()}</span>
							{/if}
						</label>
					{/each}
				</div>
			</fieldset>
		{/each}

		{#if problem === 'unanswered'}
			<Notice tone="error">{m.quiz_unanswered()}</Notice>
		{:else if problem === 'failed'}
			<Notice tone="error">{m.common_error_generic()}</Notice>
		{/if}

		{#if result === null}
			<button type="submit" class="btn btn-primary w-full" disabled={sending}>
				{sending ? m.quiz_sending() : m.quiz_submit()}
			</button>
		{:else if result.passed}
			<Notice tone="success">
				{m.quiz_passed({ score: result.score, total: result.total })}
			</Notice>
		{:else}
			<Notice tone="error">{m.quiz_failed({ score: result.score, total: result.total })}</Notice>
			<button type="button" class="btn btn-secondary w-full" onclick={retry}>
				{m.quiz_retry()}
			</button>
		{/if}
	</form>
</section>
