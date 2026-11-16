-- Run with: supabase test db
begin;
create extension if not exists pgtap with schema extensions;
select plan(18);

insert into auth.users (id, email) values
	('00000000-0000-0000-0000-00000000000a', 'a@example.test'),
	('00000000-0000-0000-0000-00000000000b', 'b@example.test');

select is((select count(*)::int from public.accounts), 2, 'signing up creates an account row');

-- Person A ------------------------------------------------------------------
set local role authenticated;
set local "request.jwt.claims" to '{"sub":"00000000-0000-0000-0000-00000000000a","role":"authenticated"}';

select lives_ok(
	$$ select public.create_learner('Aminah', true, 1990, 'P', 'v1') $$,
	'A creates her own profile');
select lives_ok(
	$$ select public.create_learner('Adik', false, 2018, 'L', 'v1', true) $$,
	'A creates a child profile with guardian consent');
select throws_ok(
	$$ select public.create_learner('Anak', false, 2019, 'L', 'v1', false) $$,
	'22023', null, 'a child profile without guardian consent is refused');
select throws_ok(
	$$ select public.create_learner('Budak', true, extract(year from now())::int - 10, 'L', 'v1') $$,
	'22023', null, 'an account holder under 18 is refused');
select throws_ok(
	$$ select public.create_learner('Aminah lagi', true, 1990, 'P', 'v1') $$,
	'23505', null, 'a second own profile is refused');
select throws_ok(
	$$ select public.create_learner('Tanpa notis', false, 2015, 'L', null, true) $$,
	'22023', null, 'a profile without the privacy notice is refused');

select is((select count(*)::int from public.learners), 2, 'A sees her two learners');
select is((select count(*)::int from public.consents), 3, 'three consent records were written');
select is((select count(*)::int from public.accounts), 1, 'A sees only her own account');

select throws_ok(
	$$ insert into public.learners (account_id, display_name)
	   values ('00000000-0000-0000-0000-00000000000a', 'Terus') $$,
	'42501', null, 'learners cannot be inserted directly');
select throws_ok(
	$$ insert into public.user_roles (account_id, role)
	   values ('00000000-0000-0000-0000-00000000000a', 'admin') $$,
	'42501', null, 'nobody can give themselves a role');
select throws_ok(
	$$ update public.learners set is_self = false $$,
	'42501', null, 'is_self cannot be changed from the browser');

-- Person B ------------------------------------------------------------------
set local "request.jwt.claims" to '{"sub":"00000000-0000-0000-0000-00000000000b","role":"authenticated"}';

select is((select count(*)::int from public.learners), 0, 'B sees none of A''s learners');
select is((select count(*)::int from public.consents), 0, 'B sees none of A''s consents');
with changed as (update public.learners set display_name = 'x' returning 1)
select is((select count(*)::int from changed), 0, 'B cannot change A''s learners');

-- Not signed in ---------------------------------------------------------------
set local role anon;
set local "request.jwt.claims" to '{"role":"anon"}';

select throws_ok($$ select count(*) from public.learners $$,
	'42501', null, 'a visitor cannot read learners');
select throws_ok($$ select public.create_learner('X', true, 1990, 'L', 'v1') $$,
	'42501', null, 'a visitor cannot create a learner');

select * from finish();
rollback;
