-- Milestone 1: levels, lessons, video links, quizzes and progress.
--
-- Who may open what:
--   * Any signed-in person sees the list of published levels and lesson titles.
--   * The video link and the quiz of a lesson are readable only when the
--     account's plan covers the lesson's level. This is checked here, in the
--     database, not in the app.
--   * Progress and quiz results are written only by the two functions at the end.

create type public.plan_id as enum ('percuma', 'asas', 'penuh');

create table public.levels (
	id uuid primary key default gen_random_uuid(),
	number smallint not null unique check (number > 0),
	title text not null check (char_length(title) between 1 and 120),
	summary text not null default '' check (char_length(summary) <= 400),
	plan public.plan_id not null default 'percuma',
	published boolean not null default false,
	created_at timestamptz not null default now()
);

create table public.lessons (
	id uuid primary key default gen_random_uuid(),
	level_id uuid not null references public.levels (id) on delete cascade,
	position smallint not null check (position > 0),
	title text not null check (char_length(title) between 1 and 120),
	summary text not null default '' check (char_length(summary) <= 400),
	duration_seconds integer check (duration_seconds >= 0),
	published boolean not null default false,
	created_at timestamptz not null default now(),
	unique (level_id, position)
);

-- Kept apart from lessons so that the title can be public while the link is not.
create table public.lesson_media (
	lesson_id uuid primary key references public.lessons (id) on delete cascade,
	provider text not null check (provider in ('youtube')),
	ref text not null check (char_length(ref) between 1 and 200)
);

create table public.quiz_questions (
	id uuid primary key default gen_random_uuid(),
	lesson_id uuid not null references public.lessons (id) on delete cascade,
	position smallint not null check (position > 0),
	prompt text not null check (char_length(prompt) between 1 and 400),
	options jsonb not null check (
		jsonb_typeof(options) = 'array' and jsonb_array_length(options) between 2 and 6
	),
	correct_index smallint not null check (correct_index >= 0),
	unique (lesson_id, position),
	check (correct_index < jsonb_array_length(options))
);

create table public.lesson_progress (
	learner_id uuid not null references public.learners (id) on delete cascade,
	lesson_id uuid not null references public.lessons (id) on delete cascade,
	completed_at timestamptz not null default now(),
	primary key (learner_id, lesson_id)
);

create index lesson_progress_lesson_id_idx on public.lesson_progress (lesson_id);

create table public.quiz_attempts (
	id uuid primary key default gen_random_uuid(),
	learner_id uuid not null references public.learners (id) on delete cascade,
	lesson_id uuid not null references public.lessons (id) on delete cascade,
	score smallint not null,
	total smallint not null,
	passed boolean not null,
	created_at timestamptz not null default now()
);

create index quiz_attempts_learner_lesson_idx on public.quiz_attempts (learner_id, lesson_id);
create index quiz_attempts_lesson_id_idx on public.quiz_attempts (lesson_id);

-- Helpers ------------------------------------------------------------------

-- The plan of the signed-in account. Everyone is on the free plan until
-- payments arrive in Milestone 2, which replaces the body of this function.
create function private.account_plan() returns public.plan_id
language sql stable security definer set search_path = '' as $$
	select 'percuma'::public.plan_id;
$$;

create function private.can_open_lesson(p_lesson uuid) returns boolean
language sql stable security definer set search_path = '' as $$
	select (select private.has_role('admin')) or exists (
		select 1
		from public.lessons l
		join public.levels v on v.id = l.level_id
		where l.id = p_lesson and l.published and v.published
			and v.plan <= (select private.account_plan())
	);
$$;

create function private.owns_learner(p_learner uuid) returns boolean
language sql stable security definer set search_path = '' as $$
	select exists (
		select 1 from public.learners
		where id = p_learner and account_id = (select auth.uid()) and archived_at is null
	);
$$;

revoke all on function private.account_plan() from public;
revoke all on function private.can_open_lesson(uuid) from public;
revoke all on function private.owns_learner(uuid) from public;
grant execute on function private.account_plan() to authenticated, service_role;
grant execute on function private.can_open_lesson(uuid) to authenticated, service_role;
grant execute on function private.owns_learner(uuid) to authenticated, service_role;

-- Row-level security -------------------------------------------------------

alter table public.levels enable row level security;
alter table public.lessons enable row level security;
alter table public.lesson_media enable row level security;
alter table public.quiz_questions enable row level security;
alter table public.lesson_progress enable row level security;
alter table public.quiz_attempts enable row level security;

create policy levels_select on public.levels for select to authenticated
	using (published or (select private.has_role('admin')));
create policy levels_admin on public.levels for all to authenticated
	using ((select private.has_role('admin'))) with check ((select private.has_role('admin')));

create policy lessons_select on public.lessons for select to authenticated
	using (
		(published and exists (select 1 from public.levels v where v.id = level_id and v.published))
		or (select private.has_role('admin'))
	);
create policy lessons_admin on public.lessons for all to authenticated
	using ((select private.has_role('admin'))) with check ((select private.has_role('admin')));

create policy lesson_media_select on public.lesson_media for select to authenticated
	using (private.can_open_lesson(lesson_id));
create policy lesson_media_admin on public.lesson_media for all to authenticated
	using ((select private.has_role('admin'))) with check ((select private.has_role('admin')));

create policy quiz_questions_select on public.quiz_questions for select to authenticated
	using (private.can_open_lesson(lesson_id));
create policy quiz_questions_admin on public.quiz_questions for all to authenticated
	using ((select private.has_role('admin'))) with check ((select private.has_role('admin')));

create policy lesson_progress_select on public.lesson_progress for select to authenticated
	using (private.owns_learner(learner_id) or (select private.has_role('admin')));

create policy quiz_attempts_select on public.quiz_attempts for select to authenticated
	using (private.owns_learner(learner_id) or (select private.has_role('admin')));

revoke all on public.levels, public.lessons, public.lesson_media, public.quiz_questions,
	public.lesson_progress, public.quiz_attempts from anon, authenticated;

-- Row-level security limits the write grants below to admins.
grant select, insert, update, delete on public.levels, public.lessons, public.lesson_media
	to authenticated;
-- The answer column is never readable from the browser.
grant select (id, lesson_id, position, prompt, options) on public.quiz_questions to authenticated;
grant insert, update, delete on public.quiz_questions to authenticated;
grant select on public.lesson_progress, public.quiz_attempts to authenticated;
grant all on public.levels, public.lessons, public.lesson_media, public.quiz_questions,
	public.lesson_progress, public.quiz_attempts to service_role;

-- Writing progress ---------------------------------------------------------

create function private.check_lesson_access(p_learner uuid, p_lesson uuid) returns void
language plpgsql stable security definer set search_path = '' as $$
begin
	if (select auth.uid()) is null then
		raise exception 'Not signed in' using errcode = '28000';
	end if;
	if not private.owns_learner(p_learner) then
		raise exception 'Not your learner' using errcode = '42501';
	end if;
	if not private.can_open_lesson(p_lesson) then
		raise exception 'This lesson is not in your plan' using errcode = '42501';
	end if;
end;
$$;

revoke all on function private.check_lesson_access(uuid, uuid) from public;

-- Marks a lesson done. Lessons with a quiz are completed by passing the quiz instead.
create function public.complete_lesson(p_learner uuid, p_lesson uuid) returns void
language plpgsql security definer set search_path = '' as $$
begin
	perform private.check_lesson_access(p_learner, p_lesson);

	if exists (select 1 from public.quiz_questions where lesson_id = p_lesson) then
		raise exception 'Pass the quiz to complete this lesson' using errcode = '22023';
	end if;

	insert into public.lesson_progress (learner_id, lesson_id)
	values (p_learner, p_lesson)
	on conflict do nothing;
end;
$$;

-- Marks the answers, records the attempt, and completes the lesson on a pass
-- (80% or more). Returns the result with the right answers for review.
create function public.submit_quiz(p_learner uuid, p_lesson uuid, p_answers integer[])
returns jsonb
language plpgsql security definer set search_path = '' as $$
declare
	v_total integer;
	v_score integer;
	v_correct jsonb;
	v_passed boolean;
begin
	perform private.check_lesson_access(p_learner, p_lesson);

	select count(*), jsonb_agg(correct_index order by position)
	into v_total, v_correct
	from public.quiz_questions where lesson_id = p_lesson;

	if v_total = 0 then
		raise exception 'This lesson has no quiz' using errcode = '22023';
	end if;
	if coalesce(array_length(p_answers, 1), 0) <> v_total then
		raise exception 'Answer every question' using errcode = '22023';
	end if;

	select count(*) into v_score
	from (
		select correct_index, row_number() over (order by position) as n
		from public.quiz_questions where lesson_id = p_lesson
	) q
	where p_answers[q.n] = q.correct_index;

	v_passed := v_score * 5 >= v_total * 4;

	insert into public.quiz_attempts (learner_id, lesson_id, score, total, passed)
	values (p_learner, p_lesson, v_score, v_total, v_passed);

	if v_passed then
		insert into public.lesson_progress (learner_id, lesson_id)
		values (p_learner, p_lesson)
		on conflict do nothing;
	end if;

	return jsonb_build_object(
		'score', v_score, 'total', v_total, 'passed', v_passed, 'correct', v_correct
	);
end;
$$;

revoke all on function public.complete_lesson(uuid, uuid) from public, anon;
revoke all on function public.submit_quiz(uuid, uuid, integer[]) from public, anon;
grant execute on function public.complete_lesson(uuid, uuid) to authenticated;
grant execute on function public.submit_quiz(uuid, uuid, integer[]) to authenticated;
