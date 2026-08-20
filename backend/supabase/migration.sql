-- BrightSmile Dental Clinic - appointments table
-- Paste this into the Supabase Dashboard SQL editor and run it.

-- 1) Create the table
create table if not exists public.appointments (
    id bigint generated always as identity primary key,
    name text not null,
    email text not null,
    phone text not null,
    preferred_date text not null,
    preferred_time text not null,
    reason text,
    status text not null default 'pending',
    receptionist_message text,
    created_at timestamptz not null default now()
);

-- If the table already exists, add the receptionist note used on rejection.
alter table public.appointments
    add column if not exists receptionist_message text;

-- 2) Enable RLS (defense in depth). Writes happen server-side with the
--    secret key, which bypasses RLS. Public/anonymous access stays locked.
alter table public.appointments enable row level security;

-- 3) Index on status so the receptionist can quickly find pending requests.
create index if not exists appointments_status_idx on public.appointments (status);

-- Optional: allow the receptionist to see rows from the dashboard with an
-- authenticated Supabase session. Comment out until you set up roles if unused.
-- create policy "receptionist can view own clinic requests"
--     on public.appointments for select
--     to authenticated
--     using (true);
