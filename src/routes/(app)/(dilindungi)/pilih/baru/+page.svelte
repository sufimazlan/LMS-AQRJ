<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { createLearner, type CreateLearnerFailure } from '#lib/learners/api.js';
	import { learners } from '#lib/learners/store.svelte.js';
	import {
		birthYearOptions,
		MAX_NAME_LENGTH,
		validateLearner,
		type LearnerErrorCode,
		type LearnerErrors
	} from '#lib/learners/validate.js';
	import { m } from '#lib/paraglide/messages.js';
	import type { Gender } from '#lib/supabase/database.types.js';
	import Notice from '#lib/ui/Notice.svelte';

	const thisYear = new Date().getFullYear();
	const years = birthYearOptions(thisYear);

	const errorText: Record<LearnerErrorCode, () => string> = {
		name_required: m.learner_err_name_required,
		name_too_long: m.learner_err_name_too_long,
		birth_year_invalid: m.learner_err_birth_year_invalid,
		minor_needs_guardian: m.learner_err_minor_needs_guardian,
		guardian_required: m.learner_err_guardian_required,
		privacy_required: m.learner_err_privacy_required
	};

	const failureText: Record<CreateLearnerFailure, () => string> = {
		self_exists: m.learner_err_self_exists,
		limit_reached: m.learner_err_limit_reached,
		rejected: m.learner_err_rejected,
		unknown: m.common_error_generic
	};

	let displayName = $state('');
	let who = $state<'self' | 'child'>('self');
	let birthYear = $state('');
	let gender = $state<Gender | ''>('');
	let privacyAccepted = $state(false);
	let guardianConfirmed = $state(false);

	let errors = $state<LearnerErrors>({});
	let failure = $state<CreateLearnerFailure | null>(null);
	let saving = $state(false);

	$effect(() => {
		void learners.load();
	});

	const isFirst = $derived(learners.list !== null && learners.list.length === 0);
	// An account has at most one profile for the account holder.
	const selfTaken = $derived(learners.list?.some((learner) => learner.is_self) ?? false);
	const isSelf = $derived(who === 'self' && !selfTaken);

	async function save(event: SubmitEvent) {
		event.preventDefault();
		failure = null;

		const result = validateLearner(
			{
				displayName,
				isSelf,
				birthYear: birthYear === '' ? null : Number(birthYear),
				gender: gender === '' ? null : gender,
				privacyAccepted,
				guardianConfirmed
			},
			thisYear
		);

		if (!result.ok) {
			errors = result.errors;
			return;
		}

		errors = {};
		saving = true;
		const created = await createLearner(result.values);
		saving = false;

		if (!created.ok) {
			failure = created.reason;
			return;
		}

		learners.add(created.learner);
		void goto(resolve('/(app)/(dilindungi)/belajar'));
	}
</script>

<svelte:head>
	<title>{m.learner_new_page_title()}</title>
</svelte:head>

<main class="mx-auto w-full max-w-md px-4 py-10">
	<h1 class="text-3xl font-bold">{m.learner_new_title()}</h1>
	{#if isFirst}
		<p class="mt-2 text-lg text-ink-soft">{m.learner_new_lead_first()}</p>
	{/if}

	<form onsubmit={save} class="mt-8 space-y-6" novalidate>
		{#if failure}
			<Notice tone="error">{failureText[failure]()}</Notice>
		{/if}

		{#if !selfTaken}
			<fieldset>
				<legend class="label">{m.learner_who_label()}</legend>
				<div class="grid gap-2">
					<label class="card flex min-h-12 cursor-pointer items-center gap-3 py-3">
						<input type="radio" name="who" value="self" bind:group={who} class="size-5" />
						<span>{m.learner_who_self()}</span>
					</label>
					<label class="card flex min-h-12 cursor-pointer items-center gap-3 py-3">
						<input type="radio" name="who" value="child" bind:group={who} class="size-5" />
						<span>{m.learner_who_child()}</span>
					</label>
				</div>
			</fieldset>
		{/if}

		<div>
			<label for="display-name" class="label">{m.learner_name_label()}</label>
			<input
				id="display-name"
				name="display-name"
				type="text"
				class="field"
				autocomplete="off"
				maxlength={MAX_NAME_LENGTH}
				aria-invalid={errors.displayName ? 'true' : undefined}
				aria-describedby="display-name-help"
				bind:value={displayName}
			/>
			<p id="display-name-help" class={errors.displayName ? 'error-text' : 'hint'}>
				{errors.displayName ? errorText[errors.displayName]() : m.learner_name_hint()}
			</p>
		</div>

		<div>
			<label for="birth-year" class="label">{m.learner_birth_year_label()}</label>
			<select
				id="birth-year"
				name="birth-year"
				class="field"
				aria-invalid={errors.birthYear ? 'true' : undefined}
				aria-describedby={errors.birthYear ? 'birth-year-error' : undefined}
				bind:value={birthYear}
			>
				<option value="">{m.learner_not_stated()}</option>
				{#each years as year (year)}
					<option value={String(year)}>{year}</option>
				{/each}
			</select>
			{#if errors.birthYear}
				<p id="birth-year-error" class="error-text">{errorText[errors.birthYear]()}</p>
			{/if}
		</div>

		<div>
			<label for="gender" class="label">{m.learner_gender_label()}</label>
			<select
				id="gender"
				name="gender"
				class="field"
				aria-describedby="gender-help"
				bind:value={gender}
			>
				<option value="">{m.learner_not_stated()}</option>
				<option value="L">{m.learner_gender_male()}</option>
				<option value="P">{m.learner_gender_female()}</option>
			</select>
			<p id="gender-help" class="hint">{m.learner_gender_hint()}</p>
		</div>

		<div class="space-y-3">
			{#if !isSelf}
				<div>
					<label class="flex cursor-pointer items-start gap-3">
						<input
							type="checkbox"
							class="mt-1 size-5 shrink-0"
							aria-invalid={errors.guardianConfirmed ? 'true' : undefined}
							aria-describedby={errors.guardianConfirmed ? 'guardian-error' : undefined}
							bind:checked={guardianConfirmed}
						/>
						<span>{m.learner_guardian_confirm()}</span>
					</label>
					{#if errors.guardianConfirmed}
						<p id="guardian-error" class="error-text">
							{errorText[errors.guardianConfirmed]()}
						</p>
					{/if}
				</div>
			{/if}

			<div>
				<label class="flex cursor-pointer items-start gap-3">
					<input
						type="checkbox"
						class="mt-1 size-5 shrink-0"
						aria-invalid={errors.privacyAccepted ? 'true' : undefined}
						aria-describedby={errors.privacyAccepted ? 'privacy-error' : undefined}
						bind:checked={privacyAccepted}
					/>
					<span>
						{isSelf ? m.learner_privacy_self() : m.learner_privacy_guardian()}
						<a
							href={resolve('/(public)/privasi')}
							target="_blank"
							rel="noopener"
							class="underline underline-offset-4">{m.footer_privacy()}</a
						>.
					</span>
				</label>
				{#if errors.privacyAccepted}
					<p id="privacy-error" class="error-text">{errorText[errors.privacyAccepted]()}</p>
				{/if}
			</div>
		</div>

		<button type="submit" class="btn btn-primary w-full" disabled={saving}>
			{saving ? m.learner_saving() : m.learner_submit()}
		</button>
	</form>
</main>
