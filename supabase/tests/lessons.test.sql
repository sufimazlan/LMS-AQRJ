-- Run with: supabase test db
begin;
create extension if not exists pgtap with schema extensions;
select plan(17);

insert into auth.users (id, email) values
	('00000000-0000-0000-0000-00000000000a', 'a@example.test'),
	('00000000-0000-0000-0000-00000000000b', 'b@example.test');

insert into public.learners (id, account_id, display_name) values
	('10000000-0000-0000-0000-00000000000a', '00000000-0000-0000-0000-00000000000a', 'Aminah'),
	('10000000-0000-0000-0000-00000000000b', '00000000-0000-0000-0000-00000000000b', 'Bakar');

-- Start from no content: seed.sql may have run. This is undone by the rollback at the end.
delete from public.levels;

insert into public.levels (id, number, title, plan, published) values
	('20000000-0000-0000-0000-000000000001', 1, 'Percuma', 'percuma', true),
	('20000000-0000-0000-0000-000000000002', 2, 'Berbayar', 'asas', true),
	('20000000-0000-0000-0000-000000000003', 3, 'Draf', 'percuma', false);

insert into public.lessons (id, level_id, position, title, published) values
	('30000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', 1, 'Ada kuiz', true),
	('30000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000001', 2, 'Tiada kuiz', true),
	('30000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000002', 1, 'Berbayar', true),
	('30000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000003', 1, 'Draf', true);

insert into public.lesson_media (lesson_id, provider, ref) values
	('30000000-0000-0000-0000-000000000001', 'youtube', 'free'),
	('30000000-0000-0000-0000-000000000003', 'youtube', 'paid');

insert into public.quiz_questions (lesson_id, position, prompt, options, correct_index) values
	('30000000-0000-0000-0000-000000000001', 1, 'S1', '["a","b"]', 1),
	('30000000-0000-0000-0000-000000000001', 2, 'S2', '["a","b","c"]', 0),
	('30000000-0000-0000-0000-000000000003', 1, 'S3', '["a","b"]', 0);

set local role authenticated;
set local "request.jwt.claims" to '{"sub":"00000000-0000-0000-0000-00000000000a","role":"authenticated"}';

select is((select count(*)::int from public.levels), 2, 'only published levels are listed');
select is((select count(*)::int from public.lessons), 3, 'lessons of a draft level are hidden');
select is((select count(*)::int from public.lesson_media), 1, 'the video link of a paid lesson is hidden on the free plan');
select is((select count(*)::int from public.quiz_questions), 2, 'the quiz of a paid lesson is hidden on the free plan');
select throws_ok($$ select correct_index from public.quiz_questions $$,
	'42501', null, 'quiz answers cannot be read');
select throws_ok($$ insert into public.levels (number, title) values (9, 'x') $$,
	'42501', null, 'a learner cannot add a level');
select throws_ok(
	$$ insert into public.lesson_progress (learner_id, lesson_id)
	   values ('10000000-0000-0000-0000-00000000000a', '30000000-0000-0000-0000-000000000002') $$,
	'42501', null, 'progress cannot be written directly');

select throws_ok(
	$$ select public.complete_lesson('10000000-0000-0000-0000-00000000000a', '30000000-0000-0000-0000-000000000001') $$,
	'22023', null, 'a lesson with a quiz cannot be marked done by hand');
select lives_ok(
	$$ select public.complete_lesson('10000000-0000-0000-0000-00000000000a', '30000000-0000-0000-0000-000000000002') $$,
	'a lesson without a quiz can be marked done');
select throws_ok(
	$$ select public.complete_lesson('10000000-0000-0000-0000-00000000000a', '30000000-0000-0000-0000-000000000003') $$,
	'42501', null, 'a paid lesson cannot be completed on the free plan');
select throws_ok(
	$$ select public.complete_lesson('10000000-0000-0000-0000-00000000000b', '30000000-0000-0000-0000-000000000002') $$,
	'42501', null, 'progress cannot be written for someone else''s learner');

select is(
	public.submit_quiz('10000000-0000-0000-0000-00000000000a', '30000000-0000-0000-0000-000000000001', array[1, 2]) ->> 'passed',
	'false', 'one right answer out of two fails');
select is(
	public.submit_quiz('10000000-0000-0000-0000-00000000000a', '30000000-0000-0000-0000-000000000001', array[1, 0]) ->> 'passed',
	'true', 'all answers right passes');
select throws_ok(
	$$ select public.submit_quiz('10000000-0000-0000-0000-00000000000a', '30000000-0000-0000-0000-000000000001', array[1]) $$,
	'22023', null, 'every question must be answered');

select is((select count(*)::int from public.lesson_progress), 2, 'both lessons are now complete');
select is((select count(*)::int from public.quiz_attempts), 2, 'both attempts were recorded');

set local "request.jwt.claims" to '{"sub":"00000000-0000-0000-0000-00000000000b","role":"authenticated"}';
select is((select count(*)::int from public.lesson_progress), 0, 'B sees none of A''s progress');

select * from finish();
rollback;
