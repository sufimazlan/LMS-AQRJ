-- Milestone 0: accounts, roles, learner profiles and consent records.
--
-- Rules every later migration must keep:
--   * Every table has row-level security switched on and starts with no access.
--   * The browser gets only the grants listed here. Anything sensitive goes
--     through a function that checks its own rules.
--   * Helper functions live in the "private" schema, which the API does not expose.

create schema if not exists private;
revoke all on schema private from public;
grant usage on schema private to authenticated, service_role;

create type public.user_role as enum ('admin', 'guru');

-- One row per sign-in. Created by a trigger when someone signs up.
create table public.accounts (
	id uuid primary key references auth.users (id) on delete cascade,
	full_name text not null default '' check (char_length(full_name) <= 120),
	phone text check (phone is null or char_length(phone) <= 20),
	locale text not null default 'ms' check (locale in ('ms', 'en')),
	created_at timestamptz not null default now(),
	updated_at timestamptz not null default now()
);

-- Staff roles. Granted by an admin in the dashboard, never from the browser.
create table public.user_roles (
	account_id uuid not null references public.accounts (id) on delete cascade,
	role public.user_role not null,
	granted_at timestamptz not null default now(),
	primary key (account_id, role)
);

-- The people who learn. A parent account can hold several.
create table public.learners (
	id uuid primary key default gen_random_uuid(),
	account_id uuid not null references public.accounts (id) on delete cascade,
	display_name text not null check (char_length(btrim(display_name)) between 1 and 60),
	birth_year smallint check (birth_year between 1900 and 2100),
	gender text check (gender in ('L', 'P')),
	is_self boolean not null default false,
	created_at timestamptz not null default now(),
	archived_at timestamptz
);

create index learners_account_id_idx on public.learners (account_id);

-- An account has at most one profile for the account holder.
create unique index learners_one_self_idx on public.learners (account_id)
	where is_self and archived_at is null;

-- Proof of what was agreed to, and when (PDPA).
create table public.consents (
	id uuid primary key default gen_random_uuid(),
	account_id uuid not null references public.accounts (id) on delete cascade,
	learner_id uuid references public.learners (id) on delete cascade,
	kind text not null check (kind in ('privacy_notice', 'guardian_consent', 'recording')),
	version text not null check (char_length(version) between 1 and 40),
	accepted_at timestamptz not null default now()
);

create index consents_account_id_idx on public.consents (account_id);
create index consents_learner_id_idx on public.consents (learner_id);

-- Helpers ------------------------------------------------------------------

create function private.set_updated_at() returns trigger
language plpgsql set search_path = '' as $$
begin
	new.updated_at := now();
	return new;
end;
$$;

create trigger accounts_set_updated_at before update on public.accounts
	for each row execute function private.set_updated_at();

create function private.handle_new_user() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
	insert into public.accounts (id, full_name)
	values (new.id, left(coalesce(new.raw_user_meta_data ->> 'full_name', ''), 120));
	return new;
end;
$$;

create trigger on_auth_user_created after insert on auth.users
	for each row execute function private.handle_new_user();

-- Security definer so that policies can ask about roles without the caller
-- needing to read every row of user_roles.
create function private.has_role(p_role public.user_role) returns boolean
language sql stable security definer set search_path = '' as $$
	select exists (
		select 1 from public.user_roles
		where account_id = (select auth.uid()) and role = p_role
	);
$$;

revoke all on function private.set_updated_at() from public;
revoke all on function private.handle_new_user() from public;
revoke all on function private.has_role(public.user_role) from public;
grant execute on function private.has_role(public.user_role) to authenticated, service_role;

-- Row-level security -------------------------------------------------------

alter table public.accounts enable row level security;
alter table public.user_roles enable row level security;
alter table public.learners enable row level security;
alter table public.consents enable row level security;

create policy accounts_select on public.accounts for select to authenticated
	using (id = (select auth.uid()) or (select private.has_role('admin')));
create policy accounts_update on public.accounts for update to authenticated
	using (id = (select auth.uid())) with check (id = (select auth.uid()));

create policy user_roles_select on public.user_roles for select to authenticated
	using (account_id = (select auth.uid()) or (select private.has_role('admin')));

create policy learners_select on public.learners for select to authenticated
	using (account_id = (select auth.uid()) or (select private.has_role('admin')));
create policy learners_update on public.learners for update to authenticated
	using (account_id = (select auth.uid())) with check (account_id = (select auth.uid()));

create policy consents_select on public.consents for select to authenticated
	using (account_id = (select auth.uid()) or (select private.has_role('admin')));

-- Grants: start from nothing, then add the least that the app needs.
revoke all on public.accounts, public.user_roles, public.learners, public.consents
	from anon, authenticated;

grant select on public.accounts, public.user_roles, public.learners, public.consents
	to authenticated;
grant update (full_name, phone, locale) on public.accounts to authenticated;
grant update (display_name, birth_year, gender, archived_at) on public.learners to authenticated;
grant all on public.accounts, public.user_roles, public.learners, public.consents
	to service_role;

-- Creating a learner -------------------------------------------------------

-- The only way the app creates a learner. It writes the learner and the
-- consent records together, so one can never exist without the other.
create function public.create_learner(
	p_display_name text,
	p_is_self boolean,
	p_birth_year integer default null,
	p_gender text default null,
	p_privacy_version text default null,
	p_guardian_confirmed boolean default false
) returns public.learners
language plpgsql security definer set search_path = '' as $$
declare
	v_account uuid := (select auth.uid());
	v_name text := btrim(coalesce(p_display_name, ''));
	v_year integer := extract(year from now())::integer;
	v_learner public.learners;
begin
	if v_account is null then
		raise exception 'Not signed in' using errcode = '28000';
	end if;
	if p_is_self is null then
		raise exception 'is_self is required' using errcode = '22023';
	end if;
	if coalesce(btrim(p_privacy_version), '') = '' then
		raise exception 'The privacy notice must be accepted' using errcode = '22023';
	end if;
	if char_length(v_name) not between 1 and 60 then
		raise exception 'The name must have 1 to 60 characters' using errcode = '22023';
	end if;
	if p_birth_year is not null and p_birth_year not between v_year - 100 and v_year then
		raise exception 'The birth year is out of range' using errcode = '22023';
	end if;
	if p_gender is not null and p_gender not in ('L', 'P') then
		raise exception 'Unknown gender value' using errcode = '22023';
	end if;
	if p_is_self and p_birth_year is not null and v_year - p_birth_year < 18 then
		raise exception 'An account holder must be an adult' using errcode = '22023';
	end if;
	if not p_is_self and not coalesce(p_guardian_confirmed, false) then
		raise exception 'Parent or guardian consent is required' using errcode = '22023';
	end if;

	-- One account at a time, so two quick taps cannot pass the limit together.
	perform 1 from public.accounts where id = v_account for update;

	if (select count(*) from public.learners
		where account_id = v_account and archived_at is null) >= 10 then
		raise exception 'An account can hold up to 10 learners' using errcode = '54000';
	end if;

	insert into public.learners (account_id, display_name, birth_year, gender, is_self)
	values (v_account, v_name, p_birth_year, p_gender, p_is_self)
	returning * into v_learner;

	insert into public.consents (account_id, learner_id, kind, version)
	values (v_account, v_learner.id, 'privacy_notice', btrim(p_privacy_version));

	if not p_is_self then
		insert into public.consents (account_id, learner_id, kind, version)
		values (v_account, v_learner.id, 'guardian_consent', btrim(p_privacy_version));
	end if;

	return v_learner;
end;
$$;

revoke all on function public.create_learner(text, boolean, integer, text, text, boolean)
	from public, anon;
grant execute on function public.create_learner(text, boolean, integer, text, text, boolean)
	to authenticated;
