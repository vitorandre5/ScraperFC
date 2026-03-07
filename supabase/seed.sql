insert into public.sports (key, name)
values ('football', 'Football')
on conflict (key) do nothing;
