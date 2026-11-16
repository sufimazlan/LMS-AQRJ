-- First content for a new database: the draft syllabus from src/lib/content/site.ts.
-- Safe to run more than once. Run it in the Supabase SQL Editor after the migrations.
-- Videos are added later: insert a row in lesson_media with the YouTube video ID.

insert into public.levels (number, title, summary, plan, published) values
	(1, 'Kenal huruf hijaiyah', 'Mengenal dan menyebut 28 huruf dengan makhraj yang betul.', 'percuma', true),
	(2, 'Baris dan sambung huruf', 'Baris atas, bawah dan depan, serta huruf bersambung (Iqra’ 1 dan 2).', 'percuma', true),
	(3, 'Mad dan tanwin', 'Bacaan panjang, tanwin dan sukun (Iqra’ 3 dan 4).', 'asas', true),
	(4, 'Lancar Iqra’', 'Sabdu, waqaf dan bacaan ayat penuh (Iqra’ 5 dan 6).', 'asas', true),
	(5, 'Tilawah Juz Amma', 'Membaca surah-surah pendek dengan lancar.', 'penuh', true),
	(6, 'Tajwid lengkap', 'Hukum nun mati, mim mati, mad dan sifat huruf.', 'penuh', true),
	(7, 'Tilawah Al-Quran', 'Membaca 30 juzuk dengan bimbingan dan semakan berkala.', 'penuh', true),
	(8, 'Hafazan surah pilihan', 'Menghafaz surah lazim dengan kaedah ulangan.', 'penuh', true)
on conflict (number) do nothing;

insert into public.lessons (level_id, position, title, published)
select v.id, x.position, x.title, true
from (values
	(1, 1, 'Huruf alif hingga kha'),
	(1, 2, 'Huruf dal hingga dhad'),
	(1, 3, 'Huruf tha hingga ya'),
	(1, 4, 'Ulang kaji'),
	(2, 1, 'Baris fathah'),
	(2, 2, 'Baris kasrah dan dhammah'),
	(2, 3, 'Huruf bersambung'),
	(2, 4, 'Latihan bacaan'),
	(3, 1, 'Mad asli'),
	(3, 2, 'Tanwin'),
	(3, 3, 'Sukun dan qalqalah'),
	(3, 4, 'Latihan bacaan'),
	(4, 1, 'Tasydid'),
	(4, 2, 'Alif lam'),
	(4, 3, 'Tanda waqaf'),
	(4, 4, 'Ujian tamat Iqra’'),
	(5, 1, 'An-Nas hingga Ad-Dhuha'),
	(5, 2, 'Al-Lail hingga Al-A’la'),
	(5, 3, 'At-Tariq hingga An-Naba’'),
	(6, 1, 'Nun mati dan tanwin'),
	(6, 2, 'Mim mati'),
	(6, 3, 'Jenis-jenis mad'),
	(6, 4, 'Makhraj dan sifat huruf'),
	(7, 1, 'Juzuk 1 hingga 10'),
	(7, 2, 'Juzuk 11 hingga 20'),
	(7, 3, 'Juzuk 21 hingga 30'),
	(8, 1, 'Kaedah menghafaz'),
	(8, 2, 'Surah lazim'),
	(8, 3, 'Yasin, Al-Mulk dan As-Sajdah')
) as x (level_number, position, title)
join public.levels v on v.number = x.level_number
on conflict (level_id, position) do nothing;

-- CONTOH: one sample quiz so the quiz screen can be tried. Replace with real questions.
insert into public.quiz_questions (lesson_id, position, prompt, options, correct_index)
select l.id, x.position, x.prompt, x.options::jsonb, x.correct_index
from (values
	(1, 'Berapakah bilangan huruf hijaiyah yang dipelajari dalam tahap ini?', '["26", "28", "30"]', 1),
	(2, 'Apakah huruf hijaiyah yang pertama?', '["Ba", "Alif", "Ta"]', 1)
) as x (position, prompt, options, correct_index)
join public.levels v on v.number = 1
join public.lessons l on l.level_id = v.id and l.position = 4
on conflict (lesson_id, position) do nothing;
